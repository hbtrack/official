"""0031 - Create competitions module tables

Revision ID: 0031_create_competitions_module
Revises: 0030_add_teams_membership_columns
Create Date: 2026-01-14 17:30:00

Implementa o módulo completo de competições que estava definido nos modelos
mas ausente no banco de dados. Corrige o erro "relation competitions does not exist".
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0031'
down_revision = '0030'
branch_labels = None
depends_on = None


def upgrade():
    # 1. CREATE TABLE competitions (tabela principal)
    op.create_table(
        'competitions',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('kind', sa.String(50), nullable=True),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('season', sa.String(50), nullable=True),
        sa.Column('modality', sa.String(50), nullable=True, server_default='masculino'),
        sa.Column('competition_type', sa.String(50), nullable=True),
        sa.Column('format_details', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('tiebreaker_criteria', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='["pontos", "saldo_gols", "gols_pro", "confronto_direto"]'),
        sa.Column('points_per_win', sa.Integer(), nullable=True, server_default='2'),
        sa.Column('status', sa.String(50), nullable=True, server_default='draft'),
        sa.Column('current_phase_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('regulation_file_url', sa.String(500), nullable=True),
        sa.Column('regulation_notes', sa.Text(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('deleted_reason', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_competitions_organization_id', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], name='fk_competitions_team_id', ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], name='fk_competitions_created_by', ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id', name='pk_competitions'),
        sa.CheckConstraint(
            "(deleted_at IS NULL AND deleted_reason IS NULL) OR (deleted_at IS NOT NULL AND deleted_reason IS NOT NULL)",
            name='ck_competitions_deleted_reason'
        ),
        comment='Competições esportivas. Tabela principal do módulo de competições.'
    )
    
    # Indexes para competitions
    op.create_index('ix_competitions_organization_id', 'competitions', ['organization_id'])
    op.create_index('ix_competitions_status', 'competitions', ['status'])
    op.create_index('ix_competitions_team_id', 'competitions', ['team_id'])
    op.create_index('ix_competitions_season', 'competitions', ['season'])
    op.create_index('ix_competitions_created_by', 'competitions', ['created_by'])

    # 2. CREATE TABLE competition_phases
    op.create_table(
        'competition_phases',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('competition_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('phase_type', sa.String(50), nullable=False),
        sa.Column('order_index', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_olympic_cross', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('config', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('status', sa.String(50), nullable=True, server_default='pending'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['competition_id'], ['competitions.id'], name='fk_competition_phases_competition_id', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_competition_phases'),
        comment='Fases de uma competição (grupos, semifinais, finais, etc.)'
    )
    
    op.create_index('ix_competition_phases_competition_id', 'competition_phases', ['competition_id'])
    op.create_index('ix_competition_phases_order', 'competition_phases', ['competition_id', 'order_index'])

    # 3. CREATE TABLE competition_opponent_teams  
    op.create_table(
        'competition_opponent_teams',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('competition_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('short_name', sa.String(50), nullable=True),
        sa.Column('category', sa.String(50), nullable=True),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('logo_url', sa.String(500), nullable=True),
        sa.Column('linked_team_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('group_name', sa.String(50), nullable=True),
        sa.Column('stats', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{"wins": 0, "draws": 0, "losses": 0, "played": 0, "points": 0, "goals_for": 0, "goals_against": 0, "goal_difference": 0}'),
        sa.Column('status', sa.String(50), nullable=True, server_default='active'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['competition_id'], ['competitions.id'], name='fk_competition_opponent_teams_competition_id', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['linked_team_id'], ['teams.id'], name='fk_competition_opponent_teams_linked_team_id', ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id', name='pk_competition_opponent_teams'),
        comment='Times adversários em uma competição'
    )
    
    op.create_index('ix_competition_opponent_teams_competition_id', 'competition_opponent_teams', ['competition_id'])
    op.create_index('ix_competition_opponent_teams_group', 'competition_opponent_teams', ['competition_id', 'group_name'])
    op.create_index('ix_competition_opponent_teams_linked_team_id', 'competition_opponent_teams', ['linked_team_id'])

    # 4. CREATE TABLE competition_matches
    op.create_table(
        'competition_matches',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('competition_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('phase_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('external_reference_id', sa.String(100), nullable=True),
        sa.Column('home_team_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('away_team_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('is_our_match', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('our_team_is_home', sa.Boolean(), nullable=True),
        sa.Column('linked_match_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('match_date', sa.Date(), nullable=True),
        sa.Column('match_time', sa.Time(), nullable=True),
        sa.Column('match_datetime', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('location', sa.String(255), nullable=True),
        sa.Column('round_number', sa.Integer(), nullable=True),
        sa.Column('round_name', sa.String(100), nullable=True),
        sa.Column('home_score', sa.Integer(), nullable=True),
        sa.Column('away_score', sa.Integer(), nullable=True),
        sa.Column('home_score_extra', sa.Integer(), nullable=True),
        sa.Column('away_score_extra', sa.Integer(), nullable=True),
        sa.Column('home_score_penalties', sa.Integer(), nullable=True),
        sa.Column('away_score_penalties', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(50), nullable=True, server_default='scheduled'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['competition_id'], ['competitions.id'], name='fk_competition_matches_competition_id', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['phase_id'], ['competition_phases.id'], name='fk_competition_matches_phase_id', ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['home_team_id'], ['competition_opponent_teams.id'], name='fk_competition_matches_home_team_id', ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['away_team_id'], ['competition_opponent_teams.id'], name='fk_competition_matches_away_team_id', ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['linked_match_id'], ['matches.id'], name='fk_competition_matches_linked_match_id', ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id', name='pk_competition_matches'),
        comment='Jogos específicos de uma competição'
    )
    
    op.create_index('ix_competition_matches_competition_id', 'competition_matches', ['competition_id'])
    op.create_index('ix_competition_matches_phase_id', 'competition_matches', ['phase_id'])
    op.create_index('ix_competition_matches_our_match', 'competition_matches', ['is_our_match'])
    op.create_index('ix_competition_matches_date', 'competition_matches', ['match_date'])
    op.create_index('ix_competition_matches_linked_match_id', 'competition_matches', ['linked_match_id'])

    # 5. CREATE TABLE competition_standings
    op.create_table(
        'competition_standings',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('competition_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('phase_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('opponent_team_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('group_name', sa.String(50), nullable=True),
        sa.Column('points', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('played', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('wins', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('draws', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('losses', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('goals_for', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('goals_against', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('goal_difference', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('recent_form', sa.String(10), nullable=True),
        sa.Column('qualification_status', sa.String(50), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['competition_id'], ['competitions.id'], name='fk_competition_standings_competition_id', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['phase_id'], ['competition_phases.id'], name='fk_competition_standings_phase_id', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['opponent_team_id'], ['competition_opponent_teams.id'], name='fk_competition_standings_opponent_team_id', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_competition_standings'),
        sa.UniqueConstraint('competition_id', 'phase_id', 'opponent_team_id', name='uk_competition_standings_team_phase'),
        comment='Classificação/standings de uma competição'
    )
    
    op.create_index('ix_competition_standings_competition_id', 'competition_standings', ['competition_id'])
    op.create_index('ix_competition_standings_position', 'competition_standings', ['competition_id', 'phase_id', 'position'])

    # 6. Adicionar FK current_phase_id em competitions após criar competition_phases
    op.create_foreign_key(
        'fk_competitions_current_phase_id', 
        'competitions', 
        'competition_phases', 
        ['current_phase_id'], 
        ['id'], 
        ondelete='SET NULL'
    )

    # 7. CREATE TABLE competition_seasons (vínculo competição ↔ temporada)
    op.create_table(
        'competition_seasons',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('competition_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('season_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(100), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['competition_id'], ['competitions.id'], name='fk_competition_seasons_competition_id', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['season_id'], ['seasons.id'], name='fk_competition_seasons_season_id', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_competition_seasons'),
        sa.UniqueConstraint('competition_id', 'season_id', name='uk_competition_seasons_competition_season'),
        comment='Vínculo competição ↔ temporada'
    )
    
    op.create_index('ix_competition_seasons_competition_id', 'competition_seasons', ['competition_id'])
    op.create_index('ix_competition_seasons_season_id', 'competition_seasons', ['season_id'])

    # 8. Triggers para updated_at (seguindo padrão das outras tabelas)
    op.execute("""
        CREATE TRIGGER trigger_competitions_updated_at
            BEFORE UPDATE ON competitions
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
            
        CREATE TRIGGER trigger_competition_phases_updated_at
            BEFORE UPDATE ON competition_phases
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
            
        CREATE TRIGGER trigger_competition_opponent_teams_updated_at
            BEFORE UPDATE ON competition_opponent_teams
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
            
        CREATE TRIGGER trigger_competition_matches_updated_at
            BEFORE UPDATE ON competition_matches
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
            
        CREATE TRIGGER trigger_competition_standings_updated_at
            BEFORE UPDATE ON competition_standings
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
            
        CREATE TRIGGER trigger_competition_seasons_updated_at
            BEFORE UPDATE ON competition_seasons
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade():
    # Remover triggers
    op.execute("DROP TRIGGER IF EXISTS trigger_competition_seasons_updated_at ON competition_seasons;")
    op.execute("DROP TRIGGER IF EXISTS trigger_competition_standings_updated_at ON competition_standings;")
    op.execute("DROP TRIGGER IF EXISTS trigger_competition_matches_updated_at ON competition_matches;")
    op.execute("DROP TRIGGER IF EXISTS trigger_competition_opponent_teams_updated_at ON competition_opponent_teams;")
    op.execute("DROP TRIGGER IF EXISTS trigger_competition_phases_updated_at ON competition_phases;")
    op.execute("DROP TRIGGER IF EXISTS trigger_competitions_updated_at ON competitions;")
    
    # Remover tabelas na ordem reversa (por causa das FKs)
    op.drop_table('competition_seasons')
    op.drop_table('competition_standings')
    op.drop_table('competition_matches')
    op.drop_table('competition_opponent_teams')
    op.drop_table('competition_phases')
    op.drop_table('competitions')