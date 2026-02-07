"""
Modelo WellnessPost - Bem-estar pós-treino.

Referências RAG:
- R21: Métricas de treino (session_rpe para cálculo de carga)
- RP8: Alertas de sobrecarga e fadiga
"""
from datetime import datetime
from typing import Optional
from uuid import uuid4, UUID
from decimal import Decimal

from sqlalchemy import Column, String, Boolean, Integer, SmallInteger, Text, ForeignKey, text, Numeric
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime

from app.models.base import Base


class WellnessPost(Base):
    """Modelo para wellness pós-treino."""
    
    __tablename__ = "wellness_post"
    
    # PK
    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()")
    )
    
    # Foreign keys
    organization_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="RESTRICT"),
        nullable=False,
    )
    training_session_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("training_sessions.id", ondelete="RESTRICT"),
        nullable=False,
    )
    athlete_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("athletes.id", ondelete="RESTRICT"),
        nullable=False,
    )
    created_by_user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    
    # Métricas de bem-estar
    session_rpe: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # 0-10: Rating of Perceived Exertion
    fatigue_after: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # 0-10
    mood_after: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # 0-10
    muscle_soreness_after: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)  # 0-10
    perceived_intensity: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)  # 1-5
    
    # Métricas calculadas por trigger (adicionadas em migration 0035)
    minutes_effective: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)  # 0-300: duração efetiva
    internal_load: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)  # Calculado: minutes_effective × session_rpe
    
    # Metadados
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    flag_medical_followup: Mapped[Optional[bool]] = mapped_column(Boolean, default=False, nullable=True)
    filled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()")
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()")
    )
    
    # Soft delete
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Campo de controle de edição temporal
    locked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relacionamentos
    organization = relationship("Organization", back_populates="wellness_posts", lazy="selectin")
    training_session = relationship("TrainingSession", back_populates="wellness_posts", lazy="selectin")
    athlete = relationship("Athlete", back_populates="wellness_posts", lazy="selectin")
    created_by_user = relationship("User", foreign_keys=[created_by_user_id], lazy="selectin")

    @property
    def session_id(self) -> UUID:
        """Alias para compatibilidade com schemas/response."""
        return self.training_session_id
