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

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

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

    # PK
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    # FK User (obrigatório)
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id"),
        nullable=False,
    )

    # Relationship
    user: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="password_resets",
    )

    # Token
    token: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        unique=True,
    )

    # Tipo de token: 'reset' para recuperação, 'welcome' para novo usuário
    token_type: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default="reset",
    )

    # Status
    used: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )

    used_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Expiração
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    # Timestamps — RDB3
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP"),
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

    def __repr__(self) -> str:
        return f"<PasswordReset(id={self.id}, user_id={self.user_id}, token_type={self.token_type}, used={self.used})>"
