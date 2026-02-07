"""Add extended fields to persons table

Revision ID: c1a2b3d4e5f6
Revises: b4b136a1af44
Create Date: 2025-12-27 02:36:16

Adiciona campos estendidos à tabela persons conforme modelo Person:
- cpf, phone, email (dados de contato)
- address_* (endereço completo)
- notes (observações)
- deleted_at, deleted_reason (soft delete - RDB4)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c1a2b3d4e5f6'
down_revision: Union[str, None] = 'b4b136a1af44'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Dados de identificação e contato
    op.add_column('persons', sa.Column('cpf', sa.String(11), nullable=True))
    op.add_column('persons', sa.Column('phone', sa.String(20), nullable=True))
    op.add_column('persons', sa.Column('email', sa.String(100), nullable=True))
    
    # Endereço completo
    op.add_column('persons', sa.Column('address_street', sa.String(200), nullable=True))
    op.add_column('persons', sa.Column('address_number', sa.String(20), nullable=True))
    op.add_column('persons', sa.Column('address_complement', sa.String(100), nullable=True))
    op.add_column('persons', sa.Column('address_neighborhood', sa.String(100), nullable=True))
    op.add_column('persons', sa.Column('address_city', sa.String(100), nullable=True))
    op.add_column('persons', sa.Column('address_state', sa.String(2), nullable=True))
    op.add_column('persons', sa.Column('address_zip_code', sa.String(8), nullable=True))
    
    # Observações
    op.add_column('persons', sa.Column('notes', sa.Text(), nullable=True))
    
    # NOTA: deleted_at e deleted_reason já existem no banco (criados no initial_schema.sql)
    # Não precisamos adicionar novamente
    
    # Índice único para CPF (quando preenchido)
    op.create_index('ux_persons_cpf', 'persons', ['cpf'], unique=True, postgresql_where=sa.text('cpf IS NOT NULL'))


def downgrade() -> None:
    # Remove índice
    op.drop_index('ux_persons_cpf', table_name='persons')
    
    # Remove observações
    op.drop_column('persons', 'notes')
    
    # Remove endereço
    op.drop_column('persons', 'address_zip_code')
    op.drop_column('persons', 'address_state')
    op.drop_column('persons', 'address_city')
    op.drop_column('persons', 'address_neighborhood')
    op.drop_column('persons', 'address_complement')
    op.drop_column('persons', 'address_number')
    op.drop_column('persons', 'address_street')
    
    # Remove contato
    op.drop_column('persons', 'email')
    op.drop_column('persons', 'phone')
    op.drop_column('persons', 'cpf')
    
    # NOTA: deleted_at e deleted_reason NÃO são removidos pois existiam antes desta migração
