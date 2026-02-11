"""
Notification model - Notificações para usuários do sistema.

Step 9: Model para notificações em tempo real via WebSocket e REST.
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


# HB-AUTOGEN:BEGIN

    # AUTO-GENERATED FROM DB (SSOT). DO NOT EDIT MANUALLY.

    # Table: public.notifications

    __table_args__ = (

        Index('idx_notifications_cleanup', 'read_at', 'created_at', unique=False),

        Index('idx_notifications_created', 'created_at', unique=False),

        Index('idx_notifications_unread', 'user_id', 'created_at', unique=False, postgresql_where=sa.text('(read_at IS NULL)')),

        Index('idx_notifications_user_read', 'user_id', 'read_at', unique=False),

    )


    # NOTE: typing helpers may require: from datetime import date, datetime; from uuid import UUID


    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'))

    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('users.id', name='notifications_user_id_fkey', ondelete='CASCADE'), nullable=False)

    type: Mapped[str] = mapped_column(sa.String(length=50), nullable=False)

    message: Mapped[str] = mapped_column(sa.Text(), nullable=False)

    notification_data: Mapped[Optional[object]] = mapped_column(PG_JSONB(), nullable=True)

    read_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))

    # HB-AUTOGEN:END
    # PK

    # FK

    # Tipo e conteúdo
    
    
    # Timestamps
    

    # Relacionamento
    user: Mapped["User"] = relationship("User", back_populates="notifications")

    @property
    def is_read(self) -> bool:
        """Retorna True se a notificação foi lida."""
        return self.read_at is not None

    def __repr__(self) -> str:
        return f"<Notification(id={self.id}, user_id={self.user_id}, type={self.type}, is_read={self.is_read})>"
