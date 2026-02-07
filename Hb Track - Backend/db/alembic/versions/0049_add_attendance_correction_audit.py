"""Add correction audit fields to attendance table

Revision ID: 0049_attendance_correction
Revises: 0048
Create Date: 2026-01-21

Step 5 - Plano de Refatoração:
Adicionar campos de auditoria para correções de presença:
- correction_by_user_id: UUID do usuário que fez a correção
- correction_at: timestamp da correção

Mantém created_by_user_id intacto para preservar autor original.
Quando source='correction', estes campos são preenchidos.

Também adiciona índice para consultas de auditoria.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '0049'
down_revision = '0048'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Adiciona campos de auditoria para correções de presença.
    """

    # Adicionar coluna correction_by_user_id
    op.add_column(
        'attendance',
        sa.Column(
            'correction_by_user_id',
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey('users.id', ondelete='SET NULL'),
            nullable=True,
            comment='ID do usuário que realizou a correção (quando source=correction)'
        )
    )

    # Adicionar coluna correction_at
    op.add_column(
        'attendance',
        sa.Column(
            'correction_at',
            sa.DateTime(timezone=True),
            nullable=True,
            comment='Timestamp da correção (quando source=correction)'
        )
    )

    # Criar índice para consultas de auditoria
    op.create_index(
        'idx_attendance_corrections',
        'attendance',
        ['correction_by_user_id', 'correction_at'],
        postgresql_where=sa.text("source = 'correction'")
    )

    # Adicionar CHECK constraint para garantir consistência
    op.execute("""
        ALTER TABLE attendance
        ADD CONSTRAINT ck_attendance_correction_fields
        CHECK (
            (source != 'correction') OR
            (source = 'correction' AND correction_by_user_id IS NOT NULL AND correction_at IS NOT NULL)
        );
    """)

    # Comentário na constraint
    op.execute("""
        COMMENT ON CONSTRAINT ck_attendance_correction_fields ON attendance IS
        'Garante que correções têm correction_by_user_id e correction_at preenchidos';
    """)


def downgrade() -> None:
    """
    Remove campos de auditoria.
    """

    # Remover CHECK constraint
    op.execute("""
        ALTER TABLE attendance
        DROP CONSTRAINT IF EXISTS ck_attendance_correction_fields;
    """)

    # Remover índice
    op.drop_index('idx_attendance_corrections', table_name='attendance')

    # Remover colunas
    op.drop_column('attendance', 'correction_at')
    op.drop_column('attendance', 'correction_by_user_id')
