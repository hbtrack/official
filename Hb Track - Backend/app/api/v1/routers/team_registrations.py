"""
Router Team Registrations - FASE 5.

Escopos:
- Sempre exige equipe no path: /teams/{team_id}/registrations/...
- Permissões: papéis dirigentes/coordenadores/treinadores.
"""

import logging
from typing import Optional
from uuid import UUID
from datetime import date

from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.v1.deps.auth import permission_dep
from app.core.context import ExecutionContext
from app.core.db import get_async_db
from app.core.permissions import require_team_registration_in_season
from app.core.exceptions import NotFoundError
from app.services.team_registration_service import TeamRegistrationService
from app.models.team_registration import TeamRegistration as TeamRegistrationModel
from app.models.athlete import Athlete
from app.models.team import Team
from app.models.season import Season
from app.schemas.team_registrations import (
    TeamRegistration,
    TeamRegistrationCreate,
    TeamRegistrationPaginatedResponse,
    TeamRegistrationUpdate,
)
from app.schemas.error import ErrorResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["team-registrations"])


def _get_service(db: AsyncSession) -> TeamRegistrationService:
    return TeamRegistrationService(db)


@router.get(
    "/teams/{team_id}/registrations",
    status_code=status.HTTP_200_OK,
    summary="Listar inscrições de uma equipe",
    response_model=TeamRegistrationPaginatedResponse,
)
async def list_team_registrations(
    team_id: UUID,
    athlete_id: Optional[UUID] = Query(None, description="Filtrar por atleta"),
    season_id: Optional[UUID] = Query(None, description="Filtrar por temporada"),
    active_only: bool = Query(False, description="Apenas inscrições ativas"),
    page: int = Query(1, ge=1, description="Página"),
    limit: int = Query(50, ge=1, le=200, description="Itens por página"),
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(
        permission_dep(
            roles=["treinador", "coordenador", "dirigente"],
            require_team=True,
        )
    ),
) -> TeamRegistrationPaginatedResponse:
    service = _get_service(db)

    if athlete_id:
        regs = await service.list_by_athlete(
            athlete_id=athlete_id,
            season_id=season_id,
            active_only=active_only,
        )
        regs = [r for r in regs if str(r.team_id) == str(team_id)]
    else:
        regs = await service.list_by_team(team_id=team_id, active_only=active_only)

    total = len(regs)
    items = regs[(page - 1) * limit : page * limit]
    return TeamRegistrationPaginatedResponse(
        items=[TeamRegistration.model_validate(r) for r in items],
        page=page,
        limit=limit,
        total=total,
    )


@router.post(
    "/teams/{team_id}/registrations/{athlete_id}",
    status_code=status.HTTP_201_CREATED,
    summary="Criar inscrição atleta–equipe",
    response_model=TeamRegistration,
    responses={
        201: {"description": "Inscrição criada com sucesso"},
        401: {"description": "Token inválido ou ausente", "model": ErrorResponse},
        403: {"description": "Permissão insuficiente", "model": ErrorResponse},
        404: {"description": "Atleta ou equipe não encontrada", "model": ErrorResponse},
        409: {"description": "Período sobreposto (RDB10)", "model": ErrorResponse},
    },
)
async def create_team_registration(
    team_id: UUID,
    athlete_id: UUID,
    payload: TeamRegistrationCreate,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(
        permission_dep(
            roles=["treinador", "coordenador", "dirigente"],
            require_team=True,
        )
    ),
) -> TeamRegistration:
    # Validar consistência do payload com o path
    if str(payload.team_id) != str(team_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "invalid_team", "message": "team_id do path difere do payload"},
        )
    if str(payload.organization_id) != str(ctx.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "permission_denied", "message": "Organização fora do escopo"},
        )

    # Validar atleta existe
    athlete = await db.get(Athlete, athlete_id)
    if not athlete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="athlete_not_found")

    service = _get_service(db)
    try:
        reg = await service.create(
            athlete_id=athlete_id,
            season_id=payload.season_id,
            category_id=payload.category_id,
            team_id=team_id,
            organization_id=payload.organization_id,
            created_by_membership_id=payload.created_by_membership_id,
            role=payload.role,
            start_at=payload.start_at,
            end_at=payload.end_at,
        )
        await db.commit()
        await db.refresh(reg)
        return TeamRegistration.model_validate(reg)
    except ValueError as e:
        await db.rollback()
        code = str(e)
        if code == "period_overlap":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="period_overlap")
        if code == "invalid_date_range":
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="invalid_date_range")
        raise


@router.patch(
    "/teams/{team_id}/registrations/{registration_id}",
    status_code=status.HTTP_200_OK,
    summary="Atualizar inscrição",
    response_model=TeamRegistration,
)
async def update_team_registration(
    team_id: UUID,
    registration_id: UUID,
    payload: TeamRegistrationUpdate,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(
        permission_dep(
            roles=["treinador", "coordenador", "dirigente"],
            require_team=True,
        )
    ),
) -> TeamRegistration:
    service = _get_service(db)
    reg = await service.get_by_id(registration_id)
    if not reg or str(reg.team_id) != str(team_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="registration_not_found")

    updated = await service.update(
        registration_id=registration_id,
        end_at=payload.end_at,
        role=payload.role,
    )
    await db.commit()
    await db.refresh(updated)
    return TeamRegistration.model_validate(updated)


@router.get(
    "/teams/{team_id}/registrations/{registration_id}",
    status_code=status.HTTP_200_OK,
    summary="Obter inscrição por ID",
    response_model=TeamRegistration,
)
async def get_team_registration(
    team_id: UUID,
    registration_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(
        permission_dep(
            roles=["treinador", "coordenador", "dirigente"],
            require_team=True,
        )
    ),
) -> TeamRegistration:
    service = _get_service(db)
    reg = await service.get_by_id(registration_id)
    if not reg or str(reg.team_id) != str(team_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="registration_not_found")
    return TeamRegistration.model_validate(reg)

