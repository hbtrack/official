"""
Router: Training Analytics (Step 16)

Endpoints:
- GET /analytics/team/{team_id}/summary - Métricas agregadas do período
- GET /analytics/team/{team_id}/weekly-load - Carga semanal (últimas N semanas)
- GET /analytics/team/{team_id}/deviation-analysis - Análise de desvios com threshold
"""
from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_db
from app.core.context import ExecutionContext, get_current_context
from app.api.v1.deps.auth import permission_dep
from app.services.training_analytics_service import TrainingAnalyticsService
from app.services.prevention_effectiveness_service import PreventionEffectivenessService
from app.schemas.training_analytics import (
    TeamSummaryResponse,
    WeeklyLoadResponse,
    DeviationAnalysisResponse
)

router = APIRouter(prefix="/analytics", tags=["Training Analytics"])


@router.get(
    "/team/{team_id}/summary",
    response_model=TeamSummaryResponse,
    summary="Métricas agregadas da equipe"
)
async def get_team_summary(
    team_id: UUID,
    start_date: Optional[date] = Query(None, description="Data início (default: início do mês)"),
    end_date: Optional[date] = Query(None, description="Data fim (default: hoje)"),
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(permission_dep(roles=["dirigente","coordenador","treinador"], require_org=True))
):
    """
    Retorna métricas agregadas de analytics para uma equipe.
    
    **Estratégia de cache:**
    - Mês corrente: usa cache weekly (por microciclo)
    - Meses anteriores: usa cache monthly
    - Recalcula automaticamente se `cache_dirty=true`
    
    **Métricas incluídas (17):**
    - Total de sessões
    - Médias de focos (7 campos)
    - Carga de treino (RPE, carga interna)
    - Assiduidade
    - Wellness response rates (pré e pós)
    - Atletas com badges
    - Desvios de threshold
    
    **Permissões:**
    - Requer: `view_training_analytics`
    - Papéis: Dirigente, Coordenador, Treinador
    """
    service = TrainingAnalyticsService(db, ctx)
    result = await service.get_team_summary(
        team_id=team_id,
        start_date=start_date,
        end_date=end_date
    )
    return result


@router.get(
    "/team/{team_id}/weekly-load",
    response_model=WeeklyLoadResponse,
    summary="Carga semanal das últimas N semanas"
)
async def get_weekly_load(
    team_id: UUID,
    weeks: int = Query(4, ge=1, le=52, description="Quantidade de semanas (1-52)"),
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(permission_dep(roles=["dirigente","coordenador","treinador"], require_org=True))
):
    """
    Retorna carga semanal das últimas N semanas.
    
    **Use case:**
    - Monitorar progressão de carga ao longo das semanas
    - Identificar picos ou quedas abruptas
    - Comparar com planejamento (quando disponível)
    
    **Dados retornados:**
    - Total de sessões por semana
    - Carga interna total
    - RPE médio
    - Taxa de assiduidade
    
    **Permissões:**
    - Requer: `view_training_analytics`
    """
    service = TrainingAnalyticsService(db, ctx)
    data = await service.get_weekly_load(team_id=team_id, weeks=weeks)
    return {
        "team_id": str(team_id),
        "weeks": weeks,
        "data": data
    }


@router.get(
    "/team/{team_id}/deviation-analysis",
    response_model=DeviationAnalysisResponse,
    summary="Análise de desvios com threshold dinâmico"
)
async def get_deviation_analysis(
    team_id: UUID,
    start_date: Optional[date] = Query(None, description="Data início (default: início do mês)"),
    end_date: Optional[date] = Query(None, description="Data fim (default: hoje)"),
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(permission_dep(roles=["dirigente","coordenador","treinador"], require_org=True))
):
    """
    Análise de desvios usando `alert_threshold_multiplier` da equipe.
    
    **Como funciona:**
    1. Busca configuração `team.alert_threshold_multiplier` (Step 15)
    2. Para cada sessão: `desvio = |RPE_real - RPE_planejado| × multiplier`
    3. Lista sessões onde `desvio > multiplier`
    
    **Interpretação:**
    - `threshold_multiplier = 1.5`: Sensível (juvenis)
    - `threshold_multiplier = 2.0`: Padrão
    - `threshold_multiplier = 2.5-3.0`: Tolerante (atletas experientes)
    
    **Métricas retornadas:**
    - Total de sessões analisadas
    - Quantidade de desvios detectados
    - Lista detalhada de cada desvio
    
    **Permissões:**
    - Requer: `view_training_analytics`
    """
    service = TrainingAnalyticsService(db, ctx)
    result = await service.get_deviation_analysis(
        team_id=team_id,
        start_date=start_date,
        end_date=end_date
    )
    return result


@router.get(
    "/team/{team_id}/prevention-effectiveness",
    summary="Eficácia Preventiva - Correlação Alertas→Sugestões→Lesões"
)
async def get_prevention_effectiveness(
    team_id: UUID,
    start_date: Optional[date] = Query(None, description="Data início (default: 60 dias atrás)"),
    end_date: Optional[date] = Query(None, description="Data fim (default: hoje)"),
    category: Optional[str] = Query(None, description="Filtrar por categoria de alerta"),
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(permission_dep(roles=["dirigente","coordenador","treinador"], require_org=True))
):
    """
    Dashboard de Eficácia Preventiva (Step 22)
    
    Analisa a correlação entre alertas, sugestões e lesões para avaliar
    se as ações preventivas estão funcionando.
    
    **Lógica:**
    1. Busca alertas do período
    2. Identifica sugestões geradas por cada alerta
    3. Verifica se sugestões foram aplicadas ou rejeitadas
    4. Conta lesões em janela de +7 dias após ação
    5. Compara taxa de lesões: com sugestão aplicada vs recusada
    
    **Retorna:**
    - `summary`: Estatísticas gerais (alertas, sugestões, lesões, taxa redução)
    - `comparison`: Taxa lesões com/sem ação + redução alcançada
    - `timeline`: Array cronológico de eventos (alertas→sugestões→lesões)
    - `by_category`: Breakdown por categoria de alerta
    
    **Interpretação:**
    - `reduction_rate > 0`: Sugestões reduziram lesões (eficaz)
    - `reduction_rate < 0`: Sugestões não tiveram efeito
    - `reduction_rate > 50%`: Altamente eficaz
    
    **Permissões:**
    - Requer: `view_training_analytics`
    """
    from datetime import datetime
    
    service = PreventionEffectivenessService(db)
    
    # Converter date para datetime
    start_dt = datetime.combine(start_date, datetime.min.time()) if start_date else None
    end_dt = datetime.combine(end_date, datetime.max.time()) if end_date else None
    
    result = await service.get_prevention_effectiveness(
        team_id=team_id,
        start_date=start_dt,
        end_date=end_dt,
        category=category
    )
    return result
