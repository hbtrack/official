"""
Script para gerar todas as migrations V1.2 do zero
Execução: python scripts/generate_v1_2_migrations.py
"""
import os
from pathlib import Path

# Diretório de migrations
MIGRATIONS_DIR = Path(__file__).parent.parent / 'backend' / 'db' / 'alembic' / 'versions'

# Lista de migrations a criar
MIGRATIONS = {
    '002_v1_2_lookups': """\"\"\"V1.2 - Create lookup tables (categories, positions, schooling)

Revision ID: 002_v1_2_lookups
Revises: 001_v1_2_core
Create Date: 2025-12-28 04:50:00

REGRAS_SISTEMAS_V1.2.md: R14, R15, RD1, RD2, RDB11, RDB2.1
\"\"\"
from alembic import op
import sqlalchemy as sa

revision = '002_v1_2_lookups'
down_revision = '001_v1_2_core'
branch_labels = None
depends_on = None


def upgrade():
    # CATEGORIES (sem min_age, V1.2)
    # RDB11: Apenas max_age, sem min_age
    # RD1, RD2: Categoria derivada dinamicamente
    op.create_table(
        'categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('max_age', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.PrimaryKeyConstraint('id', name='pk_categories'),
        sa.UniqueConstraint('name', name='ux_categories_name'),
        sa.CheckConstraint('max_age > 0', name='ck_categories_max_age_positive'),
        comment='Categorias esportivas. V1.2: sem min_age, apenas max_age.'
    )

    # DEFENSIVE_POSITIONS
    op.create_table(
        'defensive_positions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(32), nullable=False),
        sa.Column('name', sa.String(64), nullable=False),
        sa.Column('abbreviation', sa.String(10), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.PrimaryKeyConstraint('id', name='pk_defensive_positions'),
        sa.UniqueConstraint('code', name='ux_defensive_positions_code'),
        comment='Posições defensivas. RD13: ID=5 é Goleira.'
    )

    # OFFENSIVE_POSITIONS
    op.create_table(
        'offensive_positions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(32), nullable=False),
        sa.Column('name', sa.String(64), nullable=False),
        sa.Column('abbreviation', sa.String(10), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.PrimaryKeyConstraint('id', name='pk_offensive_positions'),
        sa.UniqueConstraint('code', name='ux_offensive_positions_code'),
        comment='Posições ofensivas.'
    )

    # SCHOOLING_LEVELS
    op.create_table(
        'schooling_levels',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(32), nullable=False),
        sa.Column('name', sa.String(64), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.PrimaryKeyConstraint('id', name='pk_schooling_levels'),
        sa.UniqueConstraint('code', name='ux_schooling_levels_code'),
        comment='Níveis de escolaridade.'
    )


def downgrade():
    op.drop_table('schooling_levels')
    op.drop_table('offensive_positions')
    op.drop_table('defensive_positions')
    op.drop_table('categories')
""",

    '003_v1_2_teams_seasons': f"""\"\"\"V1.2 - Create teams and seasons (inverted FK)

Revision ID: 003_v1_2_teams_seasons
Revises: 002_v1_2_lookups
Create Date: 2025-12-28 05:00:00

REGRAS_SISTEMAS_V1.2.md: R8, R8.1, RDB8, RDB16
V1.2: seasons.team_id (não teams.season_id)
\"\"\"
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '003_v1_2_teams_seasons'
down_revision = '002_v1_2_lookups'
branch_labels = None
depends_on = None


def upgrade():
    # TEAMS (sem season_id, com gender obrigatório)
    # V1.2: equipes não têm season_id
    # RDB16: gender obrigatório, category_id obrigatório
    # TABELAS BANCO.txt: is_our_team, active_from/until
    op.create_table(
        'teams',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(120), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('gender', sa.String(16), nullable=False),
        sa.Column('is_our_team', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('active_from', sa.Date(), nullable=True),
        sa.Column('active_until', sa.Date(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by_user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('deleted_reason', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_teams_organization_id', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], name='fk_teams_category_id', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], name='fk_teams_created_by_user_id', ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id', name='pk_teams'),
        sa.CheckConstraint(
            "gender IN ('masculino', 'feminino', 'misto')",
            name='ck_teams_gender'
        ),
        sa.CheckConstraint(
            "(active_from IS NULL) OR (active_until IS NULL) OR (active_from <= active_until)",
            name='ck_teams_active_dates'
        ),
        sa.CheckConstraint(
            "(deleted_at IS NULL AND deleted_reason IS NULL) OR (deleted_at IS NOT NULL AND deleted_reason IS NOT NULL)",
            name='ck_teams_deleted_reason'
        ),
        comment='Equipes esportivas. V1.2: sem season_id; gender obrigatório.'
    )
    op.create_index('ix_teams_organization_id', 'teams', ['organization_id'])
    op.create_index('ix_teams_category_id', 'teams', ['category_id'])

    # SEASONS (com team_id, FK invertida)
    # V1.2: temporada por equipe + competição
    # R8.1: múltiplas temporadas simultâneas por equipe
    # RDB8: start_date < end_date obrigatório
    op.create_table(
        'seasons',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(120), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('competition_type', sa.String(32), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('canceled_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('interrupted_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by_user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('deleted_reason', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], name='fk_seasons_team_id', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], name='fk_seasons_created_by_user_id', ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id', name='pk_seasons'),
        sa.CheckConstraint(
            'start_date < end_date',
            name='ck_seasons_dates'
        ),
        sa.CheckConstraint(
            "(deleted_at IS NULL AND deleted_reason IS NULL) OR (deleted_at IS NOT NULL AND deleted_reason IS NOT NULL)",
            name='ck_seasons_deleted_reason'
        ),
        comment='Temporadas por equipe. V1.2: team_id FK (não organization_id); múltiplas competições simultâneas.'
    )
    op.create_index('ix_seasons_team_id', 'seasons', ['team_id'])
    op.create_index('ix_seasons_year', 'seasons', ['year'])

    # COMMENT nos campos especiais
    op.execute(\"\"\"
        COMMENT ON COLUMN seasons.canceled_at IS 'RF5.1: Cancelamento pré-início (apenas se sem dados vinculados)';
    \"\"\")
    op.execute(\"\"\"
        COMMENT ON COLUMN seasons.interrupted_at IS 'RF5.2: Interrupção pós-início (força maior)';
    \"\"\")


def downgrade():
    op.drop_table('seasons')
    op.drop_table('teams')
""",
}

def create_migration_file(filename, content):
    """Cria arquivo de migration"""
    filepath = MIGRATIONS_DIR / f"{filename}.py"
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"OK Criado: {filename}.py")

def main():
    print("=> Gerando migrations V1.2...")
    print(f"Diretorio: {MIGRATIONS_DIR}")
    print()

    for filename, content in MIGRATIONS.items():
        create_migration_file(filename, content)

    print()
    print("OK Migrations criadas com sucesso!")
    print()
    print("Proximos passos:")
    print("1. Revisar migrations criadas")
    print("2. Criar migrations restantes (athletes, memberships, treinos, jogos)")
    print("3. Aplicar: alembic upgrade head")

if __name__ == '__main__':
    main()
