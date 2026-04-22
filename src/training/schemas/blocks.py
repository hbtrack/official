from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from ninja import Schema


# ---------------------------------------------------------------------------
# SessionBlock schemas
# ---------------------------------------------------------------------------

class SessionBlockOut(Schema):
    id: uuid.UUID
    session_id: uuid.UUID
    phase: str
    order_index: int
    duration_minutes: int
    block_objective: str
    intensity: str
    is_optional: bool
    created_at: datetime
    updated_at: datetime
    exercise_id: Optional[uuid.UUID] = None
    exercise_version_id: Optional[uuid.UUID] = None
    notes: Optional[str] = None


class SessionBlockListOut(Schema):
    data: List[SessionBlockOut]


class AddSessionBlockIn(Schema):
    phase: str
    order_index: int
    duration_minutes: int
    block_objective: str
    intensity: str
    is_optional: bool
    exercise_id: Optional[uuid.UUID] = None
    exercise_version_id: Optional[uuid.UUID] = None
    notes: Optional[str] = None


class UpdateSessionBlockIn(Schema):
    phase: Optional[str] = None
    duration_minutes: Optional[int] = None
    block_objective: Optional[str] = None
    intensity: Optional[str] = None
    is_optional: Optional[bool] = None
    exercise_id: Optional[uuid.UUID] = None
    exercise_version_id: Optional[uuid.UUID] = None
    notes: Optional[str] = None


class ReorderSessionBlocksIn(Schema):
    block_ids: List[uuid.UUID]
