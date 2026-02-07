"""
Service para relatórios individuais de atleta

Referências RAG:
- R12: Atleta permanente
- R13/R14: Estados e impactos
- RP4: Escopo de participação
"""
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.schemas.reports.athlete import (
    AthleteIndividualReport,
    AthleteReadinessMetrics,
    AthleteTrainingLoadMetrics,
    AthleteAttendanceMetrics,
    AthleteWellnessMetrics,
    AthleteIndividualFilters
)


class AthleteReportService:
    """Service para relatórios individuais de atleta"""

    @staticmethod
    def get_athlete_report(
        db: Session,
        athlete_id: UUID
    ) -> Optional[AthleteIndividualReport]:
        """
        Retorna relatório individual de uma atleta

        Referências:
        - R12: Atleta permanente no histórico
        - R13/R14: Estados e seus impactos
        - RP4: Escopo da participação

        Args:
            db: Sessão do banco
            athlete_id: ID da atleta

        Returns:
            AthleteIndividualReport ou None
        """
        query = text("""
            SELECT * FROM mv_athlete_training_summary
            WHERE athlete_id = :athlete_id
        """)

        result = db.execute(query, {"athlete_id": str(athlete_id)}).fetchone()

        if not result:
            return None

        # Construir métricas
        readiness = AthleteReadinessMetrics(
            avg_sleep_hours=result.avg_sleep_hours,
            avg_sleep_quality=result.avg_sleep_quality,
            avg_fatigue_pre=result.avg_fatigue_pre,
            avg_stress=result.avg_stress,
            avg_muscle_soreness=result.avg_muscle_soreness,
            last_sleep_hours=result.last_sleep_hours,
            last_fatigue=result.last_fatigue
        )

        training_load = AthleteTrainingLoadMetrics(
            avg_internal_load=result.avg_internal_load,
            avg_rpe=result.avg_rpe,
            avg_minutes=result.avg_minutes,
            load_7d=result.load_7d,
            load_28d=result.load_28d,
            last_internal_load=result.last_internal_load
        )

        attendance = AthleteAttendanceMetrics(
            total_sessions=result.total_sessions,
            sessions_presente=result.sessions_presente,
            sessions_ausente=result.sessions_ausente,
            sessions_dm=result.sessions_dm,
            sessions_lesionada=result.sessions_lesionada,
            attendance_rate=result.attendance_rate
        )

        wellness = AthleteWellnessMetrics(
            avg_fatigue_after=result.avg_fatigue_after,
            avg_mood_after=result.avg_mood_after
        )

        # Construir relatório
        report = AthleteIndividualReport(
            athlete_id=result.athlete_id,
            person_id=result.person_id,
            full_name=result.full_name,
            nickname=result.nickname,
            birth_date=result.birth_date,
            position=result.position,
            current_age=result.current_age,
            expected_category_code=result.expected_category_code,
            current_state=result.current_state,
            current_season_id=result.current_season_id,
            current_team_id=result.current_team_id,
            organization_id=result.organization_id,
            readiness=readiness,
            training_load=training_load,
            attendance=attendance,
            wellness=wellness,
            active_medical_cases=result.active_medical_cases,
            last_session_at=result.last_session_at
        )

        return report

    @staticmethod
    def list_athlete_reports(
        db: Session,
        filters: AthleteIndividualFilters
    ) -> list[AthleteIndividualReport]:
        """
        Lista relatórios individuais de atletas com filtros

        Args:
            db: Sessão
            filters: Filtros de busca

        Returns:
            Lista de AthleteIndividualReport
        """
        query = text("""
            SELECT * FROM mv_athlete_training_summary
            WHERE organization_id = :org_id
              AND (:season_id IS NULL OR current_season_id = :season_id)
              AND (:team_id IS NULL OR current_team_id = :team_id)
              AND (:state IS NULL OR current_state = :state)
              AND (:min_attendance IS NULL OR attendance_rate >= :min_attendance)
            ORDER BY full_name
            LIMIT :limit OFFSET :skip
        """)

        result = db.execute(query, {
            "org_id": str(filters.organization_id),
            "season_id": str(filters.season_id) if filters.season_id else None,
            "team_id": str(filters.team_id) if filters.team_id else None,
            "state": filters.state,
            "min_attendance": filters.min_attendance_rate,
            "skip": filters.skip,
            "limit": filters.limit
        })

        reports = []
        for row in result:
            # Reutilizar lógica de get_athlete_report
            readiness = AthleteReadinessMetrics(
                avg_sleep_hours=row.avg_sleep_hours,
                avg_sleep_quality=row.avg_sleep_quality,
                avg_fatigue_pre=row.avg_fatigue_pre,
                avg_stress=row.avg_stress,
                avg_muscle_soreness=row.avg_muscle_soreness,
                last_sleep_hours=row.last_sleep_hours,
                last_fatigue=row.last_fatigue
            )

            training_load = AthleteTrainingLoadMetrics(
                avg_internal_load=row.avg_internal_load,
                avg_rpe=row.avg_rpe,
                avg_minutes=row.avg_minutes,
                load_7d=row.load_7d,
                load_28d=row.load_28d,
                last_internal_load=row.last_internal_load
            )

            attendance = AthleteAttendanceMetrics(
                total_sessions=row.total_sessions,
                sessions_presente=row.sessions_presente,
                sessions_ausente=row.sessions_ausente,
                sessions_dm=row.sessions_dm,
                sessions_lesionada=row.sessions_lesionada,
                attendance_rate=row.attendance_rate
            )

            wellness = AthleteWellnessMetrics(
                avg_fatigue_after=row.avg_fatigue_after,
                avg_mood_after=row.avg_mood_after
            )

            report = AthleteIndividualReport(
                athlete_id=row.athlete_id,
                person_id=row.person_id,
                full_name=row.full_name,
                nickname=row.nickname,
                birth_date=row.birth_date,
                position=row.position,
                current_age=row.current_age,
                expected_category_code=row.expected_category_code,
                current_state=row.current_state,
                current_season_id=row.current_season_id,
                current_team_id=row.current_team_id,
                organization_id=row.organization_id,
                readiness=readiness,
                training_load=training_load,
                attendance=attendance,
                wellness=wellness,
                active_medical_cases=row.active_medical_cases,
                last_session_at=row.last_session_at
            )
            reports.append(report)

        return reports