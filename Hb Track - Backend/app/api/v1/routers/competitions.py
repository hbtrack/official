"""
Router para Competitions — FASE 4 Implementação.

Endpoints:
- GET  /v1/competitions                   → listCompetitions
- POST /v1/competitions                   → createCompetition
- GET  /v1/competitions/{competition_id}  → getCompetitionById
- PATCH /v1/competitions/{competition_id} → updateCompetition

Regras de negócio aplicáveis:
- R25/R26: Permissões por papel e escopo
  - Dirigente/Coordenador: acesso administrativo/total
  - Treinador: escopo às suas equipes/competições na temporada
  - Atleta: somente leitura aos próprios dados
- R29: Exclusão lógica obrigatória — não há DELETE físico
- R33: Regra de ouro (nada fora de vínculo, nada apagado, histórico com rastro)
- R34: Clube único na V1; contexto organizacional implícito via token
- R42: Modo somente leitura sem vínculo ativo

Campo kind:
- Texto livre na V1
- Exemplos: "official", "friendly", "training-game"

Erros mapeados:
- 401 unauthorized: Token inválido ou ausente
- 403 permission_denied (R25/R26): Permissão insuficiente
- 404 not_found: Competição não encontrada
- 422 validation_error: Payload inválido
"""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps.auth import permission_dep
from app.core.context import ExecutionContext, get_current_context
from app.core.db import get_async_db
from app.schemas.competitions import (
    Competition as CompetitionSchema,
    CompetitionCreate,
    CompetitionPaginatedResponse,
    CompetitionUpdate,
)
from app.schemas.error import ErrorResponse
from app.services.competition_service import CompetitionService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["competitions"])


@router.get(
    "/competitions",
    status_code=status.HTTP_200_OK,
    summary="Listar competições",
    operation_id="listCompetitions",
    response_model=CompetitionPaginatedResponse,
    responses={
        200: {"description": "Lista paginada de competições"},
        401: {"description": "Token inválido ou ausente", "model": ErrorResponse},
        403: {"description": "Permissão insuficiente (R25/R26)", "model": ErrorResponse},
    },
)
async def list_competitions(
    db: AsyncSession = Depends(get_async_db),
    context: ExecutionContext = Depends(get_current_context),
    page: int = Query(
        1,
        ge=1,
        description="Número da página (1-indexed)",
    ),
    limit: int = Query(
        50,
        ge=1,
        le=100,
        description="Itens por página (máximo 100)",
    ),
    order_by: str = Query(
        "created_at",
        description="Campo para ordenação",
        pattern="^(created_at|name|updated_at)$",
    ),
    order_dir: str = Query(
        "desc",
        description="Direção da ordenação",
        pattern="^(asc|desc)$",
    ),
    name: Optional[str] = Query(
        None,
        description="Filtro por nome (case-insensitive)",
    ),
    kind: Optional[str] = Query(
        None,
        description="Filtro por tipo de competição",
    ),
) -> CompetitionPaginatedResponse:
    """
    Lista paginada de competições da organização.

    **Regras aplicáveis:**
    - R25/R26: Permissões por papel e escopo
    - R34: Clube único na V1 (contexto implícito do token)
    - R42: Modo somente leitura sem vínculo ativo

    **Filtros disponíveis:**
    - name: filtro por nome (case-insensitive, ilike)
    - kind: filtro por tipo de competição

    **Ordenação:**
    - order_by: created_at (padrão), name, updated_at
    - order_dir: desc (padrão), asc

    **Paginação:**
    - page: Número da página (1-indexed)
    - limit: Itens por página (1-100, padrão 50)

    **Envelope de resposta:** {items, page, limit, total}
    """
    service = CompetitionService(db, context)
    competitions, total = await service.list_competitions(
        page=page,
        limit=limit,
        order_by=order_by,
        order_dir=order_dir,
        name=name,
        kind=kind,
    )

    return CompetitionPaginatedResponse(
        items=[CompetitionSchema.model_validate(c) for c in competitions],
        page=page,
        limit=limit,
        total=total,
    )


@router.post(
    "/competitions",
    status_code=status.HTTP_201_CREATED,
    summary="Criar competição",
    operation_id="createCompetition",
    response_model=CompetitionSchema,
    responses={
        201: {"description": "Competição criada com sucesso"},
        401: {"description": "Token inválido ou ausente", "model": ErrorResponse},
        403: {"description": "Permissão insuficiente (R25/R26)", "model": ErrorResponse},
        422: {"description": "Erro de validação", "model": ErrorResponse},
    },
)
async def create_competition(
    payload: CompetitionCreate,
    db: AsyncSession = Depends(get_async_db),
    context: ExecutionContext = Depends(permission_dep(roles=["admin", "coordinator"])),
) -> CompetitionSchema:
    """
    Cria uma nova competição (registro base).

    **Regras aplicáveis:**
    - R25/R26: Permissões por papel e escopo
    - R29: Exclusão lógica (sem delete físico)
    - R34: Clube único na V1 (organization_id do contexto)

    **Campos obrigatórios:**
    - name: Nome da competição

    **Campo kind:**
    Texto livre. Exemplos: "official", "friendly", "training-game"
    
    **Nota:** A organização é determinada automaticamente pelo token de autenticação.
    """
    service = CompetitionService(db, context)
    competition = await service.create_competition(payload)
    db.commit()
    db.refresh(competition)

    logger.info(f"Competition {competition.id} created by user {context.user_id}")
    return CompetitionSchema.model_validate(competition)


@router.get(
    "/competitions/{competition_id}",
    status_code=status.HTTP_200_OK,
    summary="Obter competição por ID",
    operation_id="getCompetitionById",
    response_model=CompetitionSchema,
    responses={
        200: {"description": "Detalhes da competição"},
        401: {"description": "Token inválido ou ausente", "model": ErrorResponse},
        403: {"description": "Permissão insuficiente (R25/R26)", "model": ErrorResponse},
        404: {"description": "Competição não encontrada", "model": ErrorResponse},
    },
)
async def get_competition_by_id(
    competition_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    context: ExecutionContext = Depends(get_current_context),
) -> CompetitionSchema:
    """
    Retorna os detalhes de uma competição específica.

    **Regras aplicáveis:**
    - R25/R26: Permissões por papel e escopo
    """
    service = CompetitionService(db, context)
    competition = await service.get_competition_by_id(competition_id)
    return CompetitionSchema.model_validate(competition)


@router.patch(
    "/competitions/{competition_id}",
    status_code=status.HTTP_200_OK,
    summary="Atualizar competição",
    operation_id="updateCompetition",
    response_model=CompetitionSchema,
    responses={
        200: {"description": "Competição atualizada com sucesso"},
        401: {"description": "Token inválido ou ausente", "model": ErrorResponse},
        403: {"description": "Permissão insuficiente (R25/R26)", "model": ErrorResponse},
        404: {"description": "Competição não encontrada", "model": ErrorResponse},
        422: {"description": "Erro de validação", "model": ErrorResponse},
    },
)
async def update_competition(
    competition_id: UUID,
    payload: CompetitionUpdate,
    db: AsyncSession = Depends(get_async_db),
    context: ExecutionContext = Depends(permission_dep(roles=["admin", "coordinator"])),
) -> CompetitionSchema:
    """
    Atualiza campos permitidos de uma competição existente.

    **Campos editáveis:**
    - name: Nome da competição
    - kind: Tipo da competição

    **Campos NÃO editáveis:**
    - organization_id (imutável após criação)

    **Regras aplicáveis:**
    - R25/R26: Permissões por papel e escopo
    - R29: Exclusão lógica (sem delete físico)
    """
    service = CompetitionService(db, context)
    competition = await service.update_competition(competition_id, payload)
    db.commit()
    db.refresh(competition)

    logger.info(f"Competition {competition_id} updated by user {context.user_id}")
    return CompetitionSchema.model_validate(competition)
