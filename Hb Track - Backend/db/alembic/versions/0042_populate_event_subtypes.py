"""Populate event_subtypes with canonical data

Revision ID: 0042
Revises: 0041
Create Date: 2026-01-17

Popula tabela event_subtypes com 21 registros canônicos do backup CSV:
- 2 tipos de falta
- 11 tipos de arremesso
- 6 tipos de perda de bola
- 2 disciplinares
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0042'
down_revision = '0041'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Popula event_subtypes com 21 registros canônicos."""
    
    op.execute("""
        -- Limpar dados existentes (caso haja inconsistências)
        DELETE FROM event_subtypes;
        
        -- Inserir 21 event_subtypes canônicos do backup
        -- Tabela usa code (VARCHAR) como PK, não ID numérico
        INSERT INTO event_subtypes (code, event_type_code, description) VALUES
        
        -- FALTAS (2 registros)
        ('defensive_foul', 'foul', 'Falta Defensiva'),
        ('offensive_foul', 'foul', 'Falta Ofensiva'),
        
        -- ARREMESSOS (13 registros)
        ('shot_6m', 'shot', 'Arremesso 6m'),
        ('shot_9m', 'shot', 'Arremesso 9m'),
        ('shot_counterattack', 'shot', 'Arremesso em Contra-Ataque'),
        ('shot_pivot', 'shot', 'Arremesso de Pivô'),
        ('shot_left_wing', 'shot', 'Arremesso de Ponta Esquerda'),
        ('shot_right_wing', 'shot', 'Arremesso de Ponta Direita'),
        ('shot_left_back', 'shot', 'Arremesso de Lateral Esquerda'),
        ('shot_right_back', 'shot', 'Arremesso de Lateral Direita'),
        ('shot_center_back', 'shot', 'Arremesso de Central'),
        ('shot_jumping', 'shot', 'Arremesso em suspensão'),
        ('shot_grounded', 'shot', 'Arremesso em Apoio'),
        
        -- PERDAS DE BOLA (6 registros)
        ('turnover_dribble', 'turnover', 'Perda de Bola - Dois Dribles'),
        ('turnover_offensive_foul', 'turnover', 'Perda de Bola - Falta de Ataque'),
        ('turnover_pass', 'turnover', 'Perda de Bola - Passe Errado'),
        ('turnover_steps', 'turnover', 'Perda de Bola - Passos'),
        ('turnover_invasion', 'turnover', 'Perda de Bola - Invasão de Área'),
        ('turnover_timeout', 'turnover', 'Perda de Bola - Mais de 3 seg'),
        
        -- DISCIPLINARES (2 registros)
        ('substitution_wrong', 'exclusion_2min', 'Erro de troca - 2 minutos'),
        ('three_exlusions_2min', 'red_card', 'Três exlusões por 2 min');
    """)


def downgrade() -> None:
    """Remove event_subtypes populados."""
    
    op.execute("""
        DELETE FROM event_subtypes WHERE code IN (
            'defensive_foul', 'offensive_foul',
            'shot_6m', 'shot_9m', 'shot_counterattack', 'shot_pivot',
            'shot_left_wing', 'shot_right_wing', 'shot_left_back',
            'shot_right_back', 'shot_center_back', 'shot_jumping', 'shot_grounded',
            'turnover_dribble', 'turnover_offensive_foul', 'turnover_pass',
            'turnover_steps', 'turnover_invasion', 'turnover_timeout',
            'substitution_wrong', 'three_exlusions_2min'
        );
    """)
