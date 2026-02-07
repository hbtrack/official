"""
SchoolingLevel model - lookup for schooling levels.

Conforme REGRAS.md V1.2:
- RDB17: Tabelas de lookup são globais (posições, escolaridade)

Estrutura real no banco (0001-neondb.sql):
- id, code, name, is_active
"""
from __future__ import annotations

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class SchoolingLevel(Base):
    __tablename__ = "schooling_levels"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        nullable=False,
    )
    code: Mapped[str] = mapped_column(String(32), nullable=False)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    def __repr__(self) -> str:
        return f"<SchoolingLevel(id={self.id}, code='{self.code}')>"
