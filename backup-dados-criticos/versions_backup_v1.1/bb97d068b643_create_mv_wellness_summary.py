"""create_mv_wellness_summary

Revision ID: bb97d068b643
Revises: 6086f19465e1
Create Date: 2025-12-25 13:42:07.285137

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bb97d068b643'
down_revision: Union[str, Sequence[str], None] = '6086f19465e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Cria materialized view mv_wellness_summary"""

    op.execute(sa.text("""
    -- ============================================================================
    -- MATERIALIZED VIEW: Resumo de Wellness Agregado por Período/Equipe
    -- Referências: RP6, RP7, RP8
    -- ============================================================================

    CREATE MATERIALIZED VIEW IF NOT EXISTS mv_wellness_summary AS
    WITH wellness_data AS (
        -- Combinar wellness_pre e wellness_post com informações de contexto
        SELECT
            wpre.athlete_id,
            wpre.organization_id,
            ts.session_at,
            ts.id AS session_id,

            -- Obter season_id e team_id através de team_registrations
            tr.season_id,
            tr.team_id,

            -- Métricas wellness pré-treino
            wpre.sleep_hours,
            wpre.sleep_quality,
            wpre.fatigue AS fatigue_pre,
            wpre.stress,
            wpre.muscle_soreness,

            -- Métricas wellness pós-treino
            wpst.fatigue_after,
            wpst.mood_after

        FROM wellness_pre wpre
        INNER JOIN training_sessions ts ON ts.id = wpre.session_id
        LEFT JOIN wellness_post wpst ON wpst.session_id = wpre.session_id AND wpst.athlete_id = wpre.athlete_id
        LEFT JOIN team_registrations tr ON tr.athlete_id = wpre.athlete_id
            AND tr.deleted_at IS NULL
            AND tr.end_at IS NULL  -- Apenas registros ativos
        WHERE wpre.deleted_at IS NULL
          AND ts.deleted_at IS NULL
    ),
    weekly_aggregates AS (
        -- Agregação semanal (últimos 7 dias a partir de session_at)
        SELECT
            organization_id,
            season_id,
            team_id,
            DATE_TRUNC('week', session_at)::date AS period_start,
            'weekly' AS period_type,

            COUNT(DISTINCT athlete_id) AS athletes_count,
            COUNT(DISTINCT session_id) AS sessions_count,

            -- Médias de wellness pré-treino
            ROUND(AVG(sleep_hours), 1) AS avg_sleep_hours,
            ROUND(AVG(sleep_quality), 1) AS avg_sleep_quality,
            ROUND(AVG(fatigue_pre), 1) AS avg_fatigue_pre,
            ROUND(AVG(stress), 1) AS avg_stress,
            ROUND(AVG(muscle_soreness), 1) AS avg_muscle_soreness,

            -- Médias de wellness pós-treino
            ROUND(AVG(fatigue_after), 1) AS avg_fatigue_after,
            ROUND(AVG(mood_after), 1) AS avg_mood_after,

            -- Desvios padrão (indicadores de variabilidade)
            ROUND(STDDEV(fatigue_pre), 1) AS stddev_fatigue_pre,
            ROUND(STDDEV(stress), 1) AS stddev_stress,

            -- Data mais recente no período
            MAX(session_at) AS last_session_at

        FROM wellness_data
        WHERE season_id IS NOT NULL AND team_id IS NOT NULL
        GROUP BY organization_id, season_id, team_id, DATE_TRUNC('week', session_at)::date
    ),
    monthly_aggregates AS (
        -- Agregação mensal
        SELECT
            organization_id,
            season_id,
            team_id,
            DATE_TRUNC('month', session_at)::date AS period_start,
            'monthly' AS period_type,

            COUNT(DISTINCT athlete_id) AS athletes_count,
            COUNT(DISTINCT session_id) AS sessions_count,

            -- Médias de wellness pré-treino
            ROUND(AVG(sleep_hours), 1) AS avg_sleep_hours,
            ROUND(AVG(sleep_quality), 1) AS avg_sleep_quality,
            ROUND(AVG(fatigue_pre), 1) AS avg_fatigue_pre,
            ROUND(AVG(stress), 1) AS avg_stress,
            ROUND(AVG(muscle_soreness), 1) AS avg_muscle_soreness,

            -- Médias de wellness pós-treino
            ROUND(AVG(fatigue_after), 1) AS avg_fatigue_after,
            ROUND(AVG(mood_after), 1) AS avg_mood_after,

            -- Desvios padrão
            ROUND(STDDEV(fatigue_pre), 1) AS stddev_fatigue_pre,
            ROUND(STDDEV(stress), 1) AS stddev_stress,

            -- Data mais recente no período
            MAX(session_at) AS last_session_at

        FROM wellness_data
        WHERE season_id IS NOT NULL AND team_id IS NOT NULL
        GROUP BY organization_id, season_id, team_id, DATE_TRUNC('month', session_at)::date
    )
    -- União de agregações semanais e mensais
    SELECT * FROM weekly_aggregates
    UNION ALL
    SELECT * FROM monthly_aggregates;

    -- Índices para performance
    CREATE INDEX IF NOT EXISTS idx_mv_wellness_summary_org_season
      ON mv_wellness_summary(organization_id, season_id);
    CREATE INDEX IF NOT EXISTS idx_mv_wellness_summary_team
      ON mv_wellness_summary(team_id);
    CREATE INDEX IF NOT EXISTS idx_mv_wellness_summary_period
      ON mv_wellness_summary(period_start DESC, period_type);
    CREATE INDEX IF NOT EXISTS idx_mv_wellness_summary_composite
      ON mv_wellness_summary(organization_id, season_id, team_id, period_type, period_start DESC);

    -- COMMENT (documentação)
    COMMENT ON MATERIALIZED VIEW mv_wellness_summary IS
    'Agregados de wellness (pré e pós-treino) por período (semanal/mensal) e equipe (RP6, RP7, RP8).
    Atualizar via REFRESH MATERIALIZED VIEW CONCURRENTLY mv_wellness_summary.';
    """))


def downgrade() -> None:
    """Remove materialized view mv_wellness_summary"""
    op.execute(sa.text("DROP MATERIALIZED VIEW IF EXISTS mv_wellness_summary CASCADE"))
