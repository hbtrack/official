"""
Service para relatórios de treino

Referências RAG:
- R18: Treinos editáveis dentro dos limites
- R22: Métricas operacionais
- RP5: Ausência = carga 0
- RP6: Participação = métricas obrigatórias
"""
from sqlalchemy import select, func, text, and_, or_
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date, datetime, timedelta
from uuid import UUID

from app.schemas.reports.training import (
    TrainingPerformanceReport,
    TrainingPerformanceMetrics,
    TrainingPerformanceFilters,
    TrainingPerformanceTrend
)


class TrainingReportService:
    """Service para relatórios de performance de treino"""

    @staticmethod
    def get_training_performance(
        db: Session,
        filters: TrainingPerformanceFilters
    ) -> list[TrainingPerformanceReport]:
        """
        Lista relatórios de performance de treinos com filtros

        Referências:
        - R18: Treinos como eventos operacionais
        - R22: Métricas de carga, PSE, assiduidade

        Args:
            db: Sessão do banco
            filters: Filtros de busca

        Returns:
            Lista de TrainingPerformanceReport
        """
        # Query na materialized view
        query = text("""
            SELECT
                session_id,
                organization_id,
                season_id,
                team_id,
                session_at,
                main_objective,
                planned_load,
                group_climate,
                total_athletes,
                presentes,
                ausentes,
                dm,
                lesionadas,
                attendance_rate,
                avg_minutes,
                avg_rpe,
                avg_internal_load,
                stddev_internal_load,
                load_ok_count,
                data_completeness_pct,
                avg_fatigue_after,
                avg_mood_after,
                created_at,
                updated_at
            FROM mv_training_performance
            WHERE organization_id = :org_id
              AND (:season_id IS NULL OR season_id = :season_id)
              AND (:team_id IS NULL OR team_id = :team_id)
              AND (:start_date IS NULL OR session_at >= :start_date)
              AND (:end_date IS NULL OR session_at <= :end_date)
              AND (:min_attendance IS NULL OR attendance_rate >= :min_attendance)
            ORDER BY session_at DESC
            LIMIT :limit OFFSET :skip
        """)

        result = db.execute(query, {
            "org_id": str(filters.organization_id),
            "season_id": str(filters.season_id) if filters.season_id else None,
            "team_id": str(filters.team_id) if filters.team_id else None,
            "start_date": filters.start_date,
            "end_date": filters.end_date,
            "min_attendance": filters.min_attendance_rate,
            "skip": filters.skip,
            "limit": filters.limit
        })

        reports = []
        for row in result:
            metrics = TrainingPerformanceMetrics(
                total_athletes=row.total_athletes,
                presentes=row.presentes,
                ausentes=row.ausentes,
                dm=row.dm,
                lesionadas=row.lesionadas,
                attendance_rate=row.attendance_rate,
                avg_minutes=row.avg_minutes,
                avg_rpe=row.avg_rpe,
                avg_internal_load=row.avg_internal_load,
                stddev_internal_load=row.stddev_internal_load,
                load_ok_count=row.load_ok_count,
                data_completeness_pct=row.data_completeness_pct,
                avg_fatigue_after=row.avg_fatigue_after,
                avg_mood_after=row.avg_mood_after
            )

            report = TrainingPerformanceReport(
                session_id=row.session_id,
                organization_id=row.organization_id,
                season_id=row.season_id,
                team_id=row.team_id,
                session_at=row.session_at,
                main_objective=row.main_objective,
                planned_load=row.planned_load,
                group_climate=row.group_climate,
                metrics=metrics,
                created_at=row.created_at,
                updated_at=row.updated_at
            )
            reports.append(report)

        return reports

    @staticmethod
    def get_training_trends(
        db: Session,
        organization_id: UUID,
        season_id: Optional[UUID],
        team_id: Optional[UUID],
        period: str = "week"  # 'week' ou 'month'
    ) -> list[TrainingPerformanceTrend]:
        """
        Calcula tendências de performance ao longo do tempo

        Referências:
        - R21: Estatísticas agregadas são derivadas
        - R22: Métricas de treino

        Args:
            db: Sessão
            organization_id: ID da organização
            season_id: ID da temporada (opcional)
            team_id: ID da equipe (opcional)
            period: Período de agregação ('week' ou 'month')

        Returns:
            Lista de tendências por período
        """
        # Determinar função de agregação temporal
        date_trunc = "week" if period == "week" else "month"

        query = text(f"""
            WITH periods AS (
                SELECT
                    date_trunc('{date_trunc}', session_at) AS period_start,
                    date_trunc('{date_trunc}', session_at) +
                        interval '1 {date_trunc}' - interval '1 day' AS period_end,
                    COUNT(*) AS sessions_count,
                    ROUND(AVG(attendance_rate), 2) AS avg_attendance_rate,
                    ROUND(AVG(avg_internal_load), 1) AS avg_internal_load,
                    ROUND(AVG(avg_fatigue_after), 1) AS avg_fatigue,
                    ROUND(AVG(avg_mood_after), 1) AS avg_mood
                FROM mv_training_performance
                WHERE organization_id = :org_id
                  AND (:season_id IS NULL OR season_id = :season_id)
                  AND (:team_id IS NULL OR team_id = :team_id)
                GROUP BY date_trunc('{date_trunc}', session_at)
                ORDER BY period_start DESC
                LIMIT 12  -- Últimas 12 semanas/meses
            )
            SELECT * FROM periods
        """)

        result = db.execute(query, {
            "org_id": str(organization_id),
            "season_id": str(season_id) if season_id else None,
            "team_id": str(team_id) if team_id else None
        })

        trends = []
        for row in result:
            trend = TrainingPerformanceTrend(
                period=period,
                period_start=row.period_start.date(),
                period_end=row.period_end.date(),
                sessions_count=row.sessions_count,
                avg_attendance_rate=row.avg_attendance_rate,
                avg_internal_load=row.avg_internal_load,
                avg_fatigue=row.avg_fatigue,
                avg_mood=row.avg_mood
            )
            trends.append(trend)

        return trends

    @staticmethod
    def refresh_materialized_view(db: Session) -> dict:
        """
        Atualiza materialized view de performance de treinos

        Referências:
        - R21: Estatísticas agregadas recalculáveis

        Returns:
            Status da atualização
        """
        try:
            db.execute(text("REFRESH MATERIALIZED VIEW CONCURRENTLY mv_training_performance"))
            db.commit()
            return {
                "status": "success",
                "view": "mv_training_performance",
                "refreshed_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            db.rollback()
            return {
                "status": "error",
                "view": "mv_training_performance",
                "error": str(e)
            }