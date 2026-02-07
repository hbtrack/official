"""
Model User - Usuários do sistema.

Regras implementadas:
- R2: Autenticação obrigatória
- R3: Identificação única por email
- R29: Sem delete físico
- RDB4: Soft delete com deleted_at/deleted_reason

Schema DB:
  - id (uuid, PK)
  - email (text, UNIQUE, NOT NULL)
  - password_hash (text, nullable)
  - status (text, CHECK IN ('ativo','inativo','arquivado'))
  - is_locked (boolean, default false)
  - is_superadmin (boolean, default false)
  - person_id (uuid, FK → persons, NOT NULL)
  - expired_at (timestamptz, nullable)
  - created_at, updated_at (timestamptz)
  - deleted_at, deleted_reason (soft delete)

Nota: Relação user ↔ organization é via membership (não há FK direta).
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.person import Person
    from app.models.password_reset import PasswordReset
    from app.models.competition import Competition
    from app.models.notification import Notification
    from app.models.attendance import Attendance
    from app.models.export_job import ExportJob
    from app.models.export_rate_limit import ExportRateLimit


class User(Base):
    """
    Model User - Usuários do sistema.

    Regras:
    - R2: Autenticação obrigatória
    - R3: Identificação única por email
    - R29: Sem delete físico
    - RDB4: Soft delete
    """

    __tablename__ = "users"

    # PK
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    # FK Person (obrigatório conforme DB)
    person_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("persons.id"),
        nullable=False,
    )

    # Email (único)
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    # Relationship
    person: Mapped[Optional["Person"]] = relationship(
        "Person",
        back_populates="user",
        lazy="selectin",
    )

    password_resets: Mapped[list["PasswordReset"]] = relationship(
        "PasswordReset",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    created_competitions: Mapped[list["Competition"]] = relationship(
        "Competition",
        foreign_keys="Competition.created_by",
        back_populates="creator",
        lazy="selectin",
    )

    attendances_created: Mapped[list["Attendance"]] = relationship(
        "Attendance",
        foreign_keys="Attendance.created_by_user_id",
        back_populates="created_by_user",
        lazy="selectin",
    )
    
    notifications: Mapped[list["Notification"]] = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    
    export_jobs: Mapped[list["ExportJob"]] = relationship(
        "ExportJob",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="noload",
    )
    
    export_rate_limits: Mapped[list["ExportRateLimit"]] = relationship(
        "ExportRateLimit",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="noload",
    )

    # Autenticação
    password_hash: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Status e controle
    status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default="ativo",
    )
    is_locked: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )
    is_superadmin: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )
    expired_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

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

    @property
    def is_deleted(self) -> bool:
        """Verifica se usuário foi soft-deleted."""
        return self.deleted_at is not None

    @property
    def is_active(self) -> bool:
        """Verifica se usuário está ativo."""
        return self.status == "ativo" and not self.is_deleted and not self.is_locked

    @property
    def is_expired(self) -> bool:
        """Verifica se conta expirou."""
        if self.expired_at is None:
            return False
        return datetime.now(timezone.utc) > self.expired_at

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', status={self.status})>"
