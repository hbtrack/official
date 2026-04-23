from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Optional

from ...domain.rules import RoleLabel


@dataclass
class SubmitWellnessPreInput:
    session_id: uuid.UUID
    athlete_id: uuid.UUID
    actor_role: RoleLabel
    actor_id: uuid.UUID
    readiness: Optional[int] = None
    sleep_quality: Optional[int] = None
    sleep_hours: Optional[float] = None
    mood: Optional[int] = None
    fatigue: Optional[int] = None
    muscle_soreness: Optional[int] = None
    notes: Optional[str] = None


@dataclass
class SubmitWellnessPostInput:
    session_id: uuid.UUID
    athlete_id: uuid.UUID
    actor_role: RoleLabel
    actor_id: uuid.UUID
    perceived_exertion: Optional[int] = None
    enjoyment: Optional[int] = None
    technical_learning: Optional[int] = None
    notes: Optional[str] = None


@dataclass
class GetWellnessPreInput:
    session_id: uuid.UUID
    athlete_id: uuid.UUID
    actor_role: RoleLabel
    actor_id: uuid.UUID


@dataclass
class UpdateWellnessPreInput:
    session_id: uuid.UUID
    athlete_id: uuid.UUID
    actor_role: RoleLabel
    actor_id: uuid.UUID
    readiness: Optional[int] = None
    sleep_quality: Optional[int] = None
    sleep_hours: Optional[float] = None
    mood: Optional[int] = None
    fatigue: Optional[int] = None
    muscle_soreness: Optional[int] = None
    notes: Optional[str] = None


@dataclass
class GetWellnessPostInput:
    session_id: uuid.UUID
    athlete_id: uuid.UUID
    actor_role: RoleLabel
    actor_id: uuid.UUID


@dataclass
class UpdateWellnessPostInput:
    session_id: uuid.UUID
    athlete_id: uuid.UUID
    actor_role: RoleLabel
    actor_id: uuid.UUID
    perceived_exertion: Optional[int] = None
    enjoyment: Optional[int] = None
    technical_learning: Optional[int] = None
    notes: Optional[str] = None
