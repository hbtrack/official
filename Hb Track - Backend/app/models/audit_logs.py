"""
Auto-generated model skeleton for table audit_logs.
Do not edit HB-AUTOGEN blocks manually.
"""

# HB-AUTOGEN-IMPORTS:BEGIN
from __future__ import annotations

from datetime import date, datetime
from typing import Optional
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import ForeignKey, CheckConstraint, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB as PG_JSONB, INET as PG_INET, ENUM as PG_ENUM
# HB-AUTOGEN-IMPORTS:END
from app.models.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"


# HB-AUTOGEN:BEGIN
    # AUTO-GENERATED FROM DB (SSOT). DO NOT EDIT MANUALLY.
    # Table: public.audit_logs
    __table_args__ = (
        Index('ix_audit_logs_actor_id', 'actor_id', unique=False),
        Index('ix_audit_logs_created_at', 'created_at', unique=False),
        Index('ix_audit_logs_entity', 'entity', unique=False),
        Index('ix_audit_logs_entity_id', 'entity_id', unique=False),
    )

    # NOTE: typing helpers may require: from datetime import date, datetime; from uuid import UUID

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'))
    entity: Mapped[str] = mapped_column(sa.String(length=64), nullable=False)
    entity_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    action: Mapped[str] = mapped_column(sa.String(length=64), nullable=False)
    actor_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('users.id', name='fk_audit_logs_actor_id', ondelete='SET NULL'), nullable=True)
    context: Mapped[Optional[object]] = mapped_column(PG_JSONB(), nullable=True)
    old_value: Mapped[Optional[object]] = mapped_column(PG_JSONB(), nullable=True)
    new_value: Mapped[Optional[object]] = mapped_column(PG_JSONB(), nullable=True)
    justification: Mapped[Optional[str]] = mapped_column(sa.Text(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    # HB-AUTOGEN:END
    # Manual customizations below (preserved across regen)
