"""
Router para Lookup Tables - Tabelas de referência estáticas.

Endpoints:
- GET /offensive-positions - Posições ofensivas
- GET /defensive-positions - Posições defensivas
- GET /schooling-levels - Níveis de escolaridade

Regras RAG:
- RDB17: Tabelas de lookup globais
- RD13: Goleiras (defensive_position_id=5) não podem ter posição ofensiva
"""
from typing import List
from pydantic import BaseModel

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.auth import get_current_context
from app.core.context import ExecutionContext
from app.models.offensive_position import OffensivePosition
from app.models.defensive_position import DefensivePosition
from app.models.schooling_level import SchoolingLevel


# === Schemas ===

class PositionResponse(BaseModel):
    """Schema para posições (ofensiva/defensiva)"""
    id: int
    code: str
    name: str
    abbreviation: str | None = None
    is_active: bool = True

    class Config:
        from_attributes = True


class SchoolingLevelResponse(BaseModel):
    """Schema para níveis de escolaridade"""
    id: int
    code: str
    name: str
    is_active: bool = True

    class Config:
        from_attributes = True


# === Routers ===

offensive_router = APIRouter(
    prefix="/offensive-positions",
    tags=["Lookup Tables"],
)

defensive_router = APIRouter(
    prefix="/defensive-positions",
    tags=["Lookup Tables"],
)

schooling_router = APIRouter(
    prefix="/schooling-levels",
    tags=["Lookup Tables"],
)


@offensive_router.get(
    "",
    response_model=List[PositionResponse],
    summary="Listar posições ofensivas",
    description="Retorna todas as posições ofensivas disponíveis (Armador Central, Armador Lateral, Ponta, Pivô).",
)
def list_offensive_positions(
    db: Session = Depends(get_db),
    ctx: ExecutionContext = Depends(get_current_context),
):
    """Lista posições ofensivas - RDB17"""
    positions = db.query(OffensivePosition).order_by(OffensivePosition.id).all()
    return positions


@defensive_router.get(
    "",
    response_model=List[PositionResponse],
    summary="Listar posições defensivas",
    description="Retorna todas as posições defensivas disponíveis (Goleira, Central, Lateral, Ponta).",
)
def list_defensive_positions(
    db: Session = Depends(get_db),
    ctx: ExecutionContext = Depends(get_current_context),
):
    """Lista posições defensivas - RDB17"""
    positions = db.query(DefensivePosition).order_by(DefensivePosition.id).all()
    return positions


@schooling_router.get(
    "",
    response_model=List[SchoolingLevelResponse],
    summary="Listar níveis de escolaridade",
    description="Retorna todos os níveis de escolaridade disponíveis.",
)
def list_schooling_levels(
    db: Session = Depends(get_db),
    ctx: ExecutionContext = Depends(get_current_context),
):
    """Lista níveis de escolaridade - RDB17"""
    levels = db.query(SchoolingLevel).order_by(SchoolingLevel.id).all()
    return levels
