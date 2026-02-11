"""
TeamMembership model - Vínculo de staff (coordenadores/treinadores) com equipes.

Análogo a TeamRegistration (atletas), mas para staff.
"""

# HB-AUTOGEN-IMPORTS:BEGIN
from __future__ import annotations

from datetime import date, datetime
from typing import Optional, TYPE_CHECKING
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import ForeignKey, CheckConstraint, Index, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB as PG_JSONB, INET as PG_INET, ENUM as PG_ENUM
# HB-AUTOGEN-IMPORTS:END


from app.models.base import Base

if TYPE_CHECKING:
    from app.models.person import Person
    from app.models.team import Team
    from app.models.membership import OrgMembership


class TeamMembership(Base):
    """
    Vínculo de staff (coordenador/treinador) com equipe específica.
    
    Diferente de OrgMembership (vínculo organizacional), este modelo
    representa o vínculo com uma equipe específica.
    
    Campos:
    - id: UUID PK
    - person_id: FK → persons
    - team_id: FK → teams
    - org_membership_id: FK → org_memberships (referência ao cargo organizacional)
    - start_at: início do vínculo (NOT NULL)
    - end_at: fim do vínculo, NULL se ativo
    - status: 'pendente' | 'ativo' | 'inativo'
    - created_at, updated_at: timestamps
    - deleted_at, deleted_reason: soft delete
    """

    __tablename__ = "team_memberships"


# HB-AUTOGEN:BEGIN

    # AUTO-GENERATED FROM DB (SSOT). DO NOT EDIT MANUALLY.

    # Table: public.team_memberships

    __table_args__ = (

        CheckConstraint("status = ANY (ARRAY['pendente'::text, 'ativo'::text, 'inativo'::text])", name='check_team_memberships_status'),

        Index('idx_team_memberships_active', 'team_id', 'status', 'end_at', unique=False),

        Index('idx_team_memberships_org_membership_id', 'org_membership_id', unique=False),

        Index('idx_team_memberships_person_id', 'person_id', unique=False),

        Index('idx_team_memberships_person_team_active', 'person_id', 'team_id', unique=True, postgresql_where=sa.text("((deleted_at IS NULL) AND (end_at IS NULL) AND (status = ANY (ARRAY['pendente'::text, 'ativo'::text])))")),

        Index('idx_team_memberships_status', 'status', unique=False),

        Index('idx_team_memberships_team_active', 'team_id', 'status', unique=False, postgresql_where=sa.text('((deleted_at IS NULL) AND (end_at IS NULL))')),

        Index('idx_team_memberships_team_id', 'team_id', unique=False),

    )


    # NOTE: typing helpers may require: from datetime import date, datetime; from uuid import UUID


    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'))

    person_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('persons.id', name='team_memberships_person_id_fkey', ondelete='CASCADE'), nullable=False)

    team_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('teams.id', name='team_memberships_team_id_fkey', ondelete='CASCADE'), nullable=False)

    org_membership_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('org_memberships.id', name='team_memberships_org_membership_id_fkey', ondelete='SET NULL'), nullable=True)

    start_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))

    end_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)

    status: Mapped[str] = mapped_column(sa.Text(), nullable=False, server_default=sa.text("'pendente'::text"))

    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))

    updated_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))

    deleted_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)

    deleted_reason: Mapped[Optional[str]] = mapped_column(sa.Text(), nullable=True)

    resend_count: Mapped[int] = mapped_column(sa.Integer(), nullable=False, server_default=sa.text('0'))

    # HB-AUTOGEN:END
    # PK

    # FKs
    
    

    # Períodos de vínculo
    
    
    # Status: pendente (aguardando aceitação), ativo, inativo
    
    # Contador de reenvios de convite (para membros pendentes)

    # Timestamps
    

    # Soft delete
    

    # Relationships
    person: Mapped["Person"] = relationship("Person", lazy="selectin")
    team: Mapped["Team"] = relationship("Team", lazy="selectin")
    org_membership: Mapped[Optional["OrgMembership"]] = relationship("OrgMembership", lazy="selectin")

    @property
    def is_active(self) -> bool:
        """Vínculo ativo se status='ativo', end_at é None e não foi deletado."""
        if self.deleted_at is not None:
            return False
        if self.end_at is not None:
            return False
        return self.status == "ativo"
    
    @property
    def is_pending(self) -> bool:
        """Vínculo pendente se status='pendente' e não foi deletado."""
        if self.deleted_at is not None:
            return False
        return self.status == "pendente"

    def __repr__(self) -> str:
        return f"<TeamMembership(id={self.id}, team={self.team_id}, person={self.person_id}, status={self.status})>"
