from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from ninja import Schema


# ---------------------------------------------------------------------------
# Attendance schemas
# ---------------------------------------------------------------------------

class AttendanceRecordOut(Schema):
    athlete_id: uuid.UUID
    status: str
    recorded_at: datetime
    source: str
    correction_by_user_id: Optional[uuid.UUID] = None
    correction_at: Optional[datetime] = None
    justification_reason: Optional[str] = None


class AttendanceListOut(Schema):
    items: List[AttendanceRecordOut]


class RecordSessionAttendanceIn(Schema):
    athlete_id: uuid.UUID
    status: str
    source: str = "coach_input"
    correction_by_user_id: Optional[uuid.UUID] = None
    correction_at: Optional[datetime] = None
    justification_reason: Optional[str] = None
    observed_at: Optional[datetime] = None
