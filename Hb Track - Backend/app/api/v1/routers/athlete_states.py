"""
Router AthleteStates - Historico de estados.
Regras: R13, R14, RF16
"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_db
from app.core.auth import get_current_user, MockUser
from app.services.athlete_service_v2 import AthleteServiceV2
from app.schemas.athletes_v2 import ChangeStateRequest, AthleteStateHistoryResponse

router = APIRouter(tags=["athlete-states"])


@router.get("/athletes/{athlete_id}/states", response_model=list[AthleteStateHistoryResponse])
async def list_athlete_states(
    athlete_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: MockUser = Depends(get_current_user),
):
    """Lista historico de estados da atleta. Regras: R13, RF16"""
    service = AthleteServiceV2(db)
    athlete = await service.get_by_id(athlete_id)

    if not athlete:
        raise HTTPException(status_code=404, detail="not_found")

    return await service.get_state_history(athlete_id)


@router.post("/athletes/{athlete_id}/state", response_model=AthleteStateHistoryResponse, status_code=status.HTTP_201_CREATED)
async def change_athlete_state(
    athlete_id: UUID,
    data: ChangeStateRequest,
    db: AsyncSession = Depends(get_async_db),
    current_user: MockUser = Depends(get_current_user),
):
    """
    Altera estado da atleta.

    Regras:
    - R13: Estados validos (ativa, lesionada, dispensada)
    - R14: Impacto nos relatorios
    - RF16: Alteracao auditavel
    - V1.1: "dispensada" encerra team_registrations
    """
    service = AthleteServiceV2(db)
    try:
        return await service.change_state(
            athlete_id,
            data,
            changed_by_membership_id=current_user.membership_id,
        )
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "invalid_state_transition",
                "message": "invalid_state_transition",
            },
        )
