"""
Model PasswordReset - Tokens de recuperação de senha

Regras:
- Token único e seguro
- Expira em 24 horas
- Soft delete (R29, RDB4)

Schema DB:
  - id (uuid, PK)
  - user_id (uuid, FK → users, NOT NULL)
  - token (text, UNIQUE, NOT NULL)
  - token_type (text, CHECK IN ('reset', 'welcome'))
  - used (boolean, default false)
  - used_at (timestamptz, nullable)
  - expires_at (timestamptz, NOT NULL)
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
    from app.models.user import User


class PasswordReset(Base):
    """
    Model PasswordReset - Tokens de recuperação de senha.

    Regras:
    - R29: Sem delete físico
    - RDB4: Soft delete com deleted_at/deleted_reason
    """

    __tablename__ = "password_resets"


# HB-AUTOGEN:BEGIN

    # AUTO-GENERATED FROM DB (SSOT). DO NOT EDIT MANUALLY.

    # Table: public.password_resets

    __table_args__ = (

        CheckConstraint('deleted_at IS NULL AND deleted_reason IS NULL OR deleted_at IS NOT NULL AND deleted_reason IS NOT NULL', name='ck_password_resets_deleted_reason'),

        CheckConstraint("token_type = ANY (ARRAY['reset'::text, 'welcome'::text])", name='ck_password_resets_token_type'),

        UniqueConstraint('token', name='password_resets_token_key'),

        Index('ix_password_resets_expires_at', 'expires_at', unique=False),

        Index('ix_password_resets_token', 'token', unique=False),

        Index('ix_password_resets_user_id', 'user_id', unique=False),

    )


    # NOTE: typing helpers may require: from datetime import date, datetime; from uuid import UUID


    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'))

    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('users.id', name='fk_password_resets_user_id'), nullable=False)

    token: Mapped[str] = mapped_column(sa.Text(), nullable=False)

    token_type: Mapped[str] = mapped_column(sa.Text(), nullable=False, server_default=sa.text("'reset'::text"))

    used: Mapped[bool] = mapped_column(sa.Boolean(), nullable=False, server_default=sa.text('false'))

    used_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)

    expires_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False)

    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'))

    updated_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'))

    deleted_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)

    deleted_reason: Mapped[Optional[str]] = mapped_column(sa.Text(), nullable=True)

    # HB-AUTOGEN:END
    # PK

    # FK User (obrigatório)

    # Relationship
    user: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="password_resets",
    )

    # Token

    # Tipo de token: 'reset' para recuperação, 'welcome' para novo usuário

    # Status


    # Expiração

    # Timestamps — RDB3


    # Soft delete — RDB4


    def __repr__(self) -> str:
        return f"<PasswordReset(id={self.id}, user_id={self.user_id}, token_type={self.token_type}, used={self.used})>"
