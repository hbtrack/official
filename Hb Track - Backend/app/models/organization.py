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

from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING

from sqlalchemy import ForeignKey, DateTime, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

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

    # PK
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    # Campos principais
    name: Mapped[str] = mapped_column(Text, nullable=False)

    # Timestamps — RDB3
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Soft delete — RDB4
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    deleted_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

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
