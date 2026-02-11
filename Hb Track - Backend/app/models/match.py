"""
Model: Match conforme schema.sql (DB SSOT).

Tabela matches: Jogos oficiais. Ponto de partida para convocação,
súmula, eventos, estatísticas e relatórios.
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

from enum import Enum


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


# HB-AUTOGEN:BEGIN
    # AUTO-GENERATED FROM DB (SSOT). DO NOT EDIT MANUALLY.
    # Table: public.matches
    __table_args__ = (
        CheckConstraint('deleted_at IS NULL AND deleted_reason IS NULL OR deleted_at IS NOT NULL AND deleted_reason IS NOT NULL', name='ck_matches_deleted_reason'),
        CheckConstraint('home_team_id <> away_team_id', name='ck_matches_different_teams'),
        CheckConstraint('our_team_id = home_team_id OR our_team_id = away_team_id', name='ck_matches_our_team'),
        CheckConstraint("phase::text = ANY (ARRAY['group'::character varying, 'semifinal'::character varying, 'final'::character varying, 'friendly'::character varying]::text[])", name='ck_matches_phase'),
        CheckConstraint('final_score_away IS NULL OR final_score_away >= 0', name='ck_matches_score_away'),
        CheckConstraint('final_score_home IS NULL OR final_score_home >= 0', name='ck_matches_score_home'),
        CheckConstraint("status::text = ANY (ARRAY['scheduled'::character varying, 'in_progress'::character varying, 'finished'::character varying, 'cancelled'::character varying]::text[])", name='ck_matches_status'),
        Index('ix_matches_away_team_id', 'away_team_id', unique=False),
        Index('ix_matches_home_team_id', 'home_team_id', unique=False),
        Index('ix_matches_match_date', 'match_date', unique=False),
        Index('ix_matches_season_date_active', 'season_id', 'match_date', unique=False, postgresql_where=sa.text('(deleted_at IS NULL)')),
        Index('ix_matches_season_id', 'season_id', unique=False),
        Index('ix_matches_status', 'status', unique=False),
    )

    # NOTE: typing helpers may require: from datetime import date, datetime; from uuid import UUID

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'))
    season_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('seasons.id', name='fk_matches_season_id', ondelete='RESTRICT'), nullable=False)
    competition_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    match_date: Mapped[date] = mapped_column(sa.Date(), nullable=False)
    start_time: Mapped[Optional[object]] = mapped_column(sa.TIME(), nullable=True)
    venue: Mapped[Optional[str]] = mapped_column(sa.String(length=120), nullable=True)
    phase: Mapped[str] = mapped_column(sa.String(length=32), nullable=False)
    status: Mapped[str] = mapped_column(sa.String(length=32), nullable=False)
    home_team_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('teams.id', name='fk_matches_home_team_id', ondelete='RESTRICT'), nullable=False)
    away_team_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('teams.id', name='fk_matches_away_team_id', ondelete='RESTRICT'), nullable=False)
    our_team_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('teams.id', name='fk_matches_our_team_id', ondelete='RESTRICT'), nullable=False)
    final_score_home: Mapped[Optional[int]] = mapped_column(sa.SmallInteger(), nullable=True)
    final_score_away: Mapped[Optional[int]] = mapped_column(sa.SmallInteger(), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(sa.Text(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    created_by_user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('users.id', name='fk_matches_created_by_user_id', ondelete='RESTRICT'), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    deleted_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    deleted_reason: Mapped[Optional[str]] = mapped_column(sa.Text(), nullable=True)
    # HB-AUTOGEN:END
    # PK

    # FK para season (obrigatório)

    # Competition (opcional, sem FK no DB)

    # Data do jogo

    # Horário do jogo (opcional)

    # Local do jogo

    # Fase do jogo (group, semifinal, final, friendly)

    # Status do jogo (scheduled, in_progress, finished, cancelled)

    # FK para time da casa

    # FK para time visitante

    # FK para nosso time (deve ser home ou away)

    # Placar final


    # Notas

    # Timestamps

    # FK para user criador


    # Soft delete

    # Check constraints (conforme DB)

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
