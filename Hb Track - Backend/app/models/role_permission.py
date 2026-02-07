"""
Auto-generated model skeleton for table role_permissions.
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


class RolePermission(Base):
    __tablename__ = "role_permissions"


# HB-AUTOGEN:BEGIN
    # AUTO-GENERATED FROM DB (SSOT). DO NOT EDIT MANUALLY.
    # Table: public.role_permissions
    role_id: Mapped[int] = mapped_column(sa.SmallInteger(), ForeignKey('roles.id', name='fk_role_permissions_role_id', ondelete='CASCADE'), primary_key=True)
    permission_id: Mapped[int] = mapped_column(sa.SmallInteger(), ForeignKey('permissions.id', name='fk_role_permissions_permission_id', ondelete='CASCADE'), primary_key=True)
    # HB-AUTOGEN:END
    # Manual customizations below (preserved across regen)
