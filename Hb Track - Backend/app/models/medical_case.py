"""
Modelo MedicalCase - Casos médicos de atletas.

Referências RAG:
- R13: Estados de atleta e flags (injured)
- RP8: Alertas de retorno de lesão
"""
from datetime import datetime
from typing import Optional
from uuid import uuid4, UUID

from sqlalchemy import String, Text, ForeignKey, DateTime, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class MedicalCase(Base):
    """Modelo para casos médicos de atletas."""
    
    __tablename__ = "medical_cases"
    
    # PK
    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()")
    )
    
    # Foreign keys
    athlete_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("athletes.id", ondelete="CASCADE"),
        nullable=False,
    )
    organization_id: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=True,
    )
    created_by_user_id: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )
    
    # Dados do caso
    reason: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    status: Mapped[Optional[str]] = mapped_column(String(50), default="ativo", nullable=True)  # ativo, resolvido, em_acompanhamento
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Datas
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()")
    )
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
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
    
    # Relacionamentos
    athlete = relationship("Athlete", back_populates="medical_cases", lazy="selectin")
    organization = relationship("Organization", back_populates="medical_cases", lazy="selectin")
    created_by_user = relationship("User", foreign_keys=[created_by_user_id], lazy="selectin")
