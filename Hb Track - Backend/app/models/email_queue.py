"""
Modelo para fila de emails com retry automático
"""

# HB-AUTOGEN-IMPORTS:BEGIN
from __future__ import annotations

from datetime import date, datetime
from typing import Optional
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import ForeignKey, CheckConstraint, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB as PG_JSONB, INET as PG_INET, ENUM as PG_ENUM
# HB-AUTOGEN-IMPORTS:END

import uuid

from app.models.base import Base


class EmailQueue(Base):
    """
    Fila de emails com retry automático.
    
    Benefícios:
    - Não bloqueia cadastro se SendGrid estiver lento
    - Retry automático em caso de falha (3 tentativas)
    - Tracking de status e erros
    - Processamento assíncrono via cronjob
    
    Status possíveis:
    - pending: Aguardando envio
    - sent: Enviado com sucesso
    - failed: Falhou após max_attempts
    - cancelled: Cancelado manualmente
    """
    __tablename__ = "email_queue"


# HB-AUTOGEN:BEGIN
    # AUTO-GENERATED FROM DB (SSOT). DO NOT EDIT MANUALLY.
    # Table: public.email_queue
    __table_args__ = (
        Index('ix_email_queue_created_at', 'created_at', unique=False),
        Index('ix_email_queue_next_retry', 'next_retry_at', unique=False, postgresql_where=sa.text("((status)::text = 'pending'::text)")),
        Index('ix_email_queue_status', 'status', unique=False),
        Index('ix_email_queue_to_email', 'to_email', unique=False),
    )

    # NOTE: typing helpers may require: from datetime import date, datetime; from uuid import UUID

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'))
    template_type: Mapped[str] = mapped_column(sa.String(length=50), nullable=False)
    to_email: Mapped[str] = mapped_column(sa.String(length=255), nullable=False)
    template_data: Mapped[object] = mapped_column(PG_JSONB(), nullable=False)
    status: Mapped[str] = mapped_column(sa.String(length=20), nullable=False)
    attempts: Mapped[int] = mapped_column(sa.Integer(), nullable=False)
    max_attempts: Mapped[int] = mapped_column(sa.Integer(), nullable=False)
    next_retry_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    last_error: Mapped[Optional[str]] = mapped_column(sa.Text(), nullable=True)
    sent_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    updated_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    created_by_user_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('users.id', name='fk_email_queue_created_by_user'), nullable=True)
    # HB-AUTOGEN:END
    
    # Status e controle
    
    # Auditoria
    
    def __repr__(self):
        return f"<EmailQueue(id={self.id}, type={self.template_type}, to={self.to_email}, status={self.status})>"
