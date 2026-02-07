"""
Serviço de relatórios consolidados.

Referências RAG:
- R17: Treinos como eventos operacionais
- R19: Estatísticas primárias vinculadas a jogo + equipe
- R20: Estatísticas agregadas derivadas
- R21: Métricas de treino (carga, PSE, assiduidade)
- RP5: Ausência = carga 0
- RP6: Participação = métricas obrigatórias

Cache:
- TTL de 120s para reduzir carga no DB
- Invalidado em writes de attendance, training_sessions, wellness_post
"""
from datetime import date, timedelta
from typing import Optional, List
from uuid import UUID

from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import Session

from app.models.athlete import Athlete
from app.models.team import Team
from app.models.season import Season
from app.models.team_registration import TeamRegistration
from app.models.training_session import TrainingSession
from app.models.attendance import Attendance
from app.models.wellness_post import WellnessPost
from app.schemas.reports.consolidated import (
    AthleteAttendanceRecord,
    AttendanceReportResponse,
    AthleteMinutesRecord,
    MinutesReportResponse,
    AthleteLoadRecord,
    LoadReportResponse,
)
from app.core.cache import (
    make_report_key,
    get_cached_report,
    set_cached_report,
)
from app.schemas.reports.consolidated import PaginationMeta


# =============================================================================
# HELPERS DE ORDENAÇÃO
# =============================================================================

def _sort_records(records: list, order_by: str | None, order_dir: str, default_field: str):
    """
    Ordena lista de records em memória.
    
    Args:
        records: Lista de records (Pydantic models)
        order_by: Campo para ordenar
        order_dir: Direção (asc/desc)
        default_field: Campo padrão se order_by não for válido
    """
    effective_field = order_by if order_by and hasattr(records[0], order_by) else default_field
    reverse = order_dir == "desc"
    return sorted(records, key=lambda x: getattr(x, effective_field, 0), reverse=reverse)


def _paginate_records(records: list, page: int, page_size: int) -> tuple[list, PaginationMeta]:
    """
    Aplica paginação em memória.
    
    Returns:
        Tupla (records_paginados, metadata)
    """
    total = len(records)
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    
    start = (page - 1) * page_size
    end = start + page_size
    paginated = records[start:end]
    
    pagination = PaginationMeta(
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
    )
    return paginated, pagination


class ConsolidatedReportService:
    """Serviço para relatórios consolidados."""

    @staticmethod
    def get_attendance_report(
        db: Session,
        team_id: UUID,
        organization_id: UUID,
        season_id: Optional[UUID] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        page: int = 1,
        page_size: int = 25,
        order_by: Optional[str] = None,
        order_dir: str = "desc",
    ) -> AttendanceReportResponse:
        """
        Relatório de assiduidade por atleta.
        
        Consistência: contagem = treinos no período
        Cache: TTL 120s (chave inclui paginação/ordenação)
        """
        # Check cache (inclui paginação/ordenação na chave)
        cache_key = make_report_key(
            "attendance",
            team_id=team_id,
            organization_id=organization_id,
            season_id=season_id,
            start_date=start_date,
            end_date=end_date,
            page=page,
            page_size=page_size,
            order_by=order_by,
            order_dir=order_dir,
        )
        cached = get_cached_report(cache_key)
        if cached:
            return cached
        
        # Buscar equipe
        team = db.get(Team, str(team_id))
        if not team or str(team.organization_id) != str(organization_id):
            raise ValueError("team_not_found_or_out_of_scope")
        
        # Buscar temporada se informada
        season_name = None
        if season_id:
            season = db.get(Season, str(season_id))
            if season:
                season_name = season.name
                if not start_date:
                    start_date = season.start_date
                if not end_date:
                    end_date = season.end_date
        
        # Default: últimos 30 dias
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Buscar atletas com registro ativo na equipe
        athletes_query = (
            select(Athlete, TeamRegistration)
            .join(TeamRegistration, TeamRegistration.athlete_id == Athlete.id)
            .where(
                TeamRegistration.team_id == team_id,
                TeamRegistration.deleted_at.is_(None),
                or_(
                    TeamRegistration.end_at.is_(None),
                    TeamRegistration.end_at >= start_date
                ),
                Athlete.deleted_at.is_(None),
            )
        )
        athletes_data = db.execute(athletes_query).all()
        
        # Contar treinos no período
        training_count_query = (
            select(func.count(TrainingSession.id))
            .where(
                TrainingSession.team_id == team_id,
                TrainingSession.deleted_at.is_(None),
                TrainingSession.session_at >= start_date,
                TrainingSession.session_at <= end_date,
            )
        )
        if season_id:
            training_count_query = training_count_query.where(
                TrainingSession.season_id == season_id
            )
        total_training_sessions = db.execute(training_count_query).scalar() or 0
        
        # Match attendance removido (tabela inexistente no schema canônico)
        total_matches = 0
        
        # Calcular assiduidade por atleta
        athlete_records = []
        for athlete, reg in athletes_data:
            # Presenças em treinos
            training_present = db.execute(
                select(func.count(Attendance.id))
                .join(TrainingSession, TrainingSession.id == Attendance.training_session_id)
                .where(
                    Attendance.athlete_id == athlete.id,
                    Attendance.deleted_at.is_(None),
                    Attendance.presence_status == "present",
                    TrainingSession.team_id == team_id,
                    TrainingSession.session_at >= start_date,
                    TrainingSession.session_at <= end_date,
                )
            ).scalar() or 0
            
            training_absent = total_training_sessions - training_present
            training_rate = (training_present / total_training_sessions * 100) if total_training_sessions > 0 else 0
            
            matches_played = 0
            matches_not_played = 0
            match_rate = 0
            
            # Taxa combinada
            total_activities = total_training_sessions
            total_present = training_present
            combined_rate = (total_present / total_activities * 100) if total_activities > 0 else 0
            
            athlete_records.append(AthleteAttendanceRecord(
                athlete_id=athlete.id,
                athlete_name=athlete.athlete_name,
                total_training_sessions=total_training_sessions,
                training_sessions_present=training_present,
                training_sessions_absent=training_absent,
                training_attendance_rate=round(training_rate, 1),
                total_matches=total_matches,
                matches_played=matches_played,
                matches_not_played=matches_not_played,
                match_participation_rate=round(match_rate, 1),
                combined_attendance_rate=round(combined_rate, 1),
            ))
        
        # Ordenar (default: combined_attendance_rate desc para destacar problemas)
        if athlete_records:
            athlete_records = _sort_records(
                athlete_records, 
                order_by, 
                order_dir, 
                default_field="combined_attendance_rate"
            )
        
        # Paginar
        paginated_athletes, pagination = _paginate_records(athlete_records, page, page_size)
        
        result = AttendanceReportResponse(
            team_id=team_id,
            team_name=team.name,
            season_id=season_id,
            season_name=season_name,
            period_start=start_date,
            period_end=end_date,
            total_training_sessions=total_training_sessions,
            total_matches=total_matches,
            athletes=paginated_athletes,
            pagination=pagination,
        )
        
        # Cache result
        set_cached_report(cache_key, result)
        return result

    @staticmethod
    def get_minutes_report(
        db: Session,
        team_id: UUID,
        organization_id: UUID,
        season_id: Optional[UUID] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        page: int = 1,
        page_size: int = 25,
        order_by: Optional[str] = None,
        order_dir: str = "desc",
    ) -> MinutesReportResponse:
        """
        Relatório de minutos por atleta.
        
        Soma de minutes_effective de attendance.
        Cache: TTL 120s (chave inclui paginação/ordenação)
        """
        # Check cache (inclui paginação/ordenação na chave)
        cache_key = make_report_key(
            "minutes",
            team_id=team_id,
            organization_id=organization_id,
            season_id=season_id,
            start_date=start_date,
            end_date=end_date,
            page=page,
            page_size=page_size,
            order_by=order_by,
            order_dir=order_dir,
        )
        cached = get_cached_report(cache_key)
        if cached:
            return cached
        
        # Buscar equipe
        team = db.get(Team, str(team_id))
        if not team or str(team.organization_id) != str(organization_id):
            raise ValueError("team_not_found_or_out_of_scope")
        
        # Buscar temporada
        season_name = None
        if season_id:
            season = db.get(Season, str(season_id))
            if season:
                season_name = season.name
                if not start_date:
                    start_date = season.start_date
                if not end_date:
                    end_date = season.end_date
        
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Buscar atletas
        athletes_query = (
            select(Athlete, TeamRegistration)
            .join(TeamRegistration, TeamRegistration.athlete_id == Athlete.id)
            .where(
                TeamRegistration.team_id == team_id,
                TeamRegistration.deleted_at.is_(None),
                or_(
                    TeamRegistration.end_at.is_(None),
                    TeamRegistration.end_at >= start_date
                ),
                Athlete.deleted_at.is_(None),
            )
        )
        athletes_data = db.execute(athletes_query).all()
        
        athlete_records = []
        for athlete, reg in athletes_data:
            total_matches = 0
            matches_played = 0
            matches_started = 0
            total_minutes_played = 0
            avg_minutes_match = 0
            
            # Minutos em treinos
            training_stats = db.execute(
                select(
                    func.count(Attendance.id).label("total_sessions"),
                    func.coalesce(func.sum(Attendance.minutes_effective), 0).label("total_minutes"),
                )
                .join(TrainingSession, TrainingSession.id == Attendance.training_session_id)
                .where(
                    Attendance.athlete_id == athlete.id,
                    Attendance.deleted_at.is_(None),
                    Attendance.presence_status == "present",
                    TrainingSession.team_id == team_id,
                    TrainingSession.session_at >= start_date,
                    TrainingSession.session_at <= end_date,
                )
            ).first()
            
            total_training_sessions = training_stats.total_sessions or 0
            total_training_minutes = training_stats.total_minutes or 0
            avg_training_minutes = total_training_minutes / total_training_sessions if total_training_sessions > 0 else 0
            
            athlete_records.append(AthleteMinutesRecord(
                athlete_id=athlete.id,
                athlete_name=athlete.athlete_name,
                total_matches=total_matches,
                matches_played=matches_played,
                matches_started=matches_started,
                total_minutes_played=total_minutes_played,
                avg_minutes_per_match=round(avg_minutes_match, 1),
                total_training_sessions=total_training_sessions,
                total_training_minutes=total_training_minutes,
                avg_training_minutes=round(avg_training_minutes, 1),
                total_activity_minutes=total_training_minutes,
            ))
        
        # Ordenar (default: total_activity_minutes desc)
        if athlete_records:
            athlete_records = _sort_records(
                athlete_records,
                order_by,
                order_dir,
                default_field="total_activity_minutes"
            )
        
        # Paginar
        paginated_athletes, pagination = _paginate_records(athlete_records, page, page_size)
        
        result = MinutesReportResponse(
            team_id=team_id,
            team_name=team.name,
            season_id=season_id,
            season_name=season_name,
            period_start=start_date,
            period_end=end_date,
            athletes=paginated_athletes,
            pagination=pagination,
        )
        
        # Cache result
        set_cached_report(cache_key, result)
        return result

    @staticmethod
    def get_load_report(
        db: Session,
        team_id: UUID,
        organization_id: UUID,
        season_id: Optional[UUID] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        load_threshold_daily: float = 500,
        load_threshold_weekly: float = 3000,
        page: int = 1,
        page_size: int = 25,
        order_by: Optional[str] = None,
        order_dir: str = "desc",
    ) -> LoadReportResponse:
        """
        Relatório de carga por período.
        
        Carga = RPE × minutos (treino).
        Cache: TTL 120s (chave inclui paginação/ordenação)
        """
        # Check cache (inclui paginação/ordenação na chave)
        cache_key = make_report_key(
            "load",
            team_id=team_id,
            organization_id=organization_id,
            season_id=season_id,
            start_date=start_date,
            end_date=end_date,
            page=page,
            page_size=page_size,
            order_by=order_by,
            order_dir=order_dir,
        )
        cached = get_cached_report(cache_key)
        if cached:
            return cached
        
        # Buscar equipe
        team = db.get(Team, str(team_id))
        if not team or str(team.organization_id) != str(organization_id):
            raise ValueError("team_not_found_or_out_of_scope")
        
        # Buscar temporada
        season_name = None
        if season_id:
            season = db.get(Season, str(season_id))
            if season:
                season_name = season.name
                if not start_date:
                    start_date = season.start_date
                if not end_date:
                    end_date = season.end_date
        
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=7)
        
        period_days = (end_date - start_date).days + 1
        
        # Buscar atletas
        athletes_query = (
            select(Athlete, TeamRegistration)
            .join(TeamRegistration, TeamRegistration.athlete_id == Athlete.id)
            .where(
                TeamRegistration.team_id == team_id,
                TeamRegistration.deleted_at.is_(None),
                or_(
                    TeamRegistration.end_at.is_(None),
                    TeamRegistration.end_at >= start_date
                ),
                Athlete.deleted_at.is_(None),
            )
        )
        athletes_data = db.execute(athletes_query).all()
        
        athlete_records = []
        team_total_load = 0
        athletes_overloaded = 0
        
        for athlete, reg in athletes_data:
            # Carga de treino (RPE × minutos)
            training_load_query = (
                select(
                    func.count(Attendance.id).label("sessions"),
                    func.coalesce(
                        func.sum(
                            func.coalesce(Attendance.minutes_effective, 0) *
                            func.coalesce(WellnessPost.session_rpe, 5)  # Default RPE = 5
                        ), 0
                    ).label("load"),
                )
                .join(TrainingSession, TrainingSession.id == Attendance.training_session_id)
                .outerjoin(
                    WellnessPost,
                    and_(
                        WellnessPost.training_session_id == Attendance.training_session_id,
                        WellnessPost.athlete_id == Attendance.athlete_id,
                        WellnessPost.deleted_at.is_(None),
                    )
                )
                .where(
                    Attendance.athlete_id == athlete.id,
                    Attendance.deleted_at.is_(None),
                    Attendance.presence_status == "present",
                    TrainingSession.team_id == team_id,
                    TrainingSession.session_at >= start_date,
                    TrainingSession.session_at <= end_date,
                )
            )
            training_stats = db.execute(training_load_query).first()
            
            training_sessions = training_stats.sessions or 0
            training_load = float(training_stats.load or 0)
            training_load_avg = training_load / training_sessions if training_sessions > 0 else 0
            
            matches = 0
            match_load = 0.0
            match_load_avg = 0.0
            
            # Totais
            total_load = training_load
            avg_daily_load = total_load / period_days if period_days > 0 else 0
            
            # Verificar sobrecarga
            is_overloaded = avg_daily_load > load_threshold_daily
            if is_overloaded:
                athletes_overloaded += 1
            
            # Determinar tendência (simplificado)
            load_trend = "stable"
            if total_load > load_threshold_weekly:
                load_trend = "high"
            elif total_load < load_threshold_weekly * 0.3:
                load_trend = "low"
            
            team_total_load += total_load
            
            athlete_records.append(AthleteLoadRecord(
                athlete_id=athlete.id,
                athlete_name=athlete.athlete_name,
                training_load_total=round(training_load, 1),
                training_sessions_count=training_sessions,
                training_load_avg=round(training_load_avg, 1),
                match_load_total=round(match_load, 1),
                matches_count=matches,
                match_load_avg=round(match_load_avg, 1),
                total_load=round(total_load, 1),
                avg_daily_load=round(avg_daily_load, 1),
                is_overloaded=is_overloaded,
                load_trend=load_trend,
            ))
        
        # Ordenar (default: total_load desc)
        if athlete_records:
            athlete_records = _sort_records(
                athlete_records,
                order_by,
                order_dir,
                default_field="total_load"
            )
        
        # Paginar
        paginated_athletes, pagination = _paginate_records(athlete_records, page, page_size)
        
        team_avg_load = team_total_load / len(athlete_records) if athlete_records else 0
        
        result = LoadReportResponse(
            team_id=team_id,
            team_name=team.name,
            season_id=season_id,
            season_name=season_name,
            period_start=start_date,
            period_end=end_date,
            period_days=period_days,
            load_threshold_daily=load_threshold_daily,
            load_threshold_weekly=load_threshold_weekly,
            team_avg_load=round(team_avg_load, 1),
            team_total_load=round(team_total_load, 1),
            athletes_overloaded_count=athletes_overloaded,
            athletes=paginated_athletes,
            pagination=pagination,
        )
        
        # Cache result
        set_cached_report(cache_key, result)
        return result
