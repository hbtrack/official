"""
Router para Competition Seasons — FASE 4 Implementação.

Endpoints:
- GET  /v1/competitions/{competition_id}/seasons     → listCompetitionSeasonsByCompetition
- POST /v1/competitions/{competition_id}/seasons     → createCompetitionSeasonForCompetition
- GET  /v1/competition_seasons/{competition_season_id} → getCompetitionSeasonById
- PATCH /v1/competition_seasons/{competition_season_id} → updateCompetitionSeason
- GET  /v1/competition_seasons                       → listCompetitionSeasons (admin)

Regras de negócio aplicáveis:
- R25/R26: Permissões por papel e escopo
  - Dirigente/Coordenador: acesso administrativo/total
  - Treinador: escopo às suas equipes/competições na temporada
  - Atleta: somente leitura aos próprios dados
- R29: Exclusão lógica obrigatória — não há DELETE físico
- R33: Regra de ouro (nada fora de vínculo, nada apagado, histórico com rastro)
- RF4: Criação de temporadas (referência para competition_seasons)

Constraint:
- UNIQUE (competition_id, season_id)
- Violação retorna 409 conflict_unique

Erros mapeados:
- 401 unauthorized: Token inválido ou ausente
- 403 permission_denied (R25/R26): Permissão insuficiente
- 404 not_found: Competição ou vínculo não encontrado
- 409 conflict_unique: Violação de unicidade (competition_id + season_id)
- 422 validation_error: Payload inválido
"""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps.auth import permission_dep
from app.core.context import ExecutionContext, get_current_context
from app.core.db import get_async_db
from app.core.exceptions import ConflictError
from app.schemas.competitions import (
    CompetitionSeason as CompetitionSeasonSchema,
    CompetitionSeasonCreate,
    CompetitionSeasonPaginatedResponse,
    CompetitionSeasonUpdate,
)
from app.schemas.error import ErrorResponse
from app.services.competition_service import CompetitionService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["competition-seasons"])


# =============================================================================
# ENDPOINTS ANINHADOS EM /competitions/{competition_id}
# =============================================================================


@router.get(
    "/competitions/{competition_id}/seasons",
    status_code=status.HTTP_200_OK,
    summary="Listar seasons de uma competição",
    operation_id="listCompetitionSeasonsByCompetition",
    response_model=list[CompetitionSeasonSchema],
    responses={
        200: {"description": "Lista de temporadas da competição"},
        401: {"description": "Token inválido ou ausente", "model": ErrorResponse},
        403: {"description": "Permissão insuficiente (R25/R26)", "model": ErrorResponse},
        404: {"description": "Competição não encontrada", "model": ErrorResponse},
    },
)
async def list_competition_seasons_by_competition(
    competition_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    context: ExecutionContext = Depends(get_current_context),
    season_id: Optional[UUID] = Query(
        None,
        description="Filtrar por temporada específica (UUID)",
    ),
) -> list[CompetitionSeasonSchema]:
    """
    Lista temporadas vinculadas a uma competição específica.

    **Regras aplicáveis:**
    - R25/R26: Permissões por papel e escopo
    - RF4: Referência a temporadas (criação de temporadas)

    **Filtros disponíveis:**
    - season_id: Filtrar por temporada específica
    """
    service = CompetitionService(db, context)
    seasons = await service.list_competition_seasons(
        competition_id,
        season_id=season_id,
    )
    return [CompetitionSeasonSchema.model_validate(s) for s in seasons]


@router.post(
    "/competitions/{competition_id}/seasons",
    status_code=status.HTTP_201_CREATED,
    summary="Criar vínculo competição ↔ temporada",
    operation_id="createCompetitionSeasonForCompetition",
    response_model=CompetitionSeasonSchema,
    responses={
        201: {"description": "Vínculo criado com sucesso"},
        401: {"description": "Token inválido ou ausente", "model": ErrorResponse},
        403: {"description": "Permissão insuficiente (R25/R26)", "model": ErrorResponse},
        404: {"description": "Competição ou temporada não encontrada", "model": ErrorResponse},
        409: {
            "description": "Violação de unicidade (competition_id + season_id)",
            "model": ErrorResponse,
        },
        422: {"description": "Erro de validação", "model": ErrorResponse},
    },
)
async def create_competition_season_for_competition(
    competition_id: UUID,
    payload: CompetitionSeasonCreate,
    db: AsyncSession = Depends(get_async_db),
    context: ExecutionContext = Depends(permission_dep(roles=["admin", "coordinator"])),
) -> CompetitionSeasonSchema:
    """
    Cria um novo vínculo entre competição e temporada.

    **Regras aplicáveis:**
    - R25/R26: Permissões por papel e escopo
    - RF4: Referência a temporadas (competition_seasons dependem de seasons válidas)
    - R29: Exclusão lógica (sem delete físico)

    **Constraint:** UNIQUE (competition_id, season_id)
    - Violação retorna 409 conflict_unique

    **Campos obrigatórios:**
    - season_id: UUID da temporada a vincular

    **Erros possíveis:**
    - 404 not_found: Competição ou temporada não existe
    - 409 conflict_unique: Vínculo já existe para este par competition_id + season_id
    """
    service = CompetitionService(db, context)
    
    try:
        cs = await service.create_competition_season(competition_id, payload)
        db.commit()
        db.refresh(cs)
    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "conflict_unique",
                "message": str(e),
            }
        )

    logger.info(
        f"CompetitionSeason {cs.id} created "
        f"(comp={competition_id}, season={payload.season_id}) "
        f"by user {context.user_id}"
    )
    return CompetitionSeasonSchema.model_validate(cs)


# =============================================================================
# ENDPOINTS INDEPENDENTES /competition_seasons
# =============================================================================


@router.get(
    "/competition_seasons/{competition_season_id}",
    status_code=status.HTTP_200_OK,
    summary="Obter competition_season por ID",
    operation_id="getCompetitionSeasonById",
    response_model=CompetitionSeasonSchema,
    responses={
        200: {"description": "Detalhes do vínculo"},
        401: {"description": "Token inválido ou ausente", "model": ErrorResponse},
        403: {"description": "Permissão insuficiente (R25/R26)", "model": ErrorResponse},
        404: {"description": "Vínculo não encontrado", "model": ErrorResponse},
    },
)
async def get_competition_season_by_id(
    competition_season_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    context: ExecutionContext = Depends(get_current_context),
) -> CompetitionSeasonSchema:
    """
    Retorna os detalhes de um vínculo competição ↔ temporada específico.

    **Regras aplicáveis:**
    - R25/R26: Permissões por papel e escopo
    """
    service = CompetitionService(db, context)
    cs = await service.get_competition_season_by_id(competition_season_id)
    return CompetitionSeasonSchema.model_validate(cs)


@router.patch(
    "/competition_seasons/{competition_season_id}",
    status_code=status.HTTP_200_OK,
    summary="Atualizar competition_season",
    operation_id="updateCompetitionSeason",
    response_model=CompetitionSeasonSchema,
    responses={
        200: {"description": "Vínculo atualizado com sucesso"},
        401: {"description": "Token inválido ou ausente", "model": ErrorResponse},
        403: {"description": "Permissão insuficiente (R25/R26)", "model": ErrorResponse},
        404: {"description": "Vínculo não encontrado", "model": ErrorResponse},
        422: {"description": "Erro de validação", "model": ErrorResponse},
    },
)
async def update_competition_season(
    competition_season_id: UUID,
    payload: CompetitionSeasonUpdate,
    db: AsyncSession = Depends(get_async_db),
    context: ExecutionContext = Depends(permission_dep(roles=["admin", "coordinator"])),
) -> CompetitionSeasonSchema:
    """
    Atualiza campos permitidos de um vínculo competição ↔ temporada.

    **Campos editáveis:**
    - name: Nome/descrição do vínculo

    **Campos NÃO editáveis:**
    - competition_id (imutável)
    - season_id (imutável)

    **Regras aplicáveis:**
    - R25/R26: Permissões por papel e escopo
    - R29: Exclusão lógica (sem delete físico)
    """
    service = CompetitionService(db, context)
    cs = await service.update_competition_season(competition_season_id, payload)
    db.commit()
    db.refresh(cs)

    logger.info(
        f"CompetitionSeason {competition_season_id} updated by user {context.user_id}"
    )
    return CompetitionSeasonSchema.model_validate(cs)


@router.get(
    "/competition_seasons",
    status_code=status.HTTP_200_OK,
    summary="Listar competition_seasons (admin)",
    operation_id="listCompetitionSeasons",
    response_model=CompetitionSeasonPaginatedResponse,
    responses={
        200: {"description": "Lista paginada de vínculos"},
        401: {"description": "Token inválido ou ausente", "model": ErrorResponse},
        403: {"description": "Permissão insuficiente (R25/R26)", "model": ErrorResponse},
    },
)
async def list_competition_seasons(
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
    competition_id: Optional[UUID] = Query(
        None,
        description="Filtrar por competição (UUID)",
    ),
    season_id: Optional[UUID] = Query(
        None,
        description="Filtrar por temporada (UUID)",
    ),
) -> CompetitionSeasonPaginatedResponse:
    """
    Lista paginada de todos os vínculos competição ↔ temporada.
    Acesso administrativo (Coordenador/Dirigente).

    **Regras aplicáveis:**
    - R25/R26: Permissões (somente Coordenador e Dirigente)

    **Filtros disponíveis:**
    - competition_id: Filtrar por competição específica
    - season_id: Filtrar por temporada específica

    **Paginação:**
    - page: Número da página (1-indexed)
    - limit: Itens por página (1-100, padrão 50)

    **Envelope de resposta:** {items, page, limit, total}
    """
    service = CompetitionService(db, context)
    seasons, total = await service.list_all_competition_seasons(
        page=page,
        limit=limit,
        competition_id=competition_id,
        season_id=season_id,
    )

    return CompetitionSeasonPaginatedResponse(
        items=[CompetitionSeasonSchema.model_validate(s) for s in seasons],
        page=page,
        limit=limit,
        total=total,
    )
