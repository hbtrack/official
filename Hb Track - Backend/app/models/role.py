"""
Role model.

Modelo de papéis do sistema.
Ref: R4 - Papéis do sistema (Dirigente, Coordenador, Treinador, Atleta)
Ref: RDB2.1 - Roles usa integer como PK (tabela lookup)
"""

# HB-AUTOGEN-IMPORTS:BEGIN
from __future__ import annotations

from datetime import date, datetime
from typing import Optional
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import ForeignKey, CheckConstraint, Index, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB as PG_JSONB, INET as PG_INET, ENUM as PG_ENUM
# HB-AUTOGEN-IMPORTS:END


from app.models.base import Base


class Role(Base):
    """
    Papel/função no sistema.
    
    Ref: R4 - Papéis são fixos (catálogo)
    Ref: RDB2.1 - PK integer (tabela lookup)
    """

    __tablename__ = "roles"


# HB-AUTOGEN:BEGIN

    # AUTO-GENERATED FROM DB (SSOT). DO NOT EDIT MANUALLY.

    # Table: public.roles

    __table_args__ = (

        UniqueConstraint('code', name='ux_roles_code'),

        UniqueConstraint('name', name='ux_roles_name'),

    )


    # NOTE: typing helpers may require: from datetime import date, datetime; from uuid import UUID


    id: Mapped[int] = mapped_column(sa.SmallInteger(), primary_key=True, server_default=sa.text('nextval(\'"public".roles_id_seq\'::regclass)'))

    code: Mapped[str] = mapped_column(sa.String(length=32), nullable=False)

    name: Mapped[str] = mapped_column(sa.String(length=64), nullable=False)

    description: Mapped[Optional[str]] = mapped_column(sa.Text(), nullable=True)

    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))

    updated_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))

    # HB-AUTOGEN:END






    def __repr__(self) -> str:
        return f"<Role(id={self.id}, code={self.code!r}, name={self.name!r})>"
