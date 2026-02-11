"""
Model: TrainingMicrocycle (Planejamento semanal)

Referências TRAINNIG.MD:
- Microciclo: planejamento da semana de treino
- Armazena focos planejados (intenção)
- Relaciona-se com mesociclo (opcional mas recomendado)
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


class TrainingMicrocycle(Base):
    """Microciclo (planejamento semanal)."""
    __tablename__ = "training_microcycles"


# HB-AUTOGEN:BEGIN
    # AUTO-GENERATED FROM DB (SSOT). DO NOT EDIT MANUALLY.
    # Table: public.training_microcycles
    __table_args__ = (
        CheckConstraint('week_start < week_end', name='check_microcycle_dates'),
        Index('idx_training_microcycles_cycle', 'cycle_id', unique=False),
        Index('idx_training_microcycles_dates', 'week_start', 'week_end', unique=False),
        Index('idx_training_microcycles_org', 'organization_id', unique=False),
        Index('idx_training_microcycles_team', 'team_id', unique=False),
    )

    # NOTE: typing helpers may require: from datetime import date, datetime; from uuid import UUID

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'))
    organization_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('organizations.id', name='training_microcycles_organization_id_fkey'), nullable=False)
    team_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('teams.id', name='training_microcycles_team_id_fkey'), nullable=False)
    week_start: Mapped[date] = mapped_column(sa.Date(), nullable=False)
    week_end: Mapped[date] = mapped_column(sa.Date(), nullable=False)
    cycle_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('training_cycles.id', name='training_microcycles_cycle_id_fkey'), nullable=True)
    planned_focus_attack_positional_pct: Mapped[Optional[object]] = mapped_column(sa.Numeric(5, 2), nullable=True)
    planned_focus_defense_positional_pct: Mapped[Optional[object]] = mapped_column(sa.Numeric(5, 2), nullable=True)
    planned_focus_transition_offense_pct: Mapped[Optional[object]] = mapped_column(sa.Numeric(5, 2), nullable=True)
    planned_focus_transition_defense_pct: Mapped[Optional[object]] = mapped_column(sa.Numeric(5, 2), nullable=True)
    planned_focus_attack_technical_pct: Mapped[Optional[object]] = mapped_column(sa.Numeric(5, 2), nullable=True)
    planned_focus_defense_technical_pct: Mapped[Optional[object]] = mapped_column(sa.Numeric(5, 2), nullable=True)
    planned_focus_physical_pct: Mapped[Optional[object]] = mapped_column(sa.Numeric(5, 2), nullable=True)
    planned_weekly_load: Mapped[Optional[int]] = mapped_column(sa.Integer(), nullable=True)
    microcycle_type: Mapped[Optional[str]] = mapped_column(sa.String(), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(sa.Text(), nullable=True)
    created_by_user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('users.id', name='training_microcycles_created_by_user_id_fkey'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    updated_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    deleted_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    deleted_reason: Mapped[Optional[str]] = mapped_column(sa.Text(), nullable=True)
    # HB-AUTOGEN:END
    # PK

    # Organization scope

    # Team context

    # Período (semana)

    # Relacionamento com mesociclo

    # Focos planejados (percentuais 0-100)

    # Carga planejada da semana

    # Tipo de microciclo

    # Observações

    # Auditoria

    # Soft delete

    # Relationships
    cycle = relationship(
        "TrainingCycle",
        back_populates="microcycles",
        lazy="selectin"
    )
    sessions = relationship(
        "TrainingSession",
        back_populates="microcycle",
        foreign_keys="TrainingSession.microcycle_id",
        lazy="selectin"
    )
    
    # Step 16: Analytics cache
    analytics_cache: Mapped[list["TrainingAnalyticsCache"]] = relationship(
        "TrainingAnalyticsCache",
        back_populates="microcycle",
        lazy="selectin"
    )

    # Check constraints

    @property
    def planned_focus_total(self) -> float:
        """Soma total dos focos planejados (deve ser ≤ 120)."""
        total = 0.0
        for attr in [
            'planned_focus_attack_positional_pct',
            'planned_focus_defense_positional_pct',
            'planned_focus_transition_offense_pct',
            'planned_focus_transition_defense_pct',
            'planned_focus_attack_technical_pct',
            'planned_focus_defense_technical_pct',
            'planned_focus_physical_pct',
        ]:
            val = getattr(self, attr)
            if val is not None:
                total += float(val)
        return total

    @property
    def duration_days(self) -> int:
        """Duração do microciclo em dias (normalmente 7)."""
        if self.week_start and self.week_end:
            return (self.week_end - self.week_start).days
        return 0

    def __repr__(self) -> str:
        return f"<TrainingMicrocycle {self.week_start} - {self.week_end}>"
