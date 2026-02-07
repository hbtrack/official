"""FASE 1.2 - Tabela idempotency_keys para Ficha Única

Revision ID: 016_ficha_unica_idempotency_keys
Revises: 2026_01_01_add_reports_alerts_indexes
Create Date: 2026-01-01

Referência: FICHA.MD - Seção 1.2
REGRAS.md: R32 (Regra de ouro - nada relevante é apagado)

Esta tabela garante idempotência nas requisições da Ficha Única,
permitindo retry seguro em caso de falhas de rede.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = '0017'
down_revision = '0016'
branch_labels = None
depends_on = None


def upgrade():
    # =========================================================
    # TABELA: idempotency_keys
    # =========================================================
    # Controle de idempotência para retry seguro de requisições
    # Usado principalmente pela Ficha Única (/intake/ficha-unica)
    
    op.create_table(
        'idempotency_keys',
        # PK
        sa.Column(
            'id', 
            postgresql.UUID(as_uuid=True), 
            primary_key=True, 
            server_default=sa.text('gen_random_uuid()')
        ),
        
        # Chave de idempotência (UUID gerado pelo cliente)
        sa.Column(
            'key', 
            sa.String(255), 
            nullable=False, 
            index=True,
            comment='Chave única de idempotência fornecida pelo cliente (geralmente UUID)'
        ),
        
        # Endpoint da requisição
        sa.Column(
            'endpoint', 
            sa.String(255), 
            nullable=False,
            comment='Endpoint da API onde a chave foi utilizada'
        ),
        
        # Hash SHA-256 do payload da requisição
        sa.Column(
            'request_hash', 
            sa.String(64), 
            nullable=False,
            comment='Hash SHA-256 do payload para validar consistência'
        ),
        
        # Resposta armazenada (JSONB para replay)
        sa.Column(
            'response_json', 
            postgresql.JSONB, 
            nullable=True,
            comment='Resposta completa para replay em caso de retry'
        ),
        
        # Status HTTP da resposta
        sa.Column(
            'status_code', 
            sa.Integer, 
            nullable=True,
            comment='Código HTTP da resposta armazenada'
        ),
        
        # Timestamps
        sa.Column(
            'created_at', 
            sa.TIMESTAMP(timezone=True), 
            server_default=sa.text('now()'), 
            nullable=False,
            index=True,
            comment='Data/hora do registro (para limpeza periódica)'
        ),
        
        # Constraint de unicidade: chave + endpoint
        sa.UniqueConstraint(
            'key', 'endpoint', 
            name='uq_idempotency_key_endpoint'
        ),
        
        comment='Controle de idempotência para retry seguro. FICHA.MD Fase 1.2'
    )
    
    # =========================================================
    # ÍNDICES ADICIONAIS
    # =========================================================
    
    # Índice composto para busca rápida por key + endpoint
    op.create_index(
        'ix_idempotency_keys_key_endpoint',
        'idempotency_keys',
        ['key', 'endpoint']
    )
    
    # Nota: created_at já tem index=True na definição da coluna
    
    # =========================================================
    # COMENTÁRIOS ADICIONAIS
    # =========================================================
    op.execute("""
        COMMENT ON INDEX ix_idempotency_keys_created_at IS 
        'Índice para otimizar limpeza de registros antigos via cron job';
    """)


def downgrade():
    # Remover índices
    op.drop_index('ix_idempotency_keys_created_at', table_name='idempotency_keys')
    op.drop_index('ix_idempotency_keys_key_endpoint', table_name='idempotency_keys')
    
    # Remover tabela
    op.drop_table('idempotency_keys')
