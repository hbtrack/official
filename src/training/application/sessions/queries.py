from __future__ import annotations

from typing import Optional

from ...application.common.paging import CursorCodec
from ...domain.entities import TrainingSession
from ...domain.policies.session_access import SessionGuard
from ...domain.rules import (
    InsufficientPrivilege,
    RoleLabel,
)
from ...infrastructure.repository import TrainingSessionRepository
from .dto import (
    GetTrainingSessionInput,
    ListTrainingSessionsInput,
    ListTrainingSessionsOutput,
)


class ListTrainingSessionsUseCase:
    def __init__(
        self,
        repo: TrainingSessionRepository,
        cursor_codec: Optional[CursorCodec] = None,
    ) -> None:
        self._repo = repo
        self._cursor_codec = cursor_codec

    def execute(self, inp: ListTrainingSessionsInput) -> ListTrainingSessionsOutput:
        # member não acessa sessões — PERMISSIONS_TRAINING.md
        if inp.actor_role == RoleLabel.MEMBER:
            raise InsufficientPrivilege("member não tem acesso a sessões de treino")

        # Decodificar cursor opaco → session_at para filtro no repositório
        repo_page_token: Optional[str] = inp.page_token
        if inp.page_token and self._cursor_codec:
            try:
                session_at, _id = self._cursor_codec.decode(inp.page_token)
                repo_page_token = session_at.isoformat()
            except ValueError:
                # Cursor inválido → ignorar (retorna primeira página)
                repo_page_token = None

        items = self._repo.list(
            organization_id=inp.organization_id,
            team_id=inp.team_id,
            season_id=inp.season_id,
            status=inp.status,
            page_size=inp.page_size,
            page_token=repo_page_token,
        )

        next_token: Optional[str] = None
        if len(items) == inp.page_size and items:
            last = items[-1]
            if self._cursor_codec:
                next_token = self._cursor_codec.encode(last.session_at, last.id)
            else:
                # Fallback legado: ISO session_at puro (deprecado — remover pós-Fase 3)
                next_token = last.session_at.isoformat()

        return ListTrainingSessionsOutput(items=items, next_page_token=next_token)


class GetTrainingSessionUseCase:
    def __init__(self, repo: TrainingSessionRepository):
        self._repo = repo
        self._guard = SessionGuard(repo)

    def execute(self, inp: GetTrainingSessionInput) -> TrainingSession:
        return self._guard.load_for_read(
            inp.id, inp.actor_role, inp.actor_id, inp.session_athlete_ids
        )
