"""training_sessions execution fields

Revision ID: 0069
Revises: 0068
Create Date: 2026-05-25 00:00:00.000000

Evidencia:
  - AR: schema drift — 9 colunas presentes no ORM mas ausentes na VPS
  - Module: TRAINING

Changes:
  1. CREATE TYPE training_execution_outcome_enum (on_time, delayed, canceled, shortened, extended)
  2. ADD COLUMN training_sessions.started_at
  3. ADD COLUMN training_sessions.ended_at
  4. ADD COLUMN training_sessions.duration_actual_minutes
  5. ADD COLUMN training_sessions.execution_outcome (enum, NOT NULL, default 'on_time')
  6. ADD COLUMN training_sessions.delay_minutes
  7. ADD COLUMN training_sessions.cancellation_reason
  8. ADD COLUMN training_sessions.post_review_completed_at
  9. ADD COLUMN training_sessions.post_review_completed_by_user_id (FK -> users.id)
  10. ADD COLUMN training_sessions.post_review_deadline_at
  11. ADD CHECK CONSTRAINT check_training_sessions_execution_outcome
  12. ADD INDEX idx_training_sessions_pending_review_deadline

Rationale:
  ORM model training_session.py referenciava estes campos mas nenhum havia sido
  incluído em alguma migration anterior. Resulta em UndefinedColumnError para
  qualquer query que toque a tabela training_sessions.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0069'
down_revision = '0068'
branch_labels = None
depends_on = None

_ENUM_NAME = 'training_execution_outcome_enum'
_ENUM_VALUES = ('on_time', 'delayed', 'canceled', 'shortened', 'extended')

_CHECK_NAME = 'check_training_sessions_execution_outcome'
_CHECK_EXPR = (
    "execution_outcome = 'on_time'::training_execution_outcome_enum "
    "AND delay_minutes IS NULL AND cancellation_reason IS NULL AND duration_actual_minutes IS NULL "
    "OR execution_outcome = 'delayed'::training_execution_outcome_enum "
    "AND delay_minutes IS NOT NULL AND delay_minutes > 0 AND cancellation_reason IS NULL "
    "OR execution_outcome = 'canceled'::training_execution_outcome_enum "
    "AND cancellation_reason IS NOT NULL AND delay_minutes IS NULL AND duration_actual_minutes IS NULL "
    "OR (execution_outcome = ANY (ARRAY['shortened'::training_execution_outcome_enum, 'extended'::training_execution_outcome_enum])) "
    "AND duration_actual_minutes IS NOT NULL AND duration_actual_minutes > 0 "
    "AND delay_minutes IS NULL AND cancellation_reason IS NULL"
)


def upgrade() -> None:
    # 1. Criar ENUM type (idempotente via DO block)
    op.execute(
        f"""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_type WHERE typname = '{_ENUM_NAME}'
            ) THEN
                CREATE TYPE {_ENUM_NAME} AS ENUM {tuple(_ENUM_VALUES)};
            END IF;
        END
        $$;
        """
    )

    # 2. Adicionar colunas na tabela training_sessions
    op.add_column(
        'training_sessions',
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True)
    )
    op.add_column(
        'training_sessions',
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True)
    )
    op.add_column(
        'training_sessions',
        sa.Column('duration_actual_minutes', sa.Integer(), nullable=True)
    )
    # execution_outcome: NOT NULL com DEFAULT para preencher rows existentes
    op.add_column(
        'training_sessions',
        sa.Column(
            'execution_outcome',
            postgresql.ENUM(*_ENUM_VALUES, name=_ENUM_NAME, create_type=False),
            nullable=False,
            server_default=sa.text("'on_time'::training_execution_outcome_enum"),
        )
    )
    op.add_column(
        'training_sessions',
        sa.Column('delay_minutes', sa.Integer(), nullable=True)
    )
    op.add_column(
        'training_sessions',
        sa.Column('cancellation_reason', sa.Text(), nullable=True)
    )
    op.add_column(
        'training_sessions',
        sa.Column('post_review_completed_at', sa.DateTime(timezone=True), nullable=True)
    )
    op.add_column(
        'training_sessions',
        sa.Column(
            'post_review_completed_by_user_id',
            postgresql.UUID(as_uuid=True),
            nullable=True,
        )
    )
    op.add_column(
        'training_sessions',
        sa.Column('post_review_deadline_at', sa.DateTime(timezone=True), nullable=True)
    )

    # 3. FK para post_review_completed_by_user_id -> users.id
    op.create_foreign_key(
        'training_sessions_post_review_completed_by_user_id_fkey',
        'training_sessions',
        'users',
        ['post_review_completed_by_user_id'],
        ['id'],
    )

    # 4. Check constraint de consistência do outcome
    op.create_check_constraint(
        _CHECK_NAME,
        'training_sessions',
        _CHECK_EXPR,
    )

    # 5. Index parcial para revisões pendentes
    op.create_index(
        'idx_training_sessions_pending_review_deadline',
        'training_sessions',
        ['post_review_deadline_at'],
        unique=False,
        postgresql_where=sa.text("(((status)::text = 'pending_review'::text) AND (deleted_at IS NULL))"),
    )


def downgrade() -> None:
    # Reverso na ordem inversa
    op.drop_index(
        'idx_training_sessions_pending_review_deadline',
        table_name='training_sessions',
    )
    op.drop_constraint(
        _CHECK_NAME,
        'training_sessions',
        type_='check',
    )
    op.drop_constraint(
        'training_sessions_post_review_completed_by_user_id_fkey',
        'training_sessions',
        type_='foreignkey',
    )
    op.drop_column('training_sessions', 'post_review_deadline_at')
    op.drop_column('training_sessions', 'post_review_completed_by_user_id')
    op.drop_column('training_sessions', 'post_review_completed_at')
    op.drop_column('training_sessions', 'cancellation_reason')
    op.drop_column('training_sessions', 'delay_minutes')
    op.drop_column('training_sessions', 'execution_outcome')
    op.drop_column('training_sessions', 'duration_actual_minutes')
    op.drop_column('training_sessions', 'ended_at')
    op.drop_column('training_sessions', 'started_at')

    # Drop do ENUM type somente se não for usado por outra tabela
    op.execute(
        f"""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM pg_type WHERE typname = '{_ENUM_NAME}'
            ) THEN
                DROP TYPE {_ENUM_NAME};
            END IF;
        END
        $$;
        """
    )
