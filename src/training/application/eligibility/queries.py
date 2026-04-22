from __future__ import annotations

from ...domain.entities import AthleteIneligibilityDeclaration
from ...domain.rules import (
    IneligibilityDeclarationNotFound,
    TrainingSessionNotFound,
    assert_can_view_athlete_record,
)
from ...infrastructure.repository import (
    AthleteIneligibilityDeclarationRepository,
    TrainingSessionRepository,
)
from .dto import GetIneligibilityStatusInput


class GetIneligibilityStatusUseCase:
    def __init__(
        self,
        session_repo: TrainingSessionRepository,
        ineligibility_repo: AthleteIneligibilityDeclarationRepository,
    ):
        self._session_repo = session_repo
        self._ineligibility_repo = ineligibility_repo

    def execute(self, inp: GetIneligibilityStatusInput) -> AthleteIneligibilityDeclaration:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        target_athlete_id = inp.athlete_id or inp.actor_id
        assert_can_view_athlete_record(inp.actor_role, inp.actor_id, target_athlete_id)
        declaration = self._ineligibility_repo.get_by_session_athlete(inp.session_id, target_athlete_id)
        if not declaration:
            raise IneligibilityDeclarationNotFound(
                f"Declaração de indisponibilidade não encontrada para atleta {target_athlete_id}"
            )
        return declaration
