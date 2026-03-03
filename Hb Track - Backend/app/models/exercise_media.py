from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.models.base import Base


class ExerciseMedia(Base):
    """
    Mídia associada a exercícios (imagens, vídeos, documentos).

    Constraints (definidos na migração 0065):
    - PK: id
    - FK: exercise_id → exercises (CASCADE)
    - FK: created_by_user_id → users (CASCADE)
    - UNIQUE: (exercise_id, order_index) — uq_exercise_media_exercise_order
    - CHECK: media_type IN ('image', 'video', 'document') — ck_exercise_media_type
    """
    __tablename__ = 'exercise_media'

    __table_args__ = (
        UniqueConstraint('exercise_id', 'order_index', name='uq_exercise_media_exercise_order'),
    )

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')
    )
    exercise_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey('exercises.id', name='exercise_media_exercise_id_fkey', ondelete='CASCADE'),
        nullable=False
    )
    media_type: Mapped[str] = mapped_column(sa.String(length=50), nullable=False)
    url: Mapped[str] = mapped_column(sa.String(length=500), nullable=False)
    title: Mapped[Optional[str]] = mapped_column(sa.String(length=200), nullable=True)
    order_index: Mapped[int] = mapped_column(sa.SmallInteger(), nullable=False, server_default=sa.text('1'))
    created_by_user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey('users.id', name='exercise_media_created_by_user_id_fkey', ondelete='CASCADE'),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')
    )

    # Relationships
    exercise = relationship('Exercise', backref='media_items', foreign_keys=[exercise_id])
    created_by = relationship('User', foreign_keys=[created_by_user_id])
