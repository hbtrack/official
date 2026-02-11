"""
Model: SessionTemplate

Templates customizados de treino criados por coaches.
Sistema permite até 50 templates por org, com favoritos e hard delete.
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
    

# HB-AUTOGEN:BEGIN
    # AUTO-GENERATED FROM DB (SSOT). DO NOT EDIT MANUALLY.
    # Table: public.session_templates
    __table_args__ = (
        CheckConstraint("icon::text = ANY (ARRAY['target'::character varying, 'activity'::character varying, 'bar-chart'::character varying, 'shield'::character varying, 'zap'::character varying, 'flame'::character varying]::text[])", name='chk_session_templates_icon'),
        CheckConstraint('(focus_attack_positional_pct + focus_defense_positional_pct + focus_transition_offense_pct + focus_transition_defense_pct + focus_attack_technical_pct + focus_defense_technical_pct + focus_physical_pct) <= 120::numeric', name='chk_session_templates_total_focus'),
        UniqueConstraint('org_id', 'name', name='uq_session_templates_org_name'),
        Index('idx_session_templates_active', 'is_active', unique=False),
        Index('idx_session_templates_org_favorite', 'org_id', 'is_favorite', 'name', unique=False),
    )

    # NOTE: typing helpers may require: from datetime import date, datetime; from uuid import UUID

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    org_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('organizations.id', name='session_templates_org_id_fkey', ondelete='CASCADE'), nullable=False)
    name: Mapped[str] = mapped_column(sa.String(length=100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(sa.Text(), nullable=True)
    icon: Mapped[str] = mapped_column(sa.String(length=20), nullable=False, server_default=sa.text("'target'::character varying"))
    focus_attack_positional_pct: Mapped[object] = mapped_column(sa.Numeric(5, 2), nullable=False, server_default=sa.text("'0'::numeric"))
    focus_defense_positional_pct: Mapped[object] = mapped_column(sa.Numeric(5, 2), nullable=False, server_default=sa.text("'0'::numeric"))
    focus_transition_offense_pct: Mapped[object] = mapped_column(sa.Numeric(5, 2), nullable=False, server_default=sa.text("'0'::numeric"))
    focus_transition_defense_pct: Mapped[object] = mapped_column(sa.Numeric(5, 2), nullable=False, server_default=sa.text("'0'::numeric"))
    focus_attack_technical_pct: Mapped[object] = mapped_column(sa.Numeric(5, 2), nullable=False, server_default=sa.text("'0'::numeric"))
    focus_defense_technical_pct: Mapped[object] = mapped_column(sa.Numeric(5, 2), nullable=False, server_default=sa.text("'0'::numeric"))
    focus_physical_pct: Mapped[object] = mapped_column(sa.Numeric(5, 2), nullable=False, server_default=sa.text("'0'::numeric"))
    is_favorite: Mapped[bool] = mapped_column(sa.Boolean(), nullable=False, server_default=sa.text('false'))
    is_active: Mapped[bool] = mapped_column(sa.Boolean(), nullable=False, server_default=sa.text('true'))
    created_by_membership_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('org_memberships.id', name='session_templates_created_by_membership_id_fkey', ondelete='SET NULL'), nullable=True)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    updated_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    # HB-AUTOGEN:END
    # PK
    
    # Organization scope
    
    # Template info
    
    # 7 focus percentages (0-100.00)
    
    # Features
    
    # Metadata
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    created_by: Mapped[Optional["OrgMembership"]] = relationship("OrgMembership")
    
