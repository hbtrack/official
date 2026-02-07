"""populate event system data - phases_of_play, advantage_states, event_types

Revision ID: 0038
Revises: 0037
Create Date: 2026-01-17

SCHEMA CANÔNICO - Substitui Migration 2f22a87ff501_populate_event_system_data
Ref: SCHEMA_CANONICO_DATABASE.md
"""
from alembic import op


# revision identifiers
revision = '0038'
down_revision = '0037'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Popular tabelas de configuração do sistema de eventos."""
    
    # =========================================================================
    # PHASES_OF_PLAY (4 registros)
    # =========================================================================
    op.execute("""
        INSERT INTO phases_of_play (code, description) VALUES
        ('attack_positional', 'Ataque Posicional'),
        ('defense', 'Defesa'),
        ('transition_defense', 'Transição Defensiva'),
        ('transition_offense', 'Transição Ofensiva')
        ON CONFLICT (code) DO NOTHING;
    """)
    
    # =========================================================================
    # ADVANTAGE_STATES (3 registros)
    # =========================================================================
    op.execute("""
        INSERT INTO advantage_states (code, delta_players, description) VALUES
        ('even', 0, 'Igualdade numérica (6x6)'),
        ('numerical_inferiority', -1, 'Inferioridade numérica (-1 jogadora)'),
        ('numerical_superiority', 1, 'Superioridade numérica (+1 jogadora)')
        ON CONFLICT (code) DO NOTHING;
    """)
    
    # =========================================================================
    # EVENT_TYPES (11 registros)
    # =========================================================================
    op.execute("""
        INSERT INTO event_types (code, description, is_shot, is_possession_ending) VALUES
        ('exclusion_2min', 'Exclusão 2 Minutos', false, false),
        ('foul', 'Falta', false, false),
        ('goal', 'Gol', true, true),
        ('goalkeeper_save', 'Defesa de Goleira', false, false),
        ('red_card', 'Cartão Vermelho', false, false),
        ('seven_meter', 'Tiro de 7 Metros', true, true),
        ('shot', 'Arremesso', true, false),
        ('substitution', 'Substituição', false, false),
        ('timeout', 'Pedido de Tempo', false, false),
        ('turnover', 'Perda de Bola', false, true),
        ('yellow_card', 'Cartão Amarelo', false, false)
        ON CONFLICT (code) DO NOTHING;
    """)


def downgrade() -> None:
    """Remover dados de configuração do sistema de eventos."""
    op.execute("DELETE FROM event_types;")
    op.execute("DELETE FROM advantage_states;")
    op.execute("DELETE FROM phases_of_play;")
