"""attendance_preconfirm_pending_items

Revision ID: 0067
Revises: 0066
Create Date: 2026-02-26 00:00:00.000000

Evidencia:
  - AR: AR_153_db_attendance_preconfirm_+_training_pending_items.md
  - INV-TRAIN-058/059: attendance.presence_status aceita preconfirm
  - INV-TRAIN-060: training_pending_items table para itens pendentes por atleta

Changes:
  1. ALTER TABLE attendance: DROP ck_attendance_status + ADD ck_attendance_status
     com preconfirm adicionado (present, absent, justified, preconfirm)
  2. CREATE TABLE training_pending_items com ck_pending_item_type + ck_pending_item_status
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0067'
down_revision = '0066'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    # =========================================================================
    # 1. ALTER TABLE attendance: update ck_attendance_status to add preconfirm
    #    PostgreSQL does not support ALTER CONSTRAINT — must DROP + ADD
    # =========================================================================

    # Check if preconfirm is already in the constraint (idempotent)
    existing = conn.execute(sa.text(
        "SELECT pg_get_constraintdef(oid) FROM pg_constraint "
        "WHERE conname = 'ck_attendance_status' AND conrelid = 'attendance'::regclass"
    )).scalar()

    if existing and 'preconfirm' not in existing:
        # Drop old constraint
        op.drop_constraint('ck_attendance_status', 'attendance', type_='check')

        # Add new constraint with preconfirm
        op.create_check_constraint(
            'ck_attendance_status',
            'attendance',
            "presence_status::text = ANY (ARRAY['present', 'absent', 'justified', 'preconfirm'])"
        )
    # If preconfirm already present or constraint missing: skip (idempotent)

    # =========================================================================
    # 2. CREATE TABLE training_pending_items (idempotent)
    # =========================================================================

    table_exists = conn.execute(sa.text(
        "SELECT 1 FROM information_schema.tables "
        "WHERE table_name = 'training_pending_items'"
    )).scalar()

    if not table_exists:
        op.create_table(
            'training_pending_items',
            sa.Column(
                'id',
                sa.dialects.postgresql.UUID(as_uuid=True),
                server_default=sa.text('gen_random_uuid()'),
                nullable=False,
            ),
            sa.Column('training_session_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('athlete_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('item_type', sa.String(50), nullable=False),
            sa.Column('description', sa.Text(), nullable=False),
            sa.Column('status', sa.String(20), server_default='open', nullable=False),
            sa.Column(
                'created_at',
                sa.DateTime(timezone=True),
                server_default=sa.text('now()'),
                nullable=False,
            ),
            sa.Column(
                'updated_at',
                sa.DateTime(timezone=True),
                server_default=sa.text('now()'),
                nullable=False,
            ),
            sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column(
                'resolved_by_user_id',
                sa.dialects.postgresql.UUID(as_uuid=True),
                nullable=True,
            ),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(
                ['training_session_id'],
                ['training_sessions.id'],
                name='fk_pending_items_session',
            ),
            sa.ForeignKeyConstraint(
                ['athlete_id'],
                ['users.id'],
                name='fk_pending_items_athlete',
            ),
            sa.ForeignKeyConstraint(
                ['resolved_by_user_id'],
                ['users.id'],
                name='fk_pending_items_resolver',
            ),
            sa.CheckConstraint(
                "item_type::text = ANY (ARRAY['equipment', 'material', 'admin', 'other'])",
                name='ck_pending_item_type',
            ),
            sa.CheckConstraint(
                "status::text = ANY (ARRAY['open', 'resolved', 'cancelled'])",
                name='ck_pending_item_status',
            ),
        )


def downgrade() -> None:
    conn = op.get_bind()

    # Drop training_pending_items if exists
    table_exists = conn.execute(sa.text(
        "SELECT 1 FROM information_schema.tables "
        "WHERE table_name = 'training_pending_items'"
    )).scalar()

    if table_exists:
        op.drop_table('training_pending_items')

    # Revert attendance constraint (remove preconfirm)
    existing = conn.execute(sa.text(
        "SELECT pg_get_constraintdef(oid) FROM pg_constraint "
        "WHERE conname = 'ck_attendance_status' AND conrelid = 'attendance'::regclass"
    )).scalar()

    if existing and 'preconfirm' in existing:
        op.drop_constraint('ck_attendance_status', 'attendance', type_='check')
        op.create_check_constraint(
            'ck_attendance_status',
            'attendance',
            "presence_status::text = ANY (ARRAY['present', 'absent', 'justified'])",
        )
