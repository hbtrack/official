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
    )
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

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
    
    # Primary Key
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        comment="UUID do alerta"
    )
    
    # Foreign Keys
    team_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="UUID do team"
    )
    
    dismissed_by_user_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="UUID do usuário que dismissou o alerta"
    )
    
    # Dados do Alerta
    alert_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Tipo: weekly_overload | low_wellness_response"
    )
    
    severity: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Severidade: warning | critical"
    )
    
    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Mensagem descritiva do alerta"
    )
    
    alert_metadata: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Dados adicionais (weekly_load, threshold, response_rate, etc.)"
    )
    
    # Timestamps
    triggered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        comment="Timestamp da criação do alerta"
    )
    
    dismissed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp do dismissal (NULL = ativo)"
    )
    
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
    __table_args__ = (
        CheckConstraint(
            alert_type.in_(["weekly_overload", "low_wellness_response"]),
            name="ck_training_alerts_type"
        ),
        CheckConstraint(
            severity.in_(["warning", "critical"]),
            name="ck_training_alerts_severity"
        ),
    )
    
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
