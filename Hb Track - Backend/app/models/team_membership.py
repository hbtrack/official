"""
TeamMembership model - Vínculo de staff (coordenadores/treinadores) com equipes.

Análogo a TeamRegistration (atletas), mas para staff.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Text, text
from sqlalchemy.dialects.postgresql import UUID as PgUUID, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship

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

    # PK
    id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # FKs
    person_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("persons.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    team_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    org_membership_id: Mapped[Optional[UUID]] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("org_memberships.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Referência ao vínculo organizacional (cargo)",
    )

    # Períodos de vínculo
    start_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
        comment="Data de início do vínculo",
    )
    
    end_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
        comment="Data de término; NULL = ativo",
    )
    
    # Status: pendente (aguardando aceitação), ativo, inativo
    status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="pendente",
        comment="Status: 'pendente', 'ativo', 'inativo'",
    )
    
    # Contador de reenvios de convite (para membros pendentes)
    resend_count: Mapped[int] = mapped_column(
        nullable=False,
        default=0,
        server_default="0",
        comment="Contador de reenvios de convite (máximo 3)",
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    # Soft delete
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
    )
    
    deleted_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

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
