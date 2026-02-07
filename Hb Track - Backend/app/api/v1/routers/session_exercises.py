"""
Router para operações de session-exercises (vínculo treinos ↔ exercícios).
Suporta drag-and-drop com add, bulk add, reorder, update e delete.
"""
from uuid import UUID
from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_db
from app.api.v1.deps.auth import permission_dep
from app.core.context import ExecutionContext
from app.services.session_exercise_service import SessionExerciseService
from app.schemas.session_exercises import (
    SessionExerciseCreate,
    SessionExerciseBulkCreate,
    SessionExerciseUpdate,
    SessionExerciseReorder,
    SessionExerciseResponse,
    SessionExerciseListResponse
)


router = APIRouter(
    prefix="/training-sessions",
    tags=["session-exercises"]
)


# ==================== ADD EXERCISES ====================

@router.post(
    "/{session_id}/exercises",
    response_model=SessionExerciseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Adicionar exercício à sessão",
    description="Adiciona um exercício ao planejamento da sessão de treino. Requer permissão modify_training_session."
)
async def add_exercise_to_session(
    session_id: UUID,
    data: SessionExerciseCreate,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(
        permission_dep(roles=["treinador", "coordenador", "dirigente"])
    )
):
    """
    Adiciona um exercício à sessão (drag-and-drop single).
    
    **Permissões:** modify_training_session (treinador, coordenador)
    
    **Body:**
    - exercise_id: UUID do exercício a adicionar
    - order_index: Posição na ordenação (0-based)
    - duration_minutes: Duração planejada (opcional)
    - notes: Notas específicas desta instância (opcional)
    
    **Returns:** SessionExerciseResponse com dados do exercício aninhados
    
    **Errors:**
    - 404: Sessão ou exercício não encontrado
    - 400: Conflict de order_index (já existe exercício naquela posição)
    - 403: Sem permissão
    """
    service = SessionExerciseService(db)
    return await service.add_exercise(
        session_id=session_id,
        data=data,
        user_id=ctx.user_id
    )


@router.post(
    "/{session_id}/exercises/bulk",
    response_model=list[SessionExerciseResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Adicionar múltiplos exercícios (bulk)",
    description="Adiciona múltiplos exercícios de uma vez. Útil para drag-and-drop com seleção múltipla."
)
async def bulk_add_exercises_to_session(
    session_id: UUID,
    data: SessionExerciseBulkCreate,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(
        permission_dep(roles=["treinador", "coordenador", "dirigente"])
    )
):
    """
    Adiciona múltiplos exercícios de uma vez (bulk insert).
    
    **Permissões:** modify_training_session
    
    **Body:**
    - exercises: Lista de exercícios a adicionar (máx 50)
    
    **Returns:** Lista de SessionExerciseResponse
    
    **Errors:**
    - 404: Sessão não encontrada
    - 400: Algum exercise_id inválido ou conflict de order_index
    - 403: Sem permissão
    """
    service = SessionExerciseService(db)
    return await service.bulk_add_exercises(
        session_id=session_id,
        data=data,
        user_id=ctx.user_id
    )


# ==================== GET EXERCISES ====================

@router.get(
    "/{session_id}/exercises",
    response_model=SessionExerciseListResponse,
    summary="Listar exercícios da sessão",
    description="Retorna todos exercícios da sessão ordenados por order_index. Requer permissão view_training_session."
)
async def get_session_exercises(
    session_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(
        permission_dep(roles=["treinador", "coordenador", "dirigente"])
    )
):
    """
    Lista todos exercícios de uma sessão ordenados.
    
    **Permissões:** view_training_session
    
    **Returns:** SessionExerciseListResponse com:
    - total_exercises: Quantidade de exercícios
    - total_duration_minutes: Soma das durações
    - exercises: Lista ordenada por order_index
    
    **Errors:**
    - 404: Sessão não encontrada
    - 403: Sem permissão
    """
    service = SessionExerciseService(db)
    return await service.get_session_exercises(
        session_id=session_id,
        user_id=ctx.user_id
    )


# ==================== UPDATE EXERCISE ====================

@router.patch(
    "/exercises/{session_exercise_id}",
    response_model=SessionExerciseResponse,
    summary="Atualizar metadados do exercício",
    description="Atualiza order_index, duration_minutes ou notes de um exercício já adicionado."
)
async def update_session_exercise(
    session_exercise_id: UUID,
    data: SessionExerciseUpdate,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(
        permission_dep(roles=["treinador", "coordenador", "dirigente"])
    )
):
    """
    Atualiza metadados de um exercício já adicionado.
    
    **Permissões:** modify_training_session
    
    **Body:** (todos opcionais)
    - order_index: Nova posição
    - duration_minutes: Nova duração
    - notes: Novas notas
    
    **Returns:** SessionExerciseResponse atualizado
    
    **Errors:**
    - 404: Vínculo não encontrado
    - 400: Conflict de order_index
    - 403: Sem permissão
    """
    service = SessionExerciseService(db)
    return await service.update_exercise(
        session_exercise_id=session_exercise_id,
        data=data,
        user_id=ctx.user_id
    )


@router.patch(
    "/{session_id}/exercises/reorder",
    summary="Reordenar exercícios (bulk)",
    description="Reordena múltiplos exercícios de uma vez. Usado após drag-and-drop de reordenação."
)
async def reorder_session_exercises(
    session_id: UUID,
    data: SessionExerciseReorder,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(
        permission_dep(roles=["treinador", "coordenador", "dirigente"])
    )
):
    """
    Reordena múltiplos exercícios (bulk update de order_index).
    
    **Permissões:** modify_training_session
    
    **Body:**
    - reorders: Lista de {id, order_index}
    
    **Returns:** {"success": true, "updated_count": N}
    
    **Errors:**
    - 404: Sessão ou algum vínculo não encontrado
    - 400: Algum ID não pertence à sessão
    - 403: Sem permissão
    """
    service = SessionExerciseService(db)
    return await service.reorder_exercises(
        session_id=session_id,
        data=data,
        user_id=ctx.user_id
    )


# ==================== DELETE EXERCISE ====================

@router.delete(
    "/exercises/{session_exercise_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover exercício da sessão",
    description="Remove exercício do planejamento da sessão (soft delete)."
)
async def remove_exercise_from_session(
    session_exercise_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(
        permission_dep(roles=["treinador", "coordenador", "dirigente"])
    )
):
    """
    Remove exercício da sessão (soft delete).
    
    **Permissões:** modify_training_session
    
    **Returns:** 204 No Content
    
    **Errors:**
    - 404: Vínculo não encontrado
    - 403: Sem permissão
    """
    service = SessionExerciseService(db)
    await service.remove_exercise(
        session_exercise_id=session_exercise_id,
        user_id=ctx.user_id
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
