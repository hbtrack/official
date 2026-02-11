"""
DefensivePosition model - lookup for defensive positions.

Conforme REGRAS.md V1.2:
- RDB17: Tabelas de lookup são globais (posições, escolaridade)
- RD13: ID=5 é Goleira (não pode ter posição ofensiva)

Estrutura real no banco (0001-neondb.sql):
- id, code, name, abbreviation, is_active
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


class DefensivePosition(Base):
    __tablename__ = "defensive_positions"


# HB-AUTOGEN:BEGIN
    # AUTO-GENERATED FROM DB (SSOT). DO NOT EDIT MANUALLY.
    # Table: public.defensive_positions
    __table_args__ = (
        UniqueConstraint('code', name='ux_defensive_positions_code'),
    )

    id: Mapped[int] = mapped_column(sa.Integer(), primary_key=True, server_default=sa.text('nextval(\'"public".defensive_positions_id_seq\'::regclass)'))
    code: Mapped[str] = mapped_column(sa.String(length=32), nullable=False)
    name: Mapped[str] = mapped_column(sa.String(length=64), nullable=False)
    abbreviation: Mapped[Optional[str]] = mapped_column(sa.String(length=10), nullable=True)
    is_active: Mapped[bool] = mapped_column(sa.Boolean(), nullable=False, server_default=sa.text('true'))
    # HB-AUTOGEN:END

    def __repr__(self) -> str:
        return f"<DefensivePosition(id={self.id}, code='{self.code}')>"
