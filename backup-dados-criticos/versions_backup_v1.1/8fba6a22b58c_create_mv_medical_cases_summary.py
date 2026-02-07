"""create_mv_medical_cases_summary

Revision ID: 8fba6a22b58c
Revises: bb97d068b643
Create Date: 2025-12-25 13:42:10.066915

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8fba6a22b58c'
down_revision: Union[str, Sequence[str], None] = 'bb97d068b643'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Cria materialized view mv_medical_cases_summary"""

    op.execute(sa.text("""
    -- ============================================================================
    -- MATERIALIZED VIEW: Resumo de Casos Médicos e Lesões
    -- Referências: R13, R14, RP7
    -- ============================================================================

    CREATE MATERIALIZED VIEW IF NOT EXISTS mv_medical_cases_summary AS
    WITH athlete_medical_data AS (
        -- Dados médicos por atleta
        SELECT
            a.id AS athlete_id,
            a.organization_id,
            a.full_name,
            a.nickname,
            a.position,
            a.state AS current_state,

            -- Obter season_id e team_id atuais através de team_registrations
            (SELECT tr.season_id FROM team_registrations tr WHERE tr.athlete_id = a.id AND tr.deleted_at IS NULL AND tr.end_at IS NULL ORDER BY tr.created_at DESC LIMIT 1) AS current_season_id,
            (SELECT tr.team_id FROM team_registrations tr WHERE tr.athlete_id = a.id AND tr.deleted_at IS NULL AND tr.end_at IS NULL ORDER BY tr.created_at DESC LIMIT 1) AS current_team_id,

            -- Informações do caso médico
            mc.id AS case_id,
            mc.status AS case_status,
            mc.reason AS injury_type,
            mc.started_at AS injury_start_date,
            mc.ended_at AS injury_end_date,

            -- Calcular dias afastada (se ativo, até hoje; se alta, até ended_at)
            CASE
                WHEN mc.status = 'ativo' THEN CURRENT_DATE - mc.started_at
                WHEN mc.status = 'alta' AND mc.ended_at IS NOT NULL THEN mc.ended_at - mc.started_at
                ELSE 0
            END AS days_out,

            -- Histórico de estados
            (SELECT state FROM athlete_states ast WHERE ast.athlete_id = a.id ORDER BY ast.started_at DESC LIMIT 1) AS last_state

        FROM athletes a
        LEFT JOIN medical_cases mc ON mc.athlete_id = a.id AND mc.deleted_at IS NULL
        WHERE a.deleted_at IS NULL
    ),
    athlete_aggregates AS (
        -- Agregações por atleta
        SELECT
            athlete_id,
            organization_id,
            full_name,
            nickname,
            position,
            current_state,
            current_season_id,
            current_team_id,

            -- Métricas de lesões
            COUNT(case_id) AS total_injuries,
            COUNT(case_id) FILTER (WHERE case_status = 'ativo') AS active_injuries,
            ROUND(AVG(days_out), 0) AS avg_days_out,
            SUM(days_out) AS total_days_out,

            -- Contar recorrências (mesmo tipo de lesão)
            COUNT(DISTINCT injury_type) AS injury_types_count,
            COUNT(case_id) FILTER (
                WHERE injury_type IN (
                    SELECT injury_type
                    FROM athlete_medical_data amd2
                    WHERE amd2.athlete_id = athlete_medical_data.athlete_id
                    GROUP BY injury_type
                    HAVING COUNT(*) > 1
                )
            ) AS recurrence_count,

            -- Data da última lesão
            MAX(injury_start_date) AS last_injury_date,

            -- Tipo de lesão mais comum
            (
                SELECT injury_type
                FROM athlete_medical_data amd3
                WHERE amd3.athlete_id = athlete_medical_data.athlete_id
                  AND injury_type IS NOT NULL
                GROUP BY injury_type
                ORDER BY COUNT(*) DESC
                LIMIT 1
            ) AS most_common_injury_type

        FROM athlete_medical_data
        GROUP BY athlete_id, organization_id, full_name, nickname, position, current_state, current_season_id, current_team_id
    ),
    team_aggregates AS (
        -- Agregações por equipe
        SELECT
            organization_id,
            current_season_id AS season_id,
            current_team_id AS team_id,
            'team' AS aggregation_level,

            -- Métricas gerais
            COUNT(DISTINCT athlete_id) AS total_athletes,
            COUNT(DISTINCT athlete_id) FILTER (WHERE total_injuries > 0) AS athletes_with_injuries,
            COUNT(DISTINCT athlete_id) FILTER (WHERE active_injuries > 0) AS athletes_currently_injured,

            -- Estatísticas de lesões
            SUM(total_injuries) AS total_team_injuries,
            SUM(active_injuries) AS active_team_injuries,
            ROUND(AVG(avg_days_out), 0) AS avg_team_days_out,

            -- Taxa de lesionadas (%)
            ROUND(
                100.0 * COUNT(DISTINCT athlete_id) FILTER (WHERE active_injuries > 0) /
                NULLIF(COUNT(DISTINCT athlete_id), 0),
                2
            ) AS injury_rate,

            -- Tipo de lesão mais comum na equipe
            (
                SELECT injury_type
                FROM athlete_medical_data amd
                WHERE amd.current_team_id = aa.current_team_id
                  AND amd.current_season_id = aa.current_season_id
                  AND injury_type IS NOT NULL
                GROUP BY injury_type
                ORDER BY COUNT(*) DESC
                LIMIT 1
            ) AS common_injury_type,

            NULL::uuid AS athlete_id,  -- NULL para agregações de equipe
            NULL::text AS full_name,
            NULL::text AS nickname,
            NULL::text AS position,
            NULL::text AS current_state

        FROM athlete_aggregates aa
        WHERE current_team_id IS NOT NULL AND current_season_id IS NOT NULL
        GROUP BY organization_id, current_season_id, current_team_id
    )
    -- Retornar agregações individuais e de equipe
    SELECT
        athlete_id,
        organization_id,
        current_season_id AS season_id,
        current_team_id AS team_id,
        'athlete' AS aggregation_level,
        full_name,
        nickname,
        position,
        current_state,
        total_injuries,
        active_injuries,
        avg_days_out,
        total_days_out,
        injury_types_count,
        recurrence_count,
        last_injury_date,
        most_common_injury_type AS common_injury_type,
        NULL::bigint AS total_athletes,
        NULL::bigint AS athletes_with_injuries,
        NULL::bigint AS athletes_currently_injured,
        NULL::bigint AS total_team_injuries,
        NULL::bigint AS active_team_injuries,
        NULL::numeric AS avg_team_days_out,
        NULL::numeric AS injury_rate
    FROM athlete_aggregates
    WHERE total_injuries > 0  -- Apenas atletas com lesões

    UNION ALL

    SELECT
        athlete_id,
        organization_id,
        season_id,
        team_id,
        aggregation_level,
        full_name,
        nickname,
        position,
        current_state,
        NULL::bigint AS total_injuries,
        NULL::bigint AS active_injuries,
        NULL::numeric AS avg_days_out,
        NULL::bigint AS total_days_out,
        NULL::bigint AS injury_types_count,
        NULL::bigint AS recurrence_count,
        NULL::date AS last_injury_date,
        common_injury_type,
        total_athletes,
        athletes_with_injuries,
        athletes_currently_injured,
        total_team_injuries,
        active_team_injuries,
        avg_team_days_out,
        injury_rate
    FROM team_aggregates;

    -- Índices para performance
    CREATE INDEX IF NOT EXISTS idx_mv_medical_cases_summary_athlete
      ON mv_medical_cases_summary(athlete_id)
      WHERE aggregation_level = 'athlete';
    CREATE INDEX IF NOT EXISTS idx_mv_medical_cases_summary_org
      ON mv_medical_cases_summary(organization_id);
    CREATE INDEX IF NOT EXISTS idx_mv_medical_cases_summary_team
      ON mv_medical_cases_summary(team_id)
      WHERE aggregation_level = 'team';
    CREATE INDEX IF NOT EXISTS idx_mv_medical_cases_summary_season
      ON mv_medical_cases_summary(season_id);
    CREATE INDEX IF NOT EXISTS idx_mv_medical_cases_summary_composite
      ON mv_medical_cases_summary(organization_id, season_id, team_id, aggregation_level);

    -- COMMENT (documentação)
    COMMENT ON MATERIALIZED VIEW mv_medical_cases_summary IS
    'Resumo de casos médicos e lesões por atleta e equipe (R13, R14, RP7).
    Atualizar via REFRESH MATERIALIZED VIEW CONCURRENTLY mv_medical_cases_summary.';
    """))


def downgrade() -> None:
    """Remove materialized view mv_medical_cases_summary"""
    op.execute(sa.text("DROP MATERIALIZED VIEW IF EXISTS mv_medical_cases_summary CASCADE"))
