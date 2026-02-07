"""fix schooling levels data - correct educational levels

Revision ID: 0040
Revises: 0039
Create Date: 2026-01-17

SCHEMA CANÔNICO - Substitui Migration c404617118bb_fix_schooling_levels_data
Ref: SCHEMA_CANONICO_DATABASE.md
"""
from alembic import op


# revision identifiers
revision = '0040'
down_revision = '0039'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Corrigir dados de níveis de escolaridade."""
    
    # Limpar dados antigos
    op.execute("DELETE FROM schooling_levels;")
    
    # =========================================================================
    # SCHOOLING_LEVELS (6 registros)
    # =========================================================================
    op.execute("""
        INSERT INTO schooling_levels (id, code, name) VALUES
        (1, 'elementary_incomplete', 'Ensino Fundamental Incompleto'),
        (2, 'elementary_complete', 'Ensino Fundamental Completo'),
        (3, 'high_school_incomplete', 'Ensino Médio Incompleto'),
        (4, 'high_school_complete', 'Ensino Médio Completo'),
        (5, 'higher_education_incomplete', 'Ensino Superior Incompleto'),
        (6, 'higher_education_complete', 'Ensino Superior Completo');
    """)


def downgrade() -> None:
    """Reverter para dados antigos."""
    op.execute("DELETE FROM schooling_levels;")
