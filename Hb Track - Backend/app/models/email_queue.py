"""
Modelo para fila de emails com retry automático
"""
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
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

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_type = Column(String(50), nullable=False, comment='invite, welcome, reset_password')
    to_email = Column(String(255), nullable=False, index=True)
    template_data = Column(JSONB, nullable=False, comment='Dados dinâmicos do template')
    
    # Status e controle
    status = Column(String(20), nullable=False, default='pending', index=True)
    attempts = Column(Integer, nullable=False, default=0)
    max_attempts = Column(Integer, nullable=False, default=3)
    next_retry_at = Column(DateTime(timezone=True), nullable=True)
    last_error = Column(Text, nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    
    # Auditoria
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    created_by_user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    
    def __repr__(self):
        return f"<EmailQueue(id={self.id}, type={self.template_type}, to={self.to_email}, status={self.status})>"
