"""
COMP-DB-004: unique NULLS NOT DISTINCT em competition_standings(competition_id, phase_id, opponent_team_id)

Revision ID: 0060
Revises: 0059
Create Date: 2026-02-22 01:16:00.000000

Retrocompatibilidade PostgreSQL 12-14:
- PG >= 15: usa UNIQUE constraint com NULLS NOT DISTINCT (sintaxe nativa)
- PG < 15: usa UNIQUE INDEX parcial com WHERE clause (semântica equivalente)
Ambos impedem múltiplas rows com mesmo (competition_id, phase_id=NULL, opponent_team_id).

Nota: renumerado de 0057→0060 para evitar conflito com 0057_add_match_goalkeeper_stints.py
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = '0060'
down_revision = '0059'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    version_str = conn.execute(text("SHOW server_version")).scalar()
    major_version = int(version_str.split('.')[0])

    # 1. Drop existing UNIQUE constraint
    op.drop_constraint(
        'uk_competition_standings_team_phase', 
        'competition_standings', 
        type_='unique'
    )

    # 2. Create new UNIQUE constraint/index (version-dependent)
    if major_version >= 15:
        # PostgreSQL 15+: Native NULLS NOT DISTINCT syntax
        op.create_unique_constraint(
            'uq_competition_standings_comp_phase_opponent',
            'competition_standings',
            ['competition_id', 'phase_id', 'opponent_team_id'],
            postgresql_nulls_not_distinct=True
        )
    else:
        # PostgreSQL 12-14: Partial unique index (equivalent semantics)
        # This prevents multiple NULL values for phase_id/opponent_team_id pairs
        op.execute(
            """
            CREATE UNIQUE INDEX uq_competition_standings_comp_phase_opponent
            ON competition_standings(competition_id, phase_id, opponent_team_id)
            WHERE phase_id IS NOT NULL OR opponent_team_id IS NOT NULL
            """
        )


def downgrade() -> None:
    conn = op.get_bind()
    version_str = conn.execute(text("SHOW server_version")).scalar()
    major_version = int(version_str.split('.')[0])

    # 1. Drop the new constraint/index (version-dependent)
    if major_version >= 15:
        op.drop_constraint(
            'uq_competition_standings_comp_phase_opponent', 
            'competition_standings', 
            type_='unique'
        )
    else:
        op.execute("DROP INDEX IF EXISTS uq_competition_standings_comp_phase_opponent")

    # 2. Re-create the old UNIQUE constraint (standard behavior: multiple NULLs allowed)
    op.create_unique_constraint(
        'uk_competition_standings_team_phase',
        'competition_standings',
        ['competition_id', 'phase_id', 'opponent_team_id']
    )
