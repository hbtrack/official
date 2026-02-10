"""
Model: CompetitionMatch

Estrutura da tabela competition_matches:
- id (uuid, PK)
- competition_id (uuid, FK competitions, NOT NULL)
- phase_id (uuid, FK competition_phases, NULL)
- external_reference_id (varchar 100, NULL) - ID para upsert (evita duplicação ao reimportar PDF)
- home_team_id (uuid, FK competition_opponent_teams, NULL)
- away_team_id (uuid, FK competition_opponent_teams, NULL)
- is_our_match (bool, default false) - se é jogo da nossa equipe
- our_team_is_home (bool, NULL) - se nossa equipe é mandante
- linked_match_id (uuid, FK matches, NULL) - vínculo com tabela matches
- match_date (date, NULL)
- match_time (time, NULL)
- match_datetime (timestamptz, NULL)
- location (varchar 255, NULL)
- round_number (int, NULL)
- round_name (varchar 100, NULL)
- home_score, away_score (int, NULL)
- home_score_extra, away_score_extra (int, NULL) - prorrogação
- home_score_penalties, away_score_penalties (int, NULL) - pênaltis
- status (varchar 50, default 'scheduled')
- notes (text, NULL)
- created_at, updated_at (timestamptz)

Regras:
- Armazena TODOS os jogos da competição, não apenas os nossos
- external_reference_id permite reimportar PDF sem duplicar
- linked_match_id conecta com tabela matches para detalhes
"""

# HB-AUTOGEN-IMPORTS:BEGIN
from __future__ import annotations

from datetime import date, datetime
from typing import Optional
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import ForeignKey, CheckConstraint, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB as PG_JSONB, INET as PG_INET, ENUM as PG_ENUM
# HB-AUTOGEN-IMPORTS:END
from datetime import datetime, date, time
from typing import Optional, TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import DateTime, Date, Time, ForeignKey, String, Integer, Boolean, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.competition import Competition
    from app.models.competition_phase import CompetitionPhase
    from app.models.competition_opponent_team import CompetitionOpponentTeam
    from app.models.match import Match


class CompetitionMatch(Base):
    """
    Jogo de uma competição.
    
    Armazena todos os jogos da competição (não apenas os nossos).
    Permite rastrear a tabela completa e calcular classificação.
    """

    __tablename__ = "competition_matches"


# HB-AUTOGEN:BEGIN

    # AUTO-GENERATED FROM DB (SSOT). DO NOT EDIT MANUALLY.

    # Table: public.competition_matches

    __table_args__ = (

        Index('ix_competition_matches_competition_id', 'competition_id', unique=False),

        Index('ix_competition_matches_date', 'match_date', unique=False),

        Index('ix_competition_matches_linked_match_id', 'linked_match_id', unique=False),

        Index('ix_competition_matches_our_match', 'is_our_match', unique=False),

        Index('ix_competition_matches_phase_id', 'phase_id', unique=False),

    )


    # NOTE: typing helpers may require: from datetime import date, datetime; from uuid import UUID


    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'))

    competition_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('competitions.id', name='fk_competition_matches_competition_id', ondelete='CASCADE'), nullable=False)

    phase_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('competition_phases.id', name='fk_competition_matches_phase_id', ondelete='SET NULL'), nullable=True)

    external_reference_id: Mapped[Optional[str]] = mapped_column(sa.String(length=100), nullable=True)

    home_team_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('competition_opponent_teams.id', name='fk_competition_matches_home_team_id', ondelete='SET NULL'), nullable=True)

    away_team_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('competition_opponent_teams.id', name='fk_competition_matches_away_team_id', ondelete='SET NULL'), nullable=True)

    is_our_match: Mapped[Optional[bool]] = mapped_column(sa.Boolean(), nullable=True, server_default=sa.text('false'))

    our_team_is_home: Mapped[Optional[bool]] = mapped_column(sa.Boolean(), nullable=True)

    linked_match_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('matches.id', name='fk_competition_matches_linked_match_id', ondelete='SET NULL'), nullable=True)

    match_date: Mapped[Optional[date]] = mapped_column(sa.Date(), nullable=True)

    match_time: Mapped[Optional[object]] = mapped_column(sa.TIME(), nullable=True)

    match_datetime: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)

    location: Mapped[Optional[str]] = mapped_column(sa.String(length=255), nullable=True)

    round_number: Mapped[Optional[int]] = mapped_column(sa.Integer(), nullable=True)

    round_name: Mapped[Optional[str]] = mapped_column(sa.String(length=100), nullable=True)

    home_score: Mapped[Optional[int]] = mapped_column(sa.Integer(), nullable=True)

    away_score: Mapped[Optional[int]] = mapped_column(sa.Integer(), nullable=True)

    home_score_extra: Mapped[Optional[int]] = mapped_column(sa.Integer(), nullable=True)

    away_score_extra: Mapped[Optional[int]] = mapped_column(sa.Integer(), nullable=True)

    home_score_penalties: Mapped[Optional[int]] = mapped_column(sa.Integer(), nullable=True)

    away_score_penalties: Mapped[Optional[int]] = mapped_column(sa.Integer(), nullable=True)

    status: Mapped[Optional[str]] = mapped_column(sa.String(length=50), nullable=True, server_default=sa.text("'scheduled'::character varying"))

    notes: Mapped[Optional[str]] = mapped_column(sa.Text(), nullable=True)

    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))

    updated_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))

    # HB-AUTOGEN:END
    # Primary key

    # Competition FK

    # Phase FK

    # External reference (para upsert - evita duplicação ao reimportar PDF)

    # Teams


    # Flags para identificar nossos jogos


    # Vínculo com tabela matches (para detalhes do jogo)

    # Data e local




    # Rodada


    # Resultado


    # Prorrogação


    # Pênaltis


    # Status

    # Observações

    # Timestamps


    # Relationships
    competition: Mapped["Competition"] = relationship(
        "Competition",
        back_populates="matches",
    )

    phase: Mapped[Optional["CompetitionPhase"]] = relationship(
        "CompetitionPhase",
        back_populates="matches",
    )

    home_team: Mapped[Optional["CompetitionOpponentTeam"]] = relationship(
        "CompetitionOpponentTeam",
        foreign_keys=[home_team_id],
        back_populates="home_matches",
    )

    away_team: Mapped[Optional["CompetitionOpponentTeam"]] = relationship(
        "CompetitionOpponentTeam",
        foreign_keys=[away_team_id],
        back_populates="away_matches",
    )

    linked_match: Mapped[Optional["Match"]] = relationship(
        "Match",
        foreign_keys=[linked_match_id],
        lazy="selectin",
    )

    # Computed properties
    @property
    def is_finished(self) -> bool:
        """Check if match is finished."""
        return self.status == "finished"

    @property
    def has_result(self) -> bool:
        """Check if match has a result."""
        return self.home_score is not None and self.away_score is not None

    @property
    def winner_id(self) -> Optional[str]:
        """Get winner team id, None if draw or not finished."""
        if not self.has_result:
            return None
        if self.home_score > self.away_score:
            return self.home_team_id
        elif self.away_score > self.home_score:
            return self.away_team_id
        return None  # Draw

    @property
    def is_draw(self) -> bool:
        """Check if match ended in a draw."""
        if not self.has_result:
            return False
        return self.home_score == self.away_score

    def __repr__(self) -> str:
        return f"<CompetitionMatch {self.id} {self.home_score}-{self.away_score} status={self.status}>"
