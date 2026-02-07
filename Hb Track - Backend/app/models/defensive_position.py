"""
DefensivePosition model - lookup for defensive positions.

Conforme REGRAS.md V1.2:
- RDB17: Tabelas de lookup são globais (posições, escolaridade)
- RD13: ID=5 é Goleira (não pode ter posição ofensiva)

Estrutura real no banco (0001-neondb.sql):
- id, code, name, abbreviation, is_active
"""
from __future__ import annotations

from typing import Optional

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class DefensivePosition(Base):
    __tablename__ = "defensive_positions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        nullable=False,
    )
    code: Mapped[str] = mapped_column(String(32), nullable=False)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    abbreviation: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    def __repr__(self) -> str:
        return f"<DefensivePosition(id={self.id}, code='{self.code}')>"
