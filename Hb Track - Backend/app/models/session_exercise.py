"""
Model para vínculo entre sessões de treino e exercícios.
Permite adicionar exercícios ao planejamento de uma sessão com ordem, duração e notas.
⚠️ PERMITE DUPLICATAS - Mesmo exercício pode aparecer múltiplas vezes (útil para circuitos).
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, SmallInteger, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
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
    
    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="UUID único do vínculo"
    )
    
    # Foreign Keys
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('training_sessions.id', ondelete='CASCADE'),
        nullable=False,
        comment="UUID da sessão de treino"
    )
    
    exercise_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('exercises.id', ondelete='RESTRICT'),
        nullable=False,
        comment="UUID do exercício"
    )
    
    # Ordering
    order_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Ordem do exercício na sessão (0-based, permite reordenação)"
    )
    
    # Optional metadata per exercise instance
    duration_minutes: Mapped[Optional[int]] = mapped_column(
        SmallInteger,
        nullable=True,
        comment="Duração planejada deste exercício em minutos (opcional)"
    )
    
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Notas específicas desta instância do exercício (ex: '3 séries de 10 repetições')"
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        comment="Data/hora de adição do exercício à sessão"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment="Data/hora da última atualização"
    )
    
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Soft delete timestamp"
    )
    
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
    __table_args__ = (
        CheckConstraint('order_index >= 0', name='ck_session_exercises_order_positive'),
        CheckConstraint(
            'duration_minutes IS NULL OR duration_minutes >= 0',
            name='ck_session_exercises_duration_positive'
        ),
        {'comment': 'Vínculo entre sessões de treino e exercícios. ⚠️ Permite DUPLICATAS do mesmo exercício.'}
    )
    
    def __repr__(self) -> str:
        return f"<SessionExercise(session={self.session_id}, exercise={self.exercise_id}, order={self.order_index})>"
