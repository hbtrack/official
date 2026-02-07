"""FASE 1.3 - Adicionar campos de auditoria para Ficha Única

Revision ID: 017_ficha_unica_audit_fields
Revises: 016_ficha_unica_idempotency_keys
Create Date: 2026-01-01

Referência: FICHA.MD - Seção 1.3
REGRAS.md: R30 (Ações críticas auditáveis), R31 (Log obrigatório)

Adiciona campo created_by_user_id nas tabelas relacionadas à Ficha Única
para rastreabilidade completa de quem criou cada registro.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = '017_ficha_audit'
down_revision = '016_ficha_idempy'
branch_labels = None
depends_on = None


def upgrade():
    # =========================================================
    # TABELAS QUE RECEBERÃO created_by_user_id
    # =========================================================
    # Verifica existência antes de adicionar para evitar erros
    
    tables_to_audit = [
        'person_contacts',
        'person_documents',
        'person_addresses',
        'person_media',
    ]
    
    for table in tables_to_audit:
        # Adicionar coluna created_by_user_id
        op.add_column(
            table,
            sa.Column(
                'created_by_user_id',
                postgresql.UUID(as_uuid=True),
                nullable=True,
                comment='ID do usuário que criou o registro (auditoria)'
            )
        )
        
        # Adicionar FK para users
        op.create_foreign_key(
            f'fk_{table}_created_by_user',
            table,
            'users',
            ['created_by_user_id'],
            ['id'],
            ondelete='SET NULL'
        )
        
        # Adicionar índice para consultas de auditoria
        op.create_index(
            f'ix_{table}_created_by_user_id',
            table,
            ['created_by_user_id']
        )
    
    # =========================================================
    # COMENTÁRIOS
    # =========================================================
    for table in tables_to_audit:
        op.execute(f"""
            COMMENT ON COLUMN {table}.created_by_user_id IS 
            'Usuário que criou o registro. R30/R31: auditoria obrigatória.'
        """)


def downgrade():
    tables_to_audit = [
        'person_contacts',
        'person_documents',
        'person_addresses',
        'person_media',
    ]
    
    for table in reversed(tables_to_audit):
        # Remover FK
        op.drop_constraint(f'fk_{table}_created_by_user', table, type_='foreignkey')
        
        # Remover índice
        op.drop_index(f'ix_{table}_created_by_user_id', table_name=table)
        
        # Remover coluna
        op.drop_column(table, 'created_by_user_id')
