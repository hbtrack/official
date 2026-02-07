"""
Router Dashboard - Endpoint agregado otimizado

Princípios de performance:
1. Uma requisição retorna TUDO que o dashboard precisa
2. Cache por team_id + season_id com TTL 120s
3. Usa materialized views para agregações
4. Evita N+1 queries
"""
from uuid import UUID
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, Query, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_db
from app.core.context import ExecutionContext, get_current_context, require_role
from app.schemas.dashboard import DashboardSummaryResponse
from app.services.dashboard_service import DashboardService, invalidate_dashboard_cache


router = APIRouter(tags=["dashboard"])


@router.get(
    "/summary",
    response_model=DashboardSummaryResponse,
    summary="Dashboard Agregado",
    description="""
    **Endpoint otimizado que retorna TODOS os dados do dashboard em uma única requisição.**
    
    ## Performance
    - Cache: 120 segundos por team_id + season_id
    - Usa materialized views pré-calculadas
    - Evita múltiplas requisições ao backend
    
    ## Dados retornados
    - **athletes**: total, ativas, lesionadas, dispensadas
    - **training**: sessões, média de presença, carga média, últimos treinos
    - **training_trends**: tendências por semana (12 semanas)
    - **matches**: vitórias, empates, derrotas, gols
    - **wellness**: sono, fadiga, estresse, humor, score de prontidão
    - **medical**: casos ativos, recuperando, liberados
    - **alerts**: até 10 alertas prioritários
    - **next_training**: próximo treino agendado
    - **next_match**: próximo jogo agendado
    
    ## Headers de Cache
    - `X-Cache-TTL`: tempo de vida do cache em segundos
    - `X-Generated-At`: timestamp de geração dos dados
    
    ## Uso recomendado
    ```javascript
    // Frontend - usar staleTime de 60-120s
    const { data } = useQuery({
      queryKey: ['dashboard', teamId, seasonId],
      queryFn: () => fetch('/api/v1/dashboard/summary?team_id=xxx'),
      staleTime: 60_000, // 60 segundos
      keepPreviousData: true,
    })
    ```
    """,
    responses={
        200: {
            "description": "Dashboard completo",
            "headers": {
                "X-Cache-TTL": {
                    "description": "Tempo de vida do cache em segundos",
                    "schema": {"type": "integer"}
                },
                "X-Generated-At": {
                    "description": "Timestamp de geração",
                    "schema": {"type": "string", "format": "date-time"}
                }
            }
        },
        401: {"description": "Token inválido ou ausente"},
        403: {"description": "Sem permissão para acessar este time"},
    }
)
async def get_dashboard_summary(
    response: Response,
    team_id: Optional[UUID] = Query(None, description="Filtrar por equipe específica"),
    season_id: Optional[UUID] = Query(None, description="Filtrar por temporada"),
    skip_cache: bool = Query(False, description="Forçar atualização (ignora cache)"),
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(require_role(["treinador", "coordenador", "dirigente", "superadmin"]))
) -> DashboardSummaryResponse:
    """
    Retorna resumo completo do dashboard para o contexto do usuário.
    
    **Regras de acesso (R26):**
    - Treinador: apenas equipes atribuídas
    - Coordenador: todas as equipes da organização
    - Dirigente: todas as equipes da organização
    - Superadmin: acesso total
    """
    # Verificar permissão para o time específico
    if team_id and ctx.role == "treinador":
        # TODO: Verificar se o treinador tem acesso a este time
        pass
    
    # Buscar dados do dashboard
    data = await DashboardService.get_dashboard_summary(
        db=db,
        organization_id=ctx.organization_id,
        team_id=team_id,
        season_id=season_id,
        use_cache=not skip_cache
    )
    
    # Adicionar headers de cache
    response.headers["X-Cache-TTL"] = str(data.cache_ttl_seconds)
    response.headers["X-Generated-At"] = data.generated_at.isoformat()
    response.headers["Cache-Control"] = f"private, max-age={data.cache_ttl_seconds}"
    
    return data


@router.post(
    "/invalidate-cache",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Invalidar Cache do Dashboard",
    description="""
    Força a invalidação do cache do dashboard.
    
    **Usar quando:**
    - Após salvar um treino
    - Após finalizar um jogo
    - Após atualizar estado de atleta
    - Após registrar wellness
    
    Na maioria dos casos, o cache expira naturalmente em 120s.
    """
)
async def invalidate_cache(
    team_id: Optional[UUID] = Query(None, description="Invalidar cache de um time específico"),
    ctx: ExecutionContext = Depends(require_role(["treinador", "coordenador", "dirigente"]))
):
    """Invalida o cache do dashboard"""
    invalidate_dashboard_cache(ctx.organization_id, team_id)
    return None


# =============================================================================
# ENDPOINT POR TIME (ATALHO)
# =============================================================================

@router.get(
    "/teams/{team_id}/summary",
    response_model=DashboardSummaryResponse,
    summary="Dashboard de Equipe Específica",
    description="""
    Atalho para `/dashboard/summary?team_id={team_id}`
    
    Útil para URLs mais semânticas no frontend.
    """
)
async def get_team_dashboard_summary(
    team_id: UUID,
    response: Response,
    season_id: Optional[UUID] = Query(None),
    skip_cache: bool = Query(False),
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(require_role(["treinador", "coordenador", "dirigente", "superadmin"]))
) -> DashboardSummaryResponse:
    """Dashboard específico de uma equipe"""
    data = await DashboardService.get_dashboard_summary(
        db=db,
        organization_id=ctx.organization_id,
        team_id=team_id,
        season_id=season_id,
        use_cache=not skip_cache
    )
    
    response.headers["X-Cache-TTL"] = str(data.cache_ttl_seconds)
    response.headers["X-Generated-At"] = data.generated_at.isoformat()
    response.headers["Cache-Control"] = f"private, max-age={data.cache_ttl_seconds}"
    
    return data
