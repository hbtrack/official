"""
Model: Match conforme schema.sql (DB SSOT).

Tabela matches: Jogos oficiais. Ponto de partida para convocação,
súmula, eventos, estatísticas e relatórios.
"""
from datetime import datetime, date, time as time_type, timezone
from typing import Optional
from uuid import uuid4
from enum import Enum

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    SmallInteger,
    String,
    Text,
    Time,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class MatchStatus(str, Enum):
    """Estados do jogo conforme constraints do banco."""
    scheduled = "scheduled"
    in_progress = "in_progress"
    finished = "finished"
    cancelled = "cancelled"


class MatchType(str, Enum):
    """Fase/Tipo do jogo conforme constraints do banco."""
    group = "group"
    semifinal = "semifinal"
    final = "final"
    friendly = "friendly"


class Match(Base):
    """
    Jogo oficial.
    """
    __tablename__ = "matches"

    # PK
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()")
    )

    # FK para season (obrigatório)
    season_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("seasons.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

    # Competition (opcional, sem FK no DB)
    competition_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    # Data do jogo
    match_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True
    )

    # Horário do jogo (opcional)
    start_time: Mapped[Optional[time_type]] = mapped_column(
        Time(timezone=False),
        nullable=True
    )

    # Local do jogo
    venue: Mapped[Optional[str]] = mapped_column(
        String(120),
        nullable=True
    )

    # Fase do jogo (group, semifinal, final, friendly)
    phase: Mapped[str] = mapped_column(
        String(32),
        nullable=False
    )

    # Status do jogo (scheduled, in_progress, finished, cancelled)
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        index=True
    )

    # FK para time da casa
    home_team_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

    # FK para time visitante
    away_team_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

    # FK para nosso time (deve ser home ou away)
    our_team_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="RESTRICT"),
        nullable=False,
    )

    # Placar final
    final_score_home: Mapped[Optional[int]] = mapped_column(
        SmallInteger,
        nullable=True
    )

    final_score_away: Mapped[Optional[int]] = mapped_column(
        SmallInteger,
        nullable=True
    )

    # Notas
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=text("now()"),
        nullable=False
    )

    # FK para user criador
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

    # Soft delete
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    deleted_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    # Check constraints (conforme DB)
    __table_args__ = (
        CheckConstraint(
            "deleted_at IS NULL AND deleted_reason IS NULL OR "
            "deleted_at IS NOT NULL AND deleted_reason IS NOT NULL",
            name="ck_matches_deleted_reason"
        ),
        CheckConstraint(
            "home_team_id <> away_team_id",
            name="ck_matches_different_teams"
        ),
        CheckConstraint(
            "our_team_id = home_team_id OR our_team_id = away_team_id",
            name="ck_matches_our_team"
        ),
        CheckConstraint(
            "phase::text = ANY (ARRAY['group'::character varying, 'semifinal'::character varying, "
            "'final'::character varying, 'friendly'::character varying]::text[])",
            name="ck_matches_phase"
        ),
        CheckConstraint(
            "final_score_away IS NULL OR final_score_away >= 0",
            name="ck_matches_score_away"
        ),
        CheckConstraint(
            "final_score_home IS NULL OR final_score_home >= 0",
            name="ck_matches_score_home"
        ),
        CheckConstraint(
            "status::text = ANY (ARRAY['scheduled'::character varying, 'in_progress'::character varying, "
            "'finished'::character varying, 'cancelled'::character varying]::text[])",
            name="ck_matches_status"
        ),
        Index("ix_matches_season_date_active", "season_id", "match_date"),
    )

    @property
    def is_finalized(self) -> bool:
        return self.status == MatchStatus.finished.value

    @property
    def is_editable(self) -> bool:
        return not self.is_finalized

    @property
    def is_official(self) -> bool:
        return self.phase != MatchType.friendly.value

    @property
    def is_home(self) -> bool:
        return self.our_team_id == self.home_team_id

    def __repr__(self) -> str:
        return f"<Match {self.id} status={self.status}>"
