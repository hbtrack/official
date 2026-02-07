"""rename metadata to alert_metadata

Revision ID: 0037
Revises: 0036
Create Date: 2026-01-16 21:50:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0037'
down_revision = '0036'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Renomear coluna metadata para alert_metadata em training_alerts."""
    
    # Renomear coluna
    op.alter_column(
        'training_alerts',
        'metadata',
        new_column_name='alert_metadata'
    )


def downgrade() -> None:
    """Reverter renomeação."""
    
    # Reverter nome
    op.alter_column(
        'training_alerts',
        'alert_metadata',
        new_column_name='metadata'
    )
