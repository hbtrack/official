"""
Model: TrainingAnalyticsCache (Step 16)

Cache híbrido de analytics de treino:
- Weekly: granular para mês corrente (por microcycle_id)
- Monthly: agregado para histórico (por month)

Trigger fn_invalidate_analytics_cache marca cache_dirty=true automaticamente
quando training_sessions são modificadas.
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


class TrainingAnalyticsCache(Base):
    """
    Cache híbrido de analytics de treino.
    
    Granularidades:
    - weekly: cache por microcycle_id (mês corrente)
    - monthly: cache por month (histórico agregado)
    
    Invalidação:
    - Trigger tr_invalidate_analytics_cache marca cache_dirty=true
    - AnalyticsService recalcula sob demanda quando cache_dirty=true
    """
    __tablename__ = "training_analytics_cache"
    

# HB-AUTOGEN:BEGIN
    # AUTO-GENERATED FROM DB (SSOT). DO NOT EDIT MANUALLY.
    # Table: public.training_analytics_cache
    __table_args__ = (
        CheckConstraint("granularity::text = ANY (ARRAY['weekly'::character varying, 'monthly'::character varying]::text[])", name='ck_training_analytics_cache_granularity'),
        UniqueConstraint('team_id', 'microcycle_id', 'month', 'granularity', name='uq_training_analytics_cache_lookup'),
        Index('idx_analytics_lookup', 'team_id', 'granularity', 'cache_dirty', unique=False, postgresql_where=sa.text('(cache_dirty = false)')),
    )

    # NOTE: typing helpers may require: from datetime import date, datetime; from uuid import UUID

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'))
    team_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('teams.id', name='training_analytics_cache_team_id_fkey', ondelete='CASCADE'), nullable=False)
    microcycle_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('training_microcycles.id', name='training_analytics_cache_microcycle_id_fkey', ondelete='CASCADE'), nullable=True)
    month: Mapped[Optional[date]] = mapped_column(sa.Date(), nullable=True)
    granularity: Mapped[str] = mapped_column(sa.String(length=20), nullable=False)
    total_sessions: Mapped[Optional[int]] = mapped_column(sa.Integer(), nullable=True)
    avg_focus_attack_positional_pct: Mapped[Optional[object]] = mapped_column(sa.Numeric(5, 2), nullable=True)
    avg_focus_defense_positional_pct: Mapped[Optional[object]] = mapped_column(sa.Numeric(5, 2), nullable=True)
    avg_focus_transition_offense_pct: Mapped[Optional[object]] = mapped_column(sa.Numeric(5, 2), nullable=True)
    avg_focus_transition_defense_pct: Mapped[Optional[object]] = mapped_column(sa.Numeric(5, 2), nullable=True)
    avg_focus_attack_technical_pct: Mapped[Optional[object]] = mapped_column(sa.Numeric(5, 2), nullable=True)
    avg_focus_defense_technical_pct: Mapped[Optional[object]] = mapped_column(sa.Numeric(5, 2), nullable=True)
    avg_focus_physical_pct: Mapped[Optional[object]] = mapped_column(sa.Numeric(5, 2), nullable=True)
    avg_rpe: Mapped[Optional[object]] = mapped_column(sa.Numeric(5, 2), nullable=True)
    avg_internal_load: Mapped[Optional[object]] = mapped_column(sa.Numeric(10, 2), nullable=True)
    total_internal_load: Mapped[Optional[object]] = mapped_column(sa.Numeric(12, 2), nullable=True)
    attendance_rate: Mapped[Optional[object]] = mapped_column(sa.Numeric(5, 2), nullable=True)
    wellness_response_rate_pre: Mapped[Optional[object]] = mapped_column(sa.Numeric(5, 2), nullable=True)
    wellness_response_rate_post: Mapped[Optional[object]] = mapped_column(sa.Numeric(5, 2), nullable=True)
    athletes_with_badges_count: Mapped[Optional[int]] = mapped_column(sa.Integer(), nullable=True)
    deviation_count: Mapped[Optional[int]] = mapped_column(sa.Integer(), nullable=True)
    threshold_mean: Mapped[Optional[object]] = mapped_column(sa.Numeric(10, 2), nullable=True)
    threshold_stddev: Mapped[Optional[object]] = mapped_column(sa.Numeric(10, 2), nullable=True)
    cache_dirty: Mapped[bool] = mapped_column(sa.Boolean(), nullable=False, server_default=sa.text('true'))
    calculated_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    # HB-AUTOGEN:END
    # PK
    
    # Lookup keys
    
    
    
    
    # =========================================================================
    # MÉTRICAS AGREGADAS (17 campos)
    # =========================================================================
    
    
    # Focos de treino (7 médias percentuais)
    
    
    
    
    
    
    
    # Carga de treino
    
    
    
    
    # Wellness metrics (Step 16 novo)
    
    
    
    # Métricas threshold (Step 15/16)
    
    
    
    # =========================================================================
    # CONTROLE DE CACHE
    # =========================================================================
    
    
    
    # =========================================================================
    # RELATIONSHIPS
    # =========================================================================
    
    team: Mapped["Team"] = relationship("Team", back_populates="analytics_cache")
    microcycle: Mapped[Optional["TrainingMicrocycle"]] = relationship(
        "TrainingMicrocycle",
        back_populates="analytics_cache"
    )
    
    # =========================================================================
    # CONSTRAINTS
    # =========================================================================
    
    
    def __repr__(self) -> str:
        return (
            f"<TrainingAnalyticsCache(id={self.id}, team_id={self.team_id}, "
            f"granularity={self.granularity}, cache_dirty={self.cache_dirty})>"
        )
