"""
Model: MatchTeams

Tabela match_teams:
- id: UUID PK
- match_id: UUID NOT NULL FK(matches)
- team_id: UUID NOT NULL FK(teams)
- is_home: boolean NOT NULL
- is_our_team: boolean NOT NULL

Ponte entre jogos e equipes - identifica quais equipes jogaram e com qual papel.
"""
from uuid import uuid4

from sqlalchemy import ForeignKey, Boolean, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class MatchTeams(Base):
    """
    Ponte jogo ↔ equipes.
    Identifica quais equipes jogaram e com qual papel (home/away, nossa/adversária).
    """
    __tablename__ = "match_teams"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()")
    )

    match_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("matches.id"),
        nullable=False,
        index=True
    )

    team_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teams.id"),
        nullable=False,
        index=True
    )

    is_home: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False
    )

    is_our_team: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False
    )

    def __repr__(self) -> str:
        return f"<MatchTeams {self.id} match={self.match_id} team={self.team_id}>"
