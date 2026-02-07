"""Add defensive_positions table

Revision ID: d1_defensive_pos
Revises: c1a2b3d4e5f6
Create Date: 2025-12-27 10:00:00

Cria tabela defensive_positions com as posições defensivas do handebol:
- 1ª Defensora
- 2ª Defensora
- Defensora Base
- Defensora Avançada
- Goleira
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd1_defensive_pos'
down_revision: Union[str, None] = 'c1a2b3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Criar tabela defensive_positions
    op.create_table(
        'defensive_positions',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column('name', sa.String(50), nullable=False, unique=True),
        sa.Column('code', sa.String(20), nullable=False, unique=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    # Inserir dados iniciais
    op.execute("""
        INSERT INTO defensive_positions (id, name, code, description) VALUES
        (1, '1ª Defensora', 'DEF1', 'Primeira linha de defesa'),
        (2, '2ª Defensora', 'DEF2', 'Segunda linha de defesa'),
        (3, 'Defensora Base', 'DEF_BASE', 'Defensora posicionada na base'),
        (4, 'Defensora Avançada', 'DEF_AV', 'Defensora posicionada avançada'),
        (5, 'Goleira', 'GOLEIRA', 'Goleira - posição exclusivamente defensiva')
    """)

    # Resetar sequence para próximo ID ser 6
    op.execute("SELECT setval('defensive_positions_id_seq', 5, true)")


def downgrade() -> None:
    op.drop_table('defensive_positions')
