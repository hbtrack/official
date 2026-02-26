# HB-AUTOGEN-IMPORTS:BEGIN
from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
# HB-AUTOGEN-IMPORTS:END

from app.models.base import Base


class ExerciseAcl(Base):
    """
    ACL de exercícios — controle de acesso granular.
    
    Invariantes:
    - INV-EXB-ACL-002: Só aplicável a exercises com visibility_mode='restricted'
    - INV-EXB-ACL-003: user_id deve pertencer à mesma org do exercise
    - INV-EXB-ACL-006: UNIQUE (exercise_id, user_id)
    
    Constraints (definidos na migração 0065):
    - PK: id
    - FK: exercise_id → exercises (CASCADE)
    - FK: user_id → users (CASCADE)
    - FK: granted_by_user_id → users (RESTRICT)
    - UNIQUE: (exercise_id, user_id)
    """
    __tablename__ = 'exercise_acl'

    __table_args__ = (
        UniqueConstraint('exercise_id', 'user_id', name='uq_exercise_acl_exercise_user'),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'))
    exercise_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('exercises.id', name='exercise_acl_exercise_id_fkey', ondelete='CASCADE'), nullable=False)
    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('users.id', name='exercise_acl_user_id_fkey', ondelete='CASCADE'), nullable=False)
    granted_by_user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('users.id', name='exercise_acl_granted_by_user_id_fkey', ondelete='RESTRICT'), nullable=False)
    granted_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))

    # Relationships
    # exercise = relationship('Exercise', back_populates='acl_entries')
    # user = relationship('User', foreign_keys=[user_id])
    # granted_by = relationship('User', foreign_keys=[granted_by_user_id])
