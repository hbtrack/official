"""
Service para relatórios de gerenciamento de lesões

Referências RAG:
- R13: Estados de atleta (lesionada)
- R14: Impacto de estados
- RP7: Rastreamento de casos médicos
"""
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
from uuid import UUID

from app.schemas.reports.medical import (
    MedicalCasesReport,
    MedicalCasesSummaryMetrics,
    MedicalCasesFilters
)


class MedicalReportService:
    """Service para relatórios de casos médicos"""

    @staticmethod
    def get_medical_summary(
        db: Session,
        filters: MedicalCasesFilters
    ) -> Optional[MedicalCasesReport]:
        """
        Retorna resumo de casos médicos

        Referências:
        - R13: Estados de atleta
        - R14: Impacto em participação
        - RP7: Rastreamento médico

        Args:
            db: Sessão do banco
            filters: Filtros de busca

        Returns:
            MedicalCasesReport ou None
        """
        # V1.2: teams NÃO tem season_id (RDB16). Filtrar season via JOIN seasons (RDB8)
        query = text("""
            WITH medical_data AS (
                SELECT
                    mc.id,
                    mc.athlete_id,
                    mc.status,
                    mc.reason,
                    mc.started_at,
                    mc.ended_at,
                    CASE
                        WHEN mc.ended_at IS NOT NULL THEN
                            EXTRACT(epoch FROM (mc.ended_at - mc.started_at)) / 86400
                        ELSE NULL
                    END AS duration_days
                FROM medical_cases mc
                INNER JOIN athletes a ON a.id = mc.athlete_id
                INNER JOIN team_registrations tr ON tr.athlete_id = a.id AND tr.deleted_at IS NULL
                INNER JOIN teams t ON t.id = tr.team_id AND t.deleted_at IS NULL
                LEFT JOIN seasons s ON s.team_id = t.id AND s.deleted_at IS NULL
                WHERE t.organization_id = :org_id
                  AND (:season_id IS NULL OR s.id = :season_id)
                  AND (:team_id IS NULL OR tr.team_id = :team_id)
                  AND (:start_date IS NULL OR mc.started_at >= :start_date)
                  AND (:end_date IS NULL OR mc.started_at <= :end_date)
                  AND (:status IS NULL OR mc.status = :status)
            ),
            top_reasons AS (
                SELECT
                    reason,
                    COUNT(*) AS count
                FROM medical_data
                WHERE reason IS NOT NULL
                GROUP BY reason
                ORDER BY count DESC
                LIMIT 5
            ),
            aggregates AS (
                SELECT
                    COUNT(*) AS total_cases,
                    COUNT(*) FILTER (WHERE status = 'ativo') AS active_cases,
                    COUNT(*) FILTER (WHERE status = 'resolvido') AS resolved_cases,
                    COUNT(DISTINCT athlete_id) AS athletes_affected,
                    COUNT(DISTINCT athlete_id) FILTER (WHERE status = 'ativo') AS athletes_with_active_cases,
                    ROUND(AVG(duration_days) FILTER (WHERE duration_days IS NOT NULL), 1) AS avg_duration_days,
                    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY duration_days) FILTER (WHERE duration_days IS NOT NULL) AS median_duration_days
                FROM medical_data
            )
            SELECT
                agg.*,
                (
                    SELECT json_object_agg(reason, count)
                    FROM top_reasons
                ) AS top_reasons_json
            FROM aggregates agg
        """)

        result = db.execute(query, {
            "org_id": str(filters.organization_id),
            "season_id": str(filters.season_id) if filters.season_id else None,
            "team_id": str(filters.team_id) if filters.team_id else None,
            "start_date": filters.start_date,
            "end_date": filters.end_date,
            "status": filters.status
        }).fetchone()

        # V1.2: Retornar relatório vazio ao invés de None para evitar ResponseValidationError
        if not result or result.total_cases == 0:
            return MedicalCasesReport(
                organization_id=filters.organization_id,
                season_id=filters.season_id,
                team_id=filters.team_id,
                start_date=filters.start_date or date.today(),
                end_date=filters.end_date or date.today(),
                metrics=MedicalCasesSummaryMetrics(
                    total_cases=0,
                    active_cases=0,
                    resolved_cases=0,
                    top_reasons={},
                    athletes_affected=0,
                    athletes_with_history=0,
                    avg_duration_days=None,
                    median_duration_days=None
                )
            )

        # Processar top_reasons
        top_reasons = result.top_reasons_json or {}

        # Construir métricas
        metrics = MedicalCasesSummaryMetrics(
            total_cases=result.total_cases,
            active_cases=result.active_cases or 0,
            resolved_cases=result.resolved_cases or 0,
            top_reasons=top_reasons,
            athletes_affected=result.athletes_with_active_cases or 0,
            athletes_with_history=result.athletes_affected or 0,
            avg_duration_days=result.avg_duration_days,
            median_duration_days=int(result.median_duration_days) if result.median_duration_days else None
        )

        # Construir relatório
        report = MedicalCasesReport(
            organization_id=filters.organization_id,
            season_id=filters.season_id,
            team_id=filters.team_id,
            start_date=filters.start_date or date.today(),
            end_date=filters.end_date or date.today(),
            metrics=metrics
        )

        return report

    @staticmethod
    def get_athlete_medical_history(
        db: Session,
        athlete_id: UUID,
        limit: int = 10
    ) -> list[dict]:
        """
        Retorna histórico médico de uma atleta

        Referências:
        - R13: Estados de atleta
        - RP7: Rastreamento médico

        Args:
            db: Sessão
            athlete_id: ID da atleta
            limit: Limite de registros

        Returns:
            Lista de casos médicos
        """
        query = text("""
            SELECT
                mc.id,
                mc.status,
                mc.reason,
                mc.started_at,
                mc.ended_at,
                mc.notes,
                CASE
                    WHEN mc.ended_at IS NOT NULL THEN
                        EXTRACT(epoch FROM (mc.ended_at - mc.started_at)) / 86400
                    ELSE
                        EXTRACT(epoch FROM (CURRENT_TIMESTAMP - mc.started_at)) / 86400
                END AS duration_days,
                mc.created_at,
                mc.updated_at
            FROM medical_cases mc
            WHERE mc.athlete_id = :athlete_id
            ORDER BY mc.started_at DESC
            LIMIT :limit
        """)

        result = db.execute(query, {
            "athlete_id": str(athlete_id),
            "limit": limit
        })

        cases = []
        for row in result:
            cases.append({
                "id": str(row.id),
                "status": row.status,
                "reason": row.reason,
                "started_at": row.started_at.isoformat() if row.started_at else None,
                "ended_at": row.ended_at.isoformat() if row.ended_at else None,
                "notes": row.notes,
                "duration_days": int(row.duration_days) if row.duration_days else None,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "updated_at": row.updated_at.isoformat() if row.updated_at else None
            })

        return cases