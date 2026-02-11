"""
Model OrgMembership - Vínculos organizacionais (staff).

V1.2 Regras:
- R5: Papéis não acumuláveis
- R6: Vínculo organizacional (staff via org_memberships)
- R7: Vínculo ativo e exclusividade
- RDB9: Exclusividade de vínculo ativo por pessoa+organização+role

DB Schema V1.2 (org_memberships):
- id uuid PRIMARY KEY
- person_id uuid NOT NULL REFERENCES persons(id)
- role_id integer NOT NULL REFERENCES roles(id)
- organization_id uuid NOT NULL REFERENCES organizations(id)
- start_at timestamptz NOT NULL DEFAULT now()
- end_at timestamptz (NULL = vínculo ativo)
- created_at, updated_at timestamptz
- deleted_at, deleted_reason (soft delete)

V1.2 Mudanças:
- SEM season_id (vínculos staff não são sazonais)
- Dirigente NÃO cria vínculo automático (RF1.1)
- Coordenador/Treinador criam vínculo automático com org do criador
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

from enum import Enum


from app.models.base import Base

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.person import Person
    from app.models.role import Role
    from app.models.team import Team


class OrgMembership(Base):
    """
    Vínculo organizacional para staff (Dirigente, Coordenador, Treinador).
    
    V1.2 Regras aplicáveis:
    - R5: Papéis não acumuláveis (uma pessoa não pode ter múltiplos papéis ativos)
    - R6: Staff vinculado via org_memberships (sem season_id)
    - R7: Vínculo ativo e exclusividade por pessoa+org+role
    - RF1.1: Dirigente NÃO cria vínculo automático; Coordenador/Treinador SIM
    - RDB9: Exclusividade garantida por índice único parcial
    """

    __tablename__ = "org_memberships"


# HB-AUTOGEN:BEGIN

    # AUTO-GENERATED FROM DB (SSOT). DO NOT EDIT MANUALLY.

    # Table: public.org_memberships

    __table_args__ = (

        CheckConstraint('deleted_at IS NULL AND deleted_reason IS NULL OR deleted_at IS NOT NULL AND deleted_reason IS NOT NULL', name='ck_org_memberships_deleted_reason'),

        Index('ix_org_memberships_org_active', 'organization_id', unique=False, postgresql_where=sa.text('(deleted_at IS NULL)')),

        Index('ix_org_memberships_organization_id', 'organization_id', unique=False),

        Index('ix_org_memberships_person_active', 'person_id', unique=False, postgresql_where=sa.text('(deleted_at IS NULL)')),

        Index('ix_org_memberships_person_id', 'person_id', unique=False),

        Index('ix_org_memberships_person_org_active', 'person_id', 'organization_id', unique=False, postgresql_where=sa.text('((deleted_at IS NULL) AND (end_at IS NULL))')),

        Index('ix_org_memberships_role_id', 'role_id', unique=False),

        Index('ux_org_memberships_active', 'person_id', 'organization_id', 'role_id', unique=True, postgresql_where=sa.text('((end_at IS NULL) AND (deleted_at IS NULL))')),

    )


    # NOTE: typing helpers may require: from datetime import date, datetime; from uuid import UUID


    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'))

    person_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('persons.id', name='fk_org_memberships_person_id', ondelete='RESTRICT'), nullable=False)

    role_id: Mapped[int] = mapped_column(sa.Integer(), ForeignKey('roles.id', name='fk_org_memberships_role_id', ondelete='RESTRICT'), nullable=False)

    organization_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('organizations.id', name='fk_org_memberships_organization_id', ondelete='RESTRICT'), nullable=False)

    start_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))

    end_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))

    updated_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))

    deleted_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)

    deleted_reason: Mapped[Optional[str]] = mapped_column(sa.Text(), nullable=True)

    created_by_user_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('users.id', name='fk_org_memberships_created_by_user'), nullable=True)

    # HB-AUTOGEN:END






    # Soft delete (RDB4)


    # Timestamps (RDB3)


    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        lazy="selectin",
    )

    person: Mapped["Person"] = relationship(
        "Person",
        lazy="selectin",
    )

    # Reverse relationships for Team
    coached_teams: Mapped[list["Team"]] = relationship(
        "Team",
        foreign_keys="Team.coach_membership_id",
        back_populates="coach",
        lazy="selectin",
    )

    created_teams: Mapped[list["Team"]] = relationship(
        "Team",
        foreign_keys="Team.created_by_membership_id",
        back_populates="creator_membership",
        lazy="selectin",
    )

    @property
    def is_active(self) -> bool:
        """Vínculo ativo se end_at é None e não foi deletado."""
        if self.deleted_at is not None:
            return False
        return self.end_at is None

    def __repr__(self) -> str:
        return f"<OrgMembership(id={self.id}, org={self.organization_id}, person={self.person_id}, role={self.role_id})>"


# Alias for backward compatibility during migration
Membership = OrgMembership
