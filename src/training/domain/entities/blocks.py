"""
Agregado: SessionBlock.

Contrato: contracts/schemas/training/session_block.schema.json
TRAIN-DEC-049. INV-TRAIN-083 (Elastic Sum Rule).
TRAIN-DEC-047: referencia exercise_id + exercise_version_id.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from ..common.enums import SessionBlockIntensity, SessionBlockPhase


@dataclass
class SessionBlock:
    """
    Bloco operacional de sessão.
    Contrato: contracts/schemas/training/session_block.schema.json
    TRAIN-DEC-049. INV-TRAIN-083 (Elastic Sum Rule).
    TRAIN-DEC-047: referencia exercise_id + exercise_version_id.
    """
    id: uuid.UUID
    session_id: uuid.UUID
    phase: SessionBlockPhase
    order_index: int
    duration_minutes: int
    block_objective: str
    intensity: SessionBlockIntensity
    is_optional: bool
    created_at: datetime
    updated_at: datetime

    exercise_id: Optional[uuid.UUID] = None
    exercise_version_id: Optional[uuid.UUID] = None
    notes: Optional[str] = None

    def validate_invariants(self) -> None:
        """TRAIN-DEC-047: exerciseVersionId obrigatório quando exerciseId presente."""
        if self.exercise_id is not None and self.exercise_version_id is None:
            raise ValueError(
                "TRAIN-DEC-047: exerciseVersionId é obrigatório quando exerciseId está presente"
            )
        if not (1 <= self.duration_minutes <= 240):
            raise ValueError("durationMinutes deve estar em [1..240]")
        if len(self.block_objective) < 3 or len(self.block_objective) > 300:
            raise ValueError("blockObjective deve ter entre 3 e 300 caracteres")
        if self.notes and len(self.notes) > 1000:
            raise ValueError("notes excede 1000 caracteres")
        if self.order_index < 0:
            raise ValueError("orderIndex deve ser >= 0")


__all__ = ["SessionBlock"]
