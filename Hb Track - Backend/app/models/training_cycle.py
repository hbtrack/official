"""
Model: TrainingCycle (Macrociclos e Mesociclos)

Referências TRAINNIG.MD:
- Macrociclo: temporada completa ou fase longa
- Mesociclo: 4-6 semanas
- Mesociclo pertence a um Macrociclo (parent_cycle_id)
"""
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Text, CheckConstraint, Date, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import text

from app.models.base import Base


class TrainingCycle(Base):
    """Macrociclo ou Mesociclo de treinamento."""
    __tablename__ = "training_cycles"

    # PK
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()")
    )

    # Organization scope
    organization_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True
    )

    # Team context
    team_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teams.id"),
        nullable=False,
        index=True
    )

    # Tipo: macro ou meso
    type: Mapped[str] = mapped_column(nullable=False)

    # Período
    start_date: Mapped[Date] = mapped_column(Date, nullable=False, index=True)
    end_date: Mapped[Date] = mapped_column(Date, nullable=False, index=True)

    # Objetivo estratégico
    objective: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Status
    status: Mapped[str] = mapped_column(nullable=False, default='active', server_default=text("'active'"))

    # Relacionamento (mesociclo → macrociclo)
    parent_cycle_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("training_cycles.id"),
        nullable=True,
        index=True
    )

    # Auditoria
    created_by_user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=text("now()"),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=text("now()"),
        nullable=False
    )

    # Soft delete
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    deleted_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    microcycles = relationship(
        "TrainingMicrocycle",
        back_populates="cycle",
        foreign_keys="TrainingMicrocycle.cycle_id",
        lazy="selectin"
    )

    # Check constraints
    __table_args__ = (
        CheckConstraint("type IN ('macro', 'meso')", name="check_cycle_type"),
        CheckConstraint("status IN ('active', 'completed', 'cancelled')", name="check_cycle_status"),
        CheckConstraint("start_date < end_date", name="check_cycle_dates"),
    )

    @property
    def duration_days(self) -> int:
        """Duração do ciclo em dias."""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days
        return 0

    def __repr__(self) -> str:
        return f"<TrainingCycle {self.type} {self.start_date} - {self.end_date}>"
