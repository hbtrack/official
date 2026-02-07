"""Add training session focus columns

Revision ID: 20260104_training_focus
Revises: 2026010101_reports_idx
Create Date: 2026-01-04

Adiciona 7 colunas de foco de treino para análise estratégica de equipes.
Suporta correlação treino → jogo em /statistics/teams.

Focos de treino do handebol:
1. Ataque Posicionado
2. Defesa Posicionada
3. Transição Ofensiva
4. Transição Defensiva
5. Ataque Técnico
6. Defesa Técnica
7. Treino Físico

Regras de integridade:
- Cada campo: 0.00 a 100.00
- Soma permitida até 120% (treinos híbridos)
- Pelo menos um foco > 0 quando sessão fechada
- Nullable (sessões antigas não terão esses dados)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260104_training_focus'
down_revision: Union[str, Sequence[str], None] = ('2026010101_reports_idx', 'f62ede3bab26')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Adiciona colunas de foco de treino na tabela training_sessions.
    
    Cada coluna representa o percentual aproximado do tempo dedicado
    a cada foco específico de treinamento de handebol.
    """
    
    # Adicionar 7 colunas de foco (percentuais)
    op.add_column('training_sessions', 
        sa.Column('focus_attack_positional_pct', sa.NUMERIC(precision=5, scale=2), nullable=True,
                  comment='Percentual de foco em ataque posicionado (0-100)')
    )
    
    op.add_column('training_sessions',
        sa.Column('focus_defense_positional_pct', sa.NUMERIC(precision=5, scale=2), nullable=True,
                  comment='Percentual de foco em defesa posicionada (0-100)')
    )
    
    op.add_column('training_sessions',
        sa.Column('focus_transition_offense_pct', sa.NUMERIC(precision=5, scale=2), nullable=True,
                  comment='Percentual de foco em transição ofensiva (0-100)')
    )
    
    op.add_column('training_sessions',
        sa.Column('focus_transition_defense_pct', sa.NUMERIC(precision=5, scale=2), nullable=True,
                  comment='Percentual de foco em transição defensiva (0-100)')
    )
    
    op.add_column('training_sessions',
        sa.Column('focus_attack_technical_pct', sa.NUMERIC(precision=5, scale=2), nullable=True,
                  comment='Percentual de foco em ataque técnico (0-100)')
    )
    
    op.add_column('training_sessions',
        sa.Column('focus_defense_technical_pct', sa.NUMERIC(precision=5, scale=2), nullable=True,
                  comment='Percentual de foco em defesa técnica (0-100)')
    )
    
    op.add_column('training_sessions',
        sa.Column('focus_physical_pct', sa.NUMERIC(precision=5, scale=2), nullable=True,
                  comment='Percentual de foco em treino físico (0-100)')
    )
    
    # Adicionar constraint para validar valores entre 0 e 100
    op.create_check_constraint(
        'ck_training_sessions_focus_attack_positional_range',
        'training_sessions',
        'focus_attack_positional_pct IS NULL OR (focus_attack_positional_pct >= 0 AND focus_attack_positional_pct <= 100)'
    )
    
    op.create_check_constraint(
        'ck_training_sessions_focus_defense_positional_range',
        'training_sessions',
        'focus_defense_positional_pct IS NULL OR (focus_defense_positional_pct >= 0 AND focus_defense_positional_pct <= 100)'
    )
    
    op.create_check_constraint(
        'ck_training_sessions_focus_transition_offense_range',
        'training_sessions',
        'focus_transition_offense_pct IS NULL OR (focus_transition_offense_pct >= 0 AND focus_transition_offense_pct <= 100)'
    )
    
    op.create_check_constraint(
        'ck_training_sessions_focus_transition_defense_range',
        'training_sessions',
        'focus_transition_defense_pct IS NULL OR (focus_transition_defense_pct >= 0 AND focus_transition_defense_pct <= 100)'
    )
    
    op.create_check_constraint(
        'ck_training_sessions_focus_attack_technical_range',
        'training_sessions',
        'focus_attack_technical_pct IS NULL OR (focus_attack_technical_pct >= 0 AND focus_attack_technical_pct <= 100)'
    )
    
    op.create_check_constraint(
        'ck_training_sessions_focus_defense_technical_range',
        'training_sessions',
        'focus_defense_technical_pct IS NULL OR (focus_defense_technical_pct >= 0 AND focus_defense_technical_pct <= 100)'
    )
    
    op.create_check_constraint(
        'ck_training_sessions_focus_physical_range',
        'training_sessions',
        'focus_physical_pct IS NULL OR (focus_physical_pct >= 0 AND focus_physical_pct <= 100)'
    )
    
    # Constraint para validar soma total (máx 120% para treinos híbridos)
    op.create_check_constraint(
        'ck_training_sessions_focus_total_sum',
        'training_sessions',
        '''
        (
            COALESCE(focus_attack_positional_pct, 0) +
            COALESCE(focus_defense_positional_pct, 0) +
            COALESCE(focus_transition_offense_pct, 0) +
            COALESCE(focus_transition_defense_pct, 0) +
            COALESCE(focus_attack_technical_pct, 0) +
            COALESCE(focus_defense_technical_pct, 0) +
            COALESCE(focus_physical_pct, 0)
        ) <= 120
        '''
    )
    
    # Adicionar comentário na tabela documentando o uso
    op.execute("""
        COMMENT ON COLUMN training_sessions.focus_attack_positional_pct IS 
        'Percentual aproximado (0-100) do tempo dedicado ao foco Ataque Posicionado. Usado em análise estratégica /statistics/teams.'
    """)
    
    op.execute("""
        COMMENT ON COLUMN training_sessions.focus_defense_positional_pct IS 
        'Percentual aproximado (0-100) do tempo dedicado ao foco Defesa Posicionada. Usado em análise estratégica /statistics/teams.'
    """)
    
    op.execute("""
        COMMENT ON COLUMN training_sessions.focus_transition_offense_pct IS 
        'Percentual aproximado (0-100) do tempo dedicado ao foco Transição Ofensiva. Usado em análise estratégica /statistics/teams.'
    """)
    
    op.execute("""
        COMMENT ON COLUMN training_sessions.focus_transition_defense_pct IS 
        'Percentual aproximado (0-100) do tempo dedicado ao foco Transição Defensiva. Usado em análise estratégica /statistics/teams.'
    """)
    
    op.execute("""
        COMMENT ON COLUMN training_sessions.focus_attack_technical_pct IS 
        'Percentual aproximado (0-100) do tempo dedicado ao foco Ataque Técnico. Usado em análise estratégica /statistics/teams.'
    """)
    
    op.execute("""
        COMMENT ON COLUMN training_sessions.focus_defense_technical_pct IS 
        'Percentual aproximado (0-100) do tempo dedicado ao foco Defesa Técnica. Usado em análise estratégica /statistics/teams.'
    """)
    
    op.execute("""
        COMMENT ON COLUMN training_sessions.focus_physical_pct IS 
        'Percentual aproximado (0-100) do tempo dedicado ao foco Treino Físico. Usado em análise estratégica /statistics/teams.'
    """)


def downgrade() -> None:
    """
    Remove colunas de foco de treino.
    """
    
    # Remover constraints
    op.drop_constraint('ck_training_sessions_focus_total_sum', 'training_sessions', type_='check')
    op.drop_constraint('ck_training_sessions_focus_physical_range', 'training_sessions', type_='check')
    op.drop_constraint('ck_training_sessions_focus_defense_technical_range', 'training_sessions', type_='check')
    op.drop_constraint('ck_training_sessions_focus_attack_technical_range', 'training_sessions', type_='check')
    op.drop_constraint('ck_training_sessions_focus_transition_defense_range', 'training_sessions', type_='check')
    op.drop_constraint('ck_training_sessions_focus_transition_offense_range', 'training_sessions', type_='check')
    op.drop_constraint('ck_training_sessions_focus_defense_positional_range', 'training_sessions', type_='check')
    op.drop_constraint('ck_training_sessions_focus_attack_positional_range', 'training_sessions', type_='check')
    
    # Remover colunas
    op.drop_column('training_sessions', 'focus_physical_pct')
    op.drop_column('training_sessions', 'focus_defense_technical_pct')
    op.drop_column('training_sessions', 'focus_attack_technical_pct')
    op.drop_column('training_sessions', 'focus_transition_defense_pct')
    op.drop_column('training_sessions', 'focus_transition_offense_pct')
    op.drop_column('training_sessions', 'focus_defense_positional_pct')
    op.drop_column('training_sessions', 'focus_attack_positional_pct')
