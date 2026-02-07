"""
Auto-generated model skeleton for table match_periods.
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


class MatchPeriod(Base):
    __tablename__ = "match_periods"


# HB-AUTOGEN:BEGIN
    # AUTO-GENERATED FROM DB (SSOT). DO NOT EDIT MANUALLY.
    # Table: public.match_periods
    __table_args__ = (
        CheckConstraint('duration_seconds > 0', name='ck_match_periods_duration'),
        CheckConstraint('number >= 1', name='ck_match_periods_number'),
        CheckConstraint("period_type::text = ANY (ARRAY['regular'::character varying, 'extra_time'::character varying, 'shootout_7m'::character varying]::text[])", name='ck_match_periods_type'),
        Index('ix_match_periods_match_id', 'match_id', unique=False),
    )

    # NOTE: typing helpers may require: from datetime import date, datetime; from uuid import UUID

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'))
    match_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('matches.id', name='fk_match_periods_match_id', ondelete='CASCADE'), nullable=False)
    number: Mapped[int] = mapped_column(sa.SmallInteger(), nullable=False)
    duration_seconds: Mapped[int] = mapped_column(sa.Integer(), nullable=False)
    period_type: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    # HB-AUTOGEN:END
    # Manual customizations below (preserved across regen)
