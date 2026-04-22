from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from ninja import Schema


# ---------------------------------------------------------------------------
# Wellness schemas
# ---------------------------------------------------------------------------

class WellnessPreOut(Schema):
    id: uuid.UUID
    session_id: uuid.UUID
    athlete_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    readiness: Optional[int] = None
    sleep_quality: Optional[int] = None
    mood: Optional[int] = None
    fatigue: Optional[int] = None
    muscle_soreness: Optional[int] = None
    notes: Optional[str] = None


class SubmitWellnessPreIn(Schema):
    athlete_id: uuid.UUID
    readiness: Optional[int] = None
    sleep_quality: Optional[int] = None
    mood: Optional[int] = None
    fatigue: Optional[int] = None
    muscle_soreness: Optional[int] = None
    notes: Optional[str] = None


class UpdateWellnessPreIn(Schema):
    readiness: Optional[int] = None
    sleep_quality: Optional[int] = None
    mood: Optional[int] = None
    fatigue: Optional[int] = None
    muscle_soreness: Optional[int] = None
    notes: Optional[str] = None


class WellnessPostOut(Schema):
    id: uuid.UUID
    session_id: uuid.UUID
    athlete_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    perceived_exertion: Optional[int] = None
    enjoyment: Optional[int] = None
    technical_learning: Optional[int] = None
    notes: Optional[str] = None


class SubmitWellnessPostIn(Schema):
    athlete_id: uuid.UUID
    perceived_exertion: Optional[int] = None
    enjoyment: Optional[int] = None
    technical_learning: Optional[int] = None
    notes: Optional[str] = None


class UpdateWellnessPostIn(Schema):
    perceived_exertion: Optional[int] = None
    enjoyment: Optional[int] = None
    technical_learning: Optional[int] = None
    notes: Optional[str] = None
