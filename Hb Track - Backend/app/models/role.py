"""
Role model.

Modelo de papéis do sistema.
Ref: R4 - Papéis do sistema (Dirigente, Coordenador, Treinador, Atleta)
Ref: RDB2.1 - Roles usa integer como PK (tabela lookup)
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, SmallInteger, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Role(Base):
    """
    Papel/função no sistema.
    
    Ref: R4 - Papéis são fixos (catálogo)
    Ref: RDB2.1 - PK integer (tabela lookup)
    """

    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(
        SmallInteger,
        primary_key=True,
        autoincrement=True,
    )

    code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Role(id={self.id}, code={self.code!r}, name={self.name!r})>"
