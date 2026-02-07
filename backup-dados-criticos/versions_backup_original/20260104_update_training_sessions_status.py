"""Update training sessions with status and microcycle

Revision ID: 20260104_training_status
Revises: 20260104_training_cycles
Create Date: 2026-01-04

Adiciona campos de estado e relacionamento com microciclo em training_sessions:

Novos campos:
1. microcycle_id: FK para training_microcycles (opcional)
2. status: Estado da sessão (draft, in_progress, closed, readonly)
3. closed_at: Timestamp de fechamento
4. closed_by_user_id: Usuário que fechou a sessão
5. deviation_justification: Justificativa de desvio (opcional)
6. planning_deviation_flag: Flag de desvio significativo

Estados da sessão:
- draft: Rascunho (editável livremente)
- in_progress: Em andamento (opcional)
- closed: Fechado (dados validados)
- readonly: Somente leitura (>24h ou admin)

Regras de transição:
- draft → in_progress → closed → readonly
- Fechamento exige: focos > 0 e soma ≤ 120
- Desvio calculado se houver microcycle_id
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '20260104_training_status'
down_revision: Union[str, Sequence[str], None] = '20260104_training_cycles'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Adiciona campos de estado e relacionamento com microciclo.
    """

    # 1. Adicionar coluna microcycle_id (FK para training_microcycles)
    op.add_column(
        'training_sessions',
        sa.Column('microcycle_id', postgresql.UUID(as_uuid=True), nullable=True, comment='FK para microciclo (planejamento semanal)')
    )
    op.create_foreign_key(
        'fk_training_sessions_microcycle',
        'training_sessions',
        'training_microcycles',
        ['microcycle_id'],
        ['id']
    )
    op.create_index('idx_training_sessions_microcycle', 'training_sessions', ['microcycle_id'])

    # 2. Adicionar coluna status
    op.add_column(
        'training_sessions',
        sa.Column('status', sa.String(), nullable=True, comment="Estado: draft, in_progress, closed, readonly")
    )

    # Atualizar registros existentes para 'draft' (qualquer valor que não seja os permitidos)
    op.execute("UPDATE training_sessions SET status = 'draft' WHERE status IS NULL OR status NOT IN ('draft', 'in_progress', 'closed', 'readonly')")

    # Agora tornar NOT NULL
    op.alter_column('training_sessions', 'status', nullable=False, server_default="'draft'")

    # Criar constraint
    op.create_check_constraint(
        'check_training_session_status',
        'training_sessions',
        "status IN ('draft', 'in_progress', 'closed', 'readonly')"
    )
    op.create_index('idx_training_sessions_status', 'training_sessions', ['status'])

    # 3. Adicionar colunas de fechamento
    op.add_column(
        'training_sessions',
        sa.Column('closed_at', sa.DateTime(timezone=True), nullable=True, comment='Timestamp de fechamento')
    )
    op.add_column(
        'training_sessions',
        sa.Column('closed_by_user_id', postgresql.UUID(as_uuid=True), nullable=True, comment='Usuário que fechou a sessão')
    )
    op.create_foreign_key(
        'fk_training_sessions_closed_by',
        'training_sessions',
        'users',
        ['closed_by_user_id'],
        ['id']
    )

    # 4. Adicionar colunas de desvio
    op.add_column(
        'training_sessions',
        sa.Column('deviation_justification', sa.Text(), nullable=True, comment='Justificativa de desvio em relação ao planejamento')
    )
    op.add_column(
        'training_sessions',
        sa.Column('planning_deviation_flag', sa.Boolean(), nullable=False, server_default='false', comment='Flag de desvio significativo (≥20pts ou ≥30% agregado)')
    )
    op.create_index('idx_training_sessions_deviation_flag', 'training_sessions', ['planning_deviation_flag'])


def downgrade() -> None:
    """
    Remove campos de estado e relacionamento com microciclo.
    """
    # Remover índices
    op.drop_index('idx_training_sessions_deviation_flag', 'training_sessions')
    op.drop_index('idx_training_sessions_status', 'training_sessions')
    op.drop_index('idx_training_sessions_microcycle', 'training_sessions')

    # Remover constraints
    op.drop_constraint('check_training_session_status', 'training_sessions')
    op.drop_constraint('fk_training_sessions_closed_by', 'training_sessions')
    op.drop_constraint('fk_training_sessions_microcycle', 'training_sessions')

    # Remover colunas
    op.drop_column('training_sessions', 'planning_deviation_flag')
    op.drop_column('training_sessions', 'deviation_justification')
    op.drop_column('training_sessions', 'closed_by_user_id')
    op.drop_column('training_sessions', 'closed_at')
    op.drop_column('training_sessions', 'status')
    op.drop_column('training_sessions', 'microcycle_id')
