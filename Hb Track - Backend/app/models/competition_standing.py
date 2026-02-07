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

    # Unique constraint
    __table_args__ = (
        UniqueConstraint(
            "competition_id", "phase_id", "opponent_team_id",
            name="competition_standings_competition_id_phase_id_opponent_team_key"
        ),
    )

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

    # Phase FK (opcional - pode ser classificação geral)
    phase_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("competition_phases.id", ondelete="CASCADE"),
        nullable=True,
    )

    # Team FK
    opponent_team_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("competition_opponent_teams.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Position
    position: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Posição na classificação",
    )

    # Group (se houver)
    group_name: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )

    # Statistics
    points: Mapped[int] = mapped_column(
        Integer,
        nullable=True,
        default=0,
        server_default=text("0"),
    )

    played: Mapped[int] = mapped_column(
        Integer,
        nullable=True,
        default=0,
        server_default=text("0"),
    )

    wins: Mapped[int] = mapped_column(
        Integer,
        nullable=True,
        default=0,
        server_default=text("0"),
    )

    draws: Mapped[int] = mapped_column(
        Integer,
        nullable=True,
        default=0,
        server_default=text("0"),
    )

    losses: Mapped[int] = mapped_column(
        Integer,
        nullable=True,
        default=0,
        server_default=text("0"),
    )

    goals_for: Mapped[int] = mapped_column(
        Integer,
        nullable=True,
        default=0,
        server_default=text("0"),
    )

    goals_against: Mapped[int] = mapped_column(
        Integer,
        nullable=True,
        default=0,
        server_default=text("0"),
    )

    goal_difference: Mapped[int] = mapped_column(
        Integer,
        nullable=True,
        default=0,
        server_default=text("0"),
    )

    # Recent form (últimos 5 jogos: W, D, L)
    recent_form: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True,
        comment="Últimos 5 jogos (ex: WWDLL)",
    )

    # Qualification status
    qualification_status: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Status: qualified, playoffs, relegation, eliminated",
    )

    # Timestamp
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
