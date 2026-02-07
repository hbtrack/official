"""Add resend_count to team_memberships

Revision ID: 0032_add_resend_count
Revises: 0031_create_competitions_module
Create Date: 2026-01-14

Step 2: Adicionar campo resend_count para controlar limite de reenvios de convite (máximo 3)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0032'
down_revision: Union[str, None] = '0031'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Adiciona campo resend_count à tabela team_memberships.
    Usado para limitar reenvios de convite a 3 tentativas.
    """
    op.add_column(
        'team_memberships',
        sa.Column('resend_count', sa.Integer(), nullable=False, server_default='0')
    )


def downgrade() -> None:
    """Remove campo resend_count."""
    op.drop_column('team_memberships', 'resend_count')
