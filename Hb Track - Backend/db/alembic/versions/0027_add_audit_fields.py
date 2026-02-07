"""fase1_add_missing_audit_fields

Revision ID: 314e57818480
Revises: 20260101_dashboard_indexes
Create Date: 2026-01-01 16:30:51.646291

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0027'
down_revision: Union[str, Sequence[str], None] = '0026'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    FASE 1 - Adicionar campos de auditoria faltantes
    
    Adiciona created_by_user_id nas tabelas:
    - org_memberships
    - team_registrations
    """
    # Adicionar created_by_user_id em org_memberships
    op.execute("""
        ALTER TABLE org_memberships 
        ADD COLUMN IF NOT EXISTS created_by_user_id UUID
    """)
    
    op.execute("""
        ALTER TABLE org_memberships 
        ADD CONSTRAINT fk_org_memberships_created_by_user 
        FOREIGN KEY (created_by_user_id) REFERENCES users(id)
    """)
    
    # Adicionar created_by_user_id em team_registrations
    op.execute("""
        ALTER TABLE team_registrations 
        ADD COLUMN IF NOT EXISTS created_by_user_id UUID
    """)
    
    op.execute("""
        ALTER TABLE team_registrations 
        ADD CONSTRAINT fk_team_registrations_created_by_user 
        FOREIGN KEY (created_by_user_id) REFERENCES users(id)
    """)


def downgrade() -> None:
    """Downgrade schema."""
    # Remover foreign keys
    op.execute("""
        ALTER TABLE team_registrations 
        DROP CONSTRAINT IF EXISTS fk_team_registrations_created_by_user
    """)
    
    op.execute("""
        ALTER TABLE org_memberships 
        DROP CONSTRAINT IF EXISTS fk_org_memberships_created_by_user
    """)
    
    # Remover colunas
    op.execute("""
        ALTER TABLE team_registrations 
        DROP COLUMN IF EXISTS created_by_user_id
    """)
    
    op.execute("""
        ALTER TABLE org_memberships 
        DROP COLUMN IF EXISTS created_by_user_id
    """)

