"""training_sessions_standalone_flag - Add standalone BOOLEAN + ck_training_sessions_standalone

Revision ID: 0066
Revises: 0065
Create Date: 2026-02-26 00:00:00.000000

Evidencia:
  - AR: AR_149_db_training_sessions.standalone_-_cycle_hierarchy_.md
  - INV-TRAIN-054: training_sessions.standalone = (microcycle_id IS NULL)
  - INV-TRAIN-057: session date must be within microcycle week when microcycle_id is set

Nota: migration idempotente (IF NOT EXISTS) — coluna e constraint podem ja existir
no DB se a migration original (989c9c6d9f46) foi aplicada antes do incidente git restore.
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0066'
down_revision = '0065'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ADD COLUMN standalone (idempotente)
    conn = op.get_bind()
    col_exists = conn.execute(sa.text(
        "SELECT 1 FROM information_schema.columns "
        "WHERE table_name='training_sessions' AND column_name='standalone'"
    )).scalar()

    if not col_exists:
        op.add_column(
            'training_sessions',
            sa.Column('standalone', sa.Boolean(), nullable=False, server_default=sa.text('TRUE'))
        )
        # UPDATE: sessions com microcycle_id devem ser standalone=FALSE
        op.execute(sa.text(
            "UPDATE training_sessions SET standalone = FALSE WHERE microcycle_id IS NOT NULL"
        ))

    # ADD CONSTRAINT (idempotente)
    constraint_exists = conn.execute(sa.text(
        "SELECT 1 FROM information_schema.check_constraints "
        "WHERE constraint_name = 'ck_training_sessions_standalone'"
    )).scalar()

    if not constraint_exists:
        op.create_check_constraint(
            'ck_training_sessions_standalone',
            'training_sessions',
            "(standalone = TRUE AND microcycle_id IS NULL) OR "
            "(standalone = FALSE AND microcycle_id IS NOT NULL)"
        )


def downgrade() -> None:
    conn = op.get_bind()

    constraint_exists = conn.execute(sa.text(
        "SELECT 1 FROM information_schema.check_constraints "
        "WHERE constraint_name = 'ck_training_sessions_standalone'"
    )).scalar()
    if constraint_exists:
        op.drop_constraint('ck_training_sessions_standalone', 'training_sessions', type_='check')

    col_exists = conn.execute(sa.text(
        "SELECT 1 FROM information_schema.columns "
        "WHERE table_name='training_sessions' AND column_name='standalone'"
    )).scalar()
    if col_exists:
        op.drop_column('training_sessions', 'standalone')
