"""training_sessions status constraint — closed → pending_review

Revision ID: 0070
Revises: 0069
Create Date: 2026-05-25 00:00:00.000000

Evidencia:
  - AR: schema drift — check_training_session_status no DB tem 'closed'
    mas o ORM espera 'pending_review'; INSERT com status='pending_review'
    viola o constraint

Changes:
  1. Data migration: STATUS 'closed' → 'pending_review' em rows existentes
  2. DROP CONSTRAINT check_training_session_status
  3. CREATE CONSTRAINT check_training_session_status com valores corretos:
     draft | scheduled | in_progress | pending_review | readonly

Rationale:
  'closed' foi renomeado para 'pending_review' no ORM mas a migration
  correspondente nunca foi criada. Todos os testes que fazem INSERT com
  status='pending_review' falhavam com CheckViolationError.
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0070'
down_revision = '0069'
branch_labels = None
depends_on = None

_CONSTRAINT_NAME = 'check_training_session_status'

_OLD_VALUES = ('draft', 'scheduled', 'in_progress', 'closed', 'readonly')
_NEW_VALUES = ('draft', 'scheduled', 'in_progress', 'pending_review', 'readonly')

_NEW_EXPR = (
    "status::text = ANY (ARRAY["
    "'draft'::character varying, "
    "'scheduled'::character varying, "
    "'in_progress'::character varying, "
    "'pending_review'::character varying, "
    "'readonly'::character varying"
    "]::text[])"
)

_OLD_EXPR = (
    "status::text = ANY (ARRAY["
    "'draft'::character varying, "
    "'scheduled'::character varying, "
    "'in_progress'::character varying, "
    "'closed'::character varying, "
    "'readonly'::character varying"
    "]::text[])"
)


def upgrade() -> None:
    # 1. Data migration — converter rows com status='closed' antes de
    #    recriar o constraint (evita violation nos dados existentes)
    op.execute(
        "UPDATE training_sessions SET status = 'pending_review' WHERE status = 'closed'"
    )

    # 2. Dropar constraint antigo
    op.drop_constraint(
        _CONSTRAINT_NAME,
        'training_sessions',
        type_='check',
    )

    # 3. Criar constraint atualizado com pending_review
    op.create_check_constraint(
        _CONSTRAINT_NAME,
        'training_sessions',
        _NEW_EXPR,
    )


def downgrade() -> None:
    # Reverter: pending_review → closed; recriar constraint antigo
    op.execute(
        "UPDATE training_sessions SET status = 'closed' WHERE status = 'pending_review'"
    )
    op.drop_constraint(
        _CONSTRAINT_NAME,
        'training_sessions',
        type_='check',
    )
    op.create_check_constraint(
        _CONSTRAINT_NAME,
        'training_sessions',
        _OLD_EXPR,
    )
