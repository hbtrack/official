"""initial schema (consolidated)

Revision ID: 4af09f9d46a0
Revises:
Create Date: 2025-12-24

Migration inicial consolidada que aplica todo o schema do banco de dados
a partir do arquivo initial_schema.sql localizado ao lado desta migration.

Este arquivo contém:
- CREATE EXTENSION (pgcrypto, btree_gist)
- CREATE TABLE (26 tabelas: athletes, training_sessions, attendance, etc.)
- CREATE FUNCTION (38 funções: triggers, helpers, validações)
- CREATE TRIGGER (40+ triggers)
- CREATE VIEW (2 views: v_session_athlete_dashboard, v_training_session_summary)
- COMMENT ON FUNCTION (31 documentações)
- Seed inicial: roles (superadmin, dirigente, coordenador, treinador, atleta)
- Seed inicial: super admin (superadmin@seed.local)

Conforme RAG V1.1 com correções aplicadas:
- R13 V1.1: trg_athlete_state_dispense_membership encerra team_registrations
- R38: trg_membership_require_team DEFERRABLE
- RDB3: v_seasons_with_status usa UTC
"""
from typing import Sequence, Union
from pathlib import Path

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4af09f9d46a0'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Aplica todo o schema inicial a partir do arquivo SQL"""

    # Localizar o arquivo initial_schema.sql ao lado desta migration
    migration_dir = Path(__file__).parent
    sql_file = migration_dir / "initial_schema.sql"

    if not sql_file.exists():
        raise FileNotFoundError(
            f"Arquivo SQL não encontrado: {sql_file}\n"
            f"Esperado em: {migration_dir}/initial_schema.sql"
        )

    # Ler o SQL
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    # Executar usando conexão raw do psycopg2 para permitir multi-statement SQL
    connection = op.get_bind()

    # Usar conexão raw para executar todo o SQL
    raw_connection = connection.connection
    cursor = raw_connection.cursor()
    try:
        cursor.execute(sql_content)
        raw_connection.commit()
    except Exception as e:
        raw_connection.rollback()
        raise
    finally:
        cursor.close()


def downgrade() -> None:
    """Remove todo o schema (DROP CASCADE do schema public)"""

    # ATENÇÃO: Este downgrade é DESTRUTIVO e remove TODO o schema
    # Só deve ser usado em desenvolvimento/testes

    op.execute(sa.text("""
        DROP SCHEMA public CASCADE;
        CREATE SCHEMA public;
        GRANT ALL ON SCHEMA public TO public;
    """))
