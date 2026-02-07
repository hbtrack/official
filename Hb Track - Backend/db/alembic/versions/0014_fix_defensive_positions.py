"""V1.2 - Corrigir nomes das posições defensivas

Revision ID: 013_fix_defensive_positions
Revises: 012_canonical
Create Date: 2025-12-31

Corrige os nomes das posições defensivas para a nomenclatura correta do handebol brasileiro:
- Defensora Base
- Defensora Avançada
- 1ª Defensora
- 2ª Defensora
- Goleira (ID=5, especial conforme RD13)

Também garante que as posições ofensivas estejam com os nomes corretos.
"""
from alembic import op
import sqlalchemy as sa

revision = '0014'
down_revision = '0013'
branch_labels = None
depends_on = None


def upgrade():
    """Atualiza os nomes das posições para a nomenclatura correta."""
    
    # Atualizar posições defensivas
    op.execute("""
        UPDATE defensive_positions SET 
            code = 'base_defender', 
            name = 'Defensora Base', 
            abbreviation = 'DB'
        WHERE id = 1
    """)
    
    op.execute("""
        UPDATE defensive_positions SET 
            code = 'advanced_defender', 
            name = 'Defensora Avançada', 
            abbreviation = 'DA'
        WHERE id = 2
    """)
    
    op.execute("""
        UPDATE defensive_positions SET 
            code = 'first_defender', 
            name = '1ª Defensora', 
            abbreviation = '1D'
        WHERE id = 3
    """)
    
    op.execute("""
        UPDATE defensive_positions SET 
            code = 'second_defender', 
            name = '2ª Defensora', 
            abbreviation = '2D'
        WHERE id = 4
    """)
    
    op.execute("""
        UPDATE defensive_positions SET 
            code = 'goalkeeper', 
            name = 'Goleira', 
            abbreviation = 'GOL'
        WHERE id = 5
    """)
    
    # Garantir posições ofensivas com nomes corretos
    op.execute("""
        UPDATE offensive_positions SET 
            code = 'center_back', 
            name = 'Armadora Central', 
            abbreviation = 'AC'
        WHERE id = 1
    """)
    
    op.execute("""
        UPDATE offensive_positions SET 
            code = 'left_back', 
            name = 'Lateral Esquerda', 
            abbreviation = 'LE'
        WHERE id = 2
    """)
    
    op.execute("""
        UPDATE offensive_positions SET 
            code = 'right_back', 
            name = 'Lateral Direita', 
            abbreviation = 'LD'
        WHERE id = 3
    """)
    
    op.execute("""
        UPDATE offensive_positions SET 
            code = 'left_wing', 
            name = 'Ponta Esquerda', 
            abbreviation = 'PE'
        WHERE id = 4
    """)
    
    op.execute("""
        UPDATE offensive_positions SET 
            code = 'right_wing', 
            name = 'Ponta Direita', 
            abbreviation = 'PD'
        WHERE id = 5
    """)
    
    op.execute("""
        UPDATE offensive_positions SET 
            code = 'pivot', 
            name = 'Pivô', 
            abbreviation = 'PI'
        WHERE id = 6
    """)


def downgrade():
    """Reverte para os nomes antigos (incorretos)."""
    
    # Reverter posições defensivas para nomes antigos
    op.execute("""
        UPDATE defensive_positions SET 
            code = 'central_defender', 
            name = 'Armadora Central Defensiva', 
            abbreviation = 'ACD'
        WHERE id = 1
    """)
    
    op.execute("""
        UPDATE defensive_positions SET 
            code = 'left_back_defender', 
            name = 'Lateral Esquerda Defensiva', 
            abbreviation = 'LED'
        WHERE id = 2
    """)
    
    op.execute("""
        UPDATE defensive_positions SET 
            code = 'right_back_defender', 
            name = 'Lateral Direita Defensiva', 
            abbreviation = 'LDD'
        WHERE id = 3
    """)
    
    op.execute("""
        UPDATE defensive_positions SET 
            code = 'pivot_defender', 
            name = 'Pivô Defensiva', 
            abbreviation = 'PD'
        WHERE id = 4
    """)
    
    op.execute("""
        UPDATE defensive_positions SET 
            code = 'goalkeeper', 
            name = 'Goleira', 
            abbreviation = 'GOL'
        WHERE id = 5
    """)
