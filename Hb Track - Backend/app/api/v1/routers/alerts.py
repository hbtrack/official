"""
Router para alertas do sistema.

Referências RAG:
- RP8: Alertas de sobrecarga e fadiga
- R13: Impacto dos estados e flags (injured, suspended)
- R26: Permissões por papel
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.core.db import get_db
from app.core.context import ExecutionContext
from app.api.v1.deps.auth import require_role
from app.schemas.alerts import LoadExcessAlertResponse, InjuryReturnAlertResponse
from app.services.alerts.alert_service import AlertService


router = APIRouter(tags=["Alerts"])


# ============================================================================
# ALERTAS DE EXCESSO DE CARGA
# ============================================================================

@router.get(
    "/load",
    response_model=LoadExcessAlertResponse,
    summary="Alertas de Excesso de Carga",
    description="""
    Retorna alertas de atletas com carga de treino excessiva ou insuficiente.

    **Métricas analisadas:**
    - Carga semanal (7 dias)
    - ACWR (Acute:Chronic Workload Ratio)
    - Flag load_restricted

    **Limiares padrão:**
    - Carga máxima semanal: 3000
    - ACWR máximo: 1.5 (risco de lesão)
    - ACWR mínimo: 0.8 (destreinamento)

    **Referências RAG:**
    - RP8: Alertas de sobrecarga e fadiga
    - R21: Métricas de treino (carga, PSE)
    - R13: Flag load_restricted bloqueia escalação

    **Permissões:**
    - Coordenador: acesso a todas as equipes
    - Treinador: acesso às suas equipes (R26)
    """,
    responses={
        200: {
            "description": "Lista de alertas de carga por atleta",
        },
        403: {
            "description": "Equipe fora do escopo do usuário",
        },
        404: {
            "description": "Equipe não encontrada",
        }
    }
)
async def get_load_excess_alerts(
    team_id: UUID = Query(..., description="ID da equipe (obrigatório)"),
    season_id: Optional[UUID] = Query(None, description="Filtrar por temporada (opcional)"),
    db: Session = Depends(get_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador", "treinador"]))
):
    """
    Lista alertas de excesso de carga para uma equipe.
    
    Retorna atletas com:
    - ACWR > 1.5 (risco de lesão)
    - ACWR < 0.8 (possível destreinamento)
    - Carga semanal > 3000
    """
    try:
        return AlertService.get_load_excess_alerts(
            db=db,
            team_id=team_id,
            organization_id=ctx.organization_id,
            season_id=season_id,
        )
    except ValueError as e:
        if "not_found_or_out_of_scope" in str(e):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Team not found or out of scope"
            )
        raise


# ============================================================================
# ALERTAS DE RETORNO DE LESÃO
# ============================================================================

@router.get(
    "/injury-return",
    response_model=InjuryReturnAlertResponse,
    summary="Alertas de Retorno de Lesão",
    description="""
    Retorna alertas de atletas lesionados ou retornando de lesão.

    **Categorias identificadas:**
    - Atletas com flag injured=true (bloqueio total)
    - Atletas em período de retorno (14 dias após alta)
    - Atletas com restrição médica ativa

    **Monitoramento:**
    - Carga nos últimos 7 dias
    - Duração da lesão
    - Progressão pós-retorno

    **Referências RAG:**
    - R13: Flag injured bloqueia escalação
    - R13: medical_restriction requer treino adaptado
    - RP8: Gestão de retorno de atletas lesionados

    **Permissões:**
    - Coordenador: acesso a todas as equipes
    - Treinador: acesso às suas equipes (R26)
    """,
    responses={
        200: {
            "description": "Lista de alertas de lesão/retorno por atleta",
        },
        403: {
            "description": "Equipe fora do escopo do usuário",
        },
        404: {
            "description": "Equipe não encontrada",
        }
    }
)
async def get_injury_return_alerts(
    team_id: UUID = Query(..., description="ID da equipe (obrigatório)"),
    season_id: Optional[UUID] = Query(None, description="Filtrar por temporada (opcional)"),
    db: Session = Depends(get_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador", "treinador"]))
):
    """
    Lista alertas de lesão e retorno para uma equipe.
    
    Retorna atletas:
    - Atualmente lesionados
    - Retornando de lesão (primeiros 14 dias)
    - Com restrição médica ativa
    """
    try:
        return AlertService.get_injury_return_alerts(
            db=db,
            team_id=team_id,
            organization_id=ctx.organization_id,
            season_id=season_id,
        )
    except ValueError as e:
        if "not_found_or_out_of_scope" in str(e):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Team not found or out of scope"
            )
        raise
