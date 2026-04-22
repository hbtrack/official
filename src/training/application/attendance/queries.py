from __future__ import annotations

from ...domain.entities import AttendanceRecord
from ...domain.rules import (
    InsufficientPrivilege,
    RoleLabel,
    TrainingSessionNotFound,
)
from ...infrastructure.repository import AttendanceRepository, TrainingSessionRepository
from .dto import ListSessionAttendanceInput


class ListSessionAttendanceUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, attendance_repo: AttendanceRepository):
        self._session_repo = session_repo
        self._attendance_repo = attendance_repo

    def execute(self, inp: ListSessionAttendanceInput) -> list[AttendanceRecord]:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        if inp.actor_role == RoleLabel.MEMBER:
            raise InsufficientPrivilege("member não tem acesso à presença da sessão")
        records = self._attendance_repo.list_by_session(inp.session_id)
        if inp.actor_role == RoleLabel.ATHLETE:
            return [record for record in records if record.athlete_id == inp.actor_id]
        return records
