"""comp_db: ppw_not_null — make competitions.points_per_win NOT NULL (INV-COMP-007)

Revision ID: 0064
Revises: 0063
Create Date: 2025-01-01 00:00:00.000000

Evidência:
  - schema.sql: competitions.points_per_win integer DEFAULT 2
  - INV-COMP-007: competitions.points_per_win shall be NOT NULL (SSOT: scoring_rules_competitions)
  - AR: AR_080_completar_inv-comp-007_competitions.points_per_win.md
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0064'
down_revision = '0063'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Step 1: Backfill — garantir que não haja NULL antes do ALTER
    op.execute(
        "UPDATE competitions SET points_per_win = 2 WHERE points_per_win IS NULL"
    )
    # Step 2: Aplicar NOT NULL constraint
    op.alter_column(
        'competitions',
        'points_per_win',
        existing_type=sa.Integer(),
        nullable=False,
        existing_server_default=sa.text('2'),
    )


def downgrade() -> None:
    op.alter_column(
        'competitions',
        'points_per_win',
        existing_type=sa.Integer(),
        nullable=True,
        existing_server_default=sa.text('2'),
    )
