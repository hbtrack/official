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


class MatchTeams(Base):
    """
    Ponte jogo ↔ equipes.
    Identifica quais equipes jogaram e com qual papel (home/away, nossa/adversária).
    """
    __tablename__ = "match_teams"


# HB-AUTOGEN:BEGIN
    # AUTO-GENERATED FROM DB (SSOT). DO NOT EDIT MANUALLY.
    # Table: public.match_teams
    __table_args__ = (
        Index('ix_match_teams_match_id', 'match_id', unique=False),
        Index('ix_match_teams_team_id', 'team_id', unique=False),
    )

    # NOTE: typing helpers may require: from datetime import date, datetime; from uuid import UUID

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'))
    match_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('matches.id', name='fk_match_teams_match_id', ondelete='CASCADE'), nullable=False)
    team_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('teams.id', name='fk_match_teams_team_id', ondelete='RESTRICT'), nullable=False)
    is_home: Mapped[bool] = mapped_column(sa.Boolean(), nullable=False)
    is_our_team: Mapped[bool] = mapped_column(sa.Boolean(), nullable=False)
    # HB-AUTOGEN:END





    def __repr__(self) -> str:
        return f"<MatchTeams {self.id} match={self.match_id} team={self.team_id}>"
