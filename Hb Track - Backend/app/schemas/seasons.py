"""
Schemas para Season.
Ref: FASE 3 — Contrato Seasons
Regras: RF4, RF5, RF5.1, RF5.2, RDB4, RDB8, 6.1.1

Schema DB:
- year: int (obrigatório, unique)
- name: text (opcional)
- starts_at/ends_at: date (opcionais)
- is_active: boolean

API usa start_date/end_date (aliases no model).
"""

from datetime import date, datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SeasonStatus(str, Enum):
    """
    Status derivado da temporada (6.1.1).
    Não é armazenado — calculado em runtime.
    """

    planejada = "planejada"
    ativa = "ativa"
    interrompida = "interrompida"
    cancelada = "cancelada"
    encerrada = "encerrada"


class SeasonCreate(BaseModel):
    """
    Payload para criação de temporada (RF4).
    """

    team_id: UUID = Field(..., description="Equipe dona da temporada")
    year: int = Field(..., ge=2000, le=2100, description="Ano da temporada (único)")
    name: str = Field(..., min_length=1, max_length=120, description="Nome da temporada")
    competition_type: Optional[str] = Field(None, min_length=1, max_length=32, description="Tipo de competição")
    start_date: date = Field(..., description="Data de início")
    end_date: date = Field(..., description="Data de término")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "team_id": "11111111-1111-1111-1111-111111111111",
                "year": 2025,
                "name": "Temporada 2025",
                "competition_type": "Estadual",
                "start_date": "2025-01-01",
                "end_date": "2025-12-31",
            }
        }
    )


class SeasonUpdate(BaseModel):
    """
    Payload para atualização de temporada (RF5).
    Todos os campos são opcionais.
    """

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Temporada 2025 - Atualizada",
            }
        }
    )


class SeasonResponse(BaseModel):
    """
    Response completo de temporada.
    Inclui status derivado (6.1.1).
    """

    id: UUID
    team_id: UUID
    organization_id: UUID
    year: int
    name: str
    competition_type: Optional[str] = None
    start_date: date
    end_date: date
    is_active: bool = False
    status: SeasonStatus = Field(..., description="Status derivado (6.1.1)")

    # Status control
    canceled_at: Optional[datetime] = None
    interrupted_at: Optional[datetime] = None

    # Soft delete (RDB4)
    deleted_at: Optional[datetime] = None
    deleted_reason: Optional[str] = None

    created_by_user_id: Optional[UUID] = None

    # Timestamps (RDB3)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SeasonPaginatedResponse(BaseModel):
    """
    Response paginado para listagem de temporadas.
    """

    items: list[SeasonResponse]
    page: int = Field(..., ge=1, description="Página atual")
    limit: int = Field(..., ge=1, le=100, description="Itens por página")
    total: int = Field(..., ge=0, description="Total de itens")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [],
                "page": 1,
                "limit": 50,
                "total": 0,
            }
        }
    )


# Aliases para compatibilidade
Season = SeasonResponse
