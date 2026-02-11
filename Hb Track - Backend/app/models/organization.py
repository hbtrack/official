"""
Organization model.

Regras implementadas:
- R34: Clube único por organização (V1 simplificado)
- RDB4: Soft delete com deleted_at/deleted_reason
- RDB3: created_at/updated_at automáticos

Schema DB:
  - id (uuid, PK)
  - name (text, NOT NULL)
  - created_at, updated_at (timestamptz)
  - deleted_at, deleted_reason (soft delete)
"""

# HB-AUTOGEN-IMPORTS:BEGIN
from __future__ import annotations

from datetime import date, datetime
from typing import Optional, TYPE_CHECKING
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import ForeignKey, CheckConstraint, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB as PG_JSONB, INET as PG_INET, ENUM as PG_ENUM
# HB-AUTOGEN-IMPORTS:END


from app.models.base import Base

if TYPE_CHECKING:
    from app.models.season import Season
    from app.models.team import Team
    from app.models.user import User
    from app.models.competition import Competition


class Organization(Base):
    """
    Model Organization - Organizações/Clubes.

    Regras:
    - R34: Clube único por organização (V1)
    - RDB4: Soft delete obrigatório
    """

    __tablename__ = "organizations"


# HB-AUTOGEN:BEGIN

    # AUTO-GENERATED FROM DB (SSOT). DO NOT EDIT MANUALLY.

    # Table: public.organizations

    __table_args__ = (

        CheckConstraint('deleted_at IS NULL AND deleted_reason IS NULL OR deleted_at IS NOT NULL AND deleted_reason IS NOT NULL', name='ck_organizations_deleted_reason'),

        Index('ix_organizations_name', 'name', unique=False),

        Index('ix_organizations_name_trgm', 'name', unique=False, postgresql_where=sa.text('(deleted_at IS NULL)')),

    )


    # NOTE: typing helpers may require: from datetime import date, datetime; from uuid import UUID


    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'))

    name: Mapped[str] = mapped_column(sa.String(length=100), nullable=False)

    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))

    updated_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))

    deleted_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)

    deleted_reason: Mapped[Optional[str]] = mapped_column(sa.Text(), nullable=True)

    # HB-AUTOGEN:END
    # PK

    # Campos principais

    # Timestamps — RDB3

    # Soft delete — RDB4

    # Relationships
    # NOTA: Athletes agora não tem organization_id direto no V1.2
    # O vínculo é feito via team_registrations
    
    # NOTA: Season agora pertence a Team (V1.2), não a Organization
    # seasons: Mapped[list["Season"]] = relationship(...)

    teams: Mapped[list["Team"]] = relationship(
        "Team",
        back_populates="organization",
        lazy="selectin",
    )
    
    wellness_posts = relationship(
        "WellnessPost",
        back_populates="organization",
        lazy="selectin",
    )
    
    medical_cases = relationship(
        "MedicalCase",
        back_populates="organization",
        lazy="selectin",
    )
    
    # NOTA: Tabela competitions ainda não existe no banco (migrations pendentes)
    # Usar lazy="noload" até que as migrations sejam criadas
    competitions: Mapped[list["Competition"]] = relationship(
        "Competition",
        back_populates="organization",
        lazy="noload",  # Temporário: tabela não existe ainda
    )

    @property
    def is_deleted(self) -> bool:
        """Verifica se organização foi soft-deleted."""
        return self.deleted_at is not None

    def __repr__(self) -> str:
        return f"<Organization(id={self.id}, name='{self.name}')>"
