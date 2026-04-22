"""
Agregado: AttendanceRecord.

Fato append-only de presença por atleta em uma sessão.
INV-TRAIN-030, INV-TRAIN-063.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from ..common.enums import AttendanceSource, AttendanceStatus


@dataclass
class AttendanceRecord:
    """Fato append-only de presença por atleta em uma sessão."""

    id: uuid.UUID
    session_id: uuid.UUID
    athlete_id: uuid.UUID
    status: AttendanceStatus
    source: AttendanceSource
    recorded_at: datetime
    created_at: datetime
    updated_at: datetime

    correction_by_user_id: Optional[uuid.UUID] = None
    correction_at: Optional[datetime] = None
    justification_reason: Optional[str] = None

    def validate_invariants(self) -> None:
        if self.source == AttendanceSource.CORRECTION:
            if self.correction_by_user_id is None or self.correction_at is None:
                raise ValueError(
                    "INV-TRAIN-030: correction exige correctionByUserId e correctionAt"
                )
        elif self.correction_by_user_id is not None or self.correction_at is not None:
            raise ValueError(
                "INV-TRAIN-030: campos de correção só são permitidos quando source=correction"
            )

        if self.source == AttendanceSource.ATHLETE_SELFCHECK and self.status != AttendanceStatus.PRECONFIRMED:
            raise ValueError(
                "INV-TRAIN-063: athlete_selfcheck só pode registrar status PRECONFIRMED"
            )

        if self.status == AttendanceStatus.JUSTIFIED:
            if not self.justification_reason:
                raise ValueError(
                    "attendance.justificationReason é obrigatório quando status=JUSTIFIED"
                )
        elif self.justification_reason:
            raise ValueError(
                "attendance.justificationReason só é permitido quando status=JUSTIFIED"
            )

        if self.justification_reason and len(self.justification_reason) > 255:
            raise ValueError("attendance.justificationReason excede 255 caracteres")


__all__ = ["AttendanceRecord"]
