"""
COMP-DB-004: unique NULLS NOT DISTINCT em competition_standings(competition_id, phase_id, opponent_team_id)

Revision ID: 0060
Revises: 0059
Create Date: 2026-02-22 01:16:00.000000

Nota: renumerado de 0057→0060 para evitar conflito com 0057_add_match_goalkeeper_stints.py
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0060'
down_revision = '0059'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Drop existing UNIQUE constraint
    op.drop_constraint(
        'uk_competition_standings_team_phase', 
        'competition_standings', 
        type_='unique'
    )

    # 2. Create new UNIQUE constraint with NULLS NOT DISTINCT
    # This ensures that multiple rows with phase_id=NULL for the same competition and opponent are NOT allowed.
    op.create_unique_constraint(
        'uq_competition_standings_comp_phase_opponent',
        'competition_standings',
        ['competition_id', 'phase_id', 'opponent_team_id'],
        postgresql_nulls_not_distinct=True
    )


def downgrade() -> None:
    # 1. Drop the new constraint
    op.drop_constraint(
        'uq_competition_standings_comp_phase_opponent', 
        'competition_standings', 
        type_='unique'
    )

    # 2. Re-create the old UNIQUE constraint (standard behavior: multiple NULLs allowed)
    op.create_unique_constraint(
        'uk_competition_standings_team_phase',
        'competition_standings',
        ['competition_id', 'phase_id', 'opponent_team_id']
    )
