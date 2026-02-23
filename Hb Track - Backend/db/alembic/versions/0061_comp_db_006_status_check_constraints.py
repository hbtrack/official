"""
COMP-DB-006: CHECK constraints em competitions.status, competitions.modality, competition_matches.status

Revision ID: 0061
Revises: 0060
Create Date: 2026-02-22 01:54:00.000000

Nota: renumerado de 0058→0061 para evitar conflito com 0058_attendance_add_justified_status.py
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0061'
down_revision = '0060'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. ADD CHECK constraint to competitions.status
    op.create_check_constraint(
        'ck_competitions_status',
        'competitions',
        "status IN ('draft', 'active', 'finished', 'cancelled')"
    )

    # 2. ADD CHECK constraint to competitions.modality
    op.create_check_constraint(
        'ck_competitions_modality',
        'competitions',
        "modality IN ('masculino', 'feminino', 'misto')"
    )

    # 3. ADD CHECK constraint to competition_matches.status
    op.create_check_constraint(
        'ck_competition_matches_status',
        'competition_matches',
        "status IN ('scheduled', 'in_progress', 'finished', 'cancelled')"
    )


def downgrade() -> None:
    # Remove constraints in reverse order
    op.drop_constraint('ck_competition_matches_status', 'competition_matches', type_='check')
    op.drop_constraint('ck_competitions_modality', 'competitions', type_='check')
    op.drop_constraint('ck_competitions_status', 'competitions', type_='check')
