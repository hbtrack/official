"""
Modelo WellnessPre - Bem-estar pré-treino.

Referências RAG:
- R22: Wellness pré-treino são métricas operacionais
- R40: Janelas temporais de edição
- R25/R26: Permissões por papel e escopo
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


class WellnessPre(Base):
    """Modelo para wellness pré-treino."""
    
    __tablename__ = "wellness_pre"
    
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
    
    # Métricas de bem-estar pré-treino
    sleep_hours: Mapped[Decimal] = mapped_column(Numeric(4, 1), nullable=False)  # 0-24 horas
    sleep_quality: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # 1-5: qualidade sono
    fatigue_pre: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # 0-10: fadiga antes
    stress_level: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # 0-10: nível de stress
    muscle_soreness: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # 0-10: dor muscular
    
    # Campos opcionais
    menstrual_cycle_phase: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)  # folicular, lutea, menstruacao, nao_informa
    readiness_score: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)  # 0-10: prontidão
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Metadados
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
    organization = relationship("Organization", lazy="selectin")
    training_session = relationship("TrainingSession", lazy="selectin")
    athlete = relationship("Athlete", lazy="selectin")
    created_by_user = relationship("User", foreign_keys=[created_by_user_id], lazy="selectin")

    @property
    def session_id(self) -> UUID:
        """Alias para compatibilidade com schemas/response."""
        return self.training_session_id
