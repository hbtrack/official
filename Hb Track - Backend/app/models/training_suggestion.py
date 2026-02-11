"""
Model: TrainingSuggestion - Step 18

Sugestões automáticas de ajuste de carga.

Tipos de sugestões:
- compensation: Compensar sessão com focus >100% nas próximas 2-3 sessões
- reduce_next_week: Reduzir intensidade 15-30% na próxima semana (overload critical)

Status:
- pending: Aguardando decisão do treinador
- applied: Aplicada às sessões target
- dismissed: Recusada pelo treinador

Usage:
    from app.models.training_suggestion import TrainingSuggestion
    
    # Criar sugestão
    suggestion = TrainingSuggestion(
        team_id=team_id,
        type="compensation",
        origin_session_id=session_id,
        target_session_ids=[uuid1, uuid2, uuid3],
        recommended_adjustment_pct=20.0,
        reason="Sessão origem com 115% de foco total. Compensar nas próximas 3 sessões."
"""

# HB-AUTOGEN-IMPORTS:BEGIN
from __future__ import annotations

from datetime import date, datetime
from typing import Optional, List
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import ForeignKey, CheckConstraint, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB as PG_JSONB, INET as PG_INET, ENUM as PG_ENUM
# HB-AUTOGEN-IMPORTS:END


from app.models.base import Base


class TrainingSuggestion(Base):
    """
    Sugestões automáticas de ajuste de carga.
    
    Tabela: training_suggestions
    Criada em: Step 3 (migration 0036)
    
    Relacionamentos:
    - team: Team (1:N)
    - origin_session: TrainingSession (0:1)
    """
    
    __tablename__ = "training_suggestions"
    

# HB-AUTOGEN:BEGIN
    
    # AUTO-GENERATED FROM DB (SSOT). DO NOT EDIT MANUALLY.
    
    # Table: public.training_suggestions
    
    __table_args__ = (
    
        CheckConstraint("status::text = ANY (ARRAY['pending'::character varying, 'applied'::character varying, 'dismissed'::character varying]::text[])", name='ck_training_suggestions_status'),
    
        CheckConstraint("type::text = ANY (ARRAY['compensation'::character varying, 'reduce_next_week'::character varying]::text[])", name='ck_training_suggestions_type'),
    
    )

    
    # NOTE: typing helpers may require: from datetime import date, datetime; from uuid import UUID

    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'))
    
    team_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('teams.id', name='training_suggestions_team_id_fkey', ondelete='CASCADE'), nullable=False)
    
    type: Mapped[str] = mapped_column(sa.String(length=50), nullable=False)
    
    origin_session_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('training_sessions.id', name='training_suggestions_origin_session_id_fkey', ondelete='CASCADE'), nullable=True)
    
    target_session_ids: Mapped[Optional[object]] = mapped_column(sa.ARRAY(PG_UUID(as_uuid=True)), nullable=True)
    
    recommended_adjustment_pct: Mapped[Optional[object]] = mapped_column(sa.Numeric(5, 2), nullable=True)
    
    reason: Mapped[Optional[str]] = mapped_column(sa.Text(), nullable=True)
    
    status: Mapped[str] = mapped_column(sa.String(length=20), nullable=False, server_default=sa.text("'pending'::character varying"))
    
    applied_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    
    dismissed_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    
    dismissal_reason: Mapped[Optional[str]] = mapped_column(sa.Text(), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    
    # HB-AUTOGEN:END
    # Primary Key
    
    # Foreign Keys
    
    
    # Dados da Sugestão
    
    
    
    
    # Status
    
    # Timestamps
    
    
    
    
    # Relacionamentos
    team: Mapped["Team"] = relationship(
        "Team",
        back_populates="training_suggestions",
        lazy="selectin"
    )
    
    origin_session: Mapped[Optional["TrainingSession"]] = relationship(
        "TrainingSession",
        foreign_keys=[origin_session_id],
        lazy="selectin"
    )
    
    # Constraints (já definidos na migration 0036)
    
    # Properties
    @property
    def is_pending(self) -> bool:
        """Retorna True se sugestão está pendente."""
        return self.status == "pending"
    
    @property
    def is_applied(self) -> bool:
        """Retorna True se sugestão foi aplicada."""
        return self.status == "applied"
    
    @property
    def is_dismissed(self) -> bool:
        """Retorna True se sugestão foi recusada."""
        return self.status == "dismissed"
    
    @property
    def target_count(self) -> int:
        """Retorna número de sessões alvo."""
        return len(self.target_session_ids) if self.target_session_ids else 0
    
    def __repr__(self) -> str:
        return (
            f"<TrainingSuggestion("
            f"id={self.id}, "
            f"team_id={self.team_id}, "
            f"type={self.type}, "
            f"status={self.status}, "
            f"targets={self.target_count}"
            f")>"
        )
