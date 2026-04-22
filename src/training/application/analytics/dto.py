from __future__ import annotations

import uuid
from dataclasses import dataclass

from ...domain.entities import ExecutionRecord, TrainingSession
from ...domain.rules import RoleLabel


@dataclass
class GetLoadChartInput:
    session_id: uuid.UUID
    actor_role: RoleLabel


@dataclass
class GetLoadChartResult:
    session: TrainingSession
    load_entries: list[ExecutionRecord]
