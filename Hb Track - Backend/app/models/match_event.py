"""
Model: MatchEvent conforme schema.sql (DB SSOT).

Tabela match_events: Eventos de jogo lance a lance. Coração analítico:
reconstrói jogo, contexto tático e gera estatísticas.
"""

# HB-AUTOGEN-IMPORTS:BEGIN
from __future__ import annotations

from datetime import date, datetime
from typing import Optional
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import ForeignKey, CheckConstraint, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB as PG_JSONB, INET as PG_INET, ENUM as PG_ENUM
# HB-AUTOGEN-IMPORTS:END

from decimal import Decimal
from enum import Enum


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


# HB-AUTOGEN:BEGIN
    # AUTO-GENERATED FROM DB (SSOT). DO NOT EDIT MANUALLY.
    # Table: public.match_events
    __table_args__ = (
        CheckConstraint('period_number >= 1', name='ck_match_events_period'),
        CheckConstraint('score_opponent >= 0', name='ck_match_events_score_opponent'),
        CheckConstraint('score_our >= 0', name='ck_match_events_score_our'),
        CheckConstraint("source::text = ANY (ARRAY['live'::character varying, 'video'::character varying, 'post_game_correction'::character varying]::text[])", name='ck_match_events_source'),
        CheckConstraint('game_time_seconds >= 0', name='ck_match_events_time'),
        CheckConstraint('x_coord IS NULL OR x_coord >= 0::numeric AND x_coord <= 100::numeric', name='ck_match_events_x_coord'),
        CheckConstraint('y_coord IS NULL OR y_coord >= 0::numeric AND y_coord <= 100::numeric', name='ck_match_events_y_coord'),
        CheckConstraint("(deleted_at IS NULL AND deleted_reason IS NULL) OR (deleted_at IS NOT NULL AND deleted_reason IS NOT NULL)", name='ck_match_events_deleted_reason'),
        Index('ix_match_events_athlete_id', 'athlete_id', unique=False),
        Index('ix_match_events_event_type', 'event_type', unique=False),
        Index('ix_match_events_match_id', 'match_id', unique=False),
        Index('ix_match_events_phase_of_play', 'phase_of_play', unique=False),
        Index('ix_match_events_team_id', 'team_id', unique=False),
    )

    # NOTE: typing helpers may require: from datetime import date, datetime; from uuid import UUID

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'))
    match_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('matches.id', name='fk_match_events_match_id', ondelete='CASCADE'), nullable=False)
    team_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('teams.id', name='fk_match_events_team_id', ondelete='RESTRICT'), nullable=False)
    opponent_team_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('teams.id', name='fk_match_events_opponent_team_id', ondelete='RESTRICT'), nullable=True)
    athlete_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('athletes.id', name='fk_match_events_athlete_id', ondelete='RESTRICT'), nullable=True)
    assisting_athlete_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('athletes.id', name='fk_match_events_assisting_athlete_id', ondelete='RESTRICT'), nullable=True)
    secondary_athlete_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('athletes.id', name='fk_match_events_secondary_athlete_id', ondelete='RESTRICT'), nullable=True)
    period_number: Mapped[int] = mapped_column(sa.SmallInteger(), nullable=False)
    game_time_seconds: Mapped[int] = mapped_column(sa.Integer(), nullable=False)
    phase_of_play: Mapped[str] = mapped_column(sa.String(length=32), ForeignKey('phases_of_play.code', name='fk_match_events_phase_of_play', ondelete='RESTRICT'), nullable=False)
    possession_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('match_possessions.id', name='fk_match_events_possession_id', ondelete='SET NULL'), nullable=True)
    advantage_state: Mapped[str] = mapped_column(sa.String(length=32), ForeignKey('advantage_states.code', name='fk_match_events_advantage_state', ondelete='RESTRICT'), nullable=False)
    score_our: Mapped[int] = mapped_column(sa.SmallInteger(), nullable=False)
    score_opponent: Mapped[int] = mapped_column(sa.SmallInteger(), nullable=False)
    event_type: Mapped[str] = mapped_column(sa.String(length=64), ForeignKey('event_types.code', name='fk_match_events_event_type', ondelete='RESTRICT'), nullable=False)
    event_subtype: Mapped[Optional[str]] = mapped_column(sa.String(length=64), ForeignKey('event_subtypes.code', name='fk_match_events_event_subtype', ondelete='RESTRICT'), nullable=True)
    outcome: Mapped[str] = mapped_column(sa.String(length=64), nullable=False)
    is_shot: Mapped[bool] = mapped_column(sa.Boolean(), nullable=False)
    is_goal: Mapped[bool] = mapped_column(sa.Boolean(), nullable=False)
    x_coord: Mapped[Optional[object]] = mapped_column(sa.Numeric(5, 2), nullable=True)
    y_coord: Mapped[Optional[object]] = mapped_column(sa.Numeric(5, 2), nullable=True)
    related_event_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('match_events.id', name='fk_match_events_related_event_id', ondelete='SET NULL'), nullable=True)
    source: Mapped[str] = mapped_column(sa.String(length=32), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(sa.Text(), nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    deleted_reason: Mapped[Optional[str]] = mapped_column(sa.Text(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    created_by_user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('users.id', name='fk_match_events_created_by_user_id', ondelete='RESTRICT'), nullable=False)
    # HB-AUTOGEN:END
    # PK

    # FK para match

    # FK para team

    # FK para opponent team (opcional)

    # FK para athlete (opcional)

    # FK para assisting athlete (opcional)

    # FK para secondary athlete (opcional)

    # Período do jogo

    # Tempo em segundos

    # Fase do jogo (FK para phases_of_play)

    # FK para possession (opcional)

    # Estado de vantagem (FK para advantage_states)

    # Placar no momento do evento


    # Tipo de evento (FK para event_types)

    # Subtipo de evento (FK para event_subtypes, opcional)

    # Resultado do evento

    # Flags de classificação rápida


    # Posições em quadra (percentual 0-100)


    # FK para evento relacionado (auto-referência)

    # Fonte do registro

    # Notas

    # Timestamps

    # FK para user criador

    # Check constraints (conforme DB)

    def __repr__(self) -> str:
        return f"<MatchEvent {self.event_type} at {self.game_time_seconds}s (period {self.period_number})>"
