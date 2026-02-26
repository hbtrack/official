"""
Training Alerts Service - Step 18

Serviço para gerenciamento de alertas automáticos de treinamento.
Integra com NotificationService para envio de WebSocket broadcasts em alertas críticos.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from uuid import UUID
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.training_alert import TrainingAlert
from app.models.training_session import TrainingSession
from app.models.team import Team
from app.models.wellness_pre import WellnessPre
from app.schemas.training_alerts import (
    AlertCreate,
    AlertResponse,
    AlertUpdate,
    AlertStatsResponse,
    AlertFilters
)
from app.services.notification_service import NotificationService


class TrainingAlertsService:
    """Serviço para gerenciamento de alertas de treinamento."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.notification_service = NotificationService(db)
    
    # ========================
    # ALERT GENERATION METHODS
    # ========================
    
    async def check_weekly_overload(
        self,
        team_id: UUID,
        week_start: datetime,
        alert_threshold_multiplier: float = 1.5
    ) -> Optional[AlertResponse]:
        """
        Verifica sobrecarga semanal comparando total_focus_pct da semana vs threshold.
        
        Args:
            team_id: ID da equipe
            week_start: Data de início da semana (segunda-feira)
            alert_threshold_multiplier: Multiplicador do threshold (default 1.5 = 150%)
        
        Returns:
            AlertResponse se alerta criado, None caso contrário
        
        Lógica:
            - Busca todas as sessões da semana (week_start até +7 dias)
            - Soma total_focus_pct de todas as sessões
            - threshold = 100% * 7 sessões * multiplier = 1050% (se multiplier=1.5)
            - Se total > threshold: cria alerta critical
            - Se total > threshold*0.8: cria alerta warning
        """
        week_end = week_start + timedelta(days=7)
        
        # Busca sessões da semana
        stmt = select(TrainingSession).where(
            and_(
                TrainingSession.team_id == team_id,
                TrainingSession.session_at >= week_start,
                TrainingSession.session_at < week_end
            )
        )
        result = await self.db.execute(stmt)
        sessions = result.scalars().all()
        
        if not sessions:
            return None
        
        # Calcula carga total da semana
        total_load = sum(s.total_focus_pct or 0 for s in sessions)
        threshold_base = 100 * len(sessions)  # 100% por sessão
        threshold_critical = threshold_base * alert_threshold_multiplier
        threshold_warning = threshold_critical * 0.8
        
        # Verifica se deve criar alerta
        severity = None
        if total_load > threshold_critical:
            severity = "critical"
        elif total_load > threshold_warning:
            severity = "warning"
        
        if not severity:
            return None
        
        # Verifica se já existe alerta ativo para essa semana
        existing_stmt = select(TrainingAlert).where(
            and_(
                TrainingAlert.team_id == team_id,
                TrainingAlert.alert_type == "weekly_overload",
                TrainingAlert.dismissed_at.is_(None),
                func.date_trunc('week', TrainingAlert.triggered_at) == week_start.date()
            )
        )
        existing_result = await self.db.execute(existing_stmt)
        if existing_result.scalar_one_or_none():
            return None  # Alerta já existe para essa semana
        
        # Cria alerta
        alert_data = AlertCreate(
            team_id=team_id,
            alert_type="weekly_overload",
            severity=severity,
            message=f"Sobrecarga semanal detectada: {total_load:.0f}% (limite {threshold_critical:.0f}%). Risco de overtraining.",
            alert_metadata={
                "total_load": round(total_load, 2),
                "threshold_critical": round(threshold_critical, 2),
                "threshold_warning": round(threshold_warning, 2),
                "week_start": week_start.isoformat(),
                "sessions_count": len(sessions),
                "session_ids": [s.id for s in sessions]
            }
        )
        
        alert = await self.create_alert(alert_data)
        
        # Envia notificação WebSocket se crítico
        if severity == "critical":
            await self._send_critical_notification(alert)
        
        return alert
    
    async def check_wellness_response_rate(
        self,
        team_id: UUID,
        weeks_to_analyze: int = 2,
        min_response_rate: float = 70.0
    ) -> Optional[AlertResponse]:
        """
        Verifica taxa de resposta de wellness nas últimas N semanas.
        
        Args:
            team_id: ID da equipe
            weeks_to_analyze: Número de semanas para analisar
            min_response_rate: Taxa mínima aceitável (%)
        
        Returns:
            AlertResponse se alerta criado, None caso contrário
        
        Lógica:
            - Conta total de treinos das últimas N semanas
            - Conta quantos têm wellness_pre preenchido
            - response_rate = (com_wellness / total) * 100
            - Se rate < min_response_rate: cria alerta warning
        """
        date_cutoff = datetime.now() - timedelta(weeks=weeks_to_analyze)
        
        # Conta total de sessões
        total_stmt = select(func.count(TrainingSession.id)).where(
            and_(
                TrainingSession.team_id == team_id,
                TrainingSession.session_at >= date_cutoff
            )
        )
        total_result = await self.db.execute(total_stmt)
        total_sessions = total_result.scalar() or 0
        
        if total_sessions == 0:
            return None
        
        # Conta sessões com wellness_pre
        wellness_stmt = select(func.count(WellnessPre.id.distinct())).join(
            TrainingSession,
            TrainingSession.id == WellnessPre.training_session_id
        ).where(
            and_(
                TrainingSession.team_id == team_id,
                TrainingSession.session_at >= date_cutoff
            )
        )
        wellness_result = await self.db.execute(wellness_stmt)
        with_wellness = wellness_result.scalar() or 0
        
        response_rate = (with_wellness / total_sessions) * 100 if total_sessions > 0 else 0
        
        if response_rate >= min_response_rate:
            return None
        
        # Verifica se já existe alerta ativo recente (últimas 48h)
        recent_cutoff = datetime.now() - timedelta(hours=48)
        existing_stmt = select(TrainingAlert).where(
            and_(
                TrainingAlert.team_id == team_id,
                TrainingAlert.alert_type == "low_wellness_response",
                TrainingAlert.dismissed_at.is_(None),
                TrainingAlert.triggered_at >= recent_cutoff
            )
        )
        existing_result = await self.db.execute(existing_stmt)
        if existing_result.scalar_one_or_none():
            return None  # Alerta já existe (recente)
        
        # Cria alerta
        alert_data = AlertCreate(
            team_id=team_id,
            alert_type="low_wellness_response",
            severity="warning",
            message=f"Taxa de resposta de wellness baixa: {response_rate:.1f}% (mínimo {min_response_rate}%). Verificar engajamento dos atletas.",
            alert_metadata={
                "response_rate": round(response_rate, 2),
                "min_response_rate": min_response_rate,
                "total_sessions": total_sessions,
                "with_wellness": with_wellness,
                "weeks_analyzed": weeks_to_analyze,
                "period_start": date_cutoff.isoformat()
            }
        )
        
        alert = await self.create_alert(alert_data)
        return alert
    
    # ===============
    # CRUD METHODS
    # ===============
    
    async def create_alert(self, alert_data: AlertCreate) -> AlertResponse:
        """Cria novo alerta no banco."""
        alert = TrainingAlert(
            team_id=alert_data.team_id,
            alert_type=alert_data.alert_type.value,
            severity=alert_data.severity.value,
            message=alert_data.message,
            alert_metadata=alert_data.alert_metadata,
            triggered_at=datetime.now()
        )
        
        self.db.add(alert)
        await self.db.commit()
        await self.db.refresh(alert)
        
        return self._to_response(alert)
    
    async def dismiss_alert(
        self,
        alert_id: UUID,
        user_id: UUID
    ) -> Optional[AlertResponse]:
        """
        Marca alerta como dismissado.
        
        Args:
            alert_id: ID do alerta
            user_id: ID do usuário que dismissou
        
        Returns:
            AlertResponse atualizado ou None se não encontrado
        """
        stmt = select(TrainingAlert).where(TrainingAlert.id == alert_id)
        result = await self.db.execute(stmt)
        alert = result.scalar_one_or_none()
        
        if not alert or alert.dismissed_at is not None:
            return None
        
        alert.dismissed_at = datetime.now()
        alert.dismissed_by_user_id = user_id
        
        await self.db.commit()
        await self.db.refresh(alert)
        
        return self._to_response(alert)
    
    async def get_active_alerts(
        self,
        team_id: UUID,
        limit: int = 10
    ) -> list[AlertResponse]:
        """Busca alertas ativos (não dismissados) de uma equipe."""
        stmt = select(TrainingAlert).where(
            and_(
                TrainingAlert.team_id == team_id,
                TrainingAlert.dismissed_at.is_(None)
            )
        ).order_by(desc(TrainingAlert.triggered_at)).limit(limit)
        
        result = await self.db.execute(stmt)
        alerts = result.scalars().all()
        
        return [self._to_response(a) for a in alerts]
    
    async def get_alert_stats(
        self,
        team_id: UUID,
        filters: Optional[AlertFilters] = None
    ) -> AlertStatsResponse:
        """Calcula estatísticas de alertas."""
        base_stmt = select(TrainingAlert).where(TrainingAlert.team_id == team_id)
        
        # Aplica filtros
        if filters:
            if filters.alert_type:
                base_stmt = base_stmt.where(TrainingAlert.alert_type == filters.alert_type.value)
            if filters.severity:
                base_stmt = base_stmt.where(TrainingAlert.severity == filters.severity.value)
            if filters.start_date:
                base_stmt = base_stmt.where(TrainingAlert.triggered_at >= filters.start_date)
            if filters.end_date:
                base_stmt = base_stmt.where(TrainingAlert.triggered_at <= filters.end_date)
        
        # Total
        total_result = await self.db.execute(select(func.count()).select_from(base_stmt.subquery()))
        total = total_result.scalar() or 0
        
        # Active
        active_stmt = base_stmt.where(TrainingAlert.dismissed_at.is_(None))
        active_result = await self.db.execute(select(func.count()).select_from(active_stmt.subquery()))
        active = active_result.scalar() or 0
        
        # Dismissed
        dismissed = total - active
        
        # Critical e Warning (apenas ativos)
        critical_stmt = active_stmt.where(TrainingAlert.severity == "critical")
        critical_result = await self.db.execute(select(func.count()).select_from(critical_stmt.subquery()))
        critical_count = critical_result.scalar() or 0
        
        warning_stmt = active_stmt.where(TrainingAlert.severity == "warning")
        warning_result = await self.db.execute(select(func.count()).select_from(warning_stmt.subquery()))
        warning_count = warning_result.scalar() or 0
        
        # By type
        by_type_stmt = select(
            TrainingAlert.alert_type,
            func.count(TrainingAlert.id).label("count")
        ).where(TrainingAlert.team_id == team_id).group_by(TrainingAlert.alert_type)
        
        if filters:
            if filters.start_date:
                by_type_stmt = by_type_stmt.where(TrainingAlert.triggered_at >= filters.start_date)
            if filters.end_date:
                by_type_stmt = by_type_stmt.where(TrainingAlert.triggered_at <= filters.end_date)
        
        by_type_result = await self.db.execute(by_type_stmt)
        by_type = {row[0]: row[1] for row in by_type_result.all()}
        
        # Recent alerts (5 mais recentes)
        recent_stmt = base_stmt.order_by(desc(TrainingAlert.triggered_at)).limit(5)
        recent_result = await self.db.execute(recent_stmt)
        recent_alerts = [self._to_response(a) for a in recent_result.scalars().all()]
        
        return AlertStatsResponse(
            total=total,
            active=active,
            dismissed=dismissed,
            critical_count=critical_count,
            warning_count=warning_count,
            by_type=by_type,
            recent_alerts=recent_alerts
        )
    
    # ====================
    # NOTIFICATION METHODS
    # ====================
    
    async def _send_critical_notification(self, alert: AlertResponse) -> None:
        """
        Envia notificação WebSocket para alertas críticos.
        
        Args:
            alert: AlertResponse do alerta crítico
        """
        try:
            # Busca coordenadores da equipe para notificar
            team_stmt = select(Team).options(
                selectinload(Team.team_memberships)
            ).where(Team.id == alert.team_id)
            
            team_result = await self.db.execute(team_stmt)
            team = team_result.scalar_one_or_none()
            
            if not team:
                return
            
            # Filtra coordenadores (role=coordinator)
            coordinator_ids = [
                membership.user_id
                for membership in team.team_memberships
                if membership.role == "coordinator"
            ]
            
            if not coordinator_ids:
                return
            
            # Cria notificação via NotificationService
            notification = await self.notification_service.create(
                user_ids=coordinator_ids,
                title="⚠️ Alerta Crítico de Treinamento",
                message=alert.message,
                type="alert",
                entity_type="training_alert",
                entity_id=alert.id,
                metadata={
                    "alert_id": alert.id,
                    "alert_type": alert.alert_type,
                    "severity": alert.severity,
                    "team_id": alert.team_id,
                    **alert.alert_metadata
                }
            )
            
            # Broadcast via WebSocket para todos os coordenadores
            for user_id in coordinator_ids:
                await self.notification_service.broadcast_to_user(
                    user_id=user_id,
                    data={
                        "type": "training_alert",
                        "alert": {
                            "id": alert.id,
                            "team_id": alert.team_id,
                            "alert_type": alert.alert_type,
                            "severity": alert.severity,
                            "message": alert.message,
                            "triggered_at": alert.triggered_at.isoformat()
                        },
                        "notification_id": notification.id
                    }
                )
        
        except Exception as e:
            # Log error mas não falha o alerta
            print(f"Erro ao enviar notificação de alerta crítico {alert.id}: {e}")
    
    # ===============
    # HELPER METHODS
    # ===============
    
    def _to_response(self, alert: TrainingAlert) -> AlertResponse:
        """Converte TrainingAlert ORM para AlertResponse schema."""
        return AlertResponse(
            id=alert.id,
            team_id=alert.team_id,
            alert_type=alert.alert_type,
            severity=alert.severity,
            message=alert.message,
            alert_metadata=alert.alert_metadata,
            triggered_at=alert.triggered_at,
            dismissed_at=alert.dismissed_at,
            dismissed_by_user_id=alert.dismissed_by_user_id,
            is_active=alert.is_active,
            is_dismissed=alert.is_dismissed,
            is_critical=alert.is_critical
        )
