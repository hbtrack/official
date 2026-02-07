"""
Modelo para controle de idempotência de requisições

FASE 2 - Ficha Única (FICHA.MD Seção 2.1)

Este modelo armazena chaves de idempotência para evitar processamento
duplicado de requisições. Usado principalmente na rota POST /intake/ficha-unica
para garantir que resubmissões acidentais não criem registros duplicados.

Exemplo de uso:
    - Cliente envia header 'Idempotency-Key: abc123'
    - Backend verifica se existe registro com key='abc123' e endpoint='/intake/ficha-unica'
    - Se existir: retorna response_json armazenado (304 ou 200)
    - Se não existir: processa request, salva response, retorna 201

Limpeza:
    - Registros são automaticamente limpos após 24h via scheduled job
"""
from sqlalchemy import Column, String, Integer, DateTime, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid

from app.models.base import Base


class IdempotencyKey(Base):
    """
    Modelo para armazenamento de chaves de idempotência.
    
    Tabela: idempotency_keys
    
    Campos:
        id: UUID primário
        key: Chave única fornecida pelo cliente (header Idempotency-Key)
        endpoint: Rota da requisição (ex: /api/v1/intake/ficha-unica)
        request_hash: SHA256 do body da requisição para validação
        response_json: Response completo armazenado (JSONB)
        status_code: HTTP status code da response original
        created_at: Timestamp de criação para limpeza automática
    
    Constraints:
        - Unique: (key, endpoint) - mesma chave pode ser usada em endpoints diferentes
        
    Índices:
        - ix_idempotency_keys_key: Busca rápida por chave
        - ix_idempotency_keys_created_at: Limpeza de registros antigos
    """
    __tablename__ = "idempotency_keys"
    
    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4,
        comment="ID único do registro de idempotência"
    )
    
    key = Column(
        String(255), 
        nullable=False, 
        index=True,
        comment="Chave de idempotência fornecida pelo cliente"
    )
    
    endpoint = Column(
        String(255), 
        nullable=False,
        comment="Endpoint da requisição (ex: /api/v1/intake/ficha-unica)"
    )
    
    request_hash = Column(
        String(64), 
        nullable=False,
        comment="SHA256 do body da requisição para validação de payload idêntico"
    )
    
    response_json = Column(
        JSONB, 
        nullable=True,
        comment="Response completo armazenado em JSON"
    )
    
    status_code = Column(
        Integer, 
        nullable=True,
        comment="HTTP status code da response original"
    )
    
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False, 
        index=True,
        comment="Timestamp de criação para expiração automática"
    )
    
    __table_args__ = (
        UniqueConstraint('key', 'endpoint', name='uq_idempotency_key_endpoint'),
        Index('ix_idempotency_keys_key_endpoint', 'key', 'endpoint'),
        {'comment': 'Chaves de idempotência para evitar processamento duplicado de requisições'}
    )
    
    def __repr__(self):
        return f"<IdempotencyKey(key='{self.key}', endpoint='{self.endpoint}', status={self.status_code})>"
