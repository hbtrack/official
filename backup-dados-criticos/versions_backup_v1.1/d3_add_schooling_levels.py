"""Add schooling_levels table

Revision ID: d3_schooling_lvl
Revises: d2_offensive_pos
Create Date: 2025-12-27 10:02:00

Cria tabela schooling_levels com os níveis de escolaridade:
- 7º ano Ensino Fundamental
- 8º ano Ensino Fundamental
- 9º ano Ensino Fundamental
- 1º ano Ensino Médio
- 2º ano Ensino Médio
- 3º ano Ensino Médio
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd3_schooling_lvl'
down_revision: Union[str, None] = 'd2_offensive_pos'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Criar tabela schooling_levels
    op.create_table(
        'schooling_levels',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column('name', sa.String(50), nullable=False, unique=True),
        sa.Column('code', sa.String(20), nullable=False, unique=True),
        sa.Column('level_order', sa.Integer(), nullable=False, unique=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    # Inserir dados iniciais
    op.execute("""
        INSERT INTO schooling_levels (id, name, code, level_order, description) VALUES
        (1, '7º ano Ensino Fundamental', '7EF', 7, 'Sétimo ano do Ensino Fundamental'),
        (2, '8º ano Ensino Fundamental', '8EF', 8, 'Oitavo ano do Ensino Fundamental'),
        (3, '9º ano Ensino Fundamental', '9EF', 9, 'Nono ano do Ensino Fundamental'),
        (4, '1º ano Ensino Médio', '1EM', 10, 'Primeiro ano do Ensino Médio'),
        (5, '2º ano Ensino Médio', '2EM', 11, 'Segundo ano do Ensino Médio'),
        (6, '3º ano Ensino Médio', '3EM', 12, 'Terceiro ano do Ensino Médio')
    """)

    # Resetar sequence para próximo ID ser 7
    op.execute("SELECT setval('schooling_levels_id_seq', 6, true)")


def downgrade() -> None:
    op.drop_table('schooling_levels')
