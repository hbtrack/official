"""
Modelo MedicalCase - Casos médicos de atletas.

Referências RAG:
- R13: Estados de atleta e flags (injured)
- RP8: Alertas de retorno de lesão
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


class MedicalCase(Base):
    """Modelo para casos médicos de atletas."""
    
    __tablename__ = "medical_cases"
    

# HB-AUTOGEN:BEGIN
    
    # AUTO-GENERATED FROM DB (SSOT). DO NOT EDIT MANUALLY.
    
    # Table: public.medical_cases
    
    __table_args__ = (
    
        CheckConstraint('deleted_at IS NULL AND deleted_reason IS NULL OR deleted_at IS NOT NULL AND deleted_reason IS NOT NULL', name='ck_medical_cases_deleted_reason'),
    
        CheckConstraint("status::text = ANY (ARRAY['ativo'::character varying, 'resolvido'::character varying, 'em_acompanhamento'::character varying]::text[])", name='medical_cases_status_check'),
    
        Index('idx_medical_cases_athlete', 'athlete_id', unique=False),
    
        Index('idx_medical_cases_organization_id', 'organization_id', unique=False),
    
        Index('ix_medical_cases_athlete_status_active', 'athlete_id', 'status', unique=False, postgresql_where=sa.text("((deleted_at IS NULL) AND ((status)::text = ANY ((ARRAY['ativo'::character varying, 'em_acompanhamento'::character varying])::text[])))")),
    
    )

    
    # NOTE: typing helpers may require: from datetime import date, datetime; from uuid import UUID

    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'))
    
    athlete_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('athletes.id', name='fk_medical_cases_athlete_id', ondelete='RESTRICT'), nullable=False)
    
    reason: Mapped[Optional[str]] = mapped_column(sa.String(length=500), nullable=True)
    
    status: Mapped[Optional[str]] = mapped_column(sa.String(length=50), nullable=True, server_default=sa.text("'ativo'::character varying"))
    
    notes: Mapped[Optional[str]] = mapped_column(sa.Text(), nullable=True)
    
    started_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    
    ended_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    
    updated_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    
    deleted_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    
    deleted_reason: Mapped[Optional[str]] = mapped_column(sa.Text(), nullable=True)
    
    organization_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('organizations.id', name='fk_medical_cases_organization', ondelete='RESTRICT'), nullable=True)
    
    created_by_user_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('users.id', name='fk_medical_cases_created_by_user', ondelete='SET NULL'), nullable=True)
    
    # HB-AUTOGEN:END
    # PK
    
    # Foreign keys
    
    # Dados do caso
    
    # Datas
    
    # Timestamps
    
    # Soft delete
    
    # Relacionamentos
    athlete = relationship("Athlete", back_populates="medical_cases", lazy="selectin")
    organization = relationship("Organization", back_populates="medical_cases", lazy="selectin")
    created_by_user = relationship("User", foreign_keys=[created_by_user_id], lazy="selectin")
