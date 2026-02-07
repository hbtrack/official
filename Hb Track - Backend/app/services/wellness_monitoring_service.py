"""
Service para Monitoramento de Wellness com Scheduled Jobs.

Funcionalidades:
- lock_expired_wellness_daily(): Job diário que bloqueia wellness fora da janela de edição
- check_critical_wellness(): Job diário que detecta wellness crítico e cria alertas

Regras:
- R40: Wellness pré bloqueado após (session_at - 2 hours)
- R40: Wellness pós bloqueado após (created_at + 24 hours)
- RP8: Alertas de sobrecarga e fadiga alta
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any
from uuid import UUID

from sqlalchemy import select, and_, or_, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.wellness_pre import WellnessPre
from app.models.wellness_post import WellnessPost
from app.models.training_session import TrainingSession
from app.models.athlete import Athlete


class WellnessMonitoringService:
    """Service para monitoramento automático de wellness."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def lock_expired_wellness_daily(self) -> Dict[str, int]:
        """
        Job diário que bloqueia wellness fora da janela de edição.
        
        Regras R40:
        - Wellness PRÉ: Lock se session_at - 2 hours < NOW
        - Wellness PÓS: Lock se created_at + 24 hours < NOW
        
        Retorna:
        {
            "locked_pre": 10,
            "locked_post": 15
        }
        """
        now = datetime.utcnow()
        
        # 1. Bloquear wellness PRÉ fora da janela
        # Buscar sessões onde session_at - 2 hours < NOW
        deadline_pre = now - timedelta(hours=2)
        
        session_stmt = select(TrainingSession.id).where(
            TrainingSession.session_at < now + timedelta(hours=2),  # session_at - 2h < now
            TrainingSession.deleted_at.is_(None)
        )
        session_result = await self.db.execute(session_stmt)
        session_ids = [row[0] for row in session_result.all()]
        
        if session_ids:
            pre_update_stmt = (
                update(WellnessPre)
                .where(
                    WellnessPre.training_session_id.in_(session_ids),
                    WellnessPre.locked_at.is_(None),
                    WellnessPre.deleted_at.is_(None)
                )
                .values(locked_at=now, updated_at=now)
            )
            pre_result = await self.db.execute(pre_update_stmt)
            locked_pre = pre_result.rowcount
        else:
            locked_pre = 0
        
        # 2. Bloquear wellness PÓS fora da janela (created_at + 24h < NOW)
        deadline_post = now - timedelta(hours=24)
        
        post_update_stmt = (
            update(WellnessPost)
            .where(
                WellnessPost.created_at < deadline_post,
                WellnessPost.locked_at.is_(None),
                WellnessPost.deleted_at.is_(None)
            )
            .values(locked_at=now, updated_at=now)
        )
        post_result = await self.db.execute(post_update_stmt)
        locked_post = post_result.rowcount
        
        await self.db.commit()
        
        return {
            "locked_pre": locked_pre,
            "locked_post": locked_post,
            "executed_at": now.isoformat()
        }
    
    async def check_critical_wellness(
        self,
        athlete_id: Optional[UUID] = None,
        days_lookback: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Job diário que detecta wellness crítico e cria alertas.
        
        Critérios RP8 (Alertas de sobrecarga e fadiga):
        - Fadiga alta persistente: fatigue_pre >= 8 por 3+ dias consecutivos
        - RPE alto: session_rpe >= 9 por 2+ treinos consecutivos
        - Prontidão baixa: readiness_score <= 3 por 2+ dias
        - Estresse alto: stress_level >= 8 por 3+ dias
        
        Retorna lista de alertas:
        [
            {
                "athlete_id": UUID,
                "alert_type": "high_fatigue_persistent",
                "severity": "high",
                "message": "Fadiga alta por 3 dias consecutivos",
                "metric_values": [8, 9, 8],
                "detected_at": "2026-01-16T10:00:00Z"
            }
        ]
        """
        now = datetime.utcnow()
        lookback_date = now - timedelta(days=days_lookback)
        alerts = []
        
        # 1. Buscar atletas para monitorar
        if athlete_id:
            athlete_ids = [athlete_id]
        else:
            athlete_stmt = select(Athlete.id).where(Athlete.deleted_at.is_(None))
            athlete_result = await self.db.execute(athlete_stmt)
            athlete_ids = [row[0] for row in athlete_result.all()]
        
        for athlete_id in athlete_ids:
            # 2. Buscar wellness PRÉ dos últimos N dias
            pre_stmt = (
                select(WellnessPre)
                .where(
                    WellnessPre.athlete_id == athlete_id,
                    WellnessPre.filled_at >= lookback_date,
                    WellnessPre.deleted_at.is_(None)
                )
                .order_by(WellnessPre.filled_at.desc())
            )
            pre_result = await self.db.execute(pre_stmt)
            wellness_pre_list = list(pre_result.scalars().all())
            
            # 3. Buscar wellness PÓS dos últimos N dias
            post_stmt = (
                select(WellnessPost)
                .where(
                    WellnessPost.athlete_id == athlete_id,
                    WellnessPost.filled_at >= lookback_date,
                    WellnessPost.deleted_at.is_(None)
                )
                .order_by(WellnessPost.filled_at.desc())
            )
            post_result = await self.db.execute(post_stmt)
            wellness_post_list = list(post_result.scalars().all())
            
            # 4. ALERTA: Fadiga alta persistente (fatigue_pre >= 8 por 3+ dias)
            if len(wellness_pre_list) >= 3:
                recent_fatigue = [w.fatigue_pre for w in wellness_pre_list[:3]]
                if all(f >= 8 for f in recent_fatigue):
                    alerts.append({
                        "athlete_id": str(athlete_id),
                        "alert_type": "high_fatigue_persistent",
                        "severity": "high",
                        "message": f"Fadiga alta por {len(recent_fatigue)} registros consecutivos",
                        "metric_values": recent_fatigue,
                        "detected_at": now.isoformat()
                    })
            
            # 5. ALERTA: RPE alto (session_rpe >= 9 por 2+ treinos)
            if len(wellness_post_list) >= 2:
                recent_rpe = [w.session_rpe for w in wellness_post_list[:2]]
                if all(r >= 9 for r in recent_rpe):
                    alerts.append({
                        "athlete_id": str(athlete_id),
                        "alert_type": "high_rpe_persistent",
                        "severity": "high",
                        "message": f"RPE alto por {len(recent_rpe)} treinos consecutivos",
                        "metric_values": recent_rpe,
                        "detected_at": now.isoformat()
                    })
            
            # 6. ALERTA: Prontidão baixa (readiness_score <= 3 por 2+ dias)
            readiness_scores = [w.readiness_score for w in wellness_pre_list[:2] if w.readiness_score is not None]
            if len(readiness_scores) >= 2 and all(r <= 3 for r in readiness_scores):
                alerts.append({
                    "athlete_id": str(athlete_id),
                    "alert_type": "low_readiness_persistent",
                    "severity": "medium",
                    "message": f"Prontidão baixa por {len(readiness_scores)} registros",
                    "metric_values": readiness_scores,
                    "detected_at": now.isoformat()
                })
            
            # 7. ALERTA: Estresse alto (stress_level >= 8 por 3+ dias)
            if len(wellness_pre_list) >= 3:
                recent_stress = [w.stress_level for w in wellness_pre_list[:3]]
                if all(s >= 8 for s in recent_stress):
                    alerts.append({
                        "athlete_id": str(athlete_id),
                        "alert_type": "high_stress_persistent",
                        "severity": "high",
                        "message": f"Estresse alto por {len(recent_stress)} registros consecutivos",
                        "metric_values": recent_stress,
                        "detected_at": now.isoformat()
                    })
            
            # 8. ALERTA: Dor muscular persistente (muscle_soreness >= 7 por 3+ dias)
            if len(wellness_pre_list) >= 3:
                recent_soreness = [w.muscle_soreness for w in wellness_pre_list[:3]]
                if all(s >= 7 for s in recent_soreness):
                    alerts.append({
                        "athlete_id": str(athlete_id),
                        "alert_type": "high_soreness_persistent",
                        "severity": "medium",
                        "message": f"Dor muscular alta por {len(recent_soreness)} registros",
                        "metric_values": recent_soreness,
                        "detected_at": now.isoformat()
                    })
        
        # TODO: Persistir alertas na tabela training_alerts (criada em migration 0036)
        # TODO: Criar notificações in-app para treinadores
        # TODO: Criar medical_cases se flag_medical_followup=true
        
        return alerts
    
    async def get_athlete_wellness_summary(
        self,
        athlete_id: UUID,
        days_lookback: int = 30
    ) -> Dict[str, Any]:
        """
        Retorna resumo de wellness do atleta nos últimos N dias.
        
        Usado para dashboard de treinador e relatórios.
        
        Retorna:
        {
            "athlete_id": UUID,
            "period_days": 30,
            "total_sessions": 20,
            "wellness_pre_filled": 18,
            "wellness_post_filled": 15,
            "response_rate_pre": 90.0,
            "response_rate_post": 75.0,
            "avg_fatigue_pre": 5.2,
            "avg_rpe": 6.8,
            "avg_readiness": 7.1,
            "alerts_count": 2
        }
        """
        now = datetime.utcnow()
        lookback_date = now - timedelta(days=days_lookback)
        
        # 1. Buscar sessões do atleta no período (via attendance)
        from app.models.attendance import Attendance
        attendance_stmt = (
            select(Attendance)
            .join(TrainingSession, Attendance.training_session_id == TrainingSession.id)
            .where(
                Attendance.athlete_id == athlete_id,
                Attendance.presence_status == 'present',
                TrainingSession.session_at >= lookback_date,
                Attendance.deleted_at.is_(None),
                TrainingSession.deleted_at.is_(None)
            )
        )
        attendance_result = await self.db.execute(attendance_stmt)
        attendances = list(attendance_result.scalars().all())
        total_sessions = len(attendances)
        
        # 2. Buscar wellness PRÉ no período
        pre_stmt = (
            select(WellnessPre)
            .where(
                WellnessPre.athlete_id == athlete_id,
                WellnessPre.filled_at >= lookback_date,
                WellnessPre.deleted_at.is_(None)
            )
        )
        pre_result = await self.db.execute(pre_stmt)
        wellness_pre_list = list(pre_result.scalars().all())
        wellness_pre_filled = len(wellness_pre_list)
        
        # 3. Buscar wellness PÓS no período
        post_stmt = (
            select(WellnessPost)
            .where(
                WellnessPost.athlete_id == athlete_id,
                WellnessPost.filled_at >= lookback_date,
                WellnessPost.deleted_at.is_(None)
            )
        )
        post_result = await self.db.execute(post_stmt)
        wellness_post_list = list(post_result.scalars().all())
        wellness_post_filled = len(wellness_post_list)
        
        # 4. Calcular taxas de resposta
        response_rate_pre = (wellness_pre_filled / total_sessions * 100) if total_sessions > 0 else 0.0
        response_rate_post = (wellness_post_filled / total_sessions * 100) if total_sessions > 0 else 0.0
        
        # 5. Calcular médias de métricas
        avg_fatigue_pre = (
            sum(w.fatigue_pre for w in wellness_pre_list) / wellness_pre_filled
            if wellness_pre_filled > 0 else 0.0
        )
        avg_rpe = (
            sum(w.session_rpe for w in wellness_post_list) / wellness_post_filled
            if wellness_post_filled > 0 else 0.0
        )
        readiness_scores = [w.readiness_score for w in wellness_pre_list if w.readiness_score is not None]
        avg_readiness = (
            sum(readiness_scores) / len(readiness_scores)
            if readiness_scores else 0.0
        )
        
        # 6. Buscar alertas
        alerts = await self.check_critical_wellness(athlete_id=athlete_id, days_lookback=days_lookback)
        
        return {
            "athlete_id": str(athlete_id),
            "period_days": days_lookback,
            "total_sessions": total_sessions,
            "wellness_pre_filled": wellness_pre_filled,
            "wellness_post_filled": wellness_post_filled,
            "response_rate_pre": round(response_rate_pre, 2),
            "response_rate_post": round(response_rate_post, 2),
            "avg_fatigue_pre": round(avg_fatigue_pre, 2),
            "avg_rpe": round(avg_rpe, 2),
            "avg_readiness": round(avg_readiness, 2),
            "alerts_count": len(alerts),
            "alerts": alerts
        }
