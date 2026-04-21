"""
Agregado: AthleteIneligibilityDeclaration.

Declaração self-service de indisponibilidade do atleta para uma sessão.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class AthleteIneligibilityDeclaration:
    """Declaração self-service de indisponibilidade do atleta para uma sessão."""

    id: uuid.UUID
    session_id: uuid.UUID
    athlete_id: uuid.UUID
    declared_at: datetime
    created_at: datetime

    reason_flags: list[str] = field(default_factory=list)
    reason_other: Optional[str] = None
    acknowledged_by_coach: bool = False
    coach_note: Optional[str] = None

    def validate_invariants(self) -> None:
        if not self.reason_flags:
            raise ValueError("reasonFlags deve conter pelo menos um motivo")
        allowed_flags = {
            "MEDICAL_APPOINTMENT",
            "INJURY_PAIN",
            "ACTIVE_RECOVERY_ONLY",
            "TESTING_ANTI_DOPING",
            "OTHER",
        }
        invalid = [flag for flag in self.reason_flags if flag not in allowed_flags]
        if invalid:
            raise ValueError(f"reasonFlags contém valores inválidos: {invalid}")
        if "OTHER" in self.reason_flags and not self.reason_other:
            raise ValueError("reasonOther é obrigatório quando OTHER está presente em reasonFlags")
        if "OTHER" not in self.reason_flags and self.reason_other:
            raise ValueError("reasonOther só é permitido quando OTHER está presente em reasonFlags")
        if self.reason_other and len(self.reason_other) > 500:
            raise ValueError("reasonOther deve ter <= 500 caracteres")
        if self.coach_note and len(self.coach_note) > 500:
            raise ValueError("coachNote deve ter <= 500 caracteres")


__all__ = ["AthleteIneligibilityDeclaration"]
