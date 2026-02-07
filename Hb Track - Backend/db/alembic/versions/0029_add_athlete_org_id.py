"""Add organization_id to athletes table

Revision ID: 0029_add_athlete_org_id
Revises: 0028_performance_indexes
Create Date: 2026-01-10

Adiciona coluna organization_id na tabela athletes para vincular
atletas diretamente à organização proprietária.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '0029'
down_revision: Union[str, Sequence[str], None] = '0028'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Adiciona organization_id à tabela athletes."""
    
    # Adicionar coluna organization_id (nullable inicialmente para dados existentes)
    op.add_column(
        'athletes',
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=True)
    )
    
    # Criar FK para organizations
    op.create_foreign_key(
        'fk_athletes_organization_id',
        'athletes',
        'organizations',
        ['organization_id'],
        ['id'],
        ondelete='RESTRICT'
    )
    
    # Criar índice para performance de queries por organização
    op.create_index(
        'ix_athletes_organization_id',
        'athletes',
        ['organization_id'],
        postgresql_where=sa.text('deleted_at IS NULL')
    )


def downgrade() -> None:
    """Remove organization_id da tabela athletes."""
    
    op.drop_index('ix_athletes_organization_id', table_name='athletes')
    op.drop_constraint('fk_athletes_organization_id', 'athletes', type_='foreignkey')
    op.drop_column('athletes', 'organization_id')
