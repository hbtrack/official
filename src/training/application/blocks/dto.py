from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Optional

from ...domain.rules import RoleLabel


@dataclass
class ListSessionBlocksInput:
    session_id: uuid.UUID
    actor_role: RoleLabel
    actor_id: uuid.UUID
    session_athlete_ids: list[uuid.UUID] = field(default_factory=list)


@dataclass
class AddSessionBlockInput:
    session_id: uuid.UUID
    actor_role: RoleLabel
    actor_id: uuid.UUID
    phase: str
    order_index: int
    duration_minutes: int
    block_objective: str
    intensity: str
    is_optional: bool
    exercise_id: Optional[uuid.UUID] = None
    exercise_version_id: Optional[uuid.UUID] = None
    notes: Optional[str] = None


@dataclass
class UpdateSessionBlockInput:
    session_id: uuid.UUID
    block_id: uuid.UUID
    actor_role: RoleLabel
    duration_minutes: Optional[int] = None
    block_objective: Optional[str] = None
    intensity: Optional[str] = None
    phase: Optional[str] = None
    is_optional: Optional[bool] = None
    notes: Optional[str] = None
    exercise_id: Optional[uuid.UUID] = None
    exercise_version_id: Optional[uuid.UUID] = None


@dataclass
class DeleteSessionBlockInput:
    session_id: uuid.UUID
    block_id: uuid.UUID
    actor_role: RoleLabel


@dataclass
class GetSessionBlockInput:
    session_id: uuid.UUID
    block_id: uuid.UUID
    actor_role: RoleLabel
    actor_id: uuid.UUID
    session_athlete_ids: list[uuid.UUID] = field(default_factory=list)


@dataclass
class ReorderSessionBlocksInput:
    session_id: uuid.UUID
    actor_role: RoleLabel
    block_ids: list[uuid.UUID]
