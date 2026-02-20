"""
Schemas Pydantic para Matches (Partidas) alinhados ao schema real.
"""

from datetime import date, datetime, time
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.match import MatchStatus, MatchType


class MatchBase(BaseModel):
    match_date: date = Field(..., description="Data da partida")
    opponent_name: Optional[str] = Field(None, max_length=200, description="Adversário ou nota")
    match_type: MatchType = Field(default=MatchType.friendly, description="Tipo/fase da partida")
    is_home: Optional[bool] = Field(default=None, description="Se é jogo em casa")
    location: Optional[str] = Field(None, max_length=200, description="Local da partida")


class MatchCreate(MatchBase):
    team_id: UUID = Field(..., description="ID do time (our_team_id)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "team_id": "123e4567-e89b-12d3-a456-426614174000",
                "match_date": "2024-03-15",
                "opponent_name": "Adversário FC",
                "match_type": "friendly",
                "is_home": True,
                "location": "Ginásio Municipal"
            }
        }
    )


class MatchUpdate(BaseModel):
    match_date: Optional[date] = None
    opponent_name: Optional[str] = Field(None, min_length=1, max_length=200)
    match_type: Optional[MatchType] = None
    is_home: Optional[bool] = None
    location: Optional[str] = Field(None, max_length=200)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "opponent_name": "Novo Nome Adversário",
                "location": "Novo Local"
            }
        }
    )


class MatchStatusUpdate(BaseModel):
    status: MatchStatus = Field(..., description="Novo status da partida")
    admin_note: Optional[str] = Field(None, max_length=500, description="Nota administrativa")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "in_progress",
                "admin_note": "Ajuste de status"
            }
        }
    )


class MatchResponse(BaseModel):
    id: UUID
    organization_id: UUID
    season_id: UUID
    team_id: UUID
    match_date: date
    opponent_name: Optional[str]
    match_type: MatchType
    is_home: Optional[bool]
    location: Optional[str]
    status: MatchStatus

    finalized_at: Optional[datetime] = Field(None, description="Data/hora da finalização")
    validated_at: Optional[datetime] = Field(None, description="Data/hora da validação")
    reopened_at: Optional[datetime] = Field(None, description="Data/hora da última reabertura")

    deleted_at: Optional[datetime] = None
    deleted_reason: Optional[str] = None

    admin_note: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    is_finalized: bool = Field(default=False, description="Se a partida está finalizada")
    can_edit: bool = Field(default=True, description="Se a partida pode ser editada")

    model_config = ConfigDict(from_attributes=True)


class MatchSummary(BaseModel):
    id: UUID
    match_date: date
    match_time: Optional[time] = Field(None, description="Horário da partida")
    opponent_name: Optional[str]
    match_type: MatchType
    is_home: Optional[bool]
    location: Optional[str] = Field(None, description="Local da partida")
    status: MatchStatus

    model_config = ConfigDict(from_attributes=True)


class MatchList(BaseModel):
    items: list[MatchSummary]
    total: int
    page: int
    size: int
    pages: int


class MatchWithEvents(MatchResponse):
    events: list["ScoutEventRead"] = []
    total_events: int = 0


from app.schemas.match_events import ScoutEventRead  # noqa: E402

MatchWithEvents.model_rebuild()
