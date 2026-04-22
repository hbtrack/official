from __future__ import annotations

import uuid
from datetime import datetime, timezone

from ...domain.entities import AttendanceRecord, AttendanceSource, AttendanceStatus
from ...domain.rules import (
    InsufficientPrivilege,
    RoleLabel,
    TrainingSessionNotFound,
    assert_can_record_attendance,
)
from ...infrastructure.repository import AttendanceRepository, TrainingSessionRepository
from .dto import RecordSessionAttendanceInput


class RecordSessionAttendanceUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, attendance_repo: AttendanceRepository):
        self._session_repo = session_repo
        self._attendance_repo = attendance_repo

    def execute(self, inp: RecordSessionAttendanceInput) -> AttendanceRecord:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        status = AttendanceStatus(inp.status)
        source = AttendanceSource(inp.source)
        assert_can_record_attendance(inp.actor_role, inp.actor_id, inp.athlete_id, status, source)
        if inp.actor_role == RoleLabel.ATHLETE and datetime.now(tz=timezone.utc) >= session.session_at:
            raise InsufficientPrivilege(
                "INV-TRAIN-063: athlete só pode PRECONFIRM antes do início da sessão"
            )
        now = datetime.now(tz=timezone.utc)
        record = AttendanceRecord(
            id=uuid.uuid4(),
            session_id=inp.session_id,
            athlete_id=inp.athlete_id,
            status=status,
            source=source,
            recorded_at=inp.observed_at or now,
            created_at=now,
            updated_at=now,
            correction_by_user_id=inp.correction_by_user_id,
            correction_at=inp.correction_at,
            justification_reason=inp.justification_reason,
        )
        record.validate_invariants()
        return self._attendance_repo.save(record)
