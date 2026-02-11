"""
Model: TrainingCycle (Macrociclos e Mesociclos)

Referências TRAINNIG.MD:
- Macrociclo: temporada completa ou fase longa
- Mesociclo: 4-6 semanas
- Mesociclo pertence a um Macrociclo (parent_cycle_id)
"""

# HB-AUTOGEN-IMPORTS:BEGIN
from __future__ import annotations

from datetime import date, datetime
from typing import Optional
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import ForeignKey, CheckConstraint, Index, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB as PG_JSONB, INET as PG_INET, ENUM as PG_ENUM
# HB-AUTOGEN-IMPORTS:END


from app.models.base import Base


class TrainingCycle(Base):
    """Macrociclo ou Mesociclo de treinamento."""
    __tablename__ = "training_cycles"


# HB-AUTOGEN:BEGIN
    # AUTO-GENERATED FROM DB (SSOT). DO NOT EDIT MANUALLY.
    # Table: public.training_cycles
    __table_args__ = (
        CheckConstraint('start_date < end_date', name='check_cycle_dates'),
        CheckConstraint("status::text = ANY (ARRAY['active'::character varying, 'completed'::character varying, 'cancelled'::character varying]::text[])", name='check_cycle_status'),
        CheckConstraint("type::text = ANY (ARRAY['macro'::character varying, 'meso'::character varying]::text[])", name='check_cycle_type'),
        Index('idx_training_cycles_dates', 'start_date', 'end_date', unique=False),
        Index('idx_training_cycles_org', 'organization_id', unique=False),
        Index('idx_training_cycles_parent', 'parent_cycle_id', unique=False),
        Index('idx_training_cycles_status', 'status', unique=False),
        Index('idx_training_cycles_team', 'team_id', unique=False),
        Index('idx_training_cycles_type', 'type', unique=False),
    )

    # NOTE: typing helpers may require: from datetime import date, datetime; from uuid import UUID

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'))
    organization_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('organizations.id', name='training_cycles_organization_id_fkey'), nullable=False)
    team_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('teams.id', name='training_cycles_team_id_fkey'), nullable=False)
    type: Mapped[str] = mapped_column(sa.String(), nullable=False)
    start_date: Mapped[date] = mapped_column(sa.Date(), nullable=False)
    end_date: Mapped[date] = mapped_column(sa.Date(), nullable=False)
    objective: Mapped[Optional[str]] = mapped_column(sa.Text(), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(sa.Text(), nullable=True)
    status: Mapped[str] = mapped_column(sa.String(), nullable=False, server_default=sa.text("'''active'''::character varying"))
    parent_cycle_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('training_cycles.id', name='training_cycles_parent_cycle_id_fkey'), nullable=True)
    created_by_user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('users.id', name='training_cycles_created_by_user_id_fkey'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    updated_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    deleted_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    deleted_reason: Mapped[Optional[str]] = mapped_column(sa.Text(), nullable=True)
    # HB-AUTOGEN:END
    # PK

    # Organization scope

    # Team context

    # Tipo: macro ou meso

    # Período

    # Objetivo estratégico

    # Status

    # Relacionamento (mesociclo → macrociclo)

    # Auditoria

    # Soft delete

    # Relationships
    microcycles = relationship(
        "TrainingMicrocycle",
        back_populates="cycle",
        foreign_keys="TrainingMicrocycle.cycle_id",
        lazy="selectin"
    )

    # Check constraints

    @property
    def duration_days(self) -> int:
        """Duração do ciclo em dias."""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days
        return 0

    def __repr__(self) -> str:
        return f"<TrainingCycle {self.type} {self.start_date} - {self.end_date}>"
