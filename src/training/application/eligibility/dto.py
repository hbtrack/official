from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Optional

from ...domain.rules import RoleLabel


@dataclass
class GetIneligibilityStatusInput:
    session_id: uuid.UUID
    actor_role: RoleLabel
    actor_id: uuid.UUID
    athlete_id: Optional[uuid.UUID] = None


@dataclass
class SubmitIneligibilityDeclarationInput:
    session_id: uuid.UUID
    actor_role: RoleLabel
    actor_id: uuid.UUID
    athlete_id: uuid.UUID
    reason_flags: list[str]
    reason_other: Optional[str] = None
