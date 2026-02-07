"""
Service para gerenciamento de Eventos de Partida (Match Events).

Regras RAG aplicadas:
- RD1-RD91: Tipos de eventos estatísticos do handball
- R23/R24: Correção de eventos com histórico obrigatório
- RD4: Atleta deve estar no roster do jogo
- RF15: Eventos só editáveis enquanto match.status != finalizado
- RDB13: match_events com campos de correção
"""

import json
import logging
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context import ExecutionContext
from app.core.exceptions import (
    NotFoundError,
    ValidationError,
    ForbiddenError,
)
from app.models.match import Match, MatchStatus
from app.models.match_event import MatchEvent, EventType
from app.models.team_registration import TeamRegistration
from app.models.team import Team
from app.schemas.match_events import (
    MatchEventCreate,
    MatchEventUpdate,
    MatchEventCorrection,
    AthleteMatchStats,
)

logger = logging.getLogger(__name__)


class MatchEventService:
    """
    Service de Eventos de Partida.
    Ref: RD1-RD91, R23/R24, RD4, RF15
    """

    def __init__(self, db: AsyncSession, context: ExecutionContext):
        self.db = db
        self.context = context

    async def get_all_for_match(
        self,
        match_id: UUID,
        *,
        athlete_id: Optional[UUID] = None,
        event_type: Optional[EventType] = None,
        period: Optional[int] = None,
        include_deleted: bool = False,
        page: int = 1,
        size: int = 50,
    ) -> tuple[list[MatchEvent], int]:
        """
        Lista eventos de uma partida.
        Ref: RDB14 - Paginação padrão
        """
        # Verificar acesso à partida
        match = await self._get_match(match_id)

        query = select(MatchEvent).where(MatchEvent.match_id == match_id)

        if not include_deleted:
            query = query.where(MatchEvent.deleted_at.is_(None))

        if athlete_id:
            query = query.where(MatchEvent.athlete_id == athlete_id)

        if event_type:
            query = query.where(MatchEvent.event_type == event_type)

        if period:
            query = query.where(MatchEvent.period == period)

        # Count total - usar with_only_columns para evitar produto cartesiano
        count_query = query.with_only_columns(func.count()).order_by(None)
        result_count = await self.db.execute(count_query)
        total = result_count.scalar_one_or_none() or 0

        # Paginate e ordenar por período e minuto
        query = query.order_by(MatchEvent.period, MatchEvent.minute)
        query = query.offset((page - 1) * size).limit(size)

        result = await self.db.execute(query)
        events = list(result.scalars().all())

        return events, total

    async def get_by_id(
        self,
        event_id: UUID,
        *,
        include_deleted: bool = False,
    ) -> MatchEvent:
        """
        Busca evento por ID.
        """
        query = select(MatchEvent).where(MatchEvent.id == event_id)

        if not include_deleted:
            query = query.where(MatchEvent.deleted_at.is_(None))

        result = await self.db.execute(query)
        event = result.scalar_one_or_none()

        if not event:
            raise NotFoundError(f"Match event {event_id} not found")

        # Verificar acesso via match
        await self._get_match(event.match_id)

        return event

    async def create(self, data: MatchEventCreate) -> MatchEvent:
        """
        Cria novo evento.
        Ref: RD4 - Atleta deve estar no roster
        Ref: RF15 - Partida não pode estar finalizada
        """
        match = await self._get_match(data.match_id)

        # RF15: Verificar se partida permite edição
        if match.status == MatchStatus.finished:
            raise ForbiddenError(
                "Cannot add events to finalized match"
            )

        # RD4: Verificar se atleta está no roster do time
        await self._validate_athlete_in_roster(match.team_id, data.athlete_id)

        event = MatchEvent(
            match_id=data.match_id,
            athlete_id=data.athlete_id,
            event_type=data.event_type,
            minute=data.minute,
            period=data.period,
            x_position=data.x_position,
            y_position=data.y_position,
            notes=data.notes,
        )

        self.db.add(event)
        await self.db.flush()
        await self.db.refresh(event)

        logger.info(
            f"Created match event {event.id} ({event.event_type}) "
            f"for match {match.id} athlete {data.athlete_id}"
        )
        return event

    async def update(
        self,
        event_id: UUID,
        data: MatchEventUpdate,
    ) -> MatchEvent:
        """
        Atualiza evento (edição simples, sem histórico).
        Ref: RF15 - Partida não pode estar finalizada
        
        Usado para correções rápidas logo após registro.
        Para correções com histórico, usar correct().
        """
        event = await self.get_by_id(event_id)
        match = await self._get_match(event.match_id)

        # RF15: Verificar se partida permite edição
        if match.status == MatchStatus.finished:
            raise ForbiddenError(
                "Cannot edit events in finalized match"
            )

        # Atualizar campos
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(event, field, value)

        await self.db.flush()
        await self.db.refresh(event)

        logger.info(f"Updated match event {event_id}")
        return event

    async def correct(
        self,
        event_id: UUID,
        data: MatchEventCorrection,
    ) -> MatchEvent:
        """
        Corrige evento com histórico obrigatório.
        Ref: R23/R24 - Correção com justificativa e histórico
        
        Este método registra o valor anterior antes de aplicar a correção.
        Usado quando a partida está em status 'em_revisao' ou para
        correções tardias que precisam de auditoria.
        """
        event = await self.get_by_id(event_id)
        match = await self._get_match(event.match_id)

        # Permitir correção em em_revisao (não finalizado)
        if match.status == MatchStatus.finished:
            if not self.context.is_superadmin:
                raise ForbiddenError(
                    "Cannot correct events in finalized match. "
                    "SuperAdmin must reopen the match first."
                )

        # R23/R24: Salvar valores anteriores
        previous_values = {}
        update_data = data.model_dump(exclude={"correction_note"}, exclude_unset=True)
        
        for field, new_value in update_data.items():
            old_value = getattr(event, field)
            if old_value != new_value:
                # Converter enum para string se necessário
                if hasattr(old_value, "value"):
                    previous_values[field] = old_value.value
                else:
                    previous_values[field] = old_value
                setattr(event, field, new_value)

        if not previous_values:
            raise ValidationError("No changes detected in correction")

        # R23/R24: Registrar correção
        event.corrected_at = datetime.utcnow()
        event.correction_note = data.correction_note
        event.previous_value = json.dumps(previous_values)

        await self.db.flush()
        await self.db.refresh(event)

        logger.info(
            f"Corrected match event {event_id}: {previous_values} "
            f"by user {self.context.user_id}"
        )
        return event

    async def soft_delete(
        self,
        event_id: UUID,
        reason: str,
    ) -> MatchEvent:
        """
        Soft delete de evento.
        Ref: RDB3 - Soft delete
        """
        event = await self.get_by_id(event_id)
        match = await self._get_match(event.match_id)

        if match.status == MatchStatus.finished:
            if not self.context.is_superadmin:
                raise ForbiddenError(
                    "Cannot delete events in finalized match"
                )

        event.deleted_at = datetime.utcnow()
        event.deleted_reason = reason

        await self.db.flush()
        await self.db.refresh(event)

        logger.info(
            f"Soft deleted match event {event_id}: {reason}"
        )
        return event

    async def get_athlete_stats(
        self,
        match_id: UUID,
        athlete_id: UUID,
    ) -> AthleteMatchStats:
        """
        Calcula estatísticas de um atleta em uma partida.
        Ref: RD1-RD91 - Agregação de eventos por tipo
        """
        events, _ = await self.get_all_for_match(
            match_id,
            athlete_id=athlete_id,
            size=1000,  # Todos os eventos
        )

        stats = AthleteMatchStats(
            athlete_id=athlete_id,
            match_id=match_id,
        )

        for event in events:
            match event.event_type:
                case EventType.goal:
                    stats.goals += 1
                case EventType.goal_7m:
                    stats.goals_7m += 1
                case EventType.own_goal:
                    stats.own_goals += 1
                case EventType.shot:
                    stats.shots += 1
                case EventType.shot_on_target:
                    stats.shots_on_target += 1
                case EventType.save:
                    stats.saves += 1
                case EventType.goal_conceded:
                    stats.goals_conceded += 1
                case EventType.assist:
                    stats.assists += 1
                case EventType.yellow_card:
                    stats.yellow_cards += 1
                case EventType.red_card:
                    stats.red_cards += 1
                case EventType.two_minutes:
                    stats.two_minutes += 1
                case EventType.turnover:
                    stats.turnovers += 1
                case EventType.technical_foul:
                    stats.technical_fouls += 1

        return stats

    async def bulk_create(
        self,
        events: list[MatchEventCreate],
    ) -> list[MatchEvent]:
        """
        Cria múltiplos eventos de uma vez.
        Útil para importação de súmula.
        """
        if not events:
            return []

        # Todos devem ser da mesma partida
        match_ids = {e.match_id for e in events}
        if len(match_ids) > 1:
            raise ValidationError("All events must belong to the same match")

        match = await self._get_match(events[0].match_id)
        if match.status == MatchStatus.finished:
            raise ForbiddenError("Cannot add events to finalized match")

        # Validar todos os atletas
        athlete_ids = {e.athlete_id for e in events}
        for athlete_id in athlete_ids:
            await self._validate_athlete_in_roster(match.team_id, athlete_id)

        created = []
        for data in events:
            event = MatchEvent(
                match_id=data.match_id,
                athlete_id=data.athlete_id,
                event_type=data.event_type,
                minute=data.minute,
                period=data.period,
                x_position=data.x_position,
                y_position=data.y_position,
                notes=data.notes,
            )
            self.db.add(event)
            created.append(event)

        await self.db.flush()
        for event in created:
            await self.db.refresh(event)

        logger.info(
            f"Bulk created {len(created)} events for match {match.id}"
        )
        return created

    async def _get_match(self, match_id: UUID) -> Match:
        """Helper para buscar e validar acesso à partida."""
        query = select(Match).join(Team, Team.id == Match.team_id).where(
            Match.id == match_id,
        )
        if not self.context.is_superadmin:
            query = query.where(Team.organization_id == self.context.organization_id)
        result = await self.db.execute(query)
        match = result.scalar_one_or_none()

        if not match:
            raise NotFoundError(f"Match {match_id} not found")

        return match

    async def _validate_athlete_in_roster(
        self,
        team_id: UUID,
        athlete_id: UUID,
    ) -> None:
        """
        Valida que atleta está no roster do time.
        Ref: RD4 - Atleta deve estar registrado no time
        """
        query = select(TeamRegistration).where(
            and_(
                TeamRegistration.team_id == team_id,
                TeamRegistration.athlete_id == athlete_id,
                TeamRegistration.deleted_at.is_(None),
            )
        )
        result = await self.db.execute(query)
        registration = result.scalar_one_or_none()

        if not registration:
            raise ValidationError(
                f"Athlete {athlete_id} is not registered in team {team_id}"
            )
