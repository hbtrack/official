"""create_mv_training_performance

Revision ID: 92365c111182
Revises: 4af09f9d46a0
Create Date: 2025-12-24

Materialized View para agregados de performance de treinos.
Referências RAG: R18, R22, RP5, RP6
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '92365c111182'
down_revision: Union[str, Sequence[str], None] = '5c90cfd7e291'  # APÓS Phase 1
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Cria materialized view mv_training_performance"""

    op.execute(sa.text("""
    -- ============================================================================
    -- MATERIALIZED VIEW: Agregados de Performance de Treinos
    -- Referências: R18, R22, RP5, RP6
    -- ============================================================================

    CREATE MATERIALIZED VIEW IF NOT EXISTS mv_training_performance AS
    SELECT
      ts.id AS session_id,
      ts.organization_id,
      ts.season_id,
      ts.team_id,
      ts.session_at,
      ts.main_objective,
      ts.planned_load,
      ts.group_climate,

      -- Métricas de Presença (RP5)
      COUNT(DISTINCT att.athlete_id) AS total_athletes,
      COUNT(*) FILTER (WHERE att.status = 'presente') AS presentes,
      COUNT(*) FILTER (WHERE att.status = 'ausente') AS ausentes,
      COUNT(*) FILTER (WHERE att.status = 'medico') AS dm,
      COUNT(*) FILTER (WHERE att.status = 'lesionada') AS lesionadas,

      -- Taxa de presença (%)
      ROUND(
        100.0 * COUNT(*) FILTER (WHERE att.status = 'presente') /
        NULLIF(COUNT(DISTINCT att.athlete_id), 0),
        2
      ) AS attendance_rate,

      -- Métricas de Carga (R22, RP6)
      ROUND(AVG(wp.minutes) FILTER (WHERE att.status = 'presente'), 1) AS avg_minutes,
      ROUND(AVG(wp.rpe) FILTER (WHERE att.status = 'presente'), 1) AS avg_rpe,
      ROUND(AVG(wp.internal_load) FILTER (WHERE att.status = 'presente'), 0) AS avg_internal_load,

      -- Desvio padrão de carga (identifica variação individual)
      ROUND(STDDEV(wp.internal_load) FILTER (WHERE att.status = 'presente'), 0) AS stddev_internal_load,

      -- Atletas com carga registrada
      COUNT(*) FILTER (
        WHERE att.status = 'presente'
          AND wp.minutes IS NOT NULL
          AND wp.rpe IS NOT NULL
      ) AS load_ok_count,

      -- % de dados completos
      ROUND(
        100.0 * COUNT(*) FILTER (WHERE att.status = 'presente' AND wp.minutes IS NOT NULL AND wp.rpe IS NOT NULL) /
        NULLIF(COUNT(*) FILTER (WHERE att.status = 'presente'), 0),
        2
      ) AS data_completeness_pct,

      -- Fadiga e Humor Médios (wellness post)
      ROUND(AVG(wp.fatigue_after) FILTER (WHERE att.status = 'presente'), 1) AS avg_fatigue_after,
      ROUND(AVG(wp.mood_after) FILTER (WHERE att.status = 'presente'), 1) AS avg_mood_after,

      -- Timestamps
      ts.created_at,
      ts.updated_at

    FROM training_sessions ts
    LEFT JOIN attendance att ON att.session_id = ts.id
    LEFT JOIN wellness_post wp ON wp.session_id = ts.id AND wp.athlete_id = att.athlete_id
    GROUP BY ts.id, ts.organization_id, ts.season_id, ts.team_id, ts.session_at,
             ts.main_objective, ts.planned_load, ts.group_climate, ts.created_at, ts.updated_at;

    -- Índices para performance
    CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_training_performance_session
      ON mv_training_performance(session_id);
    CREATE INDEX IF NOT EXISTS idx_mv_training_performance_org_season
      ON mv_training_performance(organization_id, season_id);
    CREATE INDEX IF NOT EXISTS idx_mv_training_performance_team
      ON mv_training_performance(team_id);
    CREATE INDEX IF NOT EXISTS idx_mv_training_performance_date
      ON mv_training_performance(session_at DESC);

    -- COMMENT (documentação)
    COMMENT ON MATERIALIZED VIEW mv_training_performance IS
    'Agregados de performance de treinos (R18, R22, RP5, RP6).
    Atualizar via REFRESH MATERIALIZED VIEW CONCURRENTLY mv_training_performance.';
    """))


def downgrade() -> None:
    """Remove materialized view mv_training_performance"""
    op.execute(sa.text("DROP MATERIALIZED VIEW IF EXISTS mv_training_performance CASCADE"))