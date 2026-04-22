from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from ...domain.rules import RoleLabel


@dataclass
class ListSessionAttendanceInput:
    session_id: uuid.UUID
    actor_role: RoleLabel
    actor_id: uuid.UUID


@dataclass
class RecordSessionAttendanceInput:
    session_id: uuid.UUID
    athlete_id: uuid.UUID
    status: str
    actor_role: RoleLabel
    actor_id: uuid.UUID
    source: str = "coach_input"
    correction_by_user_id: Optional[uuid.UUID] = None
    correction_at: Optional[datetime] = None
    justification_reason: Optional[str] = None
    observed_at: Optional[datetime] = None
