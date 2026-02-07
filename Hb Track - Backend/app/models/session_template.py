"""
Model: SessionTemplate

Templates customizados de treino criados por coaches.
Sistema permite até 50 templates por org, com favoritos e hard delete.
"""
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Boolean, Numeric, CheckConstraint, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class SessionTemplate(Base):
    """
    Template de foco de treino customizado.
    
    Regras:
    - Limite 50 templates por org
    - Hard delete (não soft delete) para liberar espaço
    - Sistema de favoritos (ordenação)
    - Soma dos focos ≤ 120%
    """
    __tablename__ = "session_templates"
    
    # PK
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )
    
    # Organization scope
    organization_id: Mapped[UUID] = mapped_column(
        "org_id",
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Template info
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    icon: Mapped[str] = mapped_column(
        String(20), 
        nullable=False, 
        server_default="target"
    )
    
    # 7 focus percentages (0-100.00)
    focus_attack_positional_pct: Mapped[float] = mapped_column(
        Numeric(5, 2), 
        nullable=False, 
        server_default="0"
    )
    focus_defense_positional_pct: Mapped[float] = mapped_column(
        Numeric(5, 2), 
        nullable=False, 
        server_default="0"
    )
    focus_transition_offense_pct: Mapped[float] = mapped_column(
        Numeric(5, 2), 
        nullable=False, 
        server_default="0"
    )
    focus_transition_defense_pct: Mapped[float] = mapped_column(
        Numeric(5, 2), 
        nullable=False, 
        server_default="0"
    )
    focus_attack_technical_pct: Mapped[float] = mapped_column(
        Numeric(5, 2), 
        nullable=False, 
        server_default="0"
    )
    focus_defense_technical_pct: Mapped[float] = mapped_column(
        Numeric(5, 2), 
        nullable=False, 
        server_default="0"
    )
    focus_physical_pct: Mapped[float] = mapped_column(
        Numeric(5, 2), 
        nullable=False, 
        server_default="0"
    )
    
    # Features
    is_favorite: Mapped[bool] = mapped_column(
        Boolean, 
        nullable=False, 
        server_default="false"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, 
        nullable=False, 
        server_default="true"
    )
    
    # Metadata
    created_by_membership_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("org_memberships.id", ondelete="SET NULL"),
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    created_by: Mapped[Optional["OrgMembership"]] = relationship("OrgMembership")
    
    __table_args__ = (
        CheckConstraint(
            "icon IN ('target', 'activity', 'bar-chart', 'shield', 'zap', 'flame')",
            name="chk_session_templates_icon"
        ),
        CheckConstraint(
            """
            (focus_attack_positional_pct + focus_defense_positional_pct + 
             focus_transition_offense_pct + focus_transition_defense_pct +
             focus_attack_technical_pct + focus_defense_technical_pct + 
             focus_physical_pct) <= 120
            """,
            name="chk_session_templates_total_focus"
        ),
    )
