from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from ninja import Schema
from pydantic import ConfigDict
from pydantic.alias_generators import to_camel

_CAMEL = ConfigDict(alias_generator=to_camel, populate_by_name=True)


# ---------------------------------------------------------------------------
# Ineligibility schemas
# ---------------------------------------------------------------------------

class AthleteIneligibilityDeclarationOut(Schema):
    model_config = _CAMEL
    id: uuid.UUID
    session_id: uuid.UUID
    athlete_id: uuid.UUID
    reason_flags: List[str]
    declared_at: datetime
    created_at: datetime
    reason_other: Optional[str] = None
    acknowledged_by_coach: bool = False
    coach_note: Optional[str] = None


class SubmitIneligibilityDeclarationIn(Schema):
    model_config = _CAMEL
    athlete_id: uuid.UUID
    reason_flags: List[str]
    reason_other: Optional[str] = None
