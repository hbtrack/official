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

from datetime import date, datetime
from typing import Optional, TYPE_CHECKING
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, Integer, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

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

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    person_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("persons.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    role_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("roles.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    organization_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("organizations.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    start_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
        nullable=False,
    )

    end_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Soft delete (RDB4)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    deleted_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # Timestamps (RDB3)
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
