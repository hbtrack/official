"""Repositório do agregado AttendanceRecord (append-only)."""
from __future__ import annotations

import uuid

from ...domain.entities.attendance import AttendanceRecord
from ...domain.common.enums import AttendanceSource, AttendanceStatus
from ..models.attendance import AttendanceRecordModel


class AttendanceRepository:
    def list_by_session(self, session_id: uuid.UUID) -> list[AttendanceRecord]:
        return [
            self._to_domain(m)
            for m in AttendanceRecordModel.objects.filter(session_id=session_id).order_by("recorded_at", "created_at")
        ]

    def exists_for_session_athlete(self, session_id: uuid.UUID, athlete_id: uuid.UUID) -> bool:
        """Retorna True se já existe registro de presença para este athlete nesta sessão."""
        return AttendanceRecordModel.objects.filter(
            session_id=session_id, athlete_id=athlete_id
        ).exists()

    def save(self, attendance: AttendanceRecord) -> AttendanceRecord:
        m = AttendanceRecordModel.objects.create(
            id=attendance.id,
            session_id=attendance.session_id,
            athlete_id=attendance.athlete_id,
            status=attendance.status.value,
            source=attendance.source.value,
            recorded_at=attendance.recorded_at,
            correction_by_user_id=attendance.correction_by_user_id,
            correction_at=attendance.correction_at,
            justification_reason=attendance.justification_reason or "",
        )
        return self._to_domain(m)

    def _to_domain(self, m: AttendanceRecordModel) -> AttendanceRecord:
        return AttendanceRecord(
            id=m.id,
            session_id=m.session_id,
            athlete_id=m.athlete_id,
            status=AttendanceStatus(m.status),
            source=AttendanceSource(m.source),
            recorded_at=m.recorded_at,
            created_at=m.created_at,
            updated_at=m.updated_at,
            correction_by_user_id=m.correction_by_user_id,
            correction_at=m.correction_at,
            justification_reason=m.justification_reason or None,
        )


__all__ = ["AttendanceRepository"]
