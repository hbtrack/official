"""
Model: MatchRoster

Tabela match_roster:
- id: UUID PK
- match_id: UUID NOT NULL FK(matches)
- team_id: UUID NOT NULL FK(teams)
- athlete_id: UUID NOT NULL FK(athletes)
- jersey_number: smallint NOT NULL CHECK > 0
- is_starting: boolean
- is_goalkeeper: boolean NOT NULL
- is_available: boolean NOT NULL
- notes: text

Regras:
- RD4/RD7: Participação oficial exige convocação
- RD18: Limite máximo de 16 atletas por jogo
"""
from typing import Optional
from uuid import uuid4

from sqlalchemy import ForeignKey, Integer, Boolean, Text, text, SmallInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class MatchRoster(Base):
    """
    Súmula/convocação oficial de um jogo.
    Define quais atletas estão elegíveis para jogar.
    """
    __tablename__ = "match_roster"

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

    athlete_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("athletes.id"),
        nullable=False,
        index=True
    )

    jersey_number: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False
    )

    is_starting: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True,
        default=None
    )

    is_goalkeeper: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    is_available: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )

    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    def __repr__(self) -> str:
        return f"<MatchRoster {self.id} match={self.match_id} athlete={self.athlete_id}>"
