"""V1.2 - Create lookup tables (categories, positions, schooling)

Revision ID: 002_v1_2_lookups
Revises: 001_v1_2_core
Create Date: 2025-12-28 04:50:00

REGRAS_SISTEMAS_V1.2.md: R14, R15, RD1, RD2, RDB11, RDB2.1
"""
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
