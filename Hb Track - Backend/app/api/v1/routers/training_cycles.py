"""
Router para ciclos de treinamento (Training Cycles).

Baseado em TRAINNIG.MD:
- Macrociclo: temporada completa ou fase longa
- Mesociclo: 4-6 semanas (pertence a um macrociclo)

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
from app.schemas.training_cycles import (
    TrainingCycleCreate,
    TrainingCycleUpdate,
    TrainingCycleResponse,
    TrainingCycleWithMicrocycles,
)
from app.schemas.error import ErrorResponse
from app.services.training_cycle_service import TrainingCycleService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/training-cycles",
    tags=["training-cycles"],
)


@router.get(
    "",
    response_model=List[TrainingCycleResponse],
    summary="Lista ciclos de treinamento",
    description="Lista macrociclos e mesociclos de uma equipe com filtros opcionais",
    responses={
        200: {"description": "Lista de ciclos"},
        401: {"description": "Token inválido ou ausente", "model": ErrorResponse},
        403: {"description": "Permissão insuficiente", "model": ErrorResponse},
    },
)
async def list_training_cycles(
    team_id: Optional[UUID] = Query(None, description="ID da equipe (opcional, lista todos se omitido)"),
    cycle_type: Optional[str] = Query(None, description="Filtro por tipo: 'macro' ou 'meso'"),
    status: Optional[str] = Query(None, description="Filtro por status: 'active', 'completed', 'cancelled'"),
    include_deleted: bool = Query(False, description="Incluir ciclos deletados"),
    db: AsyncSession = Depends(get_async_db),
    context: ExecutionContext = Depends(permission_dep(["treinador", "coordenador", "dirigente"])),
):
    """
    Lista ciclos de treinamento de uma equipe ou organização.

    Filtros disponíveis:
    - team_id: Opcional (lista todos da organização se omitido)
    - cycle_type: 'macro' ou 'meso'
    - status: 'active', 'completed', 'cancelled'
    - include_deleted: Incluir ciclos deletados (soft delete)

    Requer permissão: coach ou admin
    """
    service = TrainingCycleService(db, context)

    cycles = await service.get_all(
        team_id=team_id,
        cycle_type=cycle_type,
        status=status,
        include_deleted=include_deleted,
    )

    logger.info(
        f"Listed {len(cycles)} training cycles for team {team_id} "
        f"(type={cycle_type}, status={status}) by user {context.user_id}"
    )

    return cycles


@router.get(
    "/{cycle_id}",
    response_model=TrainingCycleWithMicrocycles,
    summary="Busca ciclo por ID",
    description="Retorna detalhes de um ciclo específico com microciclos relacionados",
    responses={
        200: {"description": "Ciclo encontrado"},
        404: {"description": "Ciclo não encontrado", "model": ErrorResponse},
        401: {"description": "Token inválido ou ausente", "model": ErrorResponse},
        403: {"description": "Permissão insuficiente", "model": ErrorResponse},
    },
)
async def get_training_cycle(
    cycle_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    context: ExecutionContext = Depends(permission_dep(["treinador", "coordenador", "dirigente"])),
):
    """
    Busca um ciclo de treinamento por ID.

    Retorna o ciclo com todos os microciclos relacionados.

    Requer permissão: coach ou admin
    """
    service = TrainingCycleService(db, context)

    try:
        cycle = await service.get_by_id(cycle_id)
        logger.info(f"Retrieved training cycle {cycle_id} by user {context.user_id}")
        return cycle
    except Exception as e:
        logger.error(f"Error retrieving training cycle {cycle_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training cycle not found: {str(e)}"
        )


@router.post(
    "",
    response_model=TrainingCycleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cria novo ciclo de treinamento",
    description="Cria um macrociclo ou mesociclo com validações de hierarquia e datas",
    responses={
        201: {"description": "Ciclo criado com sucesso"},
        400: {"description": "Dados inválidos", "model": ErrorResponse},
        401: {"description": "Token inválido ou ausente", "model": ErrorResponse},
        403: {"description": "Permissão insuficiente", "model": ErrorResponse},
    },
)
async def create_training_cycle(
    data: TrainingCycleCreate,
    db: AsyncSession = Depends(get_async_db),
    context: ExecutionContext = Depends(permission_dep(["treinador", "coordenador", "dirigente"])),
):
    """
    Cria um novo ciclo de treinamento.

    Validações:
    - Macrociclo NÃO pode ter parent_cycle_id
    - Mesociclo DEVE ter parent_cycle_id
    - start_date < end_date
    - Se mesociclo, datas devem estar dentro do macrociclo pai

    Requer permissão: coach ou admin
    """
    service = TrainingCycleService(db, context)

    try:
        cycle = await service.create(data)
        await db.commit()

        logger.info(
            f"Created training cycle {cycle.id} (type={cycle.type}) "
            f"for team {data.team_id} by user {context.user_id}"
        )

        return cycle
    except ValueError as e:
        await db.rollback()
        logger.warning(f"Validation error creating training cycle: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating training cycle: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating training cycle: {str(e)}"
        )


@router.patch(
    "/{cycle_id}",
    response_model=TrainingCycleResponse,
    summary="Atualiza ciclo de treinamento",
    description="Atualiza campos específicos de um ciclo (atualização parcial)",
    responses={
        200: {"description": "Ciclo atualizado com sucesso"},
        404: {"description": "Ciclo não encontrado", "model": ErrorResponse},
        400: {"description": "Dados inválidos", "model": ErrorResponse},
        401: {"description": "Token inválido ou ausente", "model": ErrorResponse},
        403: {"description": "Permissão insuficiente", "model": ErrorResponse},
    },
)
async def update_training_cycle(
    cycle_id: UUID,
    data: TrainingCycleUpdate,
    db: AsyncSession = Depends(get_async_db),
    context: ExecutionContext = Depends(permission_dep(["treinador", "coordenador", "dirigente"])),
):
    """
    Atualiza um ciclo de treinamento existente.

    Permite atualização parcial dos campos:
    - objective
    - notes
    - status

    Requer permissão: coach ou admin
    """
    service = TrainingCycleService(db, context)

    try:
        cycle = await service.update(cycle_id, data)
        await db.commit()

        logger.info(f"Updated training cycle {cycle_id} by user {context.user_id}")

        return cycle
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating training cycle {cycle_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training cycle not found: {str(e)}"
        )


@router.delete(
    "/{cycle_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove ciclo de treinamento (soft delete)",
    description="Marca ciclo como deletado sem remover do banco (soft delete)",
    responses={
        204: {"description": "Ciclo deletado com sucesso"},
        404: {"description": "Ciclo não encontrado", "model": ErrorResponse},
        401: {"description": "Token inválido ou ausente", "model": ErrorResponse},
        403: {"description": "Permissão insuficiente", "model": ErrorResponse},
    },
)
async def delete_training_cycle(
    cycle_id: UUID,
    reason: str = Query(..., description="Motivo da exclusão"),
    db: AsyncSession = Depends(get_async_db),
    context: ExecutionContext = Depends(permission_dep(["coordenador", "dirigente"])),
):
    """
    Remove um ciclo de treinamento (soft delete).

    O ciclo não é removido fisicamente do banco, apenas marcado como deletado
    com timestamp e motivo para auditoria.

    Requer permissão: admin
    """
    service = TrainingCycleService(db, context)

    try:
        await service.soft_delete(cycle_id, reason)
        await db.commit()

        logger.info(
            f"Soft deleted training cycle {cycle_id} by user {context.user_id}: {reason}"
        )

        return None
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting training cycle {cycle_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training cycle not found: {str(e)}"
        )


@router.get(
    "/teams/{team_id}/active",
    response_model=List[TrainingCycleResponse],
    summary="Busca ciclos ativos de uma equipe",
    description="Retorna ciclos ativos em uma data específica (default: hoje)",
    responses={
        200: {"description": "Lista de ciclos ativos"},
        401: {"description": "Token inválido ou ausente", "model": ErrorResponse},
        403: {"description": "Permissão insuficiente", "model": ErrorResponse},
    },
)
async def get_active_cycles(
    team_id: UUID,
    at_date: Optional[str] = Query(None, description="Data de referência (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_async_db),
    context: ExecutionContext = Depends(permission_dep(["treinador", "coordenador", "dirigente"])),
):
    """
    Busca ciclos ativos de uma equipe em uma data específica.

    Se `at_date` não for fornecido, usa a data atual.

    Retorna macrociclos antes de mesociclos.

    Requer permissão: coach ou admin
    """
    from datetime import date

    service = TrainingCycleService(db, context)

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

    cycles = await service.get_active_cycles_for_team(
        team_id=team_id,
        at_date=target_date,
    )

    logger.info(
        f"Retrieved {len(cycles)} active cycles for team {team_id} "
        f"at {target_date or 'today'} by user {context.user_id}"
    )

    return cycles
