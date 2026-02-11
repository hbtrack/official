"""
Model para vínculo entre sessões de treino e exercícios.
Permite adicionar exercícios ao planejamento de uma sessão com ordem, duração e notas.
⚠️ PERMITE DUPLICATAS - Mesmo exercício pode aparecer múltiplas vezes (útil para circuitos).
"""

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

from app.models.base import Base
import uuid


class SessionExercise(Base):
    """
    Vínculo entre training_sessions e exercises.
    
    Regras:
    - Permite DUPLICATAS (mesmo exercise_id múltiplas vezes)
    - Ordenação via order_index (>=0)
    - Soft delete (deleted_at)
    - Cascade delete quando session deletada
    - Restrict delete quando exercise deletado (preservar histórico)
    """
    __tablename__ = 'training_session_exercises'
    

# HB-AUTOGEN:BEGIN
    # AUTO-GENERATED FROM DB (SSOT). DO NOT EDIT MANUALLY.
    # Table: public.training_session_exercises
    __table_args__ = (
        CheckConstraint('duration_minutes IS NULL OR duration_minutes >= 0', name='ck_session_exercises_duration_positive'),
        CheckConstraint('order_index >= 0', name='ck_session_exercises_order_positive'),
        Index('idx_session_exercises_exercise', 'exercise_id', unique=False, postgresql_where=sa.text('(deleted_at IS NULL)')),
        Index('idx_session_exercises_session_order', 'session_id', 'order_index', 'deleted_at', unique=False, postgresql_where=sa.text('(deleted_at IS NULL)')),
        Index('idx_session_exercises_session_order_unique', 'session_id', 'order_index', unique=True, postgresql_where=sa.text('(deleted_at IS NULL)')),
    )

    # NOTE: typing helpers may require: from datetime import date, datetime; from uuid import UUID

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'))
    session_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('training_sessions.id', name='training_session_exercises_session_id_fkey', ondelete='CASCADE'), nullable=False)
    exercise_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('exercises.id', name='training_session_exercises_exercise_id_fkey', ondelete='RESTRICT'), nullable=False)
    order_index: Mapped[int] = mapped_column(sa.Integer(), nullable=False, server_default=sa.text('0'))
    duration_minutes: Mapped[Optional[int]] = mapped_column(sa.SmallInteger(), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(sa.Text(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    updated_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    deleted_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    # HB-AUTOGEN:END
    # Primary Key
    
    # Foreign Keys
    
    
    # Ordering
    
    # Optional metadata per exercise instance
    
    
    # Timestamps
    
    
    
    # Relationships
    session: Mapped["TrainingSession"] = relationship(
        "TrainingSession",
        back_populates="session_exercises",
        lazy="selectin"
    )
    
    exercise: Mapped["Exercise"] = relationship(
        "Exercise",
        back_populates="session_usages",
        lazy="selectin"
    )
    
    # Table arguments (constraints)
    
    def __repr__(self) -> str:
        return f"<SessionExercise(session={self.session_id}, exercise={self.exercise_id}, order={self.order_index})>"
