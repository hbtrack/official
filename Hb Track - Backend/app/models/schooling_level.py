"""
SchoolingLevel model - lookup for schooling levels.

Conforme REGRAS.md V1.2:
- RDB17: Tabelas de lookup são globais (posições, escolaridade)

Estrutura real no banco (0001-neondb.sql):
- id, code, name, is_active
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


class SchoolingLevel(Base):
    __tablename__ = "schooling_levels"


# HB-AUTOGEN:BEGIN
    # AUTO-GENERATED FROM DB (SSOT). DO NOT EDIT MANUALLY.
    # Table: public.schooling_levels
    __table_args__ = (
        UniqueConstraint('code', name='ux_schooling_levels_code'),
    )

    id: Mapped[int] = mapped_column(sa.Integer(), primary_key=True, server_default=sa.text('nextval(\'"public".schooling_levels_id_seq\'::regclass)'))
    code: Mapped[str] = mapped_column(sa.String(length=32), nullable=False)
    name: Mapped[str] = mapped_column(sa.String(length=64), nullable=False)
    is_active: Mapped[bool] = mapped_column(sa.Boolean(), nullable=False, server_default=sa.text('true'))
    # HB-AUTOGEN:END

    def __repr__(self) -> str:
        return f"<SchoolingLevel(id={self.id}, code='{self.code}')>"
