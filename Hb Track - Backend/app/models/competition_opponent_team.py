"""
Model: CompetitionOpponentTeam

Estrutura da tabela competition_opponent_teams:
- id (uuid, PK)
- competition_id (uuid, FK competitions, NOT NULL)
- name (varchar 255, NOT NULL)
- short_name (varchar 50, NULL)
- category (varchar 50, NULL)
- city (varchar 100, NULL)
- logo_url (varchar 500, NULL)
- linked_team_id (uuid, FK teams, NULL) - vínculo com equipe cadastrada (fuzzy match)
- group_name (varchar 50, NULL) - grupo na competição
- stats (jsonb, default {...}) - estatísticas calculadas
- status (varchar 50, default 'active') - active, eliminated, qualified, withdrawn
- created_at, updated_at (timestamptz)

Regras:
- Equipes adversárias são cadastradas por competição
- Podem ser vinculadas a equipes do sistema (linked_team_id)
- Estatísticas são atualizadas automaticamente por trigger
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
from typing import Optional, TYPE_CHECKING, List, Any
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.competition import Competition
    from app.models.team import Team
    from app.models.competition_match import CompetitionMatch
    from app.models.competition_standing import CompetitionStanding


# Default stats structure
DEFAULT_STATS = {
    "points": 0,
    "played": 0,
    "wins": 0,
    "draws": 0,
    "losses": 0,
    "goals_for": 0,
    "goals_against": 0,
    "goal_difference": 0,
}


class CompetitionOpponentTeam(Base):
    """
    Equipe adversária em uma competição.
    
    Representa uma equipe que participa da competição (incluindo a nossa).
    As estatísticas são calculadas automaticamente após cada jogo.
    """

    __tablename__ = "competition_opponent_teams"


# HB-AUTOGEN:BEGIN

    # AUTO-GENERATED FROM DB (SSOT). DO NOT EDIT MANUALLY.

    # Table: public.competition_opponent_teams

    __table_args__ = (

        Index('ix_competition_opponent_teams_competition_id', 'competition_id', unique=False),

        Index('ix_competition_opponent_teams_group', 'competition_id', 'group_name', unique=False),

        Index('ix_competition_opponent_teams_linked_team_id', 'linked_team_id', unique=False),

        CheckConstraint("(deleted_at IS NULL AND deleted_reason IS NULL) OR (deleted_at IS NOT NULL AND deleted_reason IS NOT NULL)", name='ck_competition_opponent_teams_deleted_reason'),

    )


    # NOTE: typing helpers may require: from datetime import date, datetime; from uuid import UUID


    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'))

    competition_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('competitions.id', name='fk_competition_opponent_teams_competition_id', ondelete='CASCADE'), nullable=False)

    name: Mapped[str] = mapped_column(sa.String(length=255), nullable=False)

    short_name: Mapped[Optional[str]] = mapped_column(sa.String(length=50), nullable=True)

    category: Mapped[Optional[str]] = mapped_column(sa.String(length=50), nullable=True)

    city: Mapped[Optional[str]] = mapped_column(sa.String(length=100), nullable=True)

    logo_url: Mapped[Optional[str]] = mapped_column(sa.String(length=500), nullable=True)

    linked_team_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('teams.id', name='fk_competition_opponent_teams_linked_team_id', ondelete='SET NULL'), nullable=True)

    group_name: Mapped[Optional[str]] = mapped_column(sa.String(length=50), nullable=True)

    stats: Mapped[Optional[object]] = mapped_column(PG_JSONB(), nullable=True, server_default=sa.text('\'{"wins": 0, "draws": 0, "losses": 0, "played": 0, "points": 0, "goals_for": 0, "goals_against": 0, "goal_difference": 0}\'::jsonb'))

    status: Mapped[Optional[str]] = mapped_column(sa.String(length=50), nullable=True, server_default=sa.text("'active'::character varying"))

    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))

    updated_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))

    deleted_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)

    deleted_reason: Mapped[Optional[str]] = mapped_column(sa.Text(), nullable=True)

    # HB-AUTOGEN:END
    # Primary key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
        server_default=text("gen_random_uuid()"),
    )

    # Competition FK

    # Core fields





    # Vínculo com equipe do sistema (fuzzy match)

    # Grupo na competição

    # Estatísticas calculadas

    # Status

    # Timestamps


    # Relationships
    competition: Mapped["Competition"] = relationship(
        "Competition",
        back_populates="opponent_teams",
    )

    linked_team: Mapped[Optional["Team"]] = relationship(
        "Team",
        foreign_keys=[linked_team_id],
        lazy="selectin",
    )

    home_matches: Mapped[List["CompetitionMatch"]] = relationship(
        "CompetitionMatch",
        foreign_keys="CompetitionMatch.home_team_id",
        back_populates="home_team",
        lazy="selectin",
    )

    away_matches: Mapped[List["CompetitionMatch"]] = relationship(
        "CompetitionMatch",
        foreign_keys="CompetitionMatch.away_team_id",
        back_populates="away_team",
        lazy="selectin",
    )

    standings: Mapped[List["CompetitionStanding"]] = relationship(
        "CompetitionStanding",
        back_populates="opponent_team",
        lazy="selectin",
    )

    # Computed properties
    @property
    def points(self) -> int:
        """Total de pontos."""
        return self.stats.get("points", 0) if self.stats else 0

    @property
    def played(self) -> int:
        """Total de jogos."""
        return self.stats.get("played", 0) if self.stats else 0

    @property
    def wins(self) -> int:
        """Total de vitórias."""
        return self.stats.get("wins", 0) if self.stats else 0

    @property
    def draws(self) -> int:
        """Total de empates."""
        return self.stats.get("draws", 0) if self.stats else 0

    @property
    def losses(self) -> int:
        """Total de derrotas."""
        return self.stats.get("losses", 0) if self.stats else 0

    @property
    def goals_for(self) -> int:
        """Total de gols marcados."""
        return self.stats.get("goals_for", 0) if self.stats else 0

    @property
    def goals_against(self) -> int:
        """Total de gols sofridos."""
        return self.stats.get("goals_against", 0) if self.stats else 0

    @property
    def goal_difference(self) -> int:
        """Saldo de gols."""
        return self.stats.get("goal_difference", 0) if self.stats else 0

    def __repr__(self) -> str:
        return f"<CompetitionOpponentTeam {self.id} name={self.name}>"
