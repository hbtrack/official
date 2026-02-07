"""
Service para gerenciamento de Microciclos de Treinamento (Training Microcycles).

Baseado em TRAINNIG.MD:
- Microciclo: planejamento semanal de treinos
- Armazena focos planejados (intenção)
- Base para cálculo de desvios (planejado vs executado)

Regras:
- week_start < week_end
- Soma dos focos planejados ≤ 120
"""

import logging
from datetime import date, datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context import ExecutionContext
from app.core.exceptions import (
    NotFoundError,
    ValidationError,
)
from app.models.training_microcycle import TrainingMicrocycle
from app.schemas.training_microcycles import (
    TrainingMicrocycleCreate,
    TrainingMicrocycleUpdate,
)

logger = logging.getLogger(__name__)


class TrainingMicrocycleService:
    """
    Service de Microciclos de Treinamento.
    Ref: TRAINNIG.MD
    """

    def __init__(self, db: AsyncSession, context: ExecutionContext):
        self.db = db
        self.context = context

    async def get_all(
        self,
        *,
        team_id: UUID,
        cycle_id: Optional[UUID] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        include_deleted: bool = False,
    ) -> list[TrainingMicrocycle]:
        """
        Lista microciclos de uma equipe.

        Args:
            team_id: ID da equipe
            cycle_id: Filtro por mesociclo
            start_date: Data inicial do intervalo
            end_date: Data final do intervalo
            include_deleted: Incluir deletados
        """
        query = select(TrainingMicrocycle).where(
            and_(
                TrainingMicrocycle.organization_id == self.context.organization_id,
                TrainingMicrocycle.team_id == team_id,
            )
        )

        if not include_deleted:
            query = query.where(TrainingMicrocycle.deleted_at.is_(None))

        if cycle_id:
            query = query.where(TrainingMicrocycle.cycle_id == cycle_id)

        if start_date:
            query = query.where(TrainingMicrocycle.week_end >= start_date)

        if end_date:
            query = query.where(TrainingMicrocycle.week_start <= end_date)

        query = query.order_by(TrainingMicrocycle.week_start.desc())

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_id(
        self,
        microcycle_id: UUID,
        include_deleted: bool = False,
    ) -> TrainingMicrocycle:
        """
        Busca microciclo por ID.

        Args:
            microcycle_id: ID do microciclo
            include_deleted: Incluir deletados

        Raises:
            NotFoundError: Se microciclo não encontrado
        """
        query = select(TrainingMicrocycle).where(
            and_(
                TrainingMicrocycle.id == microcycle_id,
                TrainingMicrocycle.organization_id == self.context.organization_id,
            )
        )

        if not include_deleted:
            query = query.where(TrainingMicrocycle.deleted_at.is_(None))

        result = await self.db.execute(query)
        microcycle = result.scalar_one_or_none()

        if not microcycle:
            raise NotFoundError(f"Training microcycle {microcycle_id} not found")

        return microcycle

    async def create(
        self,
        data: TrainingMicrocycleCreate,
    ) -> TrainingMicrocycle:
        """
        Cria um novo microciclo de treinamento.

        Validações:
        - week_start < week_end
        - Soma dos focos ≤ 120 (validado pelo schema)
        - Se cycle_id fornecido, datas devem estar dentro do mesociclo

        Args:
            data: Dados do microciclo a criar

        Returns:
            Microciclo criado

        Raises:
            ValidationError: Se validações falharem
        """
        # Validação adicional: se cycle_id, verificar datas do mesociclo
        if data.cycle_id:
            from app.services.training_cycle_service import TrainingCycleService

            cycle_service = TrainingCycleService(self.db, self.context)
            cycle = await cycle_service.get_by_id(data.cycle_id)

            if data.week_start < cycle.start_date or data.week_end > cycle.end_date:
                raise ValidationError(
                    f"Datas do microciclo ({data.week_start} - {data.week_end}) "
                    f"devem estar dentro do mesociclo ({cycle.start_date} - {cycle.end_date})"
                )

        microcycle = TrainingMicrocycle(
            organization_id=self.context.organization_id,
            team_id=data.team_id,
            week_start=data.week_start,
            week_end=data.week_end,
            cycle_id=data.cycle_id,
            planned_focus_attack_positional_pct=data.planned_focus_attack_positional_pct,
            planned_focus_defense_positional_pct=data.planned_focus_defense_positional_pct,
            planned_focus_transition_offense_pct=data.planned_focus_transition_offense_pct,
            planned_focus_transition_defense_pct=data.planned_focus_transition_defense_pct,
            planned_focus_attack_technical_pct=data.planned_focus_attack_technical_pct,
            planned_focus_defense_technical_pct=data.planned_focus_defense_technical_pct,
            planned_focus_physical_pct=data.planned_focus_physical_pct,
            planned_weekly_load=data.planned_weekly_load,
            microcycle_type=data.microcycle_type,
            notes=data.notes,
            created_by_user_id=self.context.user_id,
        )

        self.db.add(microcycle)
        await self.db.flush()
        await self.db.refresh(microcycle)

        logger.info(
            f"Created training microcycle {microcycle.id} "
            f"for team {data.team_id} ({data.week_start} - {data.week_end}) "
            f"by user {self.context.user_id}"
        )
        return microcycle

    async def update(
        self,
        microcycle_id: UUID,
        data: TrainingMicrocycleUpdate,
    ) -> TrainingMicrocycle:
        """
        Atualiza microciclo de treinamento.

        Args:
            microcycle_id: ID do microciclo
            data: Dados a atualizar

        Returns:
            Microciclo atualizado
        """
        microcycle = await self.get_by_id(microcycle_id)

        # Atualizar campos fornecidos
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(microcycle, field, value)

        await self.db.flush()
        await self.db.refresh(microcycle)

        logger.info(
            f"Updated training microcycle {microcycle_id} by user {self.context.user_id}"
        )
        return microcycle

    async def soft_delete(
        self,
        microcycle_id: UUID,
        reason: str,
    ) -> TrainingMicrocycle:
        """
        Soft delete de microciclo de treinamento.

        Args:
            microcycle_id: ID do microciclo
            reason: Motivo da exclusão

        Returns:
            Microciclo deletado
        """
        microcycle = await self.get_by_id(microcycle_id)

        microcycle.deleted_at = datetime.utcnow()
        microcycle.deleted_reason = reason

        await self.db.flush()
        await self.db.refresh(microcycle)

        logger.info(
            f"Soft deleted training microcycle {microcycle_id} by user {self.context.user_id}: {reason}"
        )
        return microcycle

    async def get_current_week(
        self,
        team_id: UUID,
        at_date: Optional[date] = None,
    ) -> Optional[TrainingMicrocycle]:
        """
        Busca microciclo da semana atual de uma equipe.

        Args:
            team_id: ID da equipe
            at_date: Data de referência (default: hoje)

        Returns:
            Microciclo da semana ou None
        """
        if at_date is None:
            at_date = date.today()

        query = select(TrainingMicrocycle).where(
            and_(
                TrainingMicrocycle.organization_id == self.context.organization_id,
                TrainingMicrocycle.team_id == team_id,
                TrainingMicrocycle.week_start <= at_date,
                TrainingMicrocycle.week_end >= at_date,
                TrainingMicrocycle.deleted_at.is_(None),
            )
        )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_microcycle_execution_summary(
        self,
        microcycle_id: UUID,
    ) -> dict:
        """
        Retorna resumo de execução do microciclo (planejado vs executado).

        Calcula:
        - Total de sessões planejadas vs realizadas
        - Focos planejados vs executados (médias)
        - Carga planejada vs executada
        - Desvios agregados

        Args:
            microcycle_id: ID do microciclo

        Returns:
            Dict com resumo de execução
        """
        from app.models.training_session import TrainingSession

        microcycle = await self.get_by_id(microcycle_id)

        # Buscar sessões do microciclo
        query = select(TrainingSession).where(
            and_(
                TrainingSession.microcycle_id == microcycle_id,
                TrainingSession.deleted_at.is_(None),
            )
        )
        result = await self.db.execute(query)
        sessions = list(result.scalars().all())

        # Calcular médias executadas
        focus_fields = [
            'attack_positional',
            'defense_positional',
            'transition_offense',
            'transition_defense',
            'attack_technical',
            'defense_technical',
            'physical',
        ]

        executed_avg = {}
        for field in focus_fields:
            values = [
                getattr(s, f'focus_{field}_pct')
                for s in sessions
                if getattr(s, f'focus_{field}_pct') is not None
            ]
            executed_avg[field] = sum(values) / len(values) if values else 0

        # Focos planejados
        planned = {}
        for field in focus_fields:
            planned[field] = getattr(microcycle, f'planned_focus_{field}_pct') or 0

        # Carga
        total_load = sum(
            getattr(s, 'planned_load', 0) or 0
            for s in sessions
        )

        return {
            'microcycle_id': microcycle_id,
            'week_start': microcycle.week_start,
            'week_end': microcycle.week_end,
            'total_sessions': len(sessions),
            'planned_weekly_load': microcycle.planned_weekly_load,
            'executed_weekly_load': total_load,
            'planned_focus': planned,
            'executed_focus_avg': executed_avg,
        }
