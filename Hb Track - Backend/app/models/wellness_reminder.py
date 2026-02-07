"""
Auto-generated model skeleton for table wellness_reminders.
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


class WellnessReminder(Base):
    __tablename__ = "wellness_reminders"


# HB-AUTOGEN:BEGIN
    # AUTO-GENERATED FROM DB (SSOT). DO NOT EDIT MANUALLY.
    # Table: public.wellness_reminders
    __table_args__ = (
        UniqueConstraint('training_session_id', 'athlete_id', name='uq_wellness_reminders_session_athlete'),
        Index('idx_wellness_reminders_pending', 'training_session_id', 'athlete_id', unique=False, postgresql_where=sa.text('(responded_at IS NULL)')),
    )

    # NOTE: typing helpers may require: from datetime import date, datetime; from uuid import UUID

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'))
    training_session_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('training_sessions.id', name='wellness_reminders_training_session_id_fkey', ondelete='CASCADE'), nullable=False)
    athlete_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('athletes.id', name='wellness_reminders_athlete_id_fkey', ondelete='CASCADE'), nullable=False)
    sent_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False)
    responded_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    reminder_count: Mapped[int] = mapped_column(sa.Integer(), nullable=False, server_default=sa.text('0'))
    locked_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    # HB-AUTOGEN:END
    # Manual customizations below (preserved across regen)
