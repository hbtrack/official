"""0001 - Prepare database (install extensions)

Revision ID: 000_v1_2_prepare_database
Revises:
Create Date: 2025-12-28 04:00:00

REGRAS_SISTEMAS_V1.2.md: RDB1 - PostgreSQL 17 com pgcrypto
"""
from alembic import op
import sqlalchemy as sa

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Instala extensão pgcrypto para gen_random_uuid()
    op.execute('CREATE EXTENSION IF NOT EXISTS pgcrypto;')

    # Comentário no banco
    op.execute("""
        COMMENT ON EXTENSION pgcrypto IS
        'RDB1: Extensão para funções criptográficas, incluindo gen_random_uuid() usado em PKs UUID.';
    """)


def downgrade():
    # Não remove pgcrypto no downgrade (pode estar sendo usado por outras aplicações)
    pass
