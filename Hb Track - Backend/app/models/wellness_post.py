"""
Modelo WellnessPost - Bem-estar pós-treino.

Referências RAG:
- R21: Métricas de treino (session_rpe para cálculo de carga)
- RP8: Alertas de sobrecarga e fadiga
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


class WellnessPost(Base):
    """Modelo para wellness pós-treino."""
    
    __tablename__ = "wellness_post"
    

# HB-AUTOGEN:BEGIN
    
    # AUTO-GENERATED FROM DB (SSOT). DO NOT EDIT MANUALLY.
    
    # Table: public.wellness_post
    
    __table_args__ = (
    
        CheckConstraint('deleted_at IS NULL AND deleted_reason IS NULL OR deleted_at IS NOT NULL AND deleted_reason IS NOT NULL', name='ck_wellness_post_deleted_reason'),
    
        CheckConstraint('fatigue_after >= 0 AND fatigue_after <= 10', name='ck_wellness_post_fatigue'),
    
        CheckConstraint('perceived_intensity IS NULL OR perceived_intensity >= 1 AND perceived_intensity <= 5', name='ck_wellness_post_intensity'),
    
        CheckConstraint('mood_after >= 0 AND mood_after <= 10', name='ck_wellness_post_mood'),
    
        CheckConstraint('session_rpe >= 0 AND session_rpe <= 10', name='ck_wellness_post_rpe'),
    
        CheckConstraint('muscle_soreness_after IS NULL OR muscle_soreness_after >= 0 AND muscle_soreness_after <= 10', name='ck_wellness_post_soreness'),
    
        Index('idx_wellness_athlete_date', 'athlete_id', 'filled_at', unique=False, postgresql_where=sa.text('(athlete_id IS NOT NULL)')),
    
        Index('ix_wellness_post_athlete_id', 'athlete_id', unique=False),
    
        Index('ix_wellness_post_athlete_session_active', 'athlete_id', 'training_session_id', 'created_at', unique=False, postgresql_where=sa.text('(deleted_at IS NULL)')),
    
        Index('ix_wellness_post_training_session_id', 'training_session_id', unique=False),
    
        Index('ux_wellness_post_session_athlete', 'training_session_id', 'athlete_id', unique=True, postgresql_where=sa.text('(deleted_at IS NULL)')),
    
    )

    
    # NOTE: typing helpers may require: from datetime import date, datetime; from uuid import UUID

    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'))
    
    organization_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('organizations.id', name='fk_wellness_post_organization_id', ondelete='RESTRICT'), nullable=False)
    
    training_session_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('training_sessions.id', name='fk_wellness_post_training_session_id', ondelete='RESTRICT'), nullable=False)
    
    athlete_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('athletes.id', name='fk_wellness_post_athlete_id', ondelete='RESTRICT'), nullable=False)
    
    session_rpe: Mapped[int] = mapped_column(sa.SmallInteger(), nullable=False)
    
    fatigue_after: Mapped[int] = mapped_column(sa.SmallInteger(), nullable=False)
    
    mood_after: Mapped[int] = mapped_column(sa.SmallInteger(), nullable=False)
    
    muscle_soreness_after: Mapped[Optional[int]] = mapped_column(sa.SmallInteger(), nullable=True)
    
    notes: Mapped[Optional[str]] = mapped_column(sa.Text(), nullable=True)
    
    perceived_intensity: Mapped[Optional[int]] = mapped_column(sa.SmallInteger(), nullable=True)
    
    flag_medical_followup: Mapped[Optional[bool]] = mapped_column(sa.Boolean(), nullable=True, server_default=sa.text('false'))
    
    filled_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    
    created_by_user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('users.id', name='fk_wellness_post_created_by_user_id', ondelete='RESTRICT'), nullable=False)
    
    updated_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    
    deleted_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    
    deleted_reason: Mapped[Optional[str]] = mapped_column(sa.Text(), nullable=True)
    
    internal_load: Mapped[Optional[object]] = mapped_column(sa.Numeric(10, 2), nullable=True, server_default=sa.text('0'))
    
    minutes_effective: Mapped[Optional[int]] = mapped_column(sa.SmallInteger(), nullable=True)
    
    locked_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    
    # HB-AUTOGEN:END
    # PK
    
    # Foreign keys
    
    # Métricas de bem-estar
    
    # Métricas calculadas por trigger (adicionadas em migration 0035)
    
    # Metadados
    
    # Timestamps
    
    # Soft delete
    
    # Campo de controle de edição temporal
    
    # Relacionamentos
    organization = relationship("Organization", back_populates="wellness_posts", lazy="selectin")
    training_session = relationship("TrainingSession", back_populates="wellness_posts", lazy="selectin")
    athlete = relationship("Athlete", back_populates="wellness_posts", lazy="selectin")
    created_by_user = relationship("User", foreign_keys=[created_by_user_id], lazy="selectin")

    @property
    def session_id(self) -> UUID:
        """Alias para compatibilidade com schemas/response."""
        return self.training_session_id
