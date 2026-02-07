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
    )
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, CheckConstraint, ARRAY
from sqlalchemy.dialects.postgresql import UUID as PGUUID, NUMERIC
from sqlalchemy.orm import Mapped, mapped_column, relationship

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
    
    # Primary Key
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        comment="UUID da sugestão"
    )
    
    # Foreign Keys
    team_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="UUID do team"
    )
    
    origin_session_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("training_sessions.id", ondelete="CASCADE"),
        nullable=True,
        comment="UUID da sessão origem (pode ser NULL para sugestões semanais)"
    )
    
    # Dados da Sugestão
    type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Tipo: compensation | reduce_next_week"
    )
    
    target_session_ids: Mapped[Optional[List[UUID]]] = mapped_column(
        ARRAY(PGUUID(as_uuid=True)),
        nullable=True,
        comment="UUIDs das sessões alvo onde aplicar ajuste"
    )
    
    recommended_adjustment_pct: Mapped[Optional[float]] = mapped_column(
        NUMERIC(5, 2),
        nullable=True,
        comment="Ajuste recomendado em % (ex: 20.00 = reduzir 20%)"
    )
    
    reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Explicação da sugestão"
    )
    
    # Status
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
        comment="Status: pending | applied | dismissed"
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        comment="Timestamp da criação"
    )
    
    applied_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp da aplicação"
    )
    
    dismissed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp do dismissal"
    )
    
    dismissal_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Motivo do dismissal (50-500 chars)"
    )
    
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
    __table_args__ = (
        CheckConstraint(
            type.in_(["compensation", "reduce_next_week"]),
            name="ck_training_suggestions_type"
        ),
        CheckConstraint(
            status.in_(["pending", "applied", "dismissed"]),
            name="ck_training_suggestions_status"
        ),
    )
    
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
