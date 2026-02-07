"""
Prevention Effectiveness Service - Step 22

Serviço para análise de eficácia preventiva: correlação entre alertas, sugestões e lesões.
Avalia se sugestões aplicadas reduziram incidência de lesões.

@module prevention_effectiveness_service
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy import select, func, and_, case, distinct
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.training_alert import TrainingAlert
from app.models.training_suggestion import TrainingSuggestion
from app.models.medical_case import MedicalCase
from app.models.team import Team


class PreventionEffectivenessService:
    """Serviço para análise de eficácia preventiva."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_prevention_effectiveness(
        self,
        team_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calcula eficácia preventiva correlacionando alertas→sugestões→lesões.
        
        Args:
            team_id: UUID da equipe
            start_date: Data início do período (padrão: 60 dias atrás)
            end_date: Data fim do período (padrão: hoje)
            category: Filtro por categoria (optional)
        
        Returns:
            Dict com:
            - summary: Estatísticas gerais (total alertas, sugestões, lesões, taxa redução)
            - timeline: Array de eventos cronológicos (alertas→sugestões→lesões)
            - comparison: Taxa de lesões quando sugestão aplicada vs recusada
            - by_category: Breakdown por categoria de alerta
            - alerts_effectiveness: % de alertas que geraram sugestões aplicadas
        
        Lógica:
            1. Busca alertas do período
            2. Busca sugestões do team no período
            3. Para cada sugestão, verifica se foi aplicada (applied_at != NULL)
            4. Busca lesões no período +7 dias após sugestão
            5. Calcula: taxa_lesões_com_sugestão vs taxa_lesões_sem_sugestão
            6. Monta timeline visual com eventos ordenados
        """
        # Defaults de período
        if not end_date:
            end_date = datetime.now()
        if not start_date:
            start_date = end_date - timedelta(days=60)
        
        # ==================
        # 1. BUSCAR ALERTAS
        # ==================
        stmt = select(TrainingAlert).where(
            and_(
                TrainingAlert.team_id == team_id,
                TrainingAlert.triggered_at >= start_date,
                TrainingAlert.triggered_at <= end_date,
                TrainingAlert.dismissed_at.is_(None)  # Apenas ativos
            )
        )
        
        if category:
            stmt = stmt.where(TrainingAlert.alert_type == category)
        
        result = await self.db.execute(stmt)
        alerts = result.scalars().all()
        
        total_alerts = len(alerts)
        
        # =======================
        # 2. PROCESSAR SUGESTÕES
        # =======================
        suggestions_applied = 0
        suggestions_rejected = 0
        suggestions_pending = 0
        
        # Buscar todas sugestões do team no período
        sugg_stmt = select(TrainingSuggestion).where(
            and_(
                TrainingSuggestion.team_id == team_id,
                TrainingSuggestion.created_at >= start_date,
                TrainingSuggestion.created_at <= end_date
            )
        )
        sugg_result = await self.db.execute(sugg_stmt)
        suggestions = sugg_result.scalars().all()
        
        for sugg in suggestions:
            if sugg.applied_at:
                suggestions_applied += 1
            elif sugg.dismissed_at:  # Campo correto é dismissed_at, não rejected_at
                suggestions_rejected += 1
            else:
                suggestions_pending += 1
        
        # ===================
        # 3. BUSCAR LESÕES
        # ===================
        # Lesões no período total (alertas + 30 dias após)
        injury_end_date = end_date + timedelta(days=30)
        
        injury_stmt = select(MedicalCase).where(
            and_(
                MedicalCase.started_at >= start_date,
                MedicalCase.started_at <= injury_end_date
            )
        ).join(MedicalCase.athlete).where(
            # Filtrar por athletes do team (via team_memberships)
            # TODO: Adicionar join correto quando team_memberships estiver linkado
        )
        
        injury_result = await self.db.execute(injury_stmt)
        injuries = injury_result.scalars().all()
        total_injuries = len(injuries)
        
        # ==================================
        # 4. CORRELAÇÃO SUGESTÕES → LESÕES
        # ==================================
        # Contar lesões em janela de +7 dias após sugestão aplicada
        injuries_after_applied = 0
        injuries_after_rejected = 0
        
        for sugg in suggestions:
            if sugg.applied_at:
                # Janela: applied_at até +7 dias
                window_start = sugg.applied_at
                window_end = window_start + timedelta(days=7)
                
                injuries_in_window = [
                    inj for inj in injuries
                    if window_start <= inj.started_at <= window_end
                ]
                injuries_after_applied += len(injuries_in_window)
            
            elif sugg.dismissed_at:
                # Janela: dismissed_at até +7 dias
                window_start = sugg.dismissed_at
                window_end = window_start + timedelta(days=7)
                
                injuries_in_window = [
                    inj for inj in injuries
                    if window_start <= inj.started_at <= window_end
                ]
                injuries_after_rejected += len(injuries_in_window)
        
        # Taxa de lesões
        injury_rate_with_action = (
            (injuries_after_applied / suggestions_applied * 100)
            if suggestions_applied > 0 else 0
        )
        injury_rate_without_action = (
            (injuries_after_rejected / suggestions_rejected * 100)
            if suggestions_rejected > 0 else 0
        )
        
        reduction_rate = max(0, injury_rate_without_action - injury_rate_with_action)
        
        # =======================
        # 5. MONTAR TIMELINE
        # =======================
        timeline = []
        
        for alert in alerts:
            timeline.append({
                "type": "alert",
                "date": alert.triggered_at.isoformat(),
                "alert_type": alert.alert_type,
                "severity": alert.severity,
                "message": alert.message,
                "id": str(alert.id)
            })
        
        for sugg in suggestions:
            timeline.append({
                "type": "suggestion",
                "date": sugg.created_at.isoformat(),
                "suggestion_type": sugg.type,
                "reason": sugg.reason,
                "status": (
                    "applied" if sugg.applied_at else
                    "dismissed" if sugg.dismissed_at else
                    "pending"
                ),
                "applied_at": sugg.applied_at.isoformat() if sugg.applied_at else None,
                "dismissed_at": sugg.dismissed_at.isoformat() if sugg.dismissed_at else None,
                "id": str(sugg.id)
            })
        
        for injury in injuries:
            timeline.append({
                "type": "injury",
                "date": injury.started_at.isoformat(),
                "reason": injury.reason,
                "status": injury.status,
                "athlete_id": str(injury.athlete_id),
                "id": str(injury.id)
            })
        
        # Ordenar por data
        timeline.sort(key=lambda x: x["date"])
        
        # ============================
        # 6. BREAKDOWN POR CATEGORIA
        # ============================
        by_category = {}
        for alert in alerts:
            cat = alert.alert_type
            if cat not in by_category:
                by_category[cat] = {
                    "total_alerts": 0,
                    "suggestions_generated": len(suggestions),  # Todas sugestões do período
                    "suggestions_applied": suggestions_applied,
                    "injuries_after": injuries_after_applied
                }
            by_category[cat]["total_alerts"] += 1
        
        # ==================
        # 7. RESPONSE FINAL
        # ==================
        return {
            "team_id": team_id,
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "summary": {
                "total_alerts": total_alerts,
                "total_suggestions": len(suggestions),
                "suggestions_applied": suggestions_applied,
                "suggestions_rejected": suggestions_rejected,
                "suggestions_pending": suggestions_pending,
                "total_injuries": total_injuries,
                "injury_reduction_rate": round(reduction_rate, 2),
                "alerts_effectiveness_pct": round(
                    (suggestions_applied / total_alerts * 100) if total_alerts > 0 else 0,
                    2
                )
            },
            "comparison": {
                "injury_rate_with_action": round(injury_rate_with_action, 2),
                "injury_rate_without_action": round(injury_rate_without_action, 2),
                "reduction_achieved": round(reduction_rate, 2),
                "sample_size_with_action": suggestions_applied,
                "sample_size_without_action": suggestions_rejected
            },
            "timeline": timeline,
            "by_category": by_category
        }
