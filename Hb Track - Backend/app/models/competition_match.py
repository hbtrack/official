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

    # Phase FK
    phase_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("competition_phases.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # External reference (para upsert - evita duplicação ao reimportar PDF)
    external_reference_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="ID externo para upsert (evita duplicação ao reimportar)",
    )

    # Teams
    home_team_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("competition_opponent_teams.id", ondelete="SET NULL"),
        nullable=True,
    )

    away_team_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("competition_opponent_teams.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Flags para identificar nossos jogos
    is_our_match: Mapped[bool] = mapped_column(
        Boolean,
        nullable=True,
        default=False,
        server_default=text("false"),
        index=True,
        comment="Se é jogo da nossa equipe",
    )

    our_team_is_home: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True,
        comment="Se nossa equipe é mandante",
    )

    # Vínculo com tabela matches (para detalhes do jogo)
    linked_match_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("matches.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Vínculo com tabela matches para detalhes",
    )

    # Data e local
    match_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        index=True,
    )

    match_time: Mapped[Optional[time]] = mapped_column(
        Time,
        nullable=True,
    )

    match_datetime: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    location: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    # Rodada
    round_number: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    round_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    # Resultado
    home_score: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    away_score: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    # Prorrogação
    home_score_extra: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    away_score_extra: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    # Pênaltis
    home_score_penalties: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    away_score_penalties: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    # Status
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=True,
        default="scheduled",
        server_default=text("'scheduled'"),
        index=True,
        comment="Status: scheduled, in_progress, finished, postponed, cancelled",
    )

    # Observações
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
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
