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

from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.models.base import Base

class ExerciseTag(Base):
    __tablename__ = 'exercise_tags'

# HB-AUTOGEN:BEGIN
    # AUTO-GENERATED FROM DB (SSOT). DO NOT EDIT MANUALLY.
    # Table: public.exercise_tags
    __table_args__ = (
        UniqueConstraint('name', name='exercise_tags_name_key'),
        Index('idx_tags_parent', 'parent_tag_id', unique=False, postgresql_where=sa.text('(parent_tag_id IS NOT NULL)')),
    )

    # NOTE: typing helpers may require: from datetime import date, datetime; from uuid import UUID

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'))
    name: Mapped[str] = mapped_column(sa.String(length=50), nullable=False)
    parent_tag_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('exercise_tags.id', name='exercise_tags_parent_tag_id_fkey', ondelete='CASCADE'), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(sa.Text(), nullable=True)
    display_order: Mapped[Optional[int]] = mapped_column(sa.Integer(), nullable=True)
    is_active: Mapped[bool] = mapped_column(sa.Boolean(), nullable=False, server_default=sa.text('false'))
    suggested_by_user_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('users.id', name='exercise_tags_suggested_by_user_id_fkey', ondelete='SET NULL'), nullable=True)
    approved_by_admin_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('users.id', name='exercise_tags_approved_by_admin_id_fkey', ondelete='SET NULL'), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    # HB-AUTOGEN:END
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), nullable=False, unique=True)
    parent_tag_id = Column(UUID(as_uuid=True), ForeignKey('exercise_tags.id'), nullable=True)
    description = Column(String(255))
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, nullable=False, default=False)
    suggested_by_user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    approved_by_admin_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)

    parent = relationship('ExerciseTag', remote_side=[id], backref='children')
    # Optionally, add relationships to User if needed
