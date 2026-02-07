"""
Router para Posições (Defensivas e Ofensivas)
=============================================

Endpoints para listar posições disponíveis no sistema.
Usado nos formulários de cadastro de atletas.
"""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.db import get_db
from app.models.defensive_position import DefensivePosition
from app.models.offensive_position import OffensivePosition


router = APIRouter(
    tags=["positions"],
)


class PositionResponse(BaseModel):
    """Schema de resposta para posição."""
    id: int
    name: str
    code: str
    
    class Config:
        from_attributes = True


class PositionsListResponse(BaseModel):
    """Schema de resposta com todas as posições."""
    defensive: List[PositionResponse]
    offensive: List[PositionResponse]


# =============================================================================
# GET /v1/positions - Listar todas as posições
# =============================================================================

@router.get(
    "",
    response_model=PositionsListResponse,
    summary="Listar posições",
    description="""
Retorna todas as posições defensivas e ofensivas disponíveis.

Usado nos formulários de cadastro de atletas.

**Regras:**
- RD13: Goleiras não podem ter posição ofensiva
- Posições defensivas: goleira, ponta, meia, pivô, central
- Posições ofensivas: ponta esquerda, ponta direita, armador central, armador esquerdo, armador direito, pivô
""",
)
async def list_positions(
    db: Session = Depends(get_db),
):
    """Lista todas as posições defensivas e ofensivas."""
    
    defensive = db.query(DefensivePosition).order_by(DefensivePosition.id).all()
    offensive = db.query(OffensivePosition).order_by(OffensivePosition.id).all()
    
    return PositionsListResponse(
        defensive=[PositionResponse.model_validate(p) for p in defensive],
        offensive=[PositionResponse.model_validate(p) for p in offensive],
    )


# =============================================================================
# GET /v1/positions/defensive - Listar posições defensivas
# =============================================================================

@router.get(
    "/defensive",
    response_model=List[PositionResponse],
    summary="Listar posições defensivas",
    description="Retorna todas as posições defensivas disponíveis.",
)
async def list_defensive_positions(
    db: Session = Depends(get_db),
):
    """Lista posições defensivas."""
    positions = db.query(DefensivePosition).order_by(DefensivePosition.id).all()
    return [PositionResponse.model_validate(p) for p in positions]


# =============================================================================
# GET /v1/positions/offensive - Listar posições ofensivas
# =============================================================================

@router.get(
    "/offensive",
    response_model=List[PositionResponse],
    summary="Listar posições ofensivas",
    description="Retorna todas as posições ofensivas disponíveis.",
)
async def list_offensive_positions(
    db: Session = Depends(get_db),
):
    """Lista posições ofensivas."""
    positions = db.query(OffensivePosition).order_by(OffensivePosition.id).all()
    return [PositionResponse.model_validate(p) for p in positions]
