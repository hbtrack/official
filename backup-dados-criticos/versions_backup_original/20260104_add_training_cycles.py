"""Add training cycles and microcycles tables

Revision ID: 20260104_training_cycles
Revises: 20260104_training_focus
Create Date: 2026-01-04

Adiciona estrutura de planejamento de treinos conforme TRAINNIG.MD:

1. training_cycles: Macrociclos e Mesociclos
   - Macrociclo: temporada completa ou fase longa
   - Mesociclo: 4-6 semanas (pertence a um macrociclo)

2. training_microcycles: Microciclos (planejamento semanal)
   - Armazena focos planejados (intenção)
   - Relaciona-se com mesociclo (opcional)
   - Base para cálculo de desvios (planejado vs executado)

Regras de integridade:
- Macrociclo não pode ter parent_cycle_id
- Mesociclo deve ter parent_cycle_id (FK para macrociclo)
- Microciclo pode ter cycle_id (FK para mesociclo)
- start_date < end_date
- Soma dos focos planejados ≤ 120
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '20260104_training_cycles'
down_revision: Union[str, Sequence[str], None] = '20260104_training_focus'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Cria tabelas de ciclos e microciclos de treinamento.
    """

    # 1. Criar tabela training_cycles (macrociclos e mesociclos)
    op.create_table(
        'training_cycles',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('type', sa.String(), nullable=False, comment="Tipo: 'macro' ou 'meso'"),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('objective', sa.Text(), nullable=True, comment='Objetivo estratégico do ciclo'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('status', sa.String(), nullable=False, server_default="'active'", comment="Status: active, completed, cancelled"),
        sa.Column('parent_cycle_id', postgresql.UUID(as_uuid=True), nullable=True, comment='FK para macrociclo (apenas mesociclos)'),
        sa.Column('created_by_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_reason', sa.Text(), nullable=True),

        # Check constraints
        sa.CheckConstraint("type IN ('macro', 'meso')", name='check_cycle_type'),
        sa.CheckConstraint("status IN ('active', 'completed', 'cancelled')", name='check_cycle_status'),
        sa.CheckConstraint('start_date < end_date', name='check_cycle_dates'),

        # Foreign keys
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ),
        sa.ForeignKeyConstraint(['parent_cycle_id'], ['training_cycles.id'], ),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ),

        sa.PrimaryKeyConstraint('id')
    )

    # Índices para performance
    op.create_index('idx_training_cycles_org', 'training_cycles', ['organization_id'])
    op.create_index('idx_training_cycles_team', 'training_cycles', ['team_id'])
    op.create_index('idx_training_cycles_dates', 'training_cycles', ['start_date', 'end_date'])
    op.create_index('idx_training_cycles_parent', 'training_cycles', ['parent_cycle_id'])
    op.create_index('idx_training_cycles_type', 'training_cycles', ['type'])
    op.create_index('idx_training_cycles_status', 'training_cycles', ['status'])

    # 2. Criar tabela training_microcycles (planejamento semanal)
    op.create_table(
        'training_microcycles',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('week_start', sa.Date(), nullable=False, comment='Início da semana (seg)'),
        sa.Column('week_end', sa.Date(), nullable=False, comment='Fim da semana (dom)'),
        sa.Column('cycle_id', postgresql.UUID(as_uuid=True), nullable=True, comment='FK para mesociclo'),

        # Focos planejados (percentuais 0-100)
        sa.Column('planned_focus_attack_positional_pct', sa.Numeric(5, 2), nullable=True, comment='Percentual planejado de foco em ataque posicionado (0-100)'),
        sa.Column('planned_focus_defense_positional_pct', sa.Numeric(5, 2), nullable=True, comment='Percentual planejado de foco em defesa posicionada (0-100)'),
        sa.Column('planned_focus_transition_offense_pct', sa.Numeric(5, 2), nullable=True, comment='Percentual planejado de foco em transição ofensiva (0-100)'),
        sa.Column('planned_focus_transition_defense_pct', sa.Numeric(5, 2), nullable=True, comment='Percentual planejado de foco em transição defensiva (0-100)'),
        sa.Column('planned_focus_attack_technical_pct', sa.Numeric(5, 2), nullable=True, comment='Percentual planejado de foco em ataque técnico (0-100)'),
        sa.Column('planned_focus_defense_technical_pct', sa.Numeric(5, 2), nullable=True, comment='Percentual planejado de foco em defesa técnica (0-100)'),
        sa.Column('planned_focus_physical_pct', sa.Numeric(5, 2), nullable=True, comment='Percentual planejado de foco em treino físico (0-100)'),

        sa.Column('planned_weekly_load', sa.Integer(), nullable=True, comment='Carga planejada da semana (RPE × minutos)'),
        sa.Column('microcycle_type', sa.String(), nullable=True, comment='Tipo: carga_alta, recuperacao, pre_jogo, etc.'),
        sa.Column('notes', sa.Text(), nullable=True),

        sa.Column('created_by_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_reason', sa.Text(), nullable=True),

        # Check constraints
        sa.CheckConstraint('week_start < week_end', name='check_microcycle_dates'),

        # Foreign keys
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ),
        sa.ForeignKeyConstraint(['cycle_id'], ['training_cycles.id'], ),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ),

        sa.PrimaryKeyConstraint('id')
    )

    # Índices para performance
    op.create_index('idx_training_microcycles_org', 'training_microcycles', ['organization_id'])
    op.create_index('idx_training_microcycles_team', 'training_microcycles', ['team_id'])
    op.create_index('idx_training_microcycles_cycle', 'training_microcycles', ['cycle_id'])
    op.create_index('idx_training_microcycles_dates', 'training_microcycles', ['week_start', 'week_end'])


def downgrade() -> None:
    """
    Remove tabelas de ciclos e microciclos.
    """
    op.drop_table('training_microcycles')
    op.drop_table('training_cycles')
