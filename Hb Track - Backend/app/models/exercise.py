# HB-AUTOGEN-IMPORTS:BEGIN
from __future__ import annotations

from datetime import date, datetime
from typing import Optional
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import ForeignKey, CheckConstraint, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB as PG_JSONB, INET as PG_INET, ENUM as PG_ENUM
# HB-AUTOGEN-IMPORTS:END

import uuid
from app.models.base import Base


class Exercise(Base):
    """
    Banco de exercícios com tags hierárquicas.

    Constraints (definidos na migração 0036):
    - PK: id
    - FK: organization_id → organizations (CASCADE)
    - FK: created_by_user_id → users (CASCADE)
    - GIN INDEX: idx_exercises_tags em tag_ids
    """
    __tablename__ = 'exercises'


# HB-AUTOGEN:BEGIN
    # AUTO-GENERATED FROM DB (SSOT). DO NOT EDIT MANUALLY.
    # Table: public.exercises
    __table_args__ = (
        Index('idx_exercises_tags', 'tag_ids', unique=False),
    )

    # NOTE: typing helpers may require: from datetime import date, datetime; from uuid import UUID

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'))
    organization_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('organizations.id', name='exercises_organization_id_fkey', ondelete='CASCADE'), nullable=True)
    name: Mapped[str] = mapped_column(sa.String(length=200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(sa.Text(), nullable=True)
    tag_ids: Mapped[object] = mapped_column(sa.ARRAY(PG_UUID(as_uuid=True)), nullable=False, server_default=sa.text("'{}'::uuid[]"))
    category: Mapped[Optional[str]] = mapped_column(sa.String(length=100), nullable=True)
    media_url: Mapped[Optional[str]] = mapped_column(sa.String(length=500), nullable=True)
    created_by_user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('users.id', name='exercises_created_by_user_id_fkey', ondelete='CASCADE'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    updated_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    # HB-AUTOGEN:END

    # Fields added by migration 0065 (AR_181 — scope/visibility/soft-delete)
    scope: Mapped[str] = mapped_column(sa.String(length=20), nullable=False, server_default='ORG')
    visibility_mode: Mapped[str] = mapped_column(sa.String(length=20), nullable=False, server_default='restricted')
    deleted_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    deleted_reason: Mapped[Optional[str]] = mapped_column(sa.Text(), nullable=True)

    # Relationships
    creator = relationship('User', backref='created_exercises', foreign_keys=[created_by_user_id])
    organization = relationship('Organization', backref='exercises')
    session_usages = relationship(
        'SessionExercise',
        back_populates='exercise',
        lazy='selectin'
    )
