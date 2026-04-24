from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from ninja import Schema
from pydantic import ConfigDict, Field
from pydantic.alias_generators import to_camel

_CAMEL = ConfigDict(alias_generator=to_camel, populate_by_name=True)


# ---------------------------------------------------------------------------
# Wellness schemas
# ---------------------------------------------------------------------------

class WellnessPreOut(Schema):
    model_config = _CAMEL
    id: uuid.UUID
    # alias explícito: session_id → trainingSessionId (alinha com contrato wellness_pre.yaml)
    session_id: uuid.UUID = Field(alias="trainingSessionId")
    athlete_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    readiness: Optional[int] = None
    sleep_quality: Optional[int] = None
    sleep_hours: Optional[float] = None
    mood: Optional[int] = None
    fatigue: Optional[int] = None
    muscle_soreness: Optional[int] = None
    notes: Optional[str] = None


class SubmitWellnessPreIn(Schema):
    model_config = _CAMEL
    athlete_id: uuid.UUID
    sleep_quality: int = Field(..., ge=1, le=5)    # required — INV-TRAIN-034
    sleep_hours: float = Field(..., ge=0, le=24)   # required — SS-TRAIN-006
    readiness: Optional[int] = Field(None, ge=1, le=5)
    mood: Optional[int] = Field(None, ge=1, le=5)
    fatigue: Optional[int] = Field(None, ge=1, le=5)
    muscle_soreness: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None


class UpdateWellnessPreIn(Schema):
    model_config = _CAMEL
    sleep_quality: Optional[int] = Field(None, ge=1, le=5)
    sleep_hours: Optional[float] = Field(None, ge=0, le=24)
    readiness: Optional[int] = Field(None, ge=1, le=5)
    mood: Optional[int] = Field(None, ge=1, le=5)
    fatigue: Optional[int] = Field(None, ge=1, le=5)
    muscle_soreness: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None


class WellnessPostOut(Schema):
    model_config = _CAMEL
    id: uuid.UUID
    # alias explícito: session_id → trainingSessionId (alinha com contrato)
    session_id: uuid.UUID = Field(alias="trainingSessionId")
    athlete_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    perceived_exertion: Optional[int] = None
    enjoyment: Optional[int] = None
    technical_learning: Optional[int] = None
    notes: Optional[str] = None


class SubmitWellnessPostIn(Schema):
    model_config = _CAMEL
    athlete_id: uuid.UUID
    perceived_exertion: Optional[int] = None
    enjoyment: Optional[int] = None
    technical_learning: Optional[int] = None
    notes: Optional[str] = None


class UpdateWellnessPostIn(Schema):
    model_config = _CAMEL
    perceived_exertion: Optional[int] = None
    enjoyment: Optional[int] = None
    technical_learning: Optional[int] = None
    notes: Optional[str] = None
