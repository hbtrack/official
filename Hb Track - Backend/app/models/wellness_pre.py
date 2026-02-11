"""
Modelo WellnessPre - Bem-estar pré-treino.

Referências RAG:
- R22: Wellness pré-treino são métricas operacionais
- R40: Janelas temporais de edição
- R25/R26: Permissões por papel e escopo
"""

# HB-AUTOGEN-IMPORTS:BEGIN
from __future__ import annotations

from datetime import date, datetime
from typing import Optional
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import ForeignKey, CheckConstraint, Index, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB as PG_JSONB, INET as PG_INET, ENUM as PG_ENUM
# HB-AUTOGEN-IMPORTS:END

from decimal import Decimal


from app.models.base import Base


class WellnessPre(Base):
    """Modelo para wellness pré-treino."""
    
    __tablename__ = "wellness_pre"
    

# HB-AUTOGEN:BEGIN
    
    # AUTO-GENERATED FROM DB (SSOT). DO NOT EDIT MANUALLY.
    
    # Table: public.wellness_pre
    
    __table_args__ = (
    
        CheckConstraint('deleted_at IS NULL AND deleted_reason IS NULL OR deleted_at IS NOT NULL AND deleted_reason IS NOT NULL', name='ck_wellness_pre_deleted_reason'),
    
        CheckConstraint('fatigue_pre >= 0 AND fatigue_pre <= 10', name='ck_wellness_pre_fatigue'),
    
        CheckConstraint("menstrual_cycle_phase IS NULL OR (menstrual_cycle_phase::text = ANY (ARRAY['folicular'::character varying, 'lutea'::character varying, 'menstruacao'::character varying, 'nao_informa'::character varying]::text[]))", name='ck_wellness_pre_menstrual'),
    
        CheckConstraint('readiness_score IS NULL OR readiness_score >= 0 AND readiness_score <= 10', name='ck_wellness_pre_readiness'),
    
        CheckConstraint('sleep_hours >= 0::numeric AND sleep_hours <= 24::numeric', name='ck_wellness_pre_sleep_hours'),
    
        CheckConstraint('sleep_quality >= 1 AND sleep_quality <= 5', name='ck_wellness_pre_sleep_quality'),
    
        CheckConstraint('muscle_soreness >= 0 AND muscle_soreness <= 10', name='ck_wellness_pre_soreness'),
    
        CheckConstraint('stress_level >= 0 AND stress_level <= 10', name='ck_wellness_pre_stress'),
    
        Index('idx_wellness_session_athlete', 'training_session_id', 'athlete_id', unique=False),
    
        Index('ix_wellness_pre_athlete_id', 'athlete_id', unique=False),
    
        Index('ix_wellness_pre_training_session_id', 'training_session_id', unique=False),
    
        Index('ux_wellness_pre_session_athlete', 'training_session_id', 'athlete_id', unique=True, postgresql_where=sa.text('(deleted_at IS NULL)')),
    
    )

    
    # NOTE: typing helpers may require: from datetime import date, datetime; from uuid import UUID

    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'))
    
    organization_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('organizations.id', name='fk_wellness_pre_organization_id', ondelete='RESTRICT'), nullable=False)
    
    training_session_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('training_sessions.id', name='fk_wellness_pre_training_session_id', ondelete='RESTRICT'), nullable=False)
    
    athlete_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('athletes.id', name='fk_wellness_pre_athlete_id', ondelete='RESTRICT'), nullable=False)
    
    sleep_hours: Mapped[object] = mapped_column(sa.Numeric(4, 1), nullable=False)
    
    sleep_quality: Mapped[int] = mapped_column(sa.SmallInteger(), nullable=False)
    
    fatigue_pre: Mapped[int] = mapped_column(sa.SmallInteger(), nullable=False)
    
    stress_level: Mapped[int] = mapped_column(sa.SmallInteger(), nullable=False)
    
    muscle_soreness: Mapped[int] = mapped_column(sa.SmallInteger(), nullable=False)
    
    notes: Mapped[Optional[str]] = mapped_column(sa.Text(), nullable=True)
    
    menstrual_cycle_phase: Mapped[Optional[str]] = mapped_column(sa.String(length=32), nullable=True)
    
    readiness_score: Mapped[Optional[int]] = mapped_column(sa.SmallInteger(), nullable=True)
    
    filled_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    
    created_by_user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('users.id', name='fk_wellness_pre_created_by_user_id', ondelete='RESTRICT'), nullable=False)
    
    updated_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    
    deleted_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    
    deleted_reason: Mapped[Optional[str]] = mapped_column(sa.Text(), nullable=True)
    
    locked_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    
    # HB-AUTOGEN:END
    # PK
    
    # Foreign keys
    
    # Métricas de bem-estar pré-treino
    
    # Campos opcionais
    
    # Metadados
    
    # Timestamps
    
    # Soft delete
    
    # Campo de controle de edição temporal
    
    # Relacionamentos
    organization = relationship("Organization", lazy="selectin")
    training_session = relationship("TrainingSession", lazy="selectin")
    athlete = relationship("Athlete", lazy="selectin")
    created_by_user = relationship("User", foreign_keys=[created_by_user_id], lazy="selectin")

    @property
    def session_id(self) -> UUID:
        """Alias para compatibilidade com schemas/response."""
        return self.training_session_id
