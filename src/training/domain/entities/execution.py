"""
Agregado: ExecutionRecord.

Registro append-only de execução.
TRAIN-DEC-007/008/009, INV-TRAIN-087.
DR-TRAIN-015: sempre vinculado a sessionId.
DR-TRAIN-017: plannedContent e actualContent separados.
DR-TRAIN-019: LIVE_ADJUSTMENT / CONSTRAINT_OVERRIDE exigem coachRationale.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from ..common.enums import ExecutionType


@dataclass
class ExecutionRecord:
    """
    Registro de execução — append-only.
    TRAIN-DEC-007/008/009. INV-TRAIN-087.
    DR-TRAIN-015: sempre vinculado a sessionId.
    DR-TRAIN-017: plannedContent e actualContent separados.
    """
    id: uuid.UUID
    session_id: uuid.UUID
    execution_type: ExecutionType
    recorded_at: datetime
    created_by_user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    block_id: Optional[uuid.UUID] = None
    planned_value: Optional[float] = None
    actual_value: Optional[float] = None
    planned_unit: Optional[str] = None
    actual_unit: Optional[str] = None
    adjustment_reason_type: Optional[str] = None
    coach_rationale: Optional[str] = None
    notes: Optional[str] = None

    def validate_invariants(self) -> None:
        if self.execution_type in (
            ExecutionType.LIVE_ADJUSTMENT, ExecutionType.CONSTRAINT_OVERRIDE
        ):
            if not self.coach_rationale or len(self.coach_rationale) < 5:
                raise ValueError(
                    "DR-TRAIN-019: coachRationale obrigatório (mínimo 5 chars) para "
                    f"executionType={self.execution_type}"
                )
        if self.planned_unit and len(self.planned_unit) > 32:
            raise ValueError("plannedUnit excede 32 caracteres")
        if self.actual_unit and len(self.actual_unit) > 32:
            raise ValueError("actualUnit excede 32 caracteres")


__all__ = ["ExecutionRecord"]
