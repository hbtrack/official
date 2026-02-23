"""COMP-DB-003: scoring rules — points_per_draw e points_per_loss em competitions

Revision ID: 0056
Revises: 0055
Create Date: 2026-02-21
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0056'
down_revision = '0055'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'competitions',
        sa.Column('points_per_draw', sa.Integer(), nullable=False, server_default=sa.text('1')),
    )
    op.add_column(
        'competitions',
        sa.Column('points_per_loss', sa.Integer(), nullable=False, server_default=sa.text('0')),
    )


def downgrade() -> None:
    op.drop_column('competitions', 'points_per_loss')
    op.drop_column('competitions', 'points_per_draw')
