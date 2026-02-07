"""
Notification model - Notificações para usuários do sistema.

Step 9: Model para notificações em tempo real via WebSocket e REST.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import text

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class Notification(Base):
    """
    Notificação para usuário.
    
    Tipos de notificação:
    - team_assignment: Atribuído como treinador de equipe
    - coach_removal: Removido como treinador de equipe
    - member_added: Novo membro adicionado à equipe
    - invite: Convite para ingressar em equipe
    - game: Notificações relacionadas a jogos
    - training: Notificações relacionadas a treinos
    
    Campos:
    - id: UUID PK
    - user_id: FK → users (CASCADE delete)
    - type: tipo da notificação (50 chars)
    - message: mensagem de texto
    - metadata: dados adicionais em JSON (team_id, team_name, etc)
    - read_at: timestamp de leitura, NULL se não lida
    - created_at: timestamp de criação
    """

    __tablename__ = "notifications"

    # PK
    id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()"),
    )

    # FK
    user_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Tipo e conteúdo
    type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Tipo: team_assignment, coach_removal, member_added, invite, game, training",
    )
    
    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Mensagem de texto da notificação",
    )
    
    notification_data: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Dados adicionais em JSON (team_id, team_name, etc)",
    )

    # Timestamps
    read_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp de leitura, NULL se não lida",
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
        comment="Timestamp de criação",
    )

    # Relacionamento
    user: Mapped["User"] = relationship("User", back_populates="notifications")

    @property
    def is_read(self) -> bool:
        """Retorna True se a notificação foi lida."""
        return self.read_at is not None

    def __repr__(self) -> str:
        return f"<Notification(id={self.id}, user_id={self.user_id}, type={self.type}, is_read={self.is_read})>"
