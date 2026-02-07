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

    # Primary key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
        server_default=text("gen_random_uuid()"),
    )

    # Competition FK
    competition_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("competitions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Core fields
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Nome da equipe adversária",
    )

    short_name: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Nome curto/sigla",
    )

    category: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Categoria (ex: Sub-17)",
    )

    city: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Cidade da equipe",
    )

    logo_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="URL do logo da equipe",
    )

    # Vínculo com equipe do sistema (fuzzy match)
    linked_team_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("teams.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Vínculo com equipe cadastrada no sistema",
    )

    # Grupo na competição
    group_name: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        index=True,
        comment="Grupo na competição (ex: A, B)",
    )

    # Estatísticas calculadas
    stats: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        default=lambda: DEFAULT_STATS.copy(),
        server_default=text(
            "'{\"wins\": 0, \"draws\": 0, \"losses\": 0, \"played\": 0, "
            "\"points\": 0, \"goals_for\": 0, \"goals_against\": 0, \"goal_difference\": 0}'::jsonb"
        ),
        comment="Estatísticas calculadas automaticamente",
    )

    # Status
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=True,
        default="active",
        server_default=text("'active'"),
        comment="Status: active, eliminated, qualified, withdrawn",
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        server_default=text("now()"),
        nullable=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        server_default=text("now()"),
        nullable=True,
    )

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
