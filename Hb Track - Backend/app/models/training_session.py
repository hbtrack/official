"""
Model: TrainingSession (R18, R40)

Referências RAG:
- R18: Treinos são eventos operacionais, editáveis dentro dos limites do sistema
- R22: Dados de treino são métricas operacionais (carga, PSE, assiduidade)
- R40: Limite temporal de edição (10min autor; até 24h superior; >24h readonly)
- RDB3: Timestamps em UTC
- RDB4: Soft delete obrigatório
- RDB13: Após 24h exige admin_note para edição
"""

# HB-AUTOGEN-IMPORTS:BEGIN
from __future__ import annotations

from datetime import date, datetime
from typing import Optional
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import ForeignKey, CheckConstraint, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB as PG_JSONB
# HB-AUTOGEN-IMPORTS:END
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    SmallInteger,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class TrainingSession(Base):
    """
    Sessão de treino.

    Regras:
    - R18: Evento operacional editável dentro dos limites
    - R40: Após 24h, somente leitura (exceto admin_note)
    - R22: Métricas operacionais (não estatísticas primárias)
    """
    __tablename__ = "training_sessions"


# HB-AUTOGEN:BEGIN
    # AUTO-GENERATED FROM DB (SSOT). DO NOT EDIT MANUALLY.
    # Table: public.training_sessions
    __table_args__ = (
        CheckConstraint("status::text = ANY (ARRAY['draft'::character varying, 'scheduled'::character varying, 'in_progress'::character varying, 'closed'::character varying, 'readonly'::character varying]::text[])", name='check_training_session_status'),
        CheckConstraint('phase_focus_attack = ((COALESCE(focus_attack_positional_pct, 0::numeric) + COALESCE(focus_attack_technical_pct, 0::numeric)) >= 5::numeric)', name='ck_phase_focus_attack_consistency'),
        CheckConstraint('phase_focus_defense = ((COALESCE(focus_defense_positional_pct, 0::numeric) + COALESCE(focus_defense_technical_pct, 0::numeric)) >= 5::numeric)', name='ck_phase_focus_defense_consistency'),
        CheckConstraint('phase_focus_transition_defense = (COALESCE(focus_transition_defense_pct, 0::numeric) >= 5::numeric)', name='ck_phase_focus_transition_defense_consistency'),
        CheckConstraint('phase_focus_transition_offense = (COALESCE(focus_transition_offense_pct, 0::numeric) >= 5::numeric)', name='ck_phase_focus_transition_offense_consistency'),
        CheckConstraint('group_climate IS NULL OR group_climate >= 1 AND group_climate <= 5', name='ck_training_sessions_climate'),
        CheckConstraint('deleted_at IS NULL AND deleted_reason IS NULL OR deleted_at IS NOT NULL AND deleted_reason IS NOT NULL', name='ck_training_sessions_deleted_reason'),
        CheckConstraint('focus_attack_positional_pct IS NULL OR focus_attack_positional_pct >= 0::numeric AND focus_attack_positional_pct <= 100::numeric', name='ck_training_sessions_focus_attack_positional_range'),
        CheckConstraint('focus_attack_technical_pct IS NULL OR focus_attack_technical_pct >= 0::numeric AND focus_attack_technical_pct <= 100::numeric', name='ck_training_sessions_focus_attack_technical_range'),
        CheckConstraint('focus_defense_positional_pct IS NULL OR focus_defense_positional_pct >= 0::numeric AND focus_defense_positional_pct <= 100::numeric', name='ck_training_sessions_focus_defense_positional_range'),
        CheckConstraint('focus_defense_technical_pct IS NULL OR focus_defense_technical_pct >= 0::numeric AND focus_defense_technical_pct <= 100::numeric', name='ck_training_sessions_focus_defense_technical_range'),
        CheckConstraint('focus_physical_pct IS NULL OR focus_physical_pct >= 0::numeric AND focus_physical_pct <= 100::numeric', name='ck_training_sessions_focus_physical_range'),
        CheckConstraint('(COALESCE(focus_attack_positional_pct, 0::numeric) + COALESCE(focus_defense_positional_pct, 0::numeric) + COALESCE(focus_transition_offense_pct, 0::numeric) + COALESCE(focus_transition_defense_pct, 0::numeric) + COALESCE(focus_attack_technical_pct, 0::numeric) + COALESCE(focus_defense_technical_pct, 0::numeric) + COALESCE(focus_physical_pct, 0::numeric)) <= 120::numeric', name='ck_training_sessions_focus_total_sum'),
        CheckConstraint('focus_transition_defense_pct IS NULL OR focus_transition_defense_pct >= 0::numeric AND focus_transition_defense_pct <= 100::numeric', name='ck_training_sessions_focus_transition_defense_range'),
        CheckConstraint('focus_transition_offense_pct IS NULL OR focus_transition_offense_pct >= 0::numeric AND focus_transition_offense_pct <= 100::numeric', name='ck_training_sessions_focus_transition_offense_range'),
        CheckConstraint('intensity_target IS NULL OR intensity_target >= 1 AND intensity_target <= 5', name='ck_training_sessions_intensity'),
        CheckConstraint("session_type::text = ANY (ARRAY['quadra'::character varying, 'fisico'::character varying, 'video'::character varying, 'reuniao'::character varying, 'teste'::character varying]::text[])", name='ck_training_sessions_type'),
        Index('idx_sessions_team_date', 'team_id', 'session_at', unique=False),
        Index('idx_training_sessions_deviation_flag', 'planning_deviation_flag', unique=False),
        Index('idx_training_sessions_microcycle', 'microcycle_id', unique=False),
        Index('idx_training_sessions_org', 'organization_id', 'deleted_at', unique=False, postgresql_where=sa.text('(deleted_at IS NULL)')),
        Index('idx_training_sessions_status', 'status', unique=False),
        Index('idx_training_sessions_team_date', 'team_id', 'session_at', 'deleted_at', unique=False, postgresql_where=sa.text('(deleted_at IS NULL)')),
        Index('ix_training_sessions_organization_id', 'organization_id', unique=False),
        Index('ix_training_sessions_season_id', 'season_id', unique=False),
        Index('ix_training_sessions_session_at', 'session_at', unique=False),
        Index('ix_training_sessions_team_date_active', 'team_id', 'session_at', unique=False, postgresql_where=sa.text('(deleted_at IS NULL)')),
        Index('ix_training_sessions_team_id', 'team_id', unique=False),
        Index('ix_training_sessions_team_season_date', 'team_id', 'season_id', 'session_at', unique=False, postgresql_where=sa.text('(deleted_at IS NULL)')),
    )

    # NOTE: typing helpers may require: from datetime import date, datetime; from uuid import UUID

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'))
    organization_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('organizations.id', name='fk_training_sessions_organization_id', ondelete='RESTRICT'), nullable=False)
    team_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('teams.id', name='fk_training_sessions_team_id', ondelete='RESTRICT'), nullable=True)
    season_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('seasons.id', name='fk_training_sessions_season_id', ondelete='RESTRICT'), nullable=True)
    session_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False)
    duration_planned_minutes: Mapped[Optional[int]] = mapped_column(sa.SmallInteger(), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(sa.String(length=120), nullable=True)
    session_type: Mapped[str] = mapped_column(sa.String(length=32), nullable=False)
    main_objective: Mapped[Optional[str]] = mapped_column(sa.String(length=255), nullable=True)
    secondary_objective: Mapped[Optional[str]] = mapped_column(sa.Text(), nullable=True)
    planned_load: Mapped[Optional[int]] = mapped_column(sa.SmallInteger(), nullable=True)
    group_climate: Mapped[Optional[int]] = mapped_column(sa.SmallInteger(), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(sa.Text(), nullable=True)
    phase_focus_defense: Mapped[bool] = mapped_column(sa.Boolean(), nullable=False, server_default=sa.text('false'))
    phase_focus_attack: Mapped[bool] = mapped_column(sa.Boolean(), nullable=False, server_default=sa.text('false'))
    phase_focus_transition_offense: Mapped[bool] = mapped_column(sa.Boolean(), nullable=False, server_default=sa.text('false'))
    phase_focus_transition_defense: Mapped[bool] = mapped_column(sa.Boolean(), nullable=False, server_default=sa.text('false'))
    intensity_target: Mapped[Optional[int]] = mapped_column(sa.SmallInteger(), nullable=True)
    session_block: Mapped[Optional[str]] = mapped_column(sa.String(length=32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    created_by_user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('users.id', name='fk_training_sessions_created_by_user_id', ondelete='RESTRICT'), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    deleted_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    deleted_reason: Mapped[Optional[str]] = mapped_column(sa.Text(), nullable=True)
    focus_attack_positional_pct: Mapped[Optional[object]] = mapped_column(sa.Numeric(5, 2), nullable=True)
    focus_defense_positional_pct: Mapped[Optional[object]] = mapped_column(sa.Numeric(5, 2), nullable=True)
    focus_transition_offense_pct: Mapped[Optional[object]] = mapped_column(sa.Numeric(5, 2), nullable=True)
    focus_transition_defense_pct: Mapped[Optional[object]] = mapped_column(sa.Numeric(5, 2), nullable=True)
    focus_attack_technical_pct: Mapped[Optional[object]] = mapped_column(sa.Numeric(5, 2), nullable=True)
    focus_defense_technical_pct: Mapped[Optional[object]] = mapped_column(sa.Numeric(5, 2), nullable=True)
    focus_physical_pct: Mapped[Optional[object]] = mapped_column(sa.Numeric(5, 2), nullable=True)
    microcycle_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('training_microcycles.id', name='fk_training_sessions_microcycle', ondelete='RESTRICT'), nullable=True)
    status: Mapped[str] = mapped_column(sa.String(), nullable=False, server_default=sa.text("'''draft'''::character varying"))
    closed_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    closed_by_user_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('users.id', name='fk_training_sessions_closed_by', ondelete='RESTRICT'), nullable=True)
    deviation_justification: Mapped[Optional[str]] = mapped_column(sa.Text(), nullable=True)
    planning_deviation_flag: Mapped[bool] = mapped_column(sa.Boolean(), nullable=False, server_default=sa.text('false'))
    # HB-AUTOGEN:END
    # PK (RDB2)
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()")
    )

    # Organization scope (R34)
    organization_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

    # Team context (opcional - pode ser treino geral)
    team_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="RESTRICT"),
        nullable=True,
        index=True
    )

    # Season context
    season_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("seasons.id", ondelete="RESTRICT"),
        nullable=True,
        index=True
    )

    # Data/hora do treino
    session_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )

    # Duração planejada em minutos
    duration_planned_minutes: Mapped[Optional[int]] = mapped_column(
        SmallInteger,
        nullable=True
    )

    # Local do treino
    location: Mapped[Optional[str]] = mapped_column(
        String(120),
        nullable=True
    )

    # Tipo de sessão (obrigatório: quadra, fisico, video, reuniao, teste)
    session_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False
    )

    # Objetivo principal
    main_objective: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )

    # Objetivo secundário
    secondary_objective: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    # Carga planejada
    planned_load: Mapped[Optional[int]] = mapped_column(
        SmallInteger,
        nullable=True
    )

    # Clima do grupo (1-5)
    group_climate: Mapped[Optional[int]] = mapped_column(
        SmallInteger,
        nullable=True
    )

    # Notas
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    # Fases de foco (booleanos derivados)
    phase_focus_defense: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false")
    )
    phase_focus_attack: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false")
    )
    phase_focus_transition_offense: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false")
    )
    phase_focus_transition_defense: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false")
    )

    # Intensidade alvo (1-5)
    intensity_target: Mapped[Optional[int]] = mapped_column(
        SmallInteger,
        nullable=True
    )

    # Bloco da sessão
    session_block: Mapped[Optional[str]] = mapped_column(
        String(32),
        nullable=True
    )

    # Timestamps (RDB3)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=text("now()"),
        nullable=False
    )

    # Criador (auditoria) - FK para users
    created_by_user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=text("now()"),
        nullable=False
    )

    # Soft delete (RDB4)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    deleted_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    # Focos de treino (percentuais 0-100) - Análise estratégica /statistics/teams
    focus_attack_positional_pct: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True
    )
    focus_defense_positional_pct: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True
    )
    focus_transition_offense_pct: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True
    )
    focus_transition_defense_pct: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True
    )
    focus_attack_technical_pct: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True
    )
    focus_defense_technical_pct: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True
    )
    focus_physical_pct: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True
    )

    # Relacionamento com microciclo (planejamento semanal)
    microcycle_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("training_microcycles.id"),
        nullable=True,
        index=True
    )

    # Estado da sessão (draft, scheduled, in_progress, closed, readonly)
    status: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default='draft',
        server_default=text("'draft'")
    )

    # Revisão concluída (congelamento)
    closed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    closed_by_user_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True
    )

    # Desvio de planejamento
    deviation_justification: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    planning_deviation_flag: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false")
    )

    @property
    def total_focus_pct(self) -> Optional[float]:
        if "_total_focus_pct_override" in self.__dict__:
            return self.__dict__["_total_focus_pct_override"]
        values = [
            self.focus_attack_positional_pct,
            self.focus_defense_positional_pct,
            self.focus_transition_offense_pct,
            self.focus_transition_defense_pct,
            self.focus_attack_technical_pct,
            self.focus_defense_technical_pct,
            self.focus_physical_pct,
        ]
        if all(v is None for v in values):
            return None
        return float(sum(float(v) if v is not None else 0 for v in values))

    @total_focus_pct.setter
    def total_focus_pct(self, value: Optional[float]) -> None:
        self.__dict__["_total_focus_pct_override"] = value

    # Check constraints (conforme DB)
    __table_args__ = (
        CheckConstraint(
            "(COALESCE(focus_attack_positional_pct, 0::numeric) + "
            "COALESCE(focus_defense_positional_pct, 0::numeric) + "
            "COALESCE(focus_transition_offense_pct, 0::numeric) + "
            "COALESCE(focus_transition_defense_pct, 0::numeric) + "
            "COALESCE(focus_attack_technical_pct, 0::numeric) + "
            "COALESCE(focus_defense_technical_pct, 0::numeric) + "
            "COALESCE(focus_physical_pct, 0::numeric)) <= 120::numeric",
            name="ck_training_sessions_focus_total_sum"
        ),
        CheckConstraint(
            "deleted_at IS NULL AND deleted_reason IS NULL OR "
            "deleted_at IS NOT NULL AND deleted_reason IS NOT NULL",
            name="ck_training_sessions_deleted_reason"
        ),
        CheckConstraint(
            "focus_attack_positional_pct IS NULL OR "
            "focus_attack_positional_pct >= 0::numeric AND focus_attack_positional_pct <= 100::numeric",
            name="ck_training_sessions_focus_attack_positional_range"
        ),
        CheckConstraint(
            "focus_attack_technical_pct IS NULL OR "
            "focus_attack_technical_pct >= 0::numeric AND focus_attack_technical_pct <= 100::numeric",
            name="ck_training_sessions_focus_attack_technical_range"
        ),
        CheckConstraint(
            "focus_defense_positional_pct IS NULL OR "
            "focus_defense_positional_pct >= 0::numeric AND focus_defense_positional_pct <= 100::numeric",
            name="ck_training_sessions_focus_defense_positional_range"
        ),
        CheckConstraint(
            "focus_defense_technical_pct IS NULL OR "
            "focus_defense_technical_pct >= 0::numeric AND focus_defense_technical_pct <= 100::numeric",
            name="ck_training_sessions_focus_defense_technical_range"
        ),
        CheckConstraint(
            "focus_physical_pct IS NULL OR "
            "focus_physical_pct >= 0::numeric AND focus_physical_pct <= 100::numeric",
            name="ck_training_sessions_focus_physical_range"
        ),
        CheckConstraint(
            "focus_transition_defense_pct IS NULL OR "
            "focus_transition_defense_pct >= 0::numeric AND focus_transition_defense_pct <= 100::numeric",
            name="ck_training_sessions_focus_transition_defense_range"
        ),
        CheckConstraint(
            "focus_transition_offense_pct IS NULL OR "
            "focus_transition_offense_pct >= 0::numeric AND focus_transition_offense_pct <= 100::numeric",
            name="ck_training_sessions_focus_transition_offense_range"
        ),
        CheckConstraint(
            "group_climate IS NULL OR group_climate >= 1 AND group_climate <= 5",
            name="ck_training_sessions_climate"
        ),
        CheckConstraint(
            "intensity_target IS NULL OR intensity_target >= 1 AND intensity_target <= 5",
            name="ck_training_sessions_intensity"
        ),
        CheckConstraint(
            "phase_focus_attack = ((COALESCE(focus_attack_positional_pct, 0::numeric) + "
            "COALESCE(focus_attack_technical_pct, 0::numeric)) >= 5::numeric)",
            name="ck_phase_focus_attack_consistency"
        ),
        CheckConstraint(
            "phase_focus_defense = ((COALESCE(focus_defense_positional_pct, 0::numeric) + "
            "COALESCE(focus_defense_technical_pct, 0::numeric)) >= 5::numeric)",
            name="ck_phase_focus_defense_consistency"
        ),
        CheckConstraint(
            "phase_focus_transition_defense = (COALESCE(focus_transition_defense_pct, 0::numeric) >= 5::numeric)",
            name="ck_phase_focus_transition_defense_consistency"
        ),
        CheckConstraint(
            "phase_focus_transition_offense = (COALESCE(focus_transition_offense_pct, 0::numeric) >= 5::numeric)",
            name="ck_phase_focus_transition_offense_consistency"
        ),
        CheckConstraint(
            "session_type::text = ANY (ARRAY['quadra'::character varying, 'fisico'::character varying, "
            "'video'::character varying, 'reuniao'::character varying, 'teste'::character varying]::text[])",
            name="ck_training_sessions_type"
        ),
        CheckConstraint(
            "status::text = ANY (ARRAY['draft'::character varying, 'scheduled'::character varying, "
            "'in_progress'::character varying, 'closed'::character varying, 'readonly'::character varying]::text[])",
            name="check_training_session_status"
        ),
        Index("idx_sessions_team_date", "team_id", "session_at"),
        Index("idx_training_sessions_deviation_flag", "planning_deviation_flag"),
        Index("idx_training_sessions_microcycle", "microcycle_id"),
        Index("idx_training_sessions_org", "organization_id", "deleted_at"),
        Index("idx_training_sessions_status", "status"),
        Index("idx_training_sessions_team_date", "team_id", "session_at", "deleted_at"),
        Index("ix_training_sessions_team_date_active", "team_id", "session_at"),
        Index("ix_training_sessions_team_season_date", "team_id", "season_id", "session_at"),
    )

    # Relationships
    wellness_posts = relationship(
        "WellnessPost",
        back_populates="training_session",
        lazy="selectin",
    )
    microcycle = relationship(
        "TrainingMicrocycle",
        back_populates="sessions",
        foreign_keys=[microcycle_id],
        lazy="selectin"
    )
    session_exercises = relationship(
        "SessionExercise",
        back_populates="session",
        lazy="selectin",
        cascade="all, delete-orphan"
    )

    @property
    def is_editable_by_author(self) -> bool:
        """
        Verifica se autor ainda pode editar (dentro de 10min).
        R40: 10 minutos para correções rápidas.
        """
        from datetime import timedelta
        cutoff = self.created_at + timedelta(minutes=10)
        return datetime.now(timezone.utc) <= cutoff

    @property
    def is_editable_by_superior(self) -> bool:
        """
        Verifica se superior pode editar (até 24h).
        R40: Até 24 horas, qualquer edição exige aprovação ou perfil superior.
        """
        from datetime import timedelta
        cutoff = self.created_at + timedelta(hours=24)
        return datetime.now(timezone.utc) <= cutoff

    @property
    def requires_admin_note(self) -> bool:
        """
        Verifica se edição requer admin_note (após 24h).
        R40: Após 24h, registro é somente leitura exceto por ação admin.
        """
        return not self.is_editable_by_superior

    # ------------------------------------------------------------------
    # Campos compatíveis (analytics) — não persistidos
    # ------------------------------------------------------------------
    @property
    def rpe_avg(self) -> Optional[float]:
        """Compatibilidade para analytics quando não há coluna persistida."""
        return None

    @property
    def planned_rpe(self) -> Optional[float]:
        """Compatibilidade para analytics quando não há coluna persistida."""
        return None

    @property
    def internal_load_avg(self) -> Optional[float]:
        """Compatibilidade para analytics quando não há coluna persistida."""
        return None

    def __repr__(self) -> str:
        return f"<TrainingSession {self.id} at {self.session_at}>"
