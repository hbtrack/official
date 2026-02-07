"""
Model: MatchEvent conforme schema.sql (DB SSOT).

Tabela match_events: Eventos de jogo lance a lance. Coração analítico:
reconstrói jogo, contexto tático e gera estatísticas.
"""
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class EventType(str, Enum):
    """Tipos de eventos conforme tabela event_types."""
    goal = "goal"
    shot = "shot"
    save = "save"
    turnover = "turnover"
    foul = "foul"
    card = "card"
    substitution = "substitution"
    timeout = "timeout"
    other = "other"


class MatchEvent(Base):
    """
    Evento de partida conforme schema real (match_events).
    """
    __tablename__ = "match_events"

    # PK
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()"),
    )

    # FK para match
    match_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("matches.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # FK para team
    team_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    # FK para opponent team (opcional)
    opponent_team_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="RESTRICT"),
        nullable=True,
    )

    # FK para athlete (opcional)
    athlete_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("athletes.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    # FK para assisting athlete (opcional)
    assisting_athlete_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("athletes.id", ondelete="RESTRICT"),
        nullable=True,
    )

    # FK para secondary athlete (opcional)
    secondary_athlete_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("athletes.id", ondelete="RESTRICT"),
        nullable=True,
    )

    # Período do jogo
    period_number: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
    )

    # Tempo em segundos
    game_time_seconds: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    # Fase do jogo (FK para phases_of_play)
    phase_of_play: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("phases_of_play.code", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    # FK para possession (opcional)
    possession_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("match_possessions.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Estado de vantagem (FK para advantage_states)
    advantage_state: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("advantage_states.code", ondelete="RESTRICT"),
        nullable=False,
    )

    # Placar no momento do evento
    score_our: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
    )

    score_opponent: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
    )

    # Tipo de evento (FK para event_types)
    event_type: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("event_types.code", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    # Subtipo de evento (FK para event_subtypes, opcional)
    event_subtype: Mapped[Optional[str]] = mapped_column(
        String(64),
        ForeignKey("event_subtypes.code", ondelete="RESTRICT"),
        nullable=True,
    )

    # Resultado do evento
    outcome: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    # Flags de classificação rápida
    is_shot: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    is_goal: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    # Posições em quadra (percentual 0-100)
    x_coord: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )

    y_coord: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )

    # FK para evento relacionado (auto-referência)
    related_event_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("match_events.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Fonte do registro
    source: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    # Notas
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=text("now()"),
        nullable=False,
    )

    # FK para user criador
    created_by_user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )

    # Check constraints (conforme DB)
    __table_args__ = (
        CheckConstraint(
            "period_number >= 1",
            name="ck_match_events_period"
        ),
        CheckConstraint(
            "score_opponent >= 0",
            name="ck_match_events_score_opponent"
        ),
        CheckConstraint(
            "score_our >= 0",
            name="ck_match_events_score_our"
        ),
        CheckConstraint(
            "source::text = ANY (ARRAY['live'::character varying, "
            "'video'::character varying, 'post_game_correction'::character varying]::text[])",
            name="ck_match_events_source"
        ),
        CheckConstraint(
            "game_time_seconds >= 0",
            name="ck_match_events_time"
        ),
        CheckConstraint(
            "x_coord IS NULL OR x_coord >= 0::numeric AND x_coord <= 100::numeric",
            name="ck_match_events_x_coord"
        ),
        CheckConstraint(
            "y_coord IS NULL OR y_coord >= 0::numeric AND y_coord <= 100::numeric",
            name="ck_match_events_y_coord"
        ),
    )

    def __repr__(self) -> str:
        return f"<MatchEvent {self.event_type} at {self.game_time_seconds}s (period {self.period_number})>"
