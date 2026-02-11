"""
Model: TrainingAlert - Step 18

Alertas automáticos de sobrecarga semanal e baixa taxa de resposta wellness.

Tipos de alertas:
- weekly_overload: Carga semanal > threshold configurado
- low_wellness_response: Taxa de resposta <70% por 2 semanas

Severidades:
- warning: 100-110% do threshold
- critical: >110% do threshold

Usage:
    from app.models.training_alert import TrainingAlert
    
    # Criar alerta
    alert = TrainingAlert(
        team_id=team_id,
        alert_type="weekly_overload",
        severity="critical",
        message="Sobrecarga detectada: 115% do threshold",
        alert_metadata={"weekly_load": 3500, "threshold": 3000}
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


class TrainingAlert(Base):
    """
    Alertas automáticos de sobrecarga e wellness.
    
    Tabela: training_alerts
    Criada em: Step 3 (migration 0036)
    
    Relacionamentos:
    - team: Team (1:N)
    - dismissed_by_user: User (0:1)
    """
    
    __tablename__ = "training_alerts"
    

# HB-AUTOGEN:BEGIN
    
    # AUTO-GENERATED FROM DB (SSOT). DO NOT EDIT MANUALLY.
    
    # Table: public.training_alerts
    
    __table_args__ = (
    
        CheckConstraint("severity::text = ANY (ARRAY['warning'::character varying, 'critical'::character varying]::text[])", name='ck_training_alerts_severity'),
    
        CheckConstraint("alert_type::text = ANY (ARRAY['weekly_overload'::character varying, 'low_wellness_response'::character varying]::text[])", name='ck_training_alerts_type'),
    
        Index('idx_alerts_active', 'team_id', 'triggered_at', unique=False, postgresql_where=sa.text('(dismissed_at IS NULL)')),
    
    )

    
    # NOTE: typing helpers may require: from datetime import date, datetime; from uuid import UUID

    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'))
    
    team_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('teams.id', name='training_alerts_team_id_fkey', ondelete='CASCADE'), nullable=False)
    
    alert_type: Mapped[str] = mapped_column(sa.String(length=50), nullable=False)
    
    severity: Mapped[str] = mapped_column(sa.String(length=20), nullable=False)
    
    message: Mapped[str] = mapped_column(sa.Text(), nullable=False)
    
    alert_metadata: Mapped[Optional[object]] = mapped_column(PG_JSONB(), nullable=True)
    
    triggered_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    
    dismissed_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    
    dismissed_by_user_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('users.id', name='training_alerts_dismissed_by_user_id_fkey', ondelete='SET NULL'), nullable=True)
    
    # HB-AUTOGEN:END
    # Primary Key
    
    # Foreign Keys
    
    
    # Dados do Alerta
    
    
    
    
    # Timestamps
    
    
    # Relacionamentos
    team: Mapped["Team"] = relationship(
        "Team",
        back_populates="training_alerts",
        lazy="selectin"
    )
    
    dismissed_by_user: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[dismissed_by_user_id],
        lazy="selectin"
    )
    
    # Constraints (já definidos na migration 0036)
    
    # Properties
    @property
    def is_active(self) -> bool:
        """Retorna True se alerta está ativo (não dismissado)."""
        return self.dismissed_at is None
    
    @property
    def is_dismissed(self) -> bool:
        """Retorna True se alerta foi dismissado."""
        return self.dismissed_at is not None
    
    @property
    def is_critical(self) -> bool:
        """Retorna True se alerta é crítico."""
        return self.severity == "critical"
    
    def __repr__(self) -> str:
        return (
            f"<TrainingAlert("
            f"id={self.id}, "
            f"team_id={self.team_id}, "
            f"type={self.alert_type}, "
            f"severity={self.severity}, "
            f"active={self.is_active}"
            f")>"
        )
