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


# HB-AUTOGEN:BEGIN

    # AUTO-GENERATED FROM DB (SSOT). DO NOT EDIT MANUALLY.

    # Table: public.users

    __table_args__ = (

        CheckConstraint('deleted_at IS NULL AND deleted_reason IS NULL OR deleted_at IS NOT NULL AND deleted_reason IS NOT NULL', name='ck_users_deleted_reason'),

        CheckConstraint("status::text = ANY (ARRAY['ativo'::character varying, 'inativo'::character varying, 'arquivado'::character varying]::text[])", name='ck_users_status'),

        Index('ix_users_person_id', 'person_id', unique=False),

        Index('ux_users_email', sa.text('lower(email::text)'), unique=True),

        Index('ux_users_superadmin', 'is_superadmin', unique=True, postgresql_where=sa.text('((is_superadmin = true) AND (deleted_at IS NULL))')),

    )


    # NOTE: typing helpers may require: from datetime import date, datetime; from uuid import UUID


    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'))

    person_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('persons.id', name='fk_users_person_id', ondelete='RESTRICT'), nullable=False)

    email: Mapped[str] = mapped_column(sa.String(length=255), nullable=False)

    password_hash: Mapped[Optional[str]] = mapped_column(sa.Text(), nullable=True)

    is_superadmin: Mapped[bool] = mapped_column(sa.Boolean(), nullable=False, server_default=sa.text('false'))

    is_locked: Mapped[bool] = mapped_column(sa.Boolean(), nullable=False, server_default=sa.text('false'))

    status: Mapped[str] = mapped_column(sa.String(length=20), nullable=False, server_default=sa.text("'ativo'::character varying"))

    expired_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))

    updated_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))

    deleted_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)

    deleted_reason: Mapped[Optional[str]] = mapped_column(sa.Text(), nullable=True)

    # HB-AUTOGEN:END
    # PK

    # FK Person (obrigatório conforme DB)

    # Email (único)

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

    # Status e controle

    # Timestamps — RDB3

    # Soft delete — RDB4

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
