"""V1.2 - Create matches, events, and event tracking system

Revision ID: 006_v1_2_matches_events
Revises: 005_v1_2_training_wellness
Create Date: 2025-12-28 05:30:00

REGRAS_SISTEMAS_V1.2.md: R18, R19, RD27 (TABELAS BANCO.txt)
V1.2: sistema completo de event tracking com phase_of_play, advantage_state, possessions
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0007'
down_revision = '0006'
branch_labels = None
depends_on = None


def upgrade():
    # PHASES_OF_PLAY (tabela auxiliar - 4 fases do jogo)
    # Lookup table: defense, transition_offense, attack_positional, transition_defense
    op.create_table(
        'phases_of_play',
        sa.Column('code', sa.String(32), nullable=False),
        sa.Column('description', sa.String(255), nullable=False),
        sa.PrimaryKeyConstraint('code', name='pk_phases_of_play'),
        comment='Fases do jogo. Lookup table fixa com 4 fases.'
    )

    # ADVANTAGE_STATES (tabela auxiliar - situações numéricas)
    # Lookup table: even, numerical_superiority, numerical_inferiority
    op.create_table(
        'advantage_states',
        sa.Column('code', sa.String(32), nullable=False),
        sa.Column('delta_players', sa.SmallInteger(), nullable=False),
        sa.Column('description', sa.String(255), nullable=True),
        sa.PrimaryKeyConstraint('code', name='pk_advantage_states'),
        comment='Estados de vantagem numérica. Lookup table.'
    )

    # EVENT_TYPES (dicionário de tipos de evento)
    op.create_table(
        'event_types',
        sa.Column('code', sa.String(64), nullable=False),
        sa.Column('description', sa.String(255), nullable=False),
        sa.Column('is_shot', sa.Boolean(), nullable=False),
        sa.Column('is_possession_ending', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('code', name='pk_event_types'),
        comment='Tipos de evento (shot, goal, goalkeeper_save, turnover, foul, etc.).'
    )

    # EVENT_SUBTYPES (detalhamento de tipos de evento)
    op.create_table(
        'event_subtypes',
        sa.Column('code', sa.String(64), nullable=False),
        sa.Column('event_type_code', sa.String(64), nullable=False),
        sa.Column('description', sa.String(255), nullable=False),
        sa.ForeignKeyConstraint(['event_type_code'], ['event_types.code'], name='fk_event_subtypes_event_type_code', ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('code', name='pk_event_subtypes'),
        comment='Subtipos de evento (shot_6m, shot_9m, shot_wing, turnover_pass, etc.).'
    )
    op.create_index('ix_event_subtypes_event_type_code', 'event_subtypes', ['event_type_code'])

    # MATCHES (registro oficial de jogo)
    op.create_table(
        'matches',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('season_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('competition_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('match_date', sa.Date(), nullable=False),
        sa.Column('start_time', sa.Time(), nullable=True),
        sa.Column('venue', sa.String(120), nullable=True),
        sa.Column('phase', sa.String(32), nullable=False),
        sa.Column('status', sa.String(32), nullable=False),
        sa.Column('home_team_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('away_team_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('our_team_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('final_score_home', sa.SmallInteger(), nullable=True),
        sa.Column('final_score_away', sa.SmallInteger(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('deleted_reason', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['season_id'], ['seasons.id'], name='fk_matches_season_id', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['home_team_id'], ['teams.id'], name='fk_matches_home_team_id', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['away_team_id'], ['teams.id'], name='fk_matches_away_team_id', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['our_team_id'], ['teams.id'], name='fk_matches_our_team_id', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], name='fk_matches_created_by_user_id', ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id', name='pk_matches'),
        sa.CheckConstraint(
            "phase IN ('group', 'semifinal', 'final', 'friendly')",
            name='ck_matches_phase'
        ),
        sa.CheckConstraint(
            "status IN ('scheduled', 'in_progress', 'finished', 'cancelled')",
            name='ck_matches_status'
        ),
        sa.CheckConstraint(
            "home_team_id != away_team_id",
            name='ck_matches_different_teams'
        ),
        sa.CheckConstraint(
            "our_team_id = home_team_id OR our_team_id = away_team_id",
            name='ck_matches_our_team'
        ),
        sa.CheckConstraint(
            "final_score_home IS NULL OR final_score_home >= 0",
            name='ck_matches_score_home'
        ),
        sa.CheckConstraint(
            "final_score_away IS NULL OR final_score_away >= 0",
            name='ck_matches_score_away'
        ),
        sa.CheckConstraint(
            "(deleted_at IS NULL AND deleted_reason IS NULL) OR (deleted_at IS NOT NULL AND deleted_reason IS NOT NULL)",
            name='ck_matches_deleted_reason'
        ),
        comment='Jogos oficiais. Ponto de partida para convocação, súmula, eventos, estatísticas e relatórios.'
    )
    op.create_index('ix_matches_season_id', 'matches', ['season_id'])
    op.create_index('ix_matches_match_date', 'matches', ['match_date'])
    op.create_index('ix_matches_status', 'matches', ['status'])
    op.create_index('ix_matches_home_team_id', 'matches', ['home_team_id'])
    op.create_index('ix_matches_away_team_id', 'matches', ['away_team_id'])

    # MATCH_TEAMS (ponte jogo ↔ equipes)
    op.create_table(
        'match_teams',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('match_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('is_home', sa.Boolean(), nullable=False),
        sa.Column('is_our_team', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['match_id'], ['matches.id'], name='fk_match_teams_match_id', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], name='fk_match_teams_team_id', ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id', name='pk_match_teams'),
        comment='Ponte jogo ↔ equipes. Identifica quais equipes jogaram e com qual papel.'
    )
    op.create_index('ix_match_teams_match_id', 'match_teams', ['match_id'])
    op.create_index('ix_match_teams_team_id', 'match_teams', ['team_id'])

    # MATCH_ROSTER (súmula/convocação oficial)
    op.create_table(
        'match_roster',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('match_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('athlete_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('jersey_number', sa.SmallInteger(), nullable=False),
        sa.Column('is_starting', sa.Boolean(), nullable=True),
        sa.Column('is_goalkeeper', sa.Boolean(), nullable=False),
        sa.Column('is_available', sa.Boolean(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['match_id'], ['matches.id'], name='fk_match_roster_match_id', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], name='fk_match_roster_team_id', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['athlete_id'], ['athletes.id'], name='fk_match_roster_athlete_id', ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id', name='pk_match_roster'),
        sa.CheckConstraint(
            "jersey_number > 0",
            name='ck_match_roster_jersey'
        ),
        comment='Súmula/convocação oficial. Define quais atletas estão elegíveis para o jogo.'
    )
    op.create_index('ix_match_roster_match_id', 'match_roster', ['match_id'])
    op.create_index('ix_match_roster_athlete_id', 'match_roster', ['athlete_id'])

    # MATCH_PERIODS (estrutura de tempo dos jogos)
    op.create_table(
        'match_periods',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('match_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('number', sa.SmallInteger(), nullable=False),
        sa.Column('duration_seconds', sa.Integer(), nullable=False),
        sa.Column('period_type', sa.String(32), nullable=False),
        sa.ForeignKeyConstraint(['match_id'], ['matches.id'], name='fk_match_periods_match_id', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_match_periods'),
        sa.CheckConstraint(
            "number >= 1",
            name='ck_match_periods_number'
        ),
        sa.CheckConstraint(
            "duration_seconds > 0",
            name='ck_match_periods_duration'
        ),
        sa.CheckConstraint(
            "period_type IN ('regular', 'extra_time', 'shootout_7m')",
            name='ck_match_periods_type'
        ),
        comment='Estrutura de tempo dos jogos (1º tempo, 2º tempo, prorrogação, 7m).'
    )
    op.create_index('ix_match_periods_match_id', 'match_periods', ['match_id'])

    # MATCH_POSSESSIONS (sequências de posse de bola)
    # RD27: posse inferida pelos eventos
    op.create_table(
        'match_possessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('match_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('start_period_number', sa.SmallInteger(), nullable=False),
        sa.Column('start_time_seconds', sa.Integer(), nullable=False),
        sa.Column('end_period_number', sa.SmallInteger(), nullable=False),
        sa.Column('end_time_seconds', sa.Integer(), nullable=False),
        sa.Column('start_score_our', sa.SmallInteger(), nullable=False),
        sa.Column('start_score_opponent', sa.SmallInteger(), nullable=False),
        sa.Column('end_score_our', sa.SmallInteger(), nullable=False),
        sa.Column('end_score_opponent', sa.SmallInteger(), nullable=False),
        sa.Column('result', sa.String(32), nullable=False),
        sa.ForeignKeyConstraint(['match_id'], ['matches.id'], name='fk_match_possessions_match_id', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], name='fk_match_possessions_team_id', ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id', name='pk_match_possessions'),
        sa.CheckConstraint(
            "start_period_number >= 1",
            name='ck_match_possessions_start_period'
        ),
        sa.CheckConstraint(
            "end_period_number >= start_period_number",
            name='ck_match_possessions_end_period'
        ),
        sa.CheckConstraint(
            "start_time_seconds >= 0",
            name='ck_match_possessions_start_time'
        ),
        sa.CheckConstraint(
            "end_time_seconds >= 0",
            name='ck_match_possessions_end_time'
        ),
        sa.CheckConstraint(
            "result IN ('goal', 'turnover', 'seven_meter_won', 'time_over')",
            name='ck_match_possessions_result'
        ),
        comment='Sequências de posse de bola. Base para análise tática de eficiência.'
    )
    op.create_index('ix_match_possessions_match_id', 'match_possessions', ['match_id'])
    op.create_index('ix_match_possessions_team_id', 'match_possessions', ['team_id'])

    # MATCH_EVENTS (coração analítico - lance a lance)
    # R19: estatísticas primárias sempre vinculadas a jogo e equipe
    op.create_table(
        'match_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('match_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('opponent_team_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('athlete_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('assisting_athlete_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('secondary_athlete_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('period_number', sa.SmallInteger(), nullable=False),
        sa.Column('game_time_seconds', sa.Integer(), nullable=False),
        sa.Column('phase_of_play', sa.String(32), nullable=False),
        sa.Column('possession_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('advantage_state', sa.String(32), nullable=False),
        sa.Column('score_our', sa.SmallInteger(), nullable=False),
        sa.Column('score_opponent', sa.SmallInteger(), nullable=False),
        sa.Column('event_type', sa.String(64), nullable=False),
        sa.Column('event_subtype', sa.String(64), nullable=True),
        sa.Column('outcome', sa.String(64), nullable=False),
        sa.Column('is_shot', sa.Boolean(), nullable=False),
        sa.Column('is_goal', sa.Boolean(), nullable=False),
        sa.Column('x_coord', sa.Numeric(5, 2), nullable=True),
        sa.Column('y_coord', sa.Numeric(5, 2), nullable=True),
        sa.Column('related_event_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('source', sa.String(32), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['match_id'], ['matches.id'], name='fk_match_events_match_id', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], name='fk_match_events_team_id', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['opponent_team_id'], ['teams.id'], name='fk_match_events_opponent_team_id', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['athlete_id'], ['athletes.id'], name='fk_match_events_athlete_id', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['assisting_athlete_id'], ['athletes.id'], name='fk_match_events_assisting_athlete_id', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['secondary_athlete_id'], ['athletes.id'], name='fk_match_events_secondary_athlete_id', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['phase_of_play'], ['phases_of_play.code'], name='fk_match_events_phase_of_play', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['possession_id'], ['match_possessions.id'], name='fk_match_events_possession_id', ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['advantage_state'], ['advantage_states.code'], name='fk_match_events_advantage_state', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['event_type'], ['event_types.code'], name='fk_match_events_event_type', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['event_subtype'], ['event_subtypes.code'], name='fk_match_events_event_subtype', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['related_event_id'], ['match_events.id'], name='fk_match_events_related_event_id', ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], name='fk_match_events_created_by_user_id', ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id', name='pk_match_events'),
        sa.CheckConstraint(
            "period_number >= 1",
            name='ck_match_events_period'
        ),
        sa.CheckConstraint(
            "game_time_seconds >= 0",
            name='ck_match_events_time'
        ),
        sa.CheckConstraint(
            "score_our >= 0",
            name='ck_match_events_score_our'
        ),
        sa.CheckConstraint(
            "score_opponent >= 0",
            name='ck_match_events_score_opponent'
        ),
        sa.CheckConstraint(
            "x_coord IS NULL OR (x_coord >= 0 AND x_coord <= 100)",
            name='ck_match_events_x_coord'
        ),
        sa.CheckConstraint(
            "y_coord IS NULL OR (y_coord >= 0 AND y_coord <= 100)",
            name='ck_match_events_y_coord'
        ),
        sa.CheckConstraint(
            "source IN ('live', 'video', 'post_game_correction')",
            name='ck_match_events_source'
        ),
        comment='Eventos de jogo lance a lance. Coração analítico: reconstrói jogo, contexto tático e gera estatísticas.'
    )
    op.create_index('ix_match_events_match_id', 'match_events', ['match_id'])
    op.create_index('ix_match_events_athlete_id', 'match_events', ['athlete_id'])
    op.create_index('ix_match_events_team_id', 'match_events', ['team_id'])
    op.create_index('ix_match_events_phase_of_play', 'match_events', ['phase_of_play'])
    op.create_index('ix_match_events_event_type', 'match_events', ['event_type'])


def downgrade():
    op.drop_table('match_events')
    op.drop_table('match_possessions')
    op.drop_table('match_periods')
    op.drop_table('match_roster')
    op.drop_table('match_teams')
    op.drop_table('matches')
    op.drop_table('event_subtypes')
    op.drop_table('event_types')
    op.drop_table('advantage_states')
    op.drop_table('phases_of_play')
