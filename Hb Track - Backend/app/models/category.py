"""
Category model – Categorias de idade/competição.

Referência:
- REGRAS.md RDB11: Categorias globais apenas com max_age (sem min_age)
- R14: Categorias globais definidas por idade máxima
- RD2: Categoria natural derivada pela idade e tabela categories

Tabela categories define faixas etárias baseadas apenas em max_age.
ID é INTEGER (lookup table - allowlist RDB2.1).
"""

from __future__ import annotations

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Category(Base):
    """
    Categorias de idade/competição (ex: Mirim, Infantil, Cadete).

    Conforme REGRAS.md RDB11:
    - id: Integer PK (lookup table)
    - name: Nome da categoria (ex: 'Mirim', 'Infantil', 'Cadete')
    - max_age: Idade máxima para a categoria (NOT NULL, > 0)
    - is_active: Se a categoria está ativa

    Exemplos:
    - Mirim (max_age=12)
    - Infantil (max_age=14)
    - Cadete (max_age=16)
    - Juvenil (max_age=18)
    - Júnior (max_age=21)
    - Adulto (max_age=36)
    - Master (max_age=60)
    """

    __tablename__ = "categories"

    # PK (Integer - lookup table, RDB2.1)
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        nullable=False,
    )

    # Nome da categoria
    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Nome da categoria (ex: 'Mirim', 'Infantil', 'Cadete')",
    )

    # Idade máxima (REGRAS.md RDB11: apenas max_age, sem min_age)
    max_age: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Idade máxima para a categoria",
    )

    # Status ativo
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
        comment="Se a categoria está ativa",
    )

    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name='{self.name}', max_age={self.max_age})>"
