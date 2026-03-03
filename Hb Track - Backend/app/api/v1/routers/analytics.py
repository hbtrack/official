"""
Router Analytics - Endpoints de análises e rankings

Endpoints para métricas, rankings e relatórios de wellness.
"""
from typing import Optional, Any, List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_db
from app.core.context import ExecutionContext
from app.api.v1.deps.auth import permission_dep
from app.services.team_wellness_ranking_service import TeamWellnessRankingService

router = APIRouter(prefix="/analytics", tags=["analytics"])


# ---------------------------------------------------------------------------
# Pydantic response schemas — AR_177 (SSOT canônico: team_id UUID string)
# ---------------------------------------------------------------------------

class WellnessRankingItemResponse(BaseModel):
    """Item de ranking de equipe para response_model canônico."""
    team_id: str
    team_name: str
    response_rate_pre: float
    response_rate_post: float
    avg_rate: float
    rank: int
    athletes_90plus: int
    calculated_at: Optional[str] = None

    model_config = {"from_attributes": True}


class Athlete90PlusItemResponse(BaseModel):
    """Item de atleta 90%+ para response_model canônico."""
    athlete_id: Any  # UUID como string ou UUID nativo
    athlete_name: str
    response_rate: float
    badge_earned: bool

    model_config = {"from_attributes": True}


class RankingCalculateResponse(BaseModel):
    """Resposta do cálculo manual de rankings."""
    month_reference: str
    teams_processed: int
    rankings_created: int
    top_team: Optional[Any] = None
    executed_at: Optional[str] = None

    model_config = {"from_attributes": True}


@router.get("/wellness-rankings", response_model=List[WellnessRankingItemResponse])
async def get_wellness_rankings(
    month: Optional[str] = Query(None, description="Mês de referência (YYYY-MM)"),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(permission_dep(roles=["dirigente","coordenador","treinador"], require_org=True)),
):
    """
    Retorna ranking de equipes por taxa de resposta de wellness
    
    Métricas calculadas:
    - response_rate_pre: Taxa de resposta wellness pré-treino
    - response_rate_post: Taxa de resposta wellness pós-treino
    - avg_rate: Média (pre + post) / 2
    - rank: Posição no ranking (1º, 2º, 3º, ...)
    - athletes_90plus: Quantidade de atletas com rate >= 90%
    
    Ordenação: Por avg_rate DESC
    
    Args:
        month: Mês específico (YYYY-MM) ou None para mês anterior
        limit: Limite de resultados
        
    Returns:
        [
            {
                "team_id": 5,
                "team_name": "Sub-20",
                "response_rate_pre": 85.5,
                "response_rate_post": 75.2,
                "avg_rate": 80.35,
                "rank": 1,
                "athletes_90plus": 12,
                "calculated_at": "2026-02-01T00:00:00"
            }
        ]
    
    Acesso:
    - Dirigente: Todos os teams da organização
    - Coordenador/Treinador: Apenas teams que coordena/treina
    """
    service = TeamWellnessRankingService(db)
    
    # Buscar rankings
    rankings = await service.get_rankings(
        month_reference=month,
        organization_id=ctx.organization_id,
        limit=limit
    )
    
    # Se não é dirigente, filtrar apenas teams do usuário
    if "dirigente" not in ctx.roles:
        # Filtrar por teams que o usuário tem acesso
        # TODO: Implementar filtro por user_team_memberships
        # Por enquanto, retornar todos (assumindo que dirigente/coordenador tem acesso)
        pass
    
    return rankings


@router.get("/wellness-rankings/{team_id}/athletes-90plus", response_model=List[Athlete90PlusItemResponse])
async def get_team_athletes_90plus(
    team_id: str,
    month: str = Query(..., description="Mês de referência (YYYY-MM)"),
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(permission_dep(roles=["dirigente","coordenador","treinador"], require_org=True)),
):
    """
    Retorna lista de atletas com response_rate >= 90% em um team
    
    Drill-down do ranking: mostra quais atletas específicos atingiram a meta.
    
    Args:
        team_id: ID do team
        month: Mês de referência (YYYY-MM)
        
    Returns:
        [
            {
                "athlete_id": 10,
                "athlete_name": "João Silva",
                "response_rate": 95.5,
                "badge_earned": true
            }
        ]
    
    Ordenação: Por response_rate DESC
    
    Acesso:
    - Dirigente: Qualquer team da organização
    - Coordenador/Treinador: Apenas teams que coordena/treina
    """
    # TODO: Verificar se usuário tem acesso ao team
    # if team_id not in ctx.user_team_ids and "dirigente" not in ctx.roles:
    #     raise HTTPException(status_code=403, detail="Sem permissão para acessar este team")
    
    service = TeamWellnessRankingService(db)
    
    # Buscar atletas 90%+
    athletes = await service.get_team_athletes_90plus(
        team_id=team_id,
        month_reference=month
    )
    
    return athletes


@router.post("/wellness-rankings/calculate", response_model=RankingCalculateResponse)
async def calculate_rankings_manually(
    month: Optional[str] = Query(None, description="Mês de referência (YYYY-MM)"),
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(permission_dep(roles=["dirigente"], require_org=True)),
):
    """
    Calcular rankings de wellness manualmente (apenas dirigentes)
    
    Normalmente executado via scheduled job no dia 1 de cada mês.
    Este endpoint permite recalcular manualmente para testes ou correções.
    
    Args:
        month: Mês específico (YYYY-MM) ou None para mês anterior
        
    Returns:
        {
            "month_reference": "2026-01",
            "teams_processed": 16,
            "rankings_created": 16,
            "top_team": {"id": 5, "name": "Sub-20", "avg_rate": 95.5},
            "executed_at": "2026-02-01T00:00:00"
        }
    """
    from datetime import datetime
    
    service = TeamWellnessRankingService(db)
    
    # Se month especificado, converter para datetime
    target_month = None
    if month:
        try:
            year, month_num = month.split("-")
            target_month = datetime(int(year), int(month_num), 1)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de mês inválido. Use YYYY-MM"
            )
    
    # Calcular rankings
    stats = await service.calculate_monthly_team_rankings(
        target_month=target_month,
        organization_id=ctx.organization_id
    )
    
    return stats
