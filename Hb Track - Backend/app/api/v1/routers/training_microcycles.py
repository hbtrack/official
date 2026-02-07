"""
Router para microciclos de treinamento (Training Microcycles).

Baseado em TRAINNIG.MD:
- Microciclo: planejamento semanal de treinos
- Armazena focos planejados (intenção)
- Base para cálculo de desvios (planejado vs executado)

Regras aplicáveis:
- R34: Organization scoping
- RDB3: Timestamps em UTC
- RDB4: Soft delete obrigatório
- Permissões por papel e escopo
"""

import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps.auth import permission_dep
from app.core.context import ExecutionContext
from app.core.db import get_async_db
from app.schemas.training_microcycles import (
    TrainingMicrocycleCreate,
    TrainingMicrocycleUpdate,
    TrainingMicrocycleResponse,
    TrainingMicrocycleWithSessions,
)
from app.schemas.error import ErrorResponse
from app.services.training_microcycle_service import TrainingMicrocycleService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/training-microcycles",
    tags=["training-microcycles"],
)


@router.get(
    "",
    response_model=List[TrainingMicrocycleResponse],
    summary="Lista microciclos de treinamento",
    description="Lista microciclos (planejamento semanal) de uma equipe com filtros opcionais",
    responses={
        200: {"description": "Lista de microciclos"},
        401: {"description": "Token inválido ou ausente", "model": ErrorResponse},
        403: {"description": "Permissão insuficiente", "model": ErrorResponse},
    },
)
async def list_training_microcycles(
    team_id: UUID = Query(..., description="ID da equipe"),
    cycle_id: Optional[UUID] = Query(None, description="Filtro por mesociclo"),
    start_date: Optional[str] = Query(None, description="Data inicial do intervalo (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Data final do intervalo (YYYY-MM-DD)"),
    include_deleted: bool = Query(False, description="Incluir microciclos deletados"),
    db: AsyncSession = Depends(get_async_db),
    context: ExecutionContext = Depends(permission_dep(["treinador", "coordenador", "dirigente"])),
):
    """
    Lista microciclos de treinamento de uma equipe.

    Filtros disponíveis:
    - team_id: Obrigatório
    - cycle_id: Filtrar por mesociclo específico
    - start_date/end_date: Intervalo de datas
    - include_deleted: Incluir microciclos deletados (soft delete)

    Requer permissão: coach ou admin
    """
    from datetime import date

    service = TrainingMicrocycleService(db, context)

    # Parse dates
    start = None
    end = None
    if start_date:
        try:
            start = date.fromisoformat(start_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid start_date format. Use YYYY-MM-DD"
            )

    if end_date:
        try:
            end = date.fromisoformat(end_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid end_date format. Use YYYY-MM-DD"
            )

    microcycles = await service.get_all(
        team_id=team_id,
        cycle_id=cycle_id,
        start_date=start,
        end_date=end,
        include_deleted=include_deleted,
    )

    logger.info(
        f"Listed {len(microcycles)} training microcycles for team {team_id} "
        f"by user {context.user_id}"
    )

    return microcycles


@router.get(
    "/teams/{team_id}/current",
    response_model=TrainingMicrocycleResponse,
    summary="Busca microciclo da semana atual",
    description="Retorna o microciclo ativo na semana atual de uma equipe",
    responses={
        200: {"description": "Microciclo da semana atual"},
        404: {"description": "Nenhum microciclo ativo na semana", "model": ErrorResponse},
        401: {"description": "Token inválido ou ausente", "model": ErrorResponse},
        403: {"description": "Permissão insuficiente", "model": ErrorResponse},
    },
)
async def get_current_microcycle(
    team_id: UUID,
    at_date: Optional[str] = Query(None, description="Data de referência (YYYY-MM-DD). Default: hoje"),
    db: AsyncSession = Depends(get_async_db),
    context: ExecutionContext = Depends(permission_dep(["treinador", "coordenador", "dirigente"])),
):
    """
    Busca o microciclo da semana atual de uma equipe.

    Se `at_date` não for fornecido, usa a data atual.

    Requer permissão: coach ou admin
    """
    from datetime import date

    service = TrainingMicrocycleService(db, context)

    # Parse date
    target_date = None
    if at_date:
        try:
            target_date = date.fromisoformat(at_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use YYYY-MM-DD"
            )

    microcycle = await service.get_current_week(
        team_id=team_id,
        at_date=target_date,
    )

    if not microcycle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active microcycle found for team {team_id} at {target_date or 'today'}"
        )

    logger.info(
        f"Retrieved current microcycle for team {team_id} "
        f"at {target_date or 'today'} by user {context.user_id}"
    )

    return microcycle


@router.get(
    "/{microcycle_id}",
    response_model=TrainingMicrocycleWithSessions,
    summary="Busca microciclo por ID",
    description="Retorna detalhes de um microciclo específico com sessões relacionadas",
    responses={
        200: {"description": "Microciclo encontrado"},
        404: {"description": "Microciclo não encontrado", "model": ErrorResponse},
        401: {"description": "Token inválido ou ausente", "model": ErrorResponse},
        403: {"description": "Permissão insuficiente", "model": ErrorResponse},
    },
)
async def get_training_microcycle(
    microcycle_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    context: ExecutionContext = Depends(permission_dep(["treinador", "coordenador", "dirigente"])),
):
    """
    Busca um microciclo de treinamento por ID.

    Retorna o microciclo com todas as sessões relacionadas.

    Requer permissão: coach ou admin
    """
    service = TrainingMicrocycleService(db, context)

    try:
        microcycle = await service.get_by_id(microcycle_id)
        logger.info(f"Retrieved training microcycle {microcycle_id} by user {context.user_id}")
        return microcycle
    except Exception as e:
        logger.error(f"Error retrieving training microcycle {microcycle_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training microcycle not found: {str(e)}"
        )


@router.post(
    "",
    response_model=TrainingMicrocycleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cria novo microciclo de treinamento",
    description="Cria um microciclo (planejamento semanal) com focos planejados",
    responses={
        201: {"description": "Microciclo criado com sucesso"},
        400: {"description": "Dados inválidos", "model": ErrorResponse},
        401: {"description": "Token inválido ou ausente", "model": ErrorResponse},
        403: {"description": "Permissão insuficiente", "model": ErrorResponse},
    },
)
async def create_training_microcycle(
    data: TrainingMicrocycleCreate,
    db: AsyncSession = Depends(get_async_db),
    context: ExecutionContext = Depends(permission_dep(["treinador", "coordenador", "dirigente"])),
):
    """
    Cria um novo microciclo de treinamento (planejamento semanal).

    Validações:
    - week_start < week_end
    - Soma dos focos planejados ≤ 120
    - Se cycle_id fornecido, datas devem estar dentro do mesociclo

    Requer permissão: coach ou admin
    """
    service = TrainingMicrocycleService(db, context)

    try:
        microcycle = await service.create(data)
        await db.commit()

        logger.info(
            f"Created training microcycle {microcycle.id} "
            f"for team {data.team_id} ({data.week_start} - {data.week_end}) "
            f"by user {context.user_id}"
        )

        return microcycle
    except ValueError as e:
        await db.rollback()
        logger.warning(f"Validation error creating training microcycle: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating training microcycle: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating training microcycle: {str(e)}"
        )


@router.patch(
    "/{microcycle_id}",
    response_model=TrainingMicrocycleResponse,
    summary="Atualiza microciclo de treinamento",
    description="Atualiza campos específicos de um microciclo (atualização parcial)",
    responses={
        200: {"description": "Microciclo atualizado com sucesso"},
        404: {"description": "Microciclo não encontrado", "model": ErrorResponse},
        400: {"description": "Dados inválidos", "model": ErrorResponse},
        401: {"description": "Token inválido ou ausente", "model": ErrorResponse},
        403: {"description": "Permissão insuficiente", "model": ErrorResponse},
    },
)
async def update_training_microcycle(
    microcycle_id: UUID,
    data: TrainingMicrocycleUpdate,
    db: AsyncSession = Depends(get_async_db),
    context: ExecutionContext = Depends(permission_dep(["treinador", "coordenador", "dirigente"])),
):
    """
    Atualiza um microciclo de treinamento existente.

    Permite atualização parcial dos campos de focos planejados, carga, tipo e notas.

    Requer permissão: coach ou admin
    """
    service = TrainingMicrocycleService(db, context)

    try:
        microcycle = await service.update(microcycle_id, data)
        await db.commit()

        logger.info(f"Updated training microcycle {microcycle_id} by user {context.user_id}")

        return microcycle
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating training microcycle {microcycle_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training microcycle not found: {str(e)}"
        )


@router.delete(
    "/{microcycle_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove microciclo de treinamento (soft delete)",
    description="Marca microciclo como deletado sem remover do banco (soft delete)",
    responses={
        204: {"description": "Microciclo deletado com sucesso"},
        404: {"description": "Microciclo não encontrado", "model": ErrorResponse},
        401: {"description": "Token inválido ou ausente", "model": ErrorResponse},
        403: {"description": "Permissão insuficiente", "model": ErrorResponse},
    },
)
async def delete_training_microcycle(
    microcycle_id: UUID,
    reason: str = Query(..., description="Motivo da exclusão"),
    db: AsyncSession = Depends(get_async_db),
    context: ExecutionContext = Depends(permission_dep(["coordenador", "dirigente"])),
):
    """
    Remove um microciclo de treinamento (soft delete).

    O microciclo não é removido fisicamente do banco, apenas marcado como deletado
    com timestamp e motivo para auditoria.

    Requer permissão: admin
    """
    service = TrainingMicrocycleService(db, context)

    try:
        await service.soft_delete(microcycle_id, reason)
        await db.commit()

        logger.info(
            f"Soft deleted training microcycle {microcycle_id} by user {context.user_id}: {reason}"
        )

        return None
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting training microcycle {microcycle_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training microcycle not found: {str(e)}"
        )


@router.get(
    "/{microcycle_id}/summary",
    response_model=dict,
    summary="Resumo de execução do microciclo",
    description="Retorna resumo analítico de planejado vs executado do microciclo",
    responses={
        200: {"description": "Resumo de execução"},
        404: {"description": "Microciclo não encontrado", "model": ErrorResponse},
        401: {"description": "Token inválido ou ausente", "model": ErrorResponse},
        403: {"description": "Permissão insuficiente", "model": ErrorResponse},
    },
)
async def get_microcycle_summary(
    microcycle_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    context: ExecutionContext = Depends(permission_dep(["treinador", "coordenador", "dirigente"])),
):
    """
    Retorna resumo analítico de execução do microciclo.

    Calcula e compara:
    - Total de sessões realizadas
    - Carga planejada vs executada
    - Focos planejados vs executados (médias)

    Útil para análise de aderência ao planejamento.

    Requer permissão: coach ou admin
    """
    service = TrainingMicrocycleService(db, context)

    try:
        summary = await service.get_microcycle_execution_summary(microcycle_id)

        logger.info(
            f"Retrieved execution summary for microcycle {microcycle_id} "
            f"by user {context.user_id}"
        )

        return summary
    except Exception as e:
        logger.error(f"Error getting microcycle summary {microcycle_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training microcycle not found: {str(e)}"
        )
