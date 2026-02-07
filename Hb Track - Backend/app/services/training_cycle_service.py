"""
Service para gerenciamento de Ciclos de Treinamento (Training Cycles).

Baseado em TRAINNIG.MD:
- Macrociclo: temporada completa ou fase longa
- Mesociclo: 4-6 semanas (pertence a um macrociclo)

Regras:
- Macrociclo não pode ter parent_cycle_id
- Mesociclo deve ter parent_cycle_id
- start_date < end_date
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
from app.models.training_cycle import TrainingCycle
from app.schemas.training_cycles import (
    TrainingCycleCreate,
    TrainingCycleUpdate,
)

logger = logging.getLogger(__name__)


class TrainingCycleService:
    """
    Service de Ciclos de Treinamento.
    Ref: TRAINNIG.MD
    """

    def __init__(self, db: AsyncSession, context: ExecutionContext):
        self.db = db
        self.context = context

    async def get_all(
        self,
        *,
        team_id: UUID,
        cycle_type: Optional[str] = None,
        status: Optional[str] = None,
        include_deleted: bool = False,
    ) -> list[TrainingCycle]:
        """
        Lista ciclos de uma equipe.

        Args:
            team_id: ID da equipe
            cycle_type: Filtro por tipo ('macro' ou 'meso')
            status: Filtro por status ('active', 'completed', 'cancelled')
            include_deleted: Incluir deletados
        """
        query = select(TrainingCycle).where(
            and_(
                TrainingCycle.organization_id == self.context.organization_id,
                TrainingCycle.team_id == team_id,
            )
        )

        if not include_deleted:
            query = query.where(TrainingCycle.deleted_at.is_(None))

        if cycle_type:
            query = query.where(TrainingCycle.type == cycle_type)

        if status:
            query = query.where(TrainingCycle.status == status)

        query = query.order_by(TrainingCycle.start_date.desc())

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_id(
        self,
        cycle_id: UUID,
        include_deleted: bool = False,
    ) -> TrainingCycle:
        """
        Busca ciclo por ID.

        Args:
            cycle_id: ID do ciclo
            include_deleted: Incluir deletados

        Raises:
            NotFoundError: Se ciclo não encontrado
        """
        query = select(TrainingCycle).where(
            and_(
                TrainingCycle.id == cycle_id,
                TrainingCycle.organization_id == self.context.organization_id,
            )
        )

        if not include_deleted:
            query = query.where(TrainingCycle.deleted_at.is_(None))

        result = await self.db.execute(query)
        cycle = result.scalar_one_or_none()

        if not cycle:
            raise NotFoundError(f"Training cycle {cycle_id} not found")

        return cycle

    async def create(
        self,
        data: TrainingCycleCreate,
    ) -> TrainingCycle:
        """
        Cria um novo ciclo de treinamento.

        Validações:
        - Macrociclo não pode ter parent_cycle_id
        - Mesociclo deve ter parent_cycle_id
        - start_date < end_date
        - Se mesociclo, datas devem estar dentro do macrociclo pai

        Args:
            data: Dados do ciclo a criar

        Returns:
            Ciclo criado

        Raises:
            ValidationError: Se validações falharem
        """
        # Validações já feitas pelo schema Pydantic
        # Validação adicional: se mesociclo, verificar datas do pai
        if data.type == 'meso' and data.parent_cycle_id:
            parent = await self.get_by_id(data.parent_cycle_id)

            if data.start_date < parent.start_date or data.end_date > parent.end_date:
                raise ValidationError(
                    f"Datas do mesociclo ({data.start_date} - {data.end_date}) "
                    f"devem estar dentro do macrociclo pai ({parent.start_date} - {parent.end_date})"
                )

        cycle = TrainingCycle(
            organization_id=self.context.organization_id,
            team_id=data.team_id,
            type=data.type,
            start_date=data.start_date,
            end_date=data.end_date,
            objective=data.objective,
            notes=data.notes,
            status=data.status,
            parent_cycle_id=data.parent_cycle_id,
            created_by_user_id=self.context.user_id,
        )

        self.db.add(cycle)
        await self.db.flush()
        await self.db.refresh(cycle)

        logger.info(
            f"Created training cycle {cycle.id} (type={cycle.type}) "
            f"for team {data.team_id} by user {self.context.user_id}"
        )
        return cycle

    async def update(
        self,
        cycle_id: UUID,
        data: TrainingCycleUpdate,
    ) -> TrainingCycle:
        """
        Atualiza ciclo de treinamento.

        Args:
            cycle_id: ID do ciclo
            data: Dados a atualizar

        Returns:
            Ciclo atualizado
        """
        cycle = await self.get_by_id(cycle_id)

        # Atualizar campos fornecidos
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(cycle, field, value)

        await self.db.flush()
        await self.db.refresh(cycle)

        logger.info(
            f"Updated training cycle {cycle_id} by user {self.context.user_id}"
        )
        return cycle

    async def soft_delete(
        self,
        cycle_id: UUID,
        reason: str,
    ) -> TrainingCycle:
        """
        Soft delete de ciclo de treinamento.

        Args:
            cycle_id: ID do ciclo
            reason: Motivo da exclusão

        Returns:
            Ciclo deletado
        """
        cycle = await self.get_by_id(cycle_id)

        cycle.deleted_at = datetime.utcnow()
        cycle.deleted_reason = reason

        await self.db.flush()
        await self.db.refresh(cycle)

        logger.info(
            f"Soft deleted training cycle {cycle_id} by user {self.context.user_id}: {reason}"
        )
        return cycle

    async def get_active_cycles_for_team(
        self,
        team_id: UUID,
        at_date: Optional[date] = None,
    ) -> list[TrainingCycle]:
        """
        Busca ciclos ativos de uma equipe em uma data específica.

        Args:
            team_id: ID da equipe
            at_date: Data de referência (default: hoje)

        Returns:
            Lista de ciclos ativos na data
        """
        if at_date is None:
            at_date = date.today()

        query = select(TrainingCycle).where(
            and_(
                TrainingCycle.organization_id == self.context.organization_id,
                TrainingCycle.team_id == team_id,
                TrainingCycle.status == 'active',
                TrainingCycle.start_date <= at_date,
                TrainingCycle.end_date >= at_date,
                TrainingCycle.deleted_at.is_(None),
            )
        ).order_by(TrainingCycle.type.desc())  # macro antes de meso

        result = await self.db.execute(query)
        return list(result.scalars().all())
