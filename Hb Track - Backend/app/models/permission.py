"""
Auto-generated model skeleton for table permissions.
Do not edit HB-AUTOGEN blocks manually.
"""

# HB-AUTOGEN-IMPORTS:BEGIN
from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import ForeignKey, CheckConstraint, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB as PG_JSONB
# HB-AUTOGEN-IMPORTS:END
from app.models.base import Base


class Permission(Base):
    __tablename__ = "permissions"


# HB-AUTOGEN:BEGIN
    # AUTO-GENERATED FROM DB (SSOT). DO NOT EDIT MANUALLY.
    # Table: public.permissions
    __table_args__ = (
        UniqueConstraint('code', name='ux_permissions_code'),
        Index('ux_permissions_code', 'code', unique=True),
    )

    # NOTE: typing helpers may require: from datetime import date, datetime; from uuid import UUID

    id: Mapped[int] = mapped_column(sa.SmallInteger(), primary_key=True, server_default=sa.text('nextval(\'"public".permissions_id_seq\'::regclass)'))
    code: Mapped[str] = mapped_column(sa.String(64), nullable=False)
    description: Mapped[str] = mapped_column(sa.Text())
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    updated_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    # HB-AUTOGEN:END
    # Manual customizations below (preserved across regen)
