"""create_mv_athlete_training_summary

Revision ID: 6086f19465e1
Revises: 92365c111182
Create Date: 2025-12-25

Materialized View para resumo individual de atleta em treinos.
Referências RAG: R12, R13, R14, RP4, RP5, RP6
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6086f19465e1'
down_revision: Union[str, Sequence[str], None] = '92365c111182'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Cria materialized view mv_athlete_training_summary"""

    op.execute(sa.text("""
    -- ============================================================================
    -- MATERIALIZED VIEW: Resumo Individual de Atleta em Treinos
    -- Referências: R12, R13, R14, RP4, RP5, RP6
    -- ============================================================================

    CREATE MATERIALIZED VIEW IF NOT EXISTS mv_athlete_training_summary AS
    WITH athlete_sessions AS (
        -- Listar todas as participações da atleta em treinos
        SELECT
            a.id AS athlete_id,
            a.person_id,
            a.full_name,
            a.nickname,
            a.birth_date,
            a.position,
            a.state AS current_state,
            a.organization_id,

            ts.id AS session_id,
            ts.season_id,
            ts.team_id,
            ts.session_at,

            att.status AS attendance_status,

            -- Wellness pré-treino
            wpre.sleep_hours,
            wpre.sleep_quality,
            wpre.fatigue AS fatigue_pre,
            wpre.stress,
            wpre.muscle_soreness,
            wpre.pain,
            wpre.pain_level,

            -- Wellness pós-treino
            wpst.minutes,
            wpst.rpe,
            wpst.internal_load,
            wpst.fatigue_after,
            wpst.mood_after

        FROM athletes a
        LEFT JOIN attendance att ON att.athlete_id = a.id
        LEFT JOIN training_sessions ts ON ts.id = att.session_id
        LEFT JOIN wellness_pre wpre ON wpre.session_id = ts.id AND wpre.athlete_id = a.id
        LEFT JOIN wellness_post wpst ON wpst.session_id = ts.id AND wpst.athlete_id = a.id
        WHERE a.deleted_at IS NULL
    ),
    athlete_aggregates AS (
        SELECT
            athlete_id,
            person_id,
            full_name,
            nickname,
            birth_date,
            position,
            current_state,
            organization_id,

            (SELECT tr.season_id FROM team_registrations tr WHERE tr.athlete_id = asess.athlete_id ORDER BY tr.created_at DESC LIMIT 1) AS current_season_id,
            (SELECT tr.team_id FROM team_registrations tr WHERE tr.athlete_id = asess.athlete_id ORDER BY tr.created_at DESC LIMIT 1) AS current_team_id,

            COUNT(DISTINCT session_id) AS total_sessions,
            COUNT(*) FILTER (WHERE attendance_status = 'presente') AS sessions_presente,
            COUNT(*) FILTER (WHERE attendance_status = 'ausente') AS sessions_ausente,
            COUNT(*) FILTER (WHERE attendance_status = 'medico') AS sessions_dm,
            COUNT(*) FILTER (WHERE attendance_status = 'lesionada') AS sessions_lesionada,

            ROUND(100.0 * COUNT(*) FILTER (WHERE attendance_status = 'presente') / NULLIF(COUNT(DISTINCT session_id), 0), 2) AS attendance_rate,

            ROUND(AVG(internal_load) FILTER (WHERE attendance_status = 'presente'), 0) AS avg_internal_load,
            ROUND(AVG(rpe) FILTER (WHERE attendance_status = 'presente'), 1) AS avg_rpe,
            ROUND(AVG(minutes) FILTER (WHERE attendance_status = 'presente'), 1) AS avg_minutes,

            ROUND(SUM(internal_load) FILTER (WHERE attendance_status = 'presente' AND session_at >= current_date - interval '7 days'), 0) AS load_7d,
            ROUND(SUM(internal_load) FILTER (WHERE attendance_status = 'presente' AND session_at >= current_date - interval '28 days'), 0) AS load_28d,

            ROUND(AVG(sleep_hours), 1) AS avg_sleep_hours,
            ROUND(AVG(sleep_quality), 1) AS avg_sleep_quality,
            ROUND(AVG(fatigue_pre), 1) AS avg_fatigue_pre,
            ROUND(AVG(stress), 1) AS avg_stress,
            ROUND(AVG(muscle_soreness), 1) AS avg_muscle_soreness,

            ROUND(AVG(fatigue_after), 1) AS avg_fatigue_after,
            ROUND(AVG(mood_after), 1) AS avg_mood_after,

            (SELECT sleep_hours FROM athlete_sessions ls WHERE ls.athlete_id = asess.athlete_id AND ls.sleep_hours IS NOT NULL ORDER BY ls.session_at DESC LIMIT 1) AS last_sleep_hours,
            (SELECT fatigue_pre FROM athlete_sessions ls WHERE ls.athlete_id = asess.athlete_id AND ls.fatigue_pre IS NOT NULL ORDER BY ls.session_at DESC LIMIT 1) AS last_fatigue,
            (SELECT internal_load FROM athlete_sessions ls WHERE ls.athlete_id = asess.athlete_id AND ls.internal_load IS NOT NULL ORDER BY ls.session_at DESC LIMIT 1) AS last_internal_load,

            MAX(session_at) AS last_session_at

        FROM athlete_sessions asess
        GROUP BY athlete_id, person_id, full_name, nickname, birth_date, position, current_state, organization_id
    )
    SELECT
        aa.*,
        (SELECT COUNT(*) FROM medical_cases mc WHERE mc.athlete_id = aa.athlete_id AND mc.status = 'ativo') AS active_medical_cases,
        DATE_PART('year', AGE(CURRENT_DATE, aa.birth_date))::int AS current_age,
        (SELECT c.code FROM categories c WHERE DATE_PART('year', AGE(CURRENT_DATE, aa.birth_date))::int >= c.min_age AND (c.max_age IS NULL OR DATE_PART('year', AGE(CURRENT_DATE, aa.birth_date))::int <= c.max_age) ORDER BY c.min_age DESC LIMIT 1) AS expected_category_code
    FROM athlete_aggregates aa;

    CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_athlete_training_summary_athlete ON mv_athlete_training_summary(athlete_id);
    CREATE INDEX IF NOT EXISTS idx_mv_athlete_training_summary_org ON mv_athlete_training_summary(organization_id);
    CREATE INDEX IF NOT EXISTS idx_mv_athlete_training_summary_season ON mv_athlete_training_summary(current_season_id);
    CREATE INDEX IF NOT EXISTS idx_mv_athlete_training_summary_team ON mv_athlete_training_summary(current_team_id);
    CREATE INDEX IF NOT EXISTS idx_mv_athlete_training_summary_state ON mv_athlete_training_summary(current_state);

    COMMENT ON MATERIALIZED VIEW mv_athlete_training_summary IS 'Resumo individual de atleta em treinos (R12, R13, R14, RP4, RP5, RP6).';
    """))


def downgrade() -> None:
    """Remove materialized view mv_athlete_training_summary"""
    op.execute(sa.text("DROP MATERIALIZED VIEW IF EXISTS mv_athlete_training_summary CASCADE"))
