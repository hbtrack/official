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
    

# HB-AUTOGEN:BEGIN
    # AUTO-GENERATED FROM DB (SSOT). DO NOT EDIT MANUALLY.
    # Table: public.idempotency_keys
    __table_args__ = (
        UniqueConstraint('key', 'endpoint', name='uq_idempotency_key_endpoint'),
        Index('ix_idempotency_keys_created_at', 'created_at', unique=False),
        Index('ix_idempotency_keys_key', 'key', unique=False),
        Index('ix_idempotency_keys_key_endpoint', 'key', 'endpoint', unique=False),
    )

    # NOTE: typing helpers may require: from datetime import date, datetime; from uuid import UUID

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'))
    key: Mapped[str] = mapped_column(sa.String(length=255), nullable=False)
    endpoint: Mapped[str] = mapped_column(sa.String(length=255), nullable=False)
    request_hash: Mapped[str] = mapped_column(sa.String(length=64), nullable=False)
    response_json: Mapped[Optional[object]] = mapped_column(PG_JSONB(), nullable=True)
    status_code: Mapped[Optional[int]] = mapped_column(sa.Integer(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    # HB-AUTOGEN:END
    
    
    
    
    
    
    
    
    def __repr__(self):
        return f"<IdempotencyKey(key='{self.key}', endpoint='{self.endpoint}', status={self.status_code})>"
