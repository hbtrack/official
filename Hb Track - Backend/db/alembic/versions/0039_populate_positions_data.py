"""populate positions data - offensive and defensive positions

Revision ID: 0039
Revises: 0038
Create Date: 2026-01-17

SCHEMA CANÔNICO - Substitui Migration 4e4b907dc739_populate_positions_data
Ref: SCHEMA_CANONICO_DATABASE.md
"""
from alembic import op


# revision identifiers
revision = '0039'
down_revision = '0038'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Popular tabelas de posições ofensivas e defensivas."""
    
    # =========================================================================
    # OFFENSIVE_POSITIONS (6 registros)
    # =========================================================================
    op.execute("""
        INSERT INTO offensive_positions (id, code, name, abbreviation) VALUES
        (1, 'center_back', 'Armadora Central', 'AC'),
        (2, 'left_back', 'Lateral Esquerda', 'LE'),
        (3, 'right_back', 'Lateral Direita', 'LD'),
        (4, 'left_wing', 'Ponta Esquerda', 'PE'),
        (5, 'right_wing', 'Ponta Direita', 'PD'),
        (6, 'pivot', 'Pivô', 'PI')
        ON CONFLICT (id) DO NOTHING;
    """)
    
    # =========================================================================
    # DEFENSIVE_POSITIONS (5 registros)
    # =========================================================================
    op.execute("""
        INSERT INTO defensive_positions (id, code, name, abbreviation) VALUES
        (1, 'base_defender', 'Defensora Base', 'DB'),
        (2, 'advanced_defender', 'Defensora Avançada', 'DA'),
        (3, 'first_defender', '1ª Defensora', '1D'),
        (4, 'second_defender', '2ª Defensora', '2D'),
        (5, 'goalkeeper', 'Goleira', 'GOL')
        ON CONFLICT (id) DO NOTHING;
    """)


def downgrade() -> None:
    """Remover dados de posições."""
    op.execute("DELETE FROM defensive_positions;")
    op.execute("DELETE FROM offensive_positions;")
