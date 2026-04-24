from __future__ import annotations

import uuid
from dataclasses import dataclass, field
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
    # Conjunto de campos explicitamente presentes no payload (tri-state PATCH):
    # ausente → não altera; presente com valor → altera; presente com null → limpa
    provided_fields: frozenset = field(default_factory=frozenset)


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
