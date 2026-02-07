"""
Model: TrainingMicrocycle (Planejamento semanal)

Referências TRAINNIG.MD:
- Microciclo: planejamento da semana de treino
- Armazena focos planejados (intenção)
- Relaciona-se com mesociclo (opcional mas recomendado)
"""
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Text, Integer, CheckConstraint, Date, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import text

from app.models.base import Base


class TrainingMicrocycle(Base):
    """Microciclo (planejamento semanal)."""
    __tablename__ = "training_microcycles"

    # PK
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()")
    )

    # Organization scope
    organization_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True
    )

    # Team context
    team_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teams.id"),
        nullable=False,
        index=True
    )

    # Período (semana)
    week_start: Mapped[Date] = mapped_column(Date, nullable=False, index=True)
    week_end: Mapped[Date] = mapped_column(Date, nullable=False, index=True)

    # Relacionamento com mesociclo
    cycle_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("training_cycles.id"),
        nullable=True,
        index=True
    )

    # Focos planejados (percentuais 0-100)
    planned_focus_attack_positional_pct: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="Percentual de foco planejado em ataque posicionado (0-100)"
    )
    planned_focus_defense_positional_pct: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="Percentual de foco planejado em defesa posicionada (0-100)"
    )
    planned_focus_transition_offense_pct: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="Percentual de foco planejado em transição ofensiva (0-100)"
    )
    planned_focus_transition_defense_pct: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="Percentual de foco planejado em transição defensiva (0-100)"
    )
    planned_focus_attack_technical_pct: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="Percentual de foco planejado em ataque técnico (0-100)"
    )
    planned_focus_defense_technical_pct: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="Percentual de foco planejado em defesa técnica (0-100)"
    )
    planned_focus_physical_pct: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="Percentual de foco planejado em treino físico (0-100)"
    )

    # Carga planejada da semana
    planned_weekly_load: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Tipo de microciclo
    microcycle_type: Mapped[Optional[str]] = mapped_column(
        nullable=True,
        comment="Tipo de microciclo: carga_alta, recuperacao, pre_jogo, etc."
    )

    # Observações
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Auditoria
    created_by_user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=text("now()"),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=text("now()"),
        nullable=False
    )

    # Soft delete
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    deleted_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

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
    __table_args__ = (
        CheckConstraint("week_start < week_end", name="check_microcycle_dates"),
    )

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
