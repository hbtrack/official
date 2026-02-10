"""
Model: CompetitionStanding

Estrutura da tabela competition_standings:
- id (uuid, PK)
- competition_id (uuid, FK competitions, NOT NULL)
- phase_id (uuid, FK competition_phases, NULL)
- opponent_team_id (uuid, FK competition_opponent_teams, NOT NULL)
- position (int, NOT NULL)
- group_name (varchar 50, NULL)
- points, played, wins, draws, losses (int, default 0)
- goals_for, goals_against, goal_difference (int, default 0)
- recent_form (varchar 10, NULL) - últimos 5 jogos (WWDLL)
- qualification_status (varchar 50, NULL) - qualified, playoffs, relegation, eliminated
- updated_at (timestamptz)

Regras:
- É uma tabela de cache para performance
- Pode ser recalculada a partir dos jogos
- Única por (competition_id, phase_id, opponent_team_id)
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
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, Integer, text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.competition import Competition
    from app.models.competition_phase import CompetitionPhase
    from app.models.competition_opponent_team import CompetitionOpponentTeam


class CompetitionStanding(Base):
    """
    Classificação de uma equipe em uma fase da competição.
    
    Tabela de cache para performance nas consultas de classificação.
    Pode ser recalculada a partir dos resultados dos jogos.
    """

    __tablename__ = "competition_standings"


# HB-AUTOGEN:BEGIN

    # AUTO-GENERATED FROM DB (SSOT). DO NOT EDIT MANUALLY.

    # Table: public.competition_standings

    __table_args__ = (

        UniqueConstraint('competition_id', 'phase_id', 'opponent_team_id', name='uk_competition_standings_team_phase'),

        Index('ix_competition_standings_competition_id', 'competition_id', unique=False),

        Index('ix_competition_standings_position', 'competition_id', 'phase_id', 'position', unique=False),

    )


    # NOTE: typing helpers may require: from datetime import date, datetime; from uuid import UUID


    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'))

    competition_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('competitions.id', name='fk_competition_standings_competition_id', ondelete='CASCADE'), nullable=False)

    phase_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('competition_phases.id', name='fk_competition_standings_phase_id', ondelete='CASCADE'), nullable=True)

    opponent_team_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('competition_opponent_teams.id', name='fk_competition_standings_opponent_team_id', ondelete='CASCADE'), nullable=False)

    position: Mapped[int] = mapped_column(sa.Integer(), nullable=False)

    group_name: Mapped[Optional[str]] = mapped_column(sa.String(length=50), nullable=True)

    points: Mapped[Optional[int]] = mapped_column(sa.Integer(), nullable=True, server_default=sa.text('0'))

    played: Mapped[Optional[int]] = mapped_column(sa.Integer(), nullable=True, server_default=sa.text('0'))

    wins: Mapped[Optional[int]] = mapped_column(sa.Integer(), nullable=True, server_default=sa.text('0'))

    draws: Mapped[Optional[int]] = mapped_column(sa.Integer(), nullable=True, server_default=sa.text('0'))

    losses: Mapped[Optional[int]] = mapped_column(sa.Integer(), nullable=True, server_default=sa.text('0'))

    goals_for: Mapped[Optional[int]] = mapped_column(sa.Integer(), nullable=True, server_default=sa.text('0'))

    goals_against: Mapped[Optional[int]] = mapped_column(sa.Integer(), nullable=True, server_default=sa.text('0'))

    goal_difference: Mapped[Optional[int]] = mapped_column(sa.Integer(), nullable=True, server_default=sa.text('0'))

    recent_form: Mapped[Optional[str]] = mapped_column(sa.String(length=10), nullable=True)

    qualification_status: Mapped[Optional[str]] = mapped_column(sa.String(length=50), nullable=True)

    updated_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))

    # HB-AUTOGEN:END
    # Unique constraint

    # Primary key

    # Competition FK

    # Phase FK (opcional - pode ser classificação geral)

    # Team FK

    # Position

    # Group (se houver)

    # Statistics








    # Recent form (últimos 5 jogos: W, D, L)

    # Qualification status

    # Timestamp

    # Relationships
    competition: Mapped["Competition"] = relationship(
        "Competition",
        back_populates="standings",
    )

    phase: Mapped[Optional["CompetitionPhase"]] = relationship(
        "CompetitionPhase",
        back_populates="standings",
    )

    opponent_team: Mapped["CompetitionOpponentTeam"] = relationship(
        "CompetitionOpponentTeam",
        back_populates="standings",
    )

    def __repr__(self) -> str:
        return f"<CompetitionStanding pos={self.position} team={self.opponent_team_id} pts={self.points}>"
