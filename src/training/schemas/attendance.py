from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from ninja import Schema
from pydantic import ConfigDict
from pydantic.alias_generators import to_camel

_CAMEL = ConfigDict(alias_generator=to_camel, populate_by_name=True)


# ---------------------------------------------------------------------------
# Attendance schemas
# ---------------------------------------------------------------------------

class AttendanceRecordOut(Schema):
    model_config = _CAMEL
    athlete_id: uuid.UUID
    status: str
    recorded_at: datetime
    source: str
    correction_by_user_id: Optional[uuid.UUID] = None
    correction_at: Optional[datetime] = None
    justification_reason: Optional[str] = None


class AttendanceListOut(Schema):
    model_config = _CAMEL
    items: List[AttendanceRecordOut]


class RecordSessionAttendanceIn(Schema):
    model_config = _CAMEL
    athlete_id: uuid.UUID
    status: str
    source: str = "coach_input"
    correction_by_user_id: Optional[uuid.UUID] = None
    correction_at: Optional[datetime] = None
    justification_reason: Optional[str] = None
    observed_at: Optional[datetime] = None
