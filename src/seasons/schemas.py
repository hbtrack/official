from __future__ import annotations

# CODEGEN CUTOVER — generated layer linked
from .generated import schemas as _gen_schemas  # noqa: F401


"""
Pydantic schemas (django-ninja) — módulo seasons.
Mapeiam contratos OpenAPI → domain entities.
Contrato: contracts/openapi/paths/seasons.yaml
"""

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from ninja import Schema

class SeasonOut(Schema):
    """Resposta canônica de Season (season.schema.json)."""
    id: UUID
    name: str
    start_date: date
    end_date: date
    status_label: str
    phase_labels: list[str]
    team_ids: list[UUID]
    competition_ids: list[UUID]
    organization_id: Optional[UUID] = None
    sport_cycle_label: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        # Mapeia atributos snake_case da entidade para camelCase no JSON
        populate_by_name = True

class SeasonListOut(Schema):
    """Resposta paginada de listSeasons."""
    data: list[SeasonOut]
    page: int
    page_size: int
    total: int

class CreateSeasonIn(Schema):
    """Payload de createSeason (POST /seasons)."""
    name: str
    start_date: date
    end_date: date
    sport_cycle_label: Optional[str] = None
    phase_labels: list[str] = []
    organization_id: Optional[UUID] = None

class PatchSeasonIn(Schema):
    """Payload de patchSeason (PATCH /seasons/{seasonId})."""
    name: Optional[str] = None
    sport_cycle_label: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status_label: Optional[str] = None
    phase_labels: Optional[list[str]] = None
