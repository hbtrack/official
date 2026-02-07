"""
Rotas: /api/training-suggestions

Sugestões inteligentes para planejamento de treinos.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.deps import permission_dep
from app.core.context import ExecutionContext
from app.services.training_suggestion_service import TrainingSuggestionService
from app.schemas.training_suggestions import (
    TrainingSuggestionsResponse,
    ApplySuggestionRequest,
)
from app.schemas.training_microcycles import TrainingMicrocycleResponse

router = APIRouter(prefix="/training-suggestions", tags=["Training Suggestions"])


@router.get("/", response_model=TrainingSuggestionsResponse)
async def get_suggestions_for_new_microcycle(
    team_id: UUID,
    microcycle_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    context: ExecutionContext = Depends(permission_dep(["coach", "admin"])),
):
    """
    Gera sugestões para um novo microciclo com base no histórico.

    Query Parameters:
    - team_id: ID da equipe (obrigatório)
    - microcycle_type: Tipo de microciclo (opcional: carga_alta, recuperacao, etc.)

    Retorna:
    - Sugestões de ajuste de foco baseadas em padrões recorrentes
    - Evidências e explicações para cada sugestão
    - Contexto da análise

    Regras:
    - Analisa últimos 90 dias
    - Mínimo 3 microciclos similares
    - Desvio mínimo 10pts para considerar
    - Consistência mínima 70% para sugerir
    """
    suggestions = TrainingSuggestionService.get_suggestions_for_new_microcycle(
        db=db,
        team_id=team_id,
        organization_id=context.organization_id,
        microcycle_type=microcycle_type,
    )

    return suggestions


@router.post("/apply", response_model=TrainingMicrocycleResponse)
async def apply_suggestion(
    request: ApplySuggestionRequest,
    db: AsyncSession = Depends(get_db),
    context: ExecutionContext = Depends(permission_dep(["coach", "admin"])),
):
    """
    Aplica uma sugestão a um microciclo.

    Body:
    - microcycle_id: ID do microciclo
    - suggestion: Sugestão a aplicar (FocusSuggestion)

    Retorna:
    - Microciclo atualizado com novo foco planejado

    Permissões:
    - Apenas coach e admin
    """
    try:
        updated_microcycle = TrainingSuggestionService.apply_suggestion_to_microcycle(
            db=db,
            microcycle_id=request.microcycle_id,
            suggestion=request.suggestion.model_dump(),
        )

        return updated_microcycle
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao aplicar sugestão: {str(e)}",
        )
