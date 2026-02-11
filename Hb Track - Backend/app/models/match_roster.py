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


from app.models.base import Base


class MatchRoster(Base):
    """
    Súmula/convocação oficial de um jogo.
    Define quais atletas estão elegíveis para jogar.
    """
    __tablename__ = "match_roster"


# HB-AUTOGEN:BEGIN
    # AUTO-GENERATED FROM DB (SSOT). DO NOT EDIT MANUALLY.
    # Table: public.match_roster
    __table_args__ = (
        CheckConstraint('jersey_number > 0', name='ck_match_roster_jersey'),
        Index('ix_match_roster_athlete_id', 'athlete_id', unique=False),
        Index('ix_match_roster_athlete_match', 'athlete_id', 'match_id', unique=False),
        Index('ix_match_roster_match_id', 'match_id', unique=False),
    )

    # NOTE: typing helpers may require: from datetime import date, datetime; from uuid import UUID

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'))
    match_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('matches.id', name='fk_match_roster_match_id', ondelete='CASCADE'), nullable=False)
    team_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('teams.id', name='fk_match_roster_team_id', ondelete='RESTRICT'), nullable=False)
    athlete_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('athletes.id', name='fk_match_roster_athlete_id', ondelete='RESTRICT'), nullable=False)
    jersey_number: Mapped[int] = mapped_column(sa.SmallInteger(), nullable=False)
    is_starting: Mapped[Optional[bool]] = mapped_column(sa.Boolean(), nullable=True)
    is_goalkeeper: Mapped[bool] = mapped_column(sa.Boolean(), nullable=False)
    is_available: Mapped[bool] = mapped_column(sa.Boolean(), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(sa.Text(), nullable=True)
    # HB-AUTOGEN:END









    def __repr__(self) -> str:
        return f"<MatchRoster {self.id} match={self.match_id} athlete={self.athlete_id}>"
