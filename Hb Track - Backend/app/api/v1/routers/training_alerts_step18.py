"""
Router para Alertas e Sugestões de Treinamento - Step 18

Endpoints para gerenciamento de alertas automáticos e sugestões de compensação.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID

from app.core.db import get_async_db
from app.core.context import ExecutionContext
from app.api.v1.deps.auth import require_role
from app.schemas.training_alerts import (
    AlertResponse,
    AlertListResponse,
    AlertStatsResponse,
    AlertUpdate,
    AlertFilters
)
from app.schemas.training_alerts_step18 import (
    SuggestionResponse,
    SuggestionListResponse,
    SuggestionStatsResponse,
    SuggestionApply,
    SuggestionDismiss,
    SuggestionFilters
)
from app.services.training_alerts_service import TrainingAlertsService
from app.services.training_suggestion_service import TrainingSuggestionService


router = APIRouter(prefix="/training/alerts-suggestions", tags=["Training Alerts & Suggestions"])


# ============================================================================
# TRAINING ALERTS ENDPOINTS
# ============================================================================

@router.get(
    "/alerts/team/{team_id}/active",
    response_model=list[AlertResponse],
    summary="Lista Alertas Ativos",
    description="Retorna alertas não-dismissados de uma equipe."
)
async def get_active_alerts(
    team_id: UUID,
    limit: int = Query(default=10, ge=1, le=50),
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador", "treinador"]))
):
    """Busca alertas ativos de uma equipe."""
    service = TrainingAlertsService(db)
    alerts = await service.get_active_alerts(team_id=team_id, limit=limit)
    return alerts


@router.get(
    "/alerts/team/{team_id}/history",
    response_model=AlertListResponse,
    summary="Histórico de Alertas",
    description="Retorna alertas paginados com filtros opcionais."
)
async def get_alert_history(
    team_id: UUID,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    alert_type: Optional[str] = Query(default=None),
    severity: Optional[str] = Query(default=None),
    is_active: Optional[bool] = Query(default=None),
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador", "treinador"]))
):
    """
    Busca histórico de alertas com paginação e filtros.
    
    Filtros opcionais:
    - alert_type: 'weekly_overload', 'low_wellness_response'
    - severity: 'warning', 'critical'
    - is_active: true (não-dismissados), false (dismissados)
    """
    from app.schemas.training_alerts import AlertType, AlertSeverity
    from app.models.training_alert import TrainingAlert
    from sqlalchemy import select, and_, desc
    
    # Build query
    stmt = select(TrainingAlert).where(TrainingAlert.team_id == team_id)
    
    if alert_type:
        stmt = stmt.where(TrainingAlert.alert_type == alert_type)
    if severity:
        stmt = stmt.where(TrainingAlert.severity == severity)
    if is_active is not None:
        if is_active:
            stmt = stmt.where(TrainingAlert.dismissed_at.is_(None))
        else:
            stmt = stmt.where(TrainingAlert.dismissed_at.isnot(None))
    
    # Count total
    from sqlalchemy import func
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0
    
    # Apply pagination
    offset = (page - 1) * limit
    stmt = stmt.order_by(desc(TrainingAlert.triggered_at)).offset(offset).limit(limit)
    
    result = await db.execute(stmt)
    alerts = result.scalars().all()
    
    service = TrainingAlertsService(db)
    items = [service._to_response(a) for a in alerts]
    
    return AlertListResponse(
        items=items,
        total=total,
        page=page,
        limit=limit,
        has_next=(offset + limit) < total
    )


@router.get(
    "/alerts/team/{team_id}/stats",
    response_model=AlertStatsResponse,
    summary="Estatísticas de Alertas",
    description="Retorna estatísticas agregadas de alertas."
)
async def get_alert_stats(
    team_id: UUID,
    alert_type: Optional[str] = Query(default=None),
    severity: Optional[str] = Query(default=None),
    start_date: Optional[str] = Query(default=None),
    end_date: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador", "treinador"]))
):
    """
    Retorna estatísticas de alertas:
    - Total, ativos, dismissados
    - Contagem por tipo
    - 5 alertas mais recentes
    """
    from datetime import datetime
    from app.schemas.training_alerts import AlertType, AlertSeverity
    
    filters = AlertFilters()
    if alert_type:
        filters.alert_type = AlertType(alert_type)
    if severity:
        filters.severity = AlertSeverity(severity)
    if start_date:
        filters.start_date = datetime.fromisoformat(start_date)
    if end_date:
        filters.end_date = datetime.fromisoformat(end_date)
    
    service = TrainingAlertsService(db)
    stats = await service.get_alert_stats(team_id=team_id, filters=filters)
    return stats


@router.post(
    "/alerts/{alert_id}/dismiss",
    response_model=AlertResponse,
    summary="Dismissar Alerta",
    description="Marca alerta como dismissado (dismissed_at, dismissed_by_user_id)."
)
async def dismiss_alert(
    alert_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador", "treinador"]))
):
    """Dismissar alerta."""
    service = TrainingAlertsService(db)
    alert = await service.dismiss_alert(alert_id=alert_id, user_id=ctx.user_id)
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alerta {alert_id} não encontrado ou já dismissado"
        )
    
    return alert


# ============================================================================
# TRAINING SUGGESTIONS ENDPOINTS
# ============================================================================

@router.get(
    "/suggestions/team/{team_id}/pending",
    response_model=list[SuggestionResponse],
    summary="Lista Sugestões Pendentes",
    description="Retorna sugestões pendentes de uma equipe."
)
async def get_pending_suggestions(
    team_id: UUID,
    limit: int = Query(default=10, ge=1, le=50),
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador", "treinador"]))
):
    """Busca sugestões pendentes de uma equipe."""
    service = TrainingSuggestionService(db)
    suggestions = await service.get_pending_suggestions(team_id=team_id, limit=limit)
    return suggestions


@router.get(
    "/suggestions/team/{team_id}/history",
    response_model=SuggestionListResponse,
    summary="Histórico de Sugestões",
    description="Retorna sugestões paginadas com filtros opcionais."
)
async def get_suggestion_history(
    team_id: UUID,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    type: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador", "treinador"]))
):
    """
    Busca histórico de sugestões com paginação e filtros.
    
    Filtros opcionais:
    - type: 'compensation', 'reduce_next_week'
    - status: 'pending', 'applied', 'dismissed'
    """
    from app.models.training_suggestion import TrainingSuggestion
    from sqlalchemy import select, and_, desc, func
    
    # Build query
    stmt = select(TrainingSuggestion).where(TrainingSuggestion.team_id == team_id)
    
    if type:
        stmt = stmt.where(TrainingSuggestion.type == type)
    if status:
        stmt = stmt.where(TrainingSuggestion.status == status)
    
    # Count total
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0
    
    # Apply pagination
    offset = (page - 1) * limit
    stmt = stmt.order_by(desc(TrainingSuggestion.created_at)).offset(offset).limit(limit)
    
    result = await db.execute(stmt)
    suggestions = result.scalars().all()
    
    service = TrainingSuggestionService(db)
    items = [service._to_response(s) for s in suggestions]
    
    return SuggestionListResponse(
        items=items,
        total=total,
        page=page,
        limit=limit,
        has_next=(offset + limit) < total
    )


@router.get(
    "/suggestions/team/{team_id}/stats",
    response_model=SuggestionStatsResponse,
    summary="Estatísticas de Sugestões",
    description="Retorna estatísticas agregadas de sugestões."
)
async def get_suggestion_stats(
    team_id: UUID,
    type: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    start_date: Optional[str] = Query(default=None),
    end_date: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador", "treinador"]))
):
    """
    Retorna estatísticas de sugestões:
    - Total, pending, applied, dismissed
    - acceptance_rate
    - Contagem por tipo
    - 5 sugestões mais recentes
    """
    from datetime import datetime
    from app.schemas.training_alerts_step18 import SuggestionType, SuggestionStatus
    
    filters = SuggestionFilters()
    if type:
        filters.type = SuggestionType(type)
    if status:
        filters.status = SuggestionStatus(status)
    if start_date:
        filters.start_date = datetime.fromisoformat(start_date)
    if end_date:
        filters.end_date = datetime.fromisoformat(end_date)
    
    service = TrainingSuggestionService(db)
    stats = await service.get_suggestion_stats(team_id=team_id, filters=filters)
    return stats


@router.post(
    "/suggestions/{suggestion_id}/apply",
    response_model=SuggestionResponse,
    summary="Aplicar Sugestão",
    description="Aplica sugestão ajustando focus_pct das sessões alvo."
)
async def apply_suggestion(
    suggestion_id: UUID,
    payload: SuggestionApply,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador", "treinador"]))
):
    """
    Aplica sugestão com ajuste final escolhido pelo usuário.
    
    Body:
    - adjustment_pct: float (10-40%) - Percentual final de ajuste
    """
    service = TrainingSuggestionService(db)
    suggestion = await service.apply_suggestion(
        suggestion_id=suggestion_id,
        adjustment_pct=payload.adjustment_pct
    )
    
    if not suggestion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sugestão {suggestion_id} não encontrada ou não está pendente"
        )
    
    return suggestion


@router.post(
    "/suggestions/{suggestion_id}/dismiss",
    response_model=SuggestionResponse,
    summary="Dismissar Sugestão",
    description="Marca sugestão como dismissada com justificativa."
)
async def dismiss_suggestion(
    suggestion_id: UUID,
    payload: SuggestionDismiss,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador", "treinador"]))
):
    """
    Dismissar sugestão com justificativa obrigatória.
    
    Body:
    - dismissal_reason: string (10-500 chars) - Motivo da rejeição
    """
    service = TrainingSuggestionService(db)
    suggestion = await service.dismiss_suggestion(
        suggestion_id=suggestion_id,
        dismissal_reason=payload.dismissal_reason
    )
    
    if not suggestion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sugestão {suggestion_id} não encontrada ou não está pendente"
        )
    
    return suggestion
