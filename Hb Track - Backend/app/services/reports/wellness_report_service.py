"""
Service para relatórios de prontidão e bem-estar

Referências RAG:
- RP6: Wellness pré e pós-treino obrigatórios
- RP7: Escalas padronizadas
- RP8: Alertas de sobrecarga
"""
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
from uuid import UUID

from app.schemas.reports.wellness import (
    WellnessSummaryReport,
    WellnessSummaryMetrics,
    WellnessSummaryFilters
)


class WellnessReportService:
    """Service para relatórios de wellness"""

    @staticmethod
    def get_wellness_summary(
        db: Session,
        filters: WellnessSummaryFilters
    ) -> Optional[WellnessSummaryReport]:
        """
        Retorna resumo de bem-estar para período e equipe

        Referências:
        - RP6: Wellness obrigatório
        - RP7: Escalas padronizadas
        - RP8: Alertas de sobrecarga

        Args:
            db: Sessão do banco
            filters: Filtros de busca

        Returns:
            WellnessSummaryReport ou None
        """
        # Query agregando wellness pré e pós-treino
        query = text("""
            WITH wellness_data AS (
                SELECT
                    a.id AS athlete_id,
                    wpre.sleep_hours,
                    wpre.sleep_quality,
                    wpre.fatigue_pre,
                    wpre.stress_level AS stress,
                    wpre.muscle_soreness,
                    wpst.fatigue_after,
                    wpst.mood_after
                FROM athletes a
                INNER JOIN team_registrations tr ON tr.athlete_id = a.id AND tr.deleted_at IS NULL
                INNER JOIN teams t ON t.id = tr.team_id AND t.deleted_at IS NULL
                LEFT JOIN attendance att ON att.athlete_id = a.id
                LEFT JOIN training_sessions ts ON ts.id = att.training_session_id
                LEFT JOIN wellness_pre wpre ON wpre.training_session_id = ts.id AND wpre.athlete_id = a.id
                LEFT JOIN wellness_post wpst ON wpst.training_session_id = ts.id AND wpst.athlete_id = a.id
                WHERE t.organization_id = :org_id
                  AND a.deleted_at IS NULL
                  AND ts.deleted_at IS NULL
                  AND (:season_id IS NULL OR ts.season_id = :season_id)
                  AND (:team_id IS NULL OR ts.team_id = :team_id)
                  AND (:start_date IS NULL OR ts.session_at >= :start_date)
                  AND (:end_date IS NULL OR ts.session_at <= :end_date)
                  AND att.presence_status = 'present'
            ),
            aggregates AS (
                SELECT
                    -- Médias
                    ROUND(AVG(sleep_hours), 1) AS avg_sleep_hours,
                    ROUND(AVG(sleep_quality), 1) AS avg_sleep_quality,
                    ROUND(AVG(fatigue_pre), 1) AS avg_fatigue_pre,
                    ROUND(AVG(stress), 1) AS avg_stress,
                    ROUND(AVG(muscle_soreness), 1) AS avg_muscle_soreness,
                    ROUND(AVG(fatigue_after), 1) AS avg_fatigue_after,
                    ROUND(AVG(mood_after), 1) AS avg_mood_after,

                    -- Alertas (RP8)
                    COUNT(DISTINCT athlete_id) FILTER (WHERE fatigue_pre > 7 OR fatigue_after > 7) AS athletes_high_fatigue,
                    COUNT(DISTINCT athlete_id) FILTER (WHERE sleep_hours < 6 OR sleep_quality < 3) AS athletes_poor_sleep,
                    COUNT(DISTINCT athlete_id) FILTER (WHERE stress > 7) AS athletes_high_stress,

                    -- Completude
                    COUNT(DISTINCT athlete_id) AS total_athletes,
                    COUNT(DISTINCT athlete_id) FILTER (
                        WHERE sleep_hours IS NOT NULL
                           OR sleep_quality IS NOT NULL
                           OR fatigue_pre IS NOT NULL
                    ) AS athletes_with_wellness
                FROM wellness_data
            )
            SELECT
                *,
                ROUND(
                    100.0 * athletes_with_wellness / NULLIF(total_athletes, 0),
                    2
                ) AS data_completeness_pct
            FROM aggregates
        """)

        result = db.execute(query, {
            "org_id": str(filters.organization_id),
            "season_id": str(filters.season_id) if filters.season_id else None,
            "team_id": str(filters.team_id) if filters.team_id else None,
            "start_date": filters.start_date,
            "end_date": filters.end_date
        }).fetchone()

        # V1.2: Retornar relatório vazio ao invés de None para evitar ResponseValidationError
        if not result or result.total_athletes == 0:
            return WellnessSummaryReport(
                organization_id=filters.organization_id,
                season_id=filters.season_id,
                team_id=filters.team_id,
                start_date=filters.start_date or date.today(),
                end_date=filters.end_date or date.today(),
                metrics=WellnessSummaryMetrics(
                    avg_sleep_hours=None,
                    avg_sleep_quality=None,
                    avg_fatigue_pre=None,
                    avg_stress=None,
                    avg_muscle_soreness=None,
                    avg_fatigue_after=None,
                    avg_mood_after=None,
                    athletes_high_fatigue=0,
                    athletes_poor_sleep=0,
                    athletes_high_stress=0,
                    total_athletes=0,
                    athletes_with_wellness=0,
                    data_completeness_pct=0.0
                )
            )

        # Construir métricas
        metrics = WellnessSummaryMetrics(
            avg_sleep_hours=result.avg_sleep_hours,
            avg_sleep_quality=result.avg_sleep_quality,
            avg_fatigue_pre=result.avg_fatigue_pre,
            avg_stress=result.avg_stress,
            avg_muscle_soreness=result.avg_muscle_soreness,
            avg_fatigue_after=result.avg_fatigue_after,
            avg_mood_after=result.avg_mood_after,
            athletes_high_fatigue=result.athletes_high_fatigue or 0,
            athletes_poor_sleep=result.athletes_poor_sleep or 0,
            athletes_high_stress=result.athletes_high_stress or 0,
            total_athletes=result.total_athletes,
            athletes_with_wellness=result.athletes_with_wellness or 0,
            data_completeness_pct=result.data_completeness_pct or 0.0
        )

        # Construir relatório
        report = WellnessSummaryReport(
            organization_id=filters.organization_id,
            season_id=filters.season_id,
            team_id=filters.team_id,
            start_date=filters.start_date or date.today(),
            end_date=filters.end_date or date.today(),
            metrics=metrics
        )

        return report

    @staticmethod
    def get_wellness_trends(
        db: Session,
        organization_id: UUID,
        season_id: Optional[UUID],
        team_id: Optional[UUID],
        period: str = "week"
    ) -> list[dict]:
        """
        Calcula tendências de wellness ao longo do tempo

        Referências:
        - RP8: Monitoramento de sobrecarga

        Args:
            db: Sessão
            organization_id: ID da organização
            season_id: ID da temporada (opcional)
            team_id: ID da equipe (opcional)
            period: Período ('week' ou 'month')

        Returns:
            Lista de tendências por período
        """
        date_trunc = "week" if period == "week" else "month"

        query = text(f"""
            WITH wellness_data AS (
                SELECT
                    date_trunc('{date_trunc}', ts.session_at) AS period_start,
                    wpre.sleep_hours,
                    wpre.sleep_quality,
                    wpre.fatigue_pre,
                    wpre.stress_level AS stress,
                    wpst.fatigue_after,
                    wpst.mood_after
                FROM training_sessions ts
                LEFT JOIN attendance att ON att.training_session_id = ts.id
                LEFT JOIN wellness_pre wpre ON wpre.training_session_id = ts.id AND wpre.athlete_id = att.athlete_id
                LEFT JOIN wellness_post wpst ON wpst.training_session_id = ts.id AND wpst.athlete_id = att.athlete_id
                WHERE ts.organization_id = :org_id
                  AND ts.deleted_at IS NULL
                  AND (:season_id IS NULL OR ts.season_id = :season_id)
                  AND (:team_id IS NULL OR ts.team_id = :team_id)
                  AND att.presence_status = 'present'
            )
            SELECT
                period_start,
                period_start + interval '1 {date_trunc}' - interval '1 day' AS period_end,
                COUNT(*) AS entries_count,
                ROUND(AVG(sleep_hours), 1) AS avg_sleep_hours,
                ROUND(AVG(sleep_quality), 1) AS avg_sleep_quality,
                ROUND(AVG(fatigue_pre), 1) AS avg_fatigue_pre,
                ROUND(AVG(stress), 1) AS avg_stress,
                ROUND(AVG(fatigue_after), 1) AS avg_fatigue_after,
                ROUND(AVG(mood_after), 1) AS avg_mood_after
            FROM wellness_data
            GROUP BY period_start
            ORDER BY period_start DESC
            LIMIT 12
        """)

        result = db.execute(query, {
            "org_id": str(organization_id),
            "season_id": str(season_id) if season_id else None,
            "team_id": str(team_id) if team_id else None
        })

        trends = []
        for row in result:
            trends.append({
                "period": period,
                "period_start": row.period_start.date(),
                "period_end": row.period_end.date(),
                "entries_count": row.entries_count,
                "avg_sleep_hours": row.avg_sleep_hours,
                "avg_sleep_quality": row.avg_sleep_quality,
                "avg_fatigue_pre": row.avg_fatigue_pre,
                "avg_stress": row.avg_stress,
                "avg_fatigue_after": row.avg_fatigue_after,
                "avg_mood_after": row.avg_mood_after
            })

        return trends