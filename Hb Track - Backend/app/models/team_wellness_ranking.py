"""
Auto-generated model skeleton for table team_wellness_rankings.
Do not edit HB-AUTOGEN blocks manually.
"""

# HB-AUTOGEN-IMPORTS:BEGIN
from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import ForeignKey, CheckConstraint, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB as PG_JSONB
# HB-AUTOGEN-IMPORTS:END
from app.models.base import Base


class TeamWellnessRanking(Base):
    __tablename__ = "team_wellness_rankings"


# HB-AUTOGEN:BEGIN
    # AUTO-GENERATED FROM DB (SSOT). DO NOT EDIT MANUALLY.
    # Table: public.team_wellness_rankings
    __table_args__ = (
        UniqueConstraint('team_id', 'month_reference', name='uq_team_wellness_rankings_team_month'),
        Index('idx_rankings_month_rank', 'month_reference', 'rank', unique=False),
        Index('idx_rankings_team_month', 'team_id', 'month_reference', unique=False),
        Index('uq_team_wellness_rankings_team_month', 'team_id', 'month_reference', unique=True),
    )

    # NOTE: typing helpers may require: from datetime import date, datetime; from uuid import UUID

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'))
    team_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('teams.id', name='team_wellness_rankings_team_id_fkey', ondelete='CASCADE'), nullable=False)
    month_reference: Mapped[date] = mapped_column(sa.Date(), nullable=False)
    response_rate_pre: Mapped[object] = mapped_column(sa.Numeric(5, 2))
    response_rate_post: Mapped[object] = mapped_column(sa.Numeric(5, 2))
    avg_rate: Mapped[object] = mapped_column(sa.Numeric(5, 2))
    rank: Mapped[int] = mapped_column(sa.Integer())
    athletes_90plus: Mapped[int] = mapped_column(sa.Integer(), nullable=False, server_default=sa.text('0'))
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    # HB-AUTOGEN:END
    # Manual customizations below (preserved across regen)
