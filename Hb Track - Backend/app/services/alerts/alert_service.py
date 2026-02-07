"""
Serviço de alertas.

Referências RAG:
- R13: Impacto dos estados e flags (injured, suspended_until, load_restricted)
- RP8: Alertas de sobrecarga e fadiga
- R21: Métricas de treino para cálculo de carga

Cache:
- TTL de 120s para reduzir carga no DB
- Invalidado em writes de attendance, wellness_post, athletes, medical_cases
"""
from datetime import date, datetime, timedelta
from typing import Optional, List
from uuid import UUID

from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import Session

from app.models.athlete import Athlete
from app.models.team import Team
from app.models.team_registration import TeamRegistration
from app.models.training_session import TrainingSession
from app.models.attendance import Attendance
from app.models.wellness_post import WellnessPost
from app.models.medical_case import MedicalCase
from app.schemas.alerts import (
    AlertSeverity,
    LoadExcessAlert,
    LoadExcessAlertResponse,
    InjuryReturnAlert,
    InjuryReturnAlertResponse,
)
from app.core.cache import (
    make_report_key,
    get_cached_report,
    set_cached_report,
)


class AlertService:
    """Serviço para alertas do sistema."""
    
    # Limiares configuráveis
    THRESHOLD_LOAD_7D = 3000  # Carga semanal máxima
    THRESHOLD_ACWR_HIGH = 1.5  # ACWR máximo (risco de lesão)
    THRESHOLD_ACWR_LOW = 0.8  # ACWR mínimo (destreinamento)
    THRESHOLD_LOAD_RETURN = 1500  # Carga máxima para atleta retornando

    @staticmethod
    def _calculate_load_7d(
        db: Session,
        athlete_id: UUID,
        team_id: UUID,
        reference_date: date,
    ) -> float:
        """Calcula carga dos últimos 7 dias."""
        start_date = reference_date - timedelta(days=7)
        
        # Carga de treino
        training_load = db.execute(
            select(
                func.coalesce(
                    func.sum(
                        func.coalesce(Attendance.minutes_effective, 0) *
                        func.coalesce(WellnessPost.session_rpe, 5)
                    ), 0
                )
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
                Attendance.athlete_id == athlete_id,
                Attendance.deleted_at.is_(None),
                Attendance.presence_status == "present",
                TrainingSession.team_id == team_id,
                TrainingSession.session_at >= start_date,
                TrainingSession.session_at <= reference_date,
            )
        ).scalar() or 0
        
        return float(training_load)

    @staticmethod
    def _calculate_load_28d(
        db: Session,
        athlete_id: UUID,
        team_id: UUID,
        reference_date: date,
    ) -> float:
        """Calcula carga dos últimos 28 dias (média semanal × 4)."""
        start_date = reference_date - timedelta(days=28)
        
        # Carga de treino
        training_load = db.execute(
            select(
                func.coalesce(
                    func.sum(
                        func.coalesce(Attendance.minutes_effective, 0) *
                        func.coalesce(WellnessPost.session_rpe, 5)
                    ), 0
                )
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
                Attendance.athlete_id == athlete_id,
                Attendance.deleted_at.is_(None),
                Attendance.presence_status == "present",
                TrainingSession.team_id == team_id,
                TrainingSession.session_at >= start_date,
                TrainingSession.session_at <= reference_date,
            )
        ).scalar() or 0
        
        return float(training_load)

    @classmethod
    def get_load_excess_alerts(
        cls,
        db: Session,
        team_id: UUID,
        organization_id: UUID,
        season_id: Optional[UUID] = None,
    ) -> LoadExcessAlertResponse:
        """
        Alertas de excesso de carga.
        
        Baseado em:
        - Carga semanal (7d) vs limiar
        - ACWR (Acute:Chronic Workload Ratio)
        
        Cache: TTL 120s
        """
        # Check cache
        cache_key = make_report_key(
            "alerts_load",
            team_id=team_id,
            organization_id=organization_id,
            season_id=season_id,
        )
        cached = get_cached_report(cache_key)
        if cached:
            return cached
        
        # Buscar equipe
        team = db.get(Team, str(team_id))
        if not team or str(team.organization_id) != str(organization_id):
            raise ValueError("team_not_found_or_out_of_scope")
        
        today = date.today()
        
        # Buscar atletas ativos
        athletes_query = (
            select(Athlete, TeamRegistration)
            .join(TeamRegistration, TeamRegistration.athlete_id == Athlete.id)
            .where(
                TeamRegistration.team_id == team_id,
                TeamRegistration.deleted_at.is_(None),
                TeamRegistration.end_at.is_(None),
                Athlete.deleted_at.is_(None),
                Athlete.state == "ativa",
            )
        )
        athletes_data = db.execute(athletes_query).all()
        
        alerts = []
        athletes_at_risk = 0
        athletes_overloaded = 0
        athletes_underloaded = 0
        
        for athlete, reg in athletes_data:
            load_7d = cls._calculate_load_7d(db, athlete.id, team_id, today)
            load_28d = cls._calculate_load_28d(db, athlete.id, team_id, today)
            avg_load_28d = load_28d / 4 if load_28d > 0 else 0
            
            # ACWR (Acute:Chronic Workload Ratio)
            acwr = load_7d / avg_load_28d if avg_load_28d > 0 else 1.0
            
            # Determinar severidade
            severity = None
            reason = ""
            recommendation = ""
            
            if acwr > cls.THRESHOLD_ACWR_HIGH:
                severity = AlertSeverity.HIGH if acwr > 1.8 else AlertSeverity.MEDIUM
                reason = f"ACWR elevado ({acwr:.2f}) - risco aumentado de lesão"
                recommendation = "Reduzir carga de treino nos próximos dias"
                athletes_overloaded += 1
            elif load_7d > cls.THRESHOLD_LOAD_7D:
                severity = AlertSeverity.MEDIUM
                reason = f"Carga semanal elevada ({load_7d:.0f})"
                recommendation = "Monitorar recuperação e ajustar próximos treinos"
                athletes_at_risk += 1
            elif acwr < cls.THRESHOLD_ACWR_LOW and load_28d > 1000:
                severity = AlertSeverity.LOW
                reason = f"ACWR baixo ({acwr:.2f}) - possível destreinamento"
                recommendation = "Aumentar gradualmente volume de treino"
                athletes_underloaded += 1
            
            if severity:
                alerts.append(LoadExcessAlert(
                    athlete_id=athlete.id,
                    athlete_name=athlete.athlete_name,
                    current_load_7d=round(load_7d, 1),
                    current_load_28d=round(load_28d, 1),
                    avg_load_28d=round(avg_load_28d, 1),
                    acwr=round(acwr, 2),
                    threshold_load_7d=cls.THRESHOLD_LOAD_7D,
                    threshold_acwr_high=cls.THRESHOLD_ACWR_HIGH,
                    threshold_acwr_low=cls.THRESHOLD_ACWR_LOW,
                    severity=severity,
                    reason=reason,
                    recommendation=recommendation,
                    is_load_restricted=athlete.load_restricted,
                ))
        
        # Ordenar por severidade
        severity_order = {AlertSeverity.CRITICAL: 0, AlertSeverity.HIGH: 1, AlertSeverity.MEDIUM: 2, AlertSeverity.LOW: 3}
        alerts.sort(key=lambda x: severity_order.get(x.severity, 4))
        
        result = LoadExcessAlertResponse(
            team_id=team_id,
            team_name=team.name,
            season_id=season_id,
            threshold_load_7d=cls.THRESHOLD_LOAD_7D,
            threshold_acwr_high=cls.THRESHOLD_ACWR_HIGH,
            threshold_acwr_low=cls.THRESHOLD_ACWR_LOW,
            total_athletes=len(athletes_data),
            athletes_at_risk=athletes_at_risk,
            athletes_overloaded=athletes_overloaded,
            athletes_underloaded=athletes_underloaded,
            alerts=alerts,
        )
        
        # Cache result
        set_cached_report(cache_key, result)
        return result

    @classmethod
    def get_injury_return_alerts(
        cls,
        db: Session,
        team_id: UUID,
        organization_id: UUID,
        season_id: Optional[UUID] = None,
    ) -> InjuryReturnAlertResponse:
        """
        Alertas de atletas retornando de lesão.
        
        Identifica:
        - Atletas com injured=true
        - Atletas com medical_restriction=true
        - Atletas com carga recente após período de lesão
        
        Cache: TTL 120s
        """
        # Check cache
        cache_key = make_report_key(
            "alerts_injury",
            team_id=team_id,
            organization_id=organization_id,
            season_id=season_id,
        )
        cached = get_cached_report(cache_key)
        if cached:
            return cached
        
        # Buscar equipe
        team = db.get(Team, str(team_id))
        if not team or str(team.organization_id) != str(organization_id):
            raise ValueError("team_not_found_or_out_of_scope")
        
        today = date.today()
        
        # Buscar atletas ativos ou com flags médicas
        athletes_query = (
            select(Athlete, TeamRegistration)
            .join(TeamRegistration, TeamRegistration.athlete_id == Athlete.id)
            .where(
                TeamRegistration.team_id == team_id,
                TeamRegistration.deleted_at.is_(None),
                TeamRegistration.end_at.is_(None),
                Athlete.deleted_at.is_(None),
                or_(
                    Athlete.injured == True,
                    Athlete.medical_restriction == True,
                    Athlete.state == "ativa",
                ),
            )
        )
        athletes_data = db.execute(athletes_query).all()
        
        alerts = []
        athletes_injured = 0
        athletes_returning = 0
        athletes_with_restriction = 0
        
        for athlete, reg in athletes_data:
            if athlete.injured:
                athletes_injured += 1
            if athlete.medical_restriction:
                athletes_with_restriction += 1
            
            # Buscar caso médico ativo
            medical_case = db.execute(
                select(MedicalCase)
                .where(
                    MedicalCase.athlete_id == athlete.id,
                    MedicalCase.deleted_at.is_(None),
                    MedicalCase.status.in_(["ativo", "em_acompanhamento"]),
                )
                .order_by(MedicalCase.started_at.desc())
            ).scalar_one_or_none()
            
            # Calcular carga recente
            load_7d = cls._calculate_load_7d(db, athlete.id, team_id, today)
            
            # Contar sessões nos últimos 7 dias
            sessions_7d = db.execute(
                select(func.count(Attendance.id))
                .join(TrainingSession, TrainingSession.id == Attendance.training_session_id)
                .where(
                    Attendance.athlete_id == athlete.id,
                    Attendance.deleted_at.is_(None),
                    Attendance.presence_status == "present",
                    TrainingSession.team_id == team_id,
                    TrainingSession.session_at >= today - timedelta(days=7),
                )
            ).scalar() or 0
            
            # Determinar se está retornando
            is_returning = False
            days_since_return = None
            injury_duration = None
            
            if medical_case and medical_case.ended_at:
                # Caso encerrado - atleta retornando
                days_since_return = (today - medical_case.ended_at.date()).days
                injury_duration = (medical_case.ended_at.date() - medical_case.started_at.date()).days
                if days_since_return <= 14:  # 2 semanas de retorno
                    is_returning = True
                    athletes_returning += 1
            
            # Gerar alerta se necessário
            severity = None
            reason = ""
            recommendation = ""
            
            if athlete.injured:
                severity = AlertSeverity.CRITICAL
                reason = "Atleta marcada como lesionada (R13: bloqueio de escalação)"
                recommendation = "Não escalar para treinos/jogos até liberação médica"
            elif is_returning and load_7d > cls.THRESHOLD_LOAD_RETURN:
                severity = AlertSeverity.HIGH
                reason = f"Retornando de lesão com carga elevada ({load_7d:.0f})"
                recommendation = f"Manter carga máxima de {cls.THRESHOLD_LOAD_RETURN} nos primeiros 14 dias"
            elif is_returning:
                severity = AlertSeverity.MEDIUM
                reason = f"Em período de retorno ({days_since_return} dias após alta)"
                recommendation = "Monitorar resposta ao treino e manter progressão gradual"
            elif athlete.medical_restriction:
                severity = AlertSeverity.MEDIUM
                reason = "Atleta com restrição médica ativa"
                recommendation = "Treino adaptado conforme orientação médica"
            
            if severity:
                alerts.append(InjuryReturnAlert(
                    athlete_id=athlete.id,
                    athlete_name=athlete.athlete_name,
                    injured=athlete.injured,
                    medical_restriction=athlete.medical_restriction,
                    injury_start_date=medical_case.started_at.date() if medical_case else None,
                    injury_duration_days=injury_duration,
                    medical_case_reason=medical_case.reason if medical_case else None,
                    load_last_7d=round(load_7d, 1),
                    sessions_last_7d=sessions_7d,
                    is_returning=is_returning,
                    days_since_return=days_since_return,
                    recommended_max_load=cls.THRESHOLD_LOAD_RETURN,
                    severity=severity,
                    reason=reason,
                    recommendation=recommendation,
                ))
        
        # Ordenar por severidade
        severity_order = {AlertSeverity.CRITICAL: 0, AlertSeverity.HIGH: 1, AlertSeverity.MEDIUM: 2, AlertSeverity.LOW: 3}
        alerts.sort(key=lambda x: severity_order.get(x.severity, 4))
        
        result = InjuryReturnAlertResponse(
            team_id=team_id,
            team_name=team.name,
            season_id=season_id,
            total_athletes=len(athletes_data),
            athletes_injured=athletes_injured,
            athletes_returning=athletes_returning,
            athletes_with_restriction=athletes_with_restriction,
            alerts=alerts,
        )
        
        # Cache result
        set_cached_report(cache_key, result)
        return result
