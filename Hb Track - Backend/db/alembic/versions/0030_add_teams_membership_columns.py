"""Add season_id, coach_membership_id, created_by_membership_id to teams

Revision ID: 0030_add_teams_membership
Revises: 0029_add_athlete_org_id
Create Date: 2026-01-13

Adiciona colunas necessárias para funcionalidade completa de teams:
- season_id: vincula team a uma temporada específica
- coach_membership_id: RF7 - atribuição de treinador principal
- created_by_membership_id: auditoria de criação via membership
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '0030'
down_revision: Union[str, Sequence[str], None] = '0029'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Adiciona season_id, coach_membership_id e created_by_membership_id à tabela teams."""
    
    # Adicionar coluna season_id (nullable - teams podem existir sem temporada definida)
    op.add_column(
        'teams',
        sa.Column('season_id', postgresql.UUID(as_uuid=True), nullable=True)
    )
    
    # Criar FK para seasons
    op.create_foreign_key(
        'fk_teams_season_id',
        'teams',
        'seasons',
        ['season_id'],
        ['id'],
        ondelete='RESTRICT'
    )
    
    # Criar índice para queries por temporada
    op.create_index(
        'ix_teams_season_id',
        'teams',
        ['season_id']
    )
    
    # Adicionar coluna coach_membership_id (nullable - RF7)
    op.add_column(
        'teams',
        sa.Column('coach_membership_id', postgresql.UUID(as_uuid=True), nullable=True)
    )
    
    # Criar FK para org_memberships
    op.create_foreign_key(
        'fk_teams_coach_membership_id',
        'teams',
        'org_memberships',
        ['coach_membership_id'],
        ['id'],
        ondelete='SET NULL'
    )
    
    # Criar índice para queries por treinador
    op.create_index(
        'ix_teams_coach_membership_id',
        'teams',
        ['coach_membership_id']
    )
    
    # Adicionar coluna created_by_membership_id (nullable - auditoria)
    op.add_column(
        'teams',
        sa.Column('created_by_membership_id', postgresql.UUID(as_uuid=True), nullable=True)
    )
    
    # Criar FK para org_memberships
    op.create_foreign_key(
        'fk_teams_created_by_membership_id',
        'teams',
        'org_memberships',
        ['created_by_membership_id'],
        ['id'],
        ondelete='SET NULL'
    )
    
    # Criar índice para auditoria
    op.create_index(
        'ix_teams_created_by_membership_id',
        'teams',
        ['created_by_membership_id']
    )
    
    # Comentários nas colunas
    op.execute("""
        COMMENT ON COLUMN teams.season_id IS 'FK para seasons - vincula team a temporada específica';
        COMMENT ON COLUMN teams.coach_membership_id IS 'RF7 - Treinador principal atribuído à equipe';
        COMMENT ON COLUMN teams.created_by_membership_id IS 'Auditoria - membership que criou a equipe';
    """)


def downgrade() -> None:
    """Remove as colunas adicionadas."""
    
    # Remover índices
    op.drop_index('ix_teams_created_by_membership_id', table_name='teams')
    op.drop_index('ix_teams_coach_membership_id', table_name='teams')
    op.drop_index('ix_teams_season_id', table_name='teams')
    
    # Remover FKs
    op.drop_constraint('fk_teams_created_by_membership_id', 'teams', type_='foreignkey')
    op.drop_constraint('fk_teams_coach_membership_id', 'teams', type_='foreignkey')
    op.drop_constraint('fk_teams_season_id', 'teams', type_='foreignkey')
    
    # Remover colunas
    op.drop_column('teams', 'created_by_membership_id')
    op.drop_column('teams', 'coach_membership_id')
    op.drop_column('teams', 'season_id')
