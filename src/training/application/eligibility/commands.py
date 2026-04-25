from __future__ import annotations

import uuid
from datetime import datetime, timezone

from ...domain.entities.eligibility import AthleteIneligibilityDeclaration
from ...domain.common.enums import TrainingSessionStatus
from ...domain.rules import (
    IneligibilityStateConflict,
    InsufficientPrivilege,
    RoleLabel,
    TrainingSessionNotFound,
)
from ...infrastructure.repository.eligibility import AthleteIneligibilityDeclarationRepository
from ...infrastructure.repository.sessions import TrainingSessionRepository
from .dto import SubmitIneligibilityDeclarationInput


class SubmitIneligibilityDeclarationUseCase:
    def __init__(
        self,
        session_repo: TrainingSessionRepository,
        ineligibility_repo: AthleteIneligibilityDeclarationRepository,
    ):
        self._session_repo = session_repo
        self._ineligibility_repo = ineligibility_repo

    def execute(self, inp: SubmitIneligibilityDeclarationInput) -> AthleteIneligibilityDeclaration:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        if session.status not in {TrainingSessionStatus.PUBLISHED, TrainingSessionStatus.IN_PROGRESS}:
            raise IneligibilityStateConflict(
                "Declaração de indisponibilidade só é permitida com sessão PUBLISHED ou IN_PROGRESS"
            )
        if inp.actor_role != RoleLabel.ATHLETE or inp.actor_id != inp.athlete_id:
            raise InsufficientPrivilege("Athlete só pode declarar indisponibilidade para si mesmo")
        now = datetime.now(tz=timezone.utc)
        existing = self._ineligibility_repo.get_by_session_athlete(inp.session_id, inp.athlete_id)
        declaration = AthleteIneligibilityDeclaration(
            id=existing.id if existing else uuid.uuid4(),
            session_id=inp.session_id,
            athlete_id=inp.athlete_id,
            reason_flags=inp.reason_flags,
            reason_other=inp.reason_other,
            acknowledged_by_coach=False,  # Reset coach acknowledgment on resubmission
            coach_note=None,  # Clear coach notes when athlete updates declaration
            declared_at=now,
            created_at=existing.created_at if existing else now,
        )
        declaration.validate_invariants()
        return self._ineligibility_repo.save(declaration)
