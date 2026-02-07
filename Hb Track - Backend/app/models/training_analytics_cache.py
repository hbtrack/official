"""
Model: TrainingAnalyticsCache (Step 16)

Cache híbrido de analytics de treino:
- Weekly: granular para mês corrente (por microcycle_id)
- Monthly: agregado para histórico (por month)

Trigger fn_invalidate_analytics_cache marca cache_dirty=true automaticamente
quando training_sessions são modificadas.
"""
from datetime import datetime, timezone, date
from typing import Optional
from uuid import uuid4

from sqlalchemy import (
    DateTime, ForeignKey, Integer, Numeric, Boolean, 
    CheckConstraint, UniqueConstraint, Index, Date, String, text
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

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
    
    # PK
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()")
    )
    
    # Lookup keys
    team_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    microcycle_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("training_microcycles.id", ondelete="CASCADE"),
        nullable=True,
        comment="Para granularity='weekly', identifica o microciclo"
    )
    
    month: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        comment="Para granularity='monthly', primeiro dia do mês (YYYY-MM-01)"
    )
    
    granularity: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="'weekly' (microcycle_id) ou 'monthly' (month)"
    )
    
    # =========================================================================
    # MÉTRICAS AGREGADAS (17 campos)
    # =========================================================================
    
    total_sessions: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Total de sessões no período"
    )
    
    # Focos de treino (7 médias percentuais)
    avg_focus_attack_positional_pct: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="Média % ataque posicional"
    )
    
    avg_focus_defense_positional_pct: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="Média % defesa posicional"
    )
    
    avg_focus_transition_offense_pct: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="Média % transição ofensiva"
    )
    
    avg_focus_transition_defense_pct: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="Média % transição defensiva"
    )
    
    avg_focus_attack_technical_pct: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="Média % técnica ofensiva"
    )
    
    avg_focus_defense_technical_pct: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="Média % técnica defensiva"
    )
    
    avg_focus_physical_pct: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="Média % físico"
    )
    
    # Carga de treino
    avg_rpe: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="Média RPE (Rating of Perceived Exertion)"
    )
    
    avg_internal_load: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        comment="Média de carga interna (RPE × duration)"
    )
    
    total_internal_load: Mapped[Optional[float]] = mapped_column(
        Numeric(12, 2),
        nullable=True,
        comment="Soma total de carga interna"
    )
    
    attendance_rate: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="Taxa de assiduidade média (%)"
    )
    
    # Wellness metrics (Step 16 novo)
    wellness_response_rate_pre: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="Taxa de resposta wellness pré-treino (%)"
    )
    
    wellness_response_rate_post: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="Taxa de resposta wellness pós-treino (%)"
    )
    
    athletes_with_badges_count: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Quantidade de atletas com badges no período"
    )
    
    # Métricas threshold (Step 15/16)
    deviation_count: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Quantidade de sessões com desvio acima do threshold"
    )
    
    threshold_mean: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        comment="Média dos desvios calculados com alert_threshold_multiplier"
    )
    
    threshold_stddev: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        comment="Desvio padrão dos desvios calculados"
    )
    
    # =========================================================================
    # CONTROLE DE CACHE
    # =========================================================================
    
    cache_dirty: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
        comment="true = recalcular; false = válido. Trigger marca automaticamente."
    )
    
    calculated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="UTC timestamp da última recalculação"
    )
    
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
    
    __table_args__ = (
        CheckConstraint(
            "granularity IN ('weekly', 'monthly')",
            name='ck_training_analytics_cache_granularity'
        ),
        UniqueConstraint(
            'team_id', 'microcycle_id', 'month', 'granularity',
            name='uq_training_analytics_cache_lookup'
        ),
        Index(
            'idx_analytics_lookup',
            'team_id', 'granularity', 'cache_dirty',
            postgresql_where=text('cache_dirty = false')
        ),
    )
    
    def __repr__(self) -> str:
        return (
            f"<TrainingAnalyticsCache(id={self.id}, team_id={self.team_id}, "
            f"granularity={self.granularity}, cache_dirty={self.cache_dirty})>"
        )
