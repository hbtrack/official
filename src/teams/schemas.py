
# CODEGEN CUTOVER — generated layer linked
from .generated import schemas as _gen_schemas  # noqa: F401


"""
Schemas Pydantic/Ninja — módulo teams.
Correspondem 1-1 aos componentes do contrato OpenAPI teams.yaml.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from ninja import Schema

class TeamOut(Schema):
    id: UUID
    organization_id: UUID
    name: str
    category_label: str
    status_label: str
    season_id: Optional[UUID] = None
    short_name: Optional[str] = None
    athlete_ids: list[UUID] = []
    staff_user_ids: list[UUID] = []
    roster_notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class TeamListOut(Schema):
    data: list[TeamOut]
    page: int
    page_size: int
    total: int

class CreateTeamIn(Schema):
    organization_id: UUID
    name: str
    category_label: str
    season_id: Optional[UUID] = None
    short_name: Optional[str] = None
    athlete_ids: list[UUID] = []
    staff_user_ids: list[UUID] = []
    roster_notes: Optional[str] = None

class PatchTeamIn(Schema):
    name: Optional[str] = None
    category_label: Optional[str] = None
    season_id: Optional[UUID] = None
    short_name: Optional[str] = None
    roster_notes: Optional[str] = None
    status_label: Optional[str] = None
