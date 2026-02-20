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

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context import ExecutionContext
from app.core.exceptions import (
    NotFoundError,
    ValidationError,
    ForbiddenError,
)
from app.models.match import Match, MatchStatus
from app.models.match_event import MatchEvent, EventType
from app.models.match_roster import MatchRoster
from app.models.event_types import EventTypes
from app.models.team import Team
from app.schemas.match_events import (
    ScoutEventCreate,
    MatchEventUpdate,
    MatchEventCorrection,
    AthleteMatchStats,
    CanonicalEventType,
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
            query = query.where(MatchEvent.period_number == period)

        # Count total - usar with_only_columns para evitar produto cartesiano
        count_query = query.with_only_columns(func.count()).order_by(None)
        result_count = await self.db.execute(count_query)
        total = result_count.scalar_one_or_none() or 0

        # Paginate e ordenar por período e tempo de jogo
        query = query.order_by(MatchEvent.period_number, MatchEvent.game_time_seconds)
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

    async def create(self, match_id: UUID, data: ScoutEventCreate) -> MatchEvent:
        """
        Cria novo evento.
        Ref: RD4 - Atleta deve estar no roster
        Ref: RF15 - Partida não pode estar finalizada
        """
        match = await self._get_match(match_id)

        # RF15: Verificar se partida permite edição
        if match.status == MatchStatus.finished:
            raise ForbiddenError(
                "Cannot add events to finalized match"
            )

        event_type_code = self._event_type_code(data.event_type)

        # RD4: Validar atletas no roster da partida (não em team_registration)
        athlete_ids = [
            data.athlete_id,
            data.assisting_athlete_id,
            data.secondary_athlete_id,
        ]
        for athlete_id in athlete_ids:
            if athlete_id:
                await self._validate_athlete_in_roster(match.id, athlete_id)

        # Resolver is_shot canônico a partir de event_types
        event_type_row = await self.db.scalar(
            select(EventTypes).where(EventTypes.code == event_type_code)
        )
        if not event_type_row:
            raise ValidationError(f"event_type '{event_type_code}' not found in event_types")
        is_shot_db = bool(event_type_row.is_shot)

        # Regra defensiva: goalkeeper_save deve apontar para shot/seven_meter da mesma partida
        if event_type_code == CanonicalEventType.goalkeeper_save.value:
            if data.related_event_id is None:
                raise ValidationError("related_event_id is required for goalkeeper_save")

            related_event = await self.db.scalar(
                select(MatchEvent.id).where(
                    MatchEvent.id == data.related_event_id,
                    MatchEvent.match_id == match.id,
                    MatchEvent.event_type.in_(
                        [CanonicalEventType.shot.value, CanonicalEventType.seven_meter.value]
                    ),
                )
            )
            if not related_event:
                raise ValidationError("related_event must be a shot or seven_meter")

        event = MatchEvent(
            match_id=match.id,
            team_id=data.team_id,
            athlete_id=data.athlete_id,
            assisting_athlete_id=data.assisting_athlete_id,
            secondary_athlete_id=data.secondary_athlete_id,
            opponent_team_id=data.opponent_team_id,
            period_number=data.period_number,
            game_time_seconds=data.game_time_seconds,
            phase_of_play=data.phase_of_play,
            possession_id=data.possession_id,
            advantage_state=data.advantage_state,
            score_our=data.score_our,
            score_opponent=data.score_opponent,
            # score_our/score_opponent representam o placar NO MOMENTO do evento;
            # o service NÃO recalcula — persiste o valor informado pelo chamador.
            event_type=event_type_code,
            event_subtype=data.event_subtype,
            outcome=data.outcome,
            is_shot=is_shot_db,
            is_goal=data.is_goal,
            x_coord=data.x_coord,
            y_coord=data.y_coord,
            related_event_id=data.related_event_id,
            source=data.source,
            notes=data.notes,
            created_by_user_id=self.context.user_id,
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
        Usa tipos canônicos: goal, shot, seven_meter, goalkeeper_save, etc.
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
            # event.event_type é string no DB, comparar com valores do enum
            event_type_str = event.event_type if isinstance(event.event_type, str) else event.event_type.value
            
            if event_type_str == CanonicalEventType.goal.value:
                stats.goals += 1
            elif event_type_str == CanonicalEventType.seven_meter.value:
                # seven_meter pode ser gol ou finalização
                if event.is_goal:
                    stats.goals_7m += 1
                stats.shots += 1
            elif event_type_str == CanonicalEventType.shot.value:
                stats.shots += 1
            elif event_type_str == CanonicalEventType.goalkeeper_save.value:
                stats.saves += 1
            elif event_type_str == CanonicalEventType.yellow_card.value:
                stats.yellow_cards += 1
            elif event_type_str == CanonicalEventType.red_card.value:
                stats.red_cards += 1
            elif event_type_str == CanonicalEventType.exclusion_2min.value:
                stats.two_minutes += 1
            elif event_type_str == CanonicalEventType.turnover.value:
                stats.turnovers += 1

        return stats

    async def bulk_create(
        self,
        match_id: UUID,
        events: list[ScoutEventCreate],
    ) -> list[MatchEvent]:
        """
        Cria múltiplos eventos de uma vez.
        Útil para importação de súmula.
        """
        if not events:
            return []

        match = await self._get_match(match_id)
        if match and match.status == MatchStatus.finished:
            raise ForbiddenError("Cannot add events to finalized match")

        # Validar atletas referenciadas nos eventos (principal/assistência/secundária)
        athlete_ids: set[UUID] = set()
        for e in events:
            for athlete_id in (e.athlete_id, e.assisting_athlete_id, e.secondary_athlete_id):
                if athlete_id:
                    athlete_ids.add(athlete_id)

        for athlete_id in athlete_ids:
            if match:
                await self._validate_athlete_in_roster(match.id, athlete_id)

        created = []
        for data in events:
            event_type_code = self._event_type_code(data.event_type)
            event_type_row = await self.db.scalar(
                select(EventTypes).where(EventTypes.code == event_type_code)
            )
            if not event_type_row:
                raise ValidationError(f"event_type '{event_type_code}' not found in event_types")

            event = MatchEvent(
                match_id=match.id,
                team_id=data.team_id,
                athlete_id=data.athlete_id,
                assisting_athlete_id=data.assisting_athlete_id,
                secondary_athlete_id=data.secondary_athlete_id,
                opponent_team_id=data.opponent_team_id,
                period_number=data.period_number,
                game_time_seconds=data.game_time_seconds,
                phase_of_play=data.phase_of_play,
                possession_id=data.possession_id,
                advantage_state=data.advantage_state,
                score_our=data.score_our,
                score_opponent=data.score_opponent,
                event_type=event_type_code,
                event_subtype=data.event_subtype,
                outcome=data.outcome,
                is_shot=bool(event_type_row.is_shot),
                is_goal=data.is_goal,
                x_coord=data.x_coord,
                y_coord=data.y_coord,
                related_event_id=data.related_event_id,
                source=data.source,
                notes=data.notes,
                created_by_user_id=self.context.user_id,
            )
            self.db.add(event)
            created.append(event)

        await self.db.flush()
        for event in created:
            await self.db.refresh(event)

        logger.info(
            f"Bulk created {len(created)} events for match {match.id if match else 'unknown'}"
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
        match_id: UUID,
        athlete_id: UUID,
    ) -> None:
        """
        Valida que atleta está no roster da partida e disponível.
        Ref: RD4 - Atleta deve estar na súmula oficial (match_roster)
        """
        query = select(MatchRoster.id).where(
            MatchRoster.match_id == match_id,
            MatchRoster.athlete_id == athlete_id,
            MatchRoster.is_available.is_(True),
        )
        registration = await self.db.scalar(query)

        if not registration:
            raise ValidationError(
                f"Athlete {athlete_id} is not available in match roster for match {match_id}"
            )

    @staticmethod
    def _event_type_code(event_type: CanonicalEventType | str) -> str:
        return event_type.value if hasattr(event_type, "value") else str(event_type)
