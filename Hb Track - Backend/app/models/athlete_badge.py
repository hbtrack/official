"""
Auto-generated model skeleton for table athlete_badges.
Do not edit HB-AUTOGEN blocks manually.
"""

# HB-AUTOGEN-IMPORTS:BEGIN
from __future__ import annotations

from datetime import date, datetime
from typing import Optional
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import ForeignKey, CheckConstraint, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB as PG_JSONB
# HB-AUTOGEN-IMPORTS:END
from app.models.base import Base


class AthleteBadge(Base):
    __tablename__ = "athlete_badges"


# HB-AUTOGEN:BEGIN
    # AUTO-GENERATED FROM DB (SSOT). DO NOT EDIT MANUALLY.
    # Table: public.athlete_badges
    __table_args__ = (
        CheckConstraint("badge_type::text = ANY (ARRAY['wellness_champion_monthly'::character varying, 'wellness_streak_3months'::character varying]::text[])", name='ck_athlete_badges_type'),
        Index('idx_badges_athlete_month', 'athlete_id', 'month_reference', unique=False),
    )

    # NOTE: typing helpers may require: from datetime import date, datetime; from uuid import UUID

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'))
    athlete_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('athletes.id', name='athlete_badges_athlete_id_fkey', ondelete='CASCADE'), nullable=False)
    badge_type: Mapped[str] = mapped_column(sa.String(50), nullable=False)
    month_reference: Mapped[Optional[date]] = mapped_column(sa.Date(), nullable=True)
    earned_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    # HB-AUTOGEN:END
    # Manual customizations below (preserved across regen)
