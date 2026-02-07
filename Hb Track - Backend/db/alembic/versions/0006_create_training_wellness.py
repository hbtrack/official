"""V1.2 - Create training sessions, attendance, and wellness tables

Revision ID: 005_v1_2_training_wellness
Revises: 004_v1_2_athletes_memberships
Create Date: 2025-12-28 05:20:00

REGRAS_SISTEMAS_V1.2.md: R17, R21, R37, RD5 (TABELAS BANCO.txt)
V1.2: treinos podem existir sem team_id/season_id; wellness integrado ao sistema
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0006'
down_revision = '0005'
branch_labels = None
depends_on = None


def upgrade():
    # TRAINING_SESSIONS
    # R37, RD5: team_id e season_id opcionais (treinos organizacionais, avaliações, captação)
    op.create_table(
        'training_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('season_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('session_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('duration_planned_minutes', sa.SmallInteger(), nullable=True),
        sa.Column('location', sa.String(120), nullable=True),
        sa.Column('session_type', sa.String(32), nullable=False),
        sa.Column('main_objective', sa.String(255), nullable=True),
        sa.Column('secondary_objective', sa.Text(), nullable=True),
        sa.Column('planned_load', sa.SmallInteger(), nullable=True),
        sa.Column('group_climate', sa.SmallInteger(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),

        # Campos de periodização
        sa.Column('phase_focus_defense', sa.Boolean(), server_default=sa.text('false'), nullable=True),
        sa.Column('phase_focus_attack', sa.Boolean(), server_default=sa.text('false'), nullable=True),
        sa.Column('phase_focus_transition_offense', sa.Boolean(), server_default=sa.text('false'), nullable=True),
        sa.Column('phase_focus_transition_defense', sa.Boolean(), server_default=sa.text('false'), nullable=True),
        sa.Column('intensity_target', sa.SmallInteger(), nullable=True),
        sa.Column('session_block', sa.String(32), nullable=True),

        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('deleted_reason', sa.Text(), nullable=True),

        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_training_sessions_organization_id', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], name='fk_training_sessions_team_id', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['season_id'], ['seasons.id'], name='fk_training_sessions_season_id', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], name='fk_training_sessions_created_by_user_id', ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id', name='pk_training_sessions'),
        sa.CheckConstraint(
            "session_type IN ('quadra', 'fisico', 'video', 'reuniao', 'teste')",
            name='ck_training_sessions_type'
        ),
        sa.CheckConstraint(
            "group_climate IS NULL OR (group_climate BETWEEN 1 AND 5)",
            name='ck_training_sessions_climate'
        ),
        sa.CheckConstraint(
            "intensity_target IS NULL OR (intensity_target BETWEEN 1 AND 5)",
            name='ck_training_sessions_intensity'
        ),
        sa.CheckConstraint(
            "(deleted_at IS NULL AND deleted_reason IS NULL) OR (deleted_at IS NOT NULL AND deleted_reason IS NOT NULL)",
            name='ck_training_sessions_deleted_reason'
        ),
        comment='Treinos. V1.2: team_id e season_id opcionais (treinos organizacionais, avaliações, captação).'
    )
    op.create_index('ix_training_sessions_organization_id', 'training_sessions', ['organization_id'])
    op.create_index('ix_training_sessions_team_id', 'training_sessions', ['team_id'])
    op.create_index('ix_training_sessions_season_id', 'training_sessions', ['season_id'])
    op.create_index('ix_training_sessions_session_at', 'training_sessions', ['session_at'])

    # ATTENDANCE (presença por treino)
    # V1.2: lista de presença gerada automaticamente via team_registrations ativos
    op.create_table(
        'attendance',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('training_session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('team_registration_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('athlete_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('presence_status', sa.String(32), nullable=False),
        sa.Column('minutes_effective', sa.SmallInteger(), nullable=True),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('source', sa.String(32), server_default=sa.text("'manual'"), nullable=False),

        # Campos adicionais
        sa.Column('participation_type', sa.String(32), nullable=True),
        sa.Column('reason_absence', sa.String(32), nullable=True),
        sa.Column('is_medical_restriction', sa.Boolean(), server_default=sa.text('false'), nullable=True),

        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('deleted_reason', sa.Text(), nullable=True),

        sa.ForeignKeyConstraint(['training_session_id'], ['training_sessions.id'], name='fk_attendance_training_session_id', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['team_registration_id'], ['team_registrations.id'], name='fk_attendance_team_registration_id', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['athlete_id'], ['athletes.id'], name='fk_attendance_athlete_id', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], name='fk_attendance_created_by_user_id', ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id', name='pk_attendance'),
        sa.CheckConstraint(
            "presence_status IN ('present', 'absent')",
            name='ck_attendance_status'
        ),
        sa.CheckConstraint(
            "participation_type IS NULL OR participation_type IN ('full', 'partial', 'adapted', 'did_not_train')",
            name='ck_attendance_participation_type'
        ),
        sa.CheckConstraint(
            "reason_absence IS NULL OR reason_absence IN ('medico', 'escola', 'familiar', 'opcional', 'outro')",
            name='ck_attendance_reason'
        ),
        sa.CheckConstraint(
            "source IN ('manual', 'import', 'correction')",
            name='ck_attendance_source'
        ),
        sa.CheckConstraint(
            "(deleted_at IS NULL AND deleted_reason IS NULL) OR (deleted_at IS NOT NULL AND deleted_reason IS NOT NULL)",
            name='ck_attendance_deleted_reason'
        ),
        comment='Presença por treino. V1.2: sem convocação formal; lista gerada por team_registrations ativos.'
    )
    op.create_index('ix_attendance_training_session_id', 'attendance', ['training_session_id'])
    op.create_index('ix_attendance_athlete_id', 'attendance', ['athlete_id'])

    # WELLNESS_PRE (bem-estar pré-treino)
    # V1.2: integrado ao sistema; atleta preenche antes do treino
    op.create_table(
        'wellness_pre',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('training_session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('athlete_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sleep_hours', sa.Numeric(4, 1), nullable=False),
        sa.Column('sleep_quality', sa.SmallInteger(), nullable=False),
        sa.Column('fatigue_pre', sa.SmallInteger(), nullable=False),
        sa.Column('stress_level', sa.SmallInteger(), nullable=False),
        sa.Column('muscle_soreness', sa.SmallInteger(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),

        # Campos opcionais
        sa.Column('menstrual_cycle_phase', sa.String(32), nullable=True),
        sa.Column('readiness_score', sa.SmallInteger(), nullable=True),

        sa.Column('filled_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('deleted_reason', sa.Text(), nullable=True),

        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_wellness_pre_organization_id', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['training_session_id'], ['training_sessions.id'], name='fk_wellness_pre_training_session_id', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['athlete_id'], ['athletes.id'], name='fk_wellness_pre_athlete_id', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], name='fk_wellness_pre_created_by_user_id', ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id', name='pk_wellness_pre'),
        sa.CheckConstraint(
            "sleep_hours >= 0 AND sleep_hours <= 24",
            name='ck_wellness_pre_sleep_hours'
        ),
        sa.CheckConstraint(
            "sleep_quality BETWEEN 1 AND 5",
            name='ck_wellness_pre_sleep_quality'
        ),
        sa.CheckConstraint(
            "fatigue_pre BETWEEN 0 AND 10",
            name='ck_wellness_pre_fatigue'
        ),
        sa.CheckConstraint(
            "stress_level BETWEEN 0 AND 10",
            name='ck_wellness_pre_stress'
        ),
        sa.CheckConstraint(
            "muscle_soreness BETWEEN 0 AND 10",
            name='ck_wellness_pre_soreness'
        ),
        sa.CheckConstraint(
            "readiness_score IS NULL OR (readiness_score BETWEEN 0 AND 10)",
            name='ck_wellness_pre_readiness'
        ),
        sa.CheckConstraint(
            "menstrual_cycle_phase IS NULL OR menstrual_cycle_phase IN ('folicular', 'lutea', 'menstruacao', 'nao_informa')",
            name='ck_wellness_pre_menstrual'
        ),
        sa.CheckConstraint(
            "(deleted_at IS NULL AND deleted_reason IS NULL) OR (deleted_at IS NOT NULL AND deleted_reason IS NOT NULL)",
            name='ck_wellness_pre_deleted_reason'
        ),
        comment='Bem-estar pré-treino. V1.2: atleta preenche antes do treino, 1 por atleta × sessão.'
    )

    # UNIQUE constraint para evitar múltiplos pré-treinos por sessão
    op.create_index(
        'ux_wellness_pre_session_athlete',
        'wellness_pre',
        ['training_session_id', 'athlete_id'],
        unique=True,
        postgresql_where=sa.text('deleted_at IS NULL')
    )
    op.create_index('ix_wellness_pre_athlete_id', 'wellness_pre', ['athlete_id'])
    op.create_index('ix_wellness_pre_training_session_id', 'wellness_pre', ['training_session_id'])

    # WELLNESS_POST (bem-estar pós-treino)
    # V1.2: integrado ao sistema; atleta preenche depois do treino
    op.create_table(
        'wellness_post',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('training_session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('athlete_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_rpe', sa.SmallInteger(), nullable=False),
        sa.Column('fatigue_after', sa.SmallInteger(), nullable=False),
        sa.Column('mood_after', sa.SmallInteger(), nullable=False),
        sa.Column('muscle_soreness_after', sa.SmallInteger(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),

        # Campos opcionais
        sa.Column('perceived_intensity', sa.SmallInteger(), nullable=True),
        sa.Column('flag_medical_followup', sa.Boolean(), server_default=sa.text('false'), nullable=True),

        sa.Column('filled_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('deleted_reason', sa.Text(), nullable=True),

        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_wellness_post_organization_id', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['training_session_id'], ['training_sessions.id'], name='fk_wellness_post_training_session_id', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['athlete_id'], ['athletes.id'], name='fk_wellness_post_athlete_id', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], name='fk_wellness_post_created_by_user_id', ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id', name='pk_wellness_post'),
        sa.CheckConstraint(
            "session_rpe BETWEEN 0 AND 10",
            name='ck_wellness_post_rpe'
        ),
        sa.CheckConstraint(
            "fatigue_after BETWEEN 0 AND 10",
            name='ck_wellness_post_fatigue'
        ),
        sa.CheckConstraint(
            "mood_after BETWEEN 0 AND 10",
            name='ck_wellness_post_mood'
        ),
        sa.CheckConstraint(
            "muscle_soreness_after IS NULL OR (muscle_soreness_after BETWEEN 0 AND 10)",
            name='ck_wellness_post_soreness'
        ),
        sa.CheckConstraint(
            "perceived_intensity IS NULL OR (perceived_intensity BETWEEN 1 AND 5)",
            name='ck_wellness_post_intensity'
        ),
        sa.CheckConstraint(
            "(deleted_at IS NULL AND deleted_reason IS NULL) OR (deleted_at IS NOT NULL AND deleted_reason IS NOT NULL)",
            name='ck_wellness_post_deleted_reason'
        ),
        comment='Bem-estar pós-treino. V1.2: atleta preenche depois do treino, 1 por atleta × sessão.'
    )

    # UNIQUE constraint para evitar múltiplos pós-treinos por sessão
    op.create_index(
        'ux_wellness_post_session_athlete',
        'wellness_post',
        ['training_session_id', 'athlete_id'],
        unique=True,
        postgresql_where=sa.text('deleted_at IS NULL')
    )
    op.create_index('ix_wellness_post_athlete_id', 'wellness_post', ['athlete_id'])
    op.create_index('ix_wellness_post_training_session_id', 'wellness_post', ['training_session_id'])


def downgrade():
    op.drop_table('wellness_post')
    op.drop_table('wellness_pre')
    op.drop_table('attendance')
    op.drop_table('training_sessions')
