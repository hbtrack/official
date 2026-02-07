"""Add offensive_positions table

Revision ID: d2_offensive_pos
Revises: d1_defensive_pos
Create Date: 2025-12-27 10:01:00

Cria tabela offensive_positions com as posições ofensivas do handebol:
- Ponta Esquerda
- Ponta Direita
- Pivô
- Lateral Esquerda
- Lateral Direita
- Armadora Central
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd2_offensive_pos'
down_revision: Union[str, None] = 'd1_defensive_pos'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Criar tabela offensive_positions
    op.create_table(
        'offensive_positions',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column('name', sa.String(50), nullable=False, unique=True),
        sa.Column('code', sa.String(20), nullable=False, unique=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    # Inserir dados iniciais
    op.execute("""
        INSERT INTO offensive_positions (id, name, code, description) VALUES
        (1, 'Ponta Esquerda', 'PE', 'Ponta esquerda - extremidade do ataque'),
        (2, 'Ponta Direita', 'PD', 'Ponta direita - extremidade do ataque'),
        (3, 'Pivô', 'PIVO', 'Pivô - jogadora de área'),
        (4, 'Lateral Esquerda', 'LE', 'Lateral esquerda - meio do ataque'),
        (5, 'Lateral Direita', 'LD', 'Lateral direita - meio do ataque'),
        (6, 'Armadora Central', 'ARM', 'Armadora central - organizadora do jogo')
    """)

    # Resetar sequence para próximo ID ser 7
    op.execute("SELECT setval('offensive_positions_id_seq', 6, true)")


def downgrade() -> None:
    op.drop_table('offensive_positions')
