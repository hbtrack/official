from __future__ import annotations

import uuid
from datetime import datetime, timezone

from ...domain.entities.planning import Mesocycle, Microcycle
from ...domain.rules import (
    MesocycleNotFound,
    MicrocycleNotFound,
    assert_can_modify_session,
)
from ...infrastructure.repository.planning import MesocycleRepository, MicrocycleRepository
from .dto import (
    CreateMesocycleInput,
    CreateMicrocycleInput,
    UpdateMesocycleInput,
    UpdateMicrocycleInput,
)


class CreateMesocycleUseCase:
    def __init__(self, repo: MesocycleRepository):
        self._repo = repo

    def execute(self, inp: CreateMesocycleInput) -> Mesocycle:
        assert_can_modify_session(inp.actor_role)
        now = datetime.now(tz=timezone.utc)
        meso = Mesocycle(
            id=uuid.uuid4(),
            organization_id=inp.organization_id,
            name=inp.name,
            started_at=inp.started_at,
            ended_at=inp.ended_at,
            season_id=inp.season_id,
            team_id=inp.team_id,
            objective=inp.objective,
            notes=inp.notes,
            created_at=now,
            updated_at=now,
        )
        meso.validate_invariants()
        return self._repo.save(meso)


class CreateMicrocycleUseCase:
    def __init__(self, repo: MicrocycleRepository):
        self._repo = repo

    def execute(self, inp: CreateMicrocycleInput) -> Microcycle:
        assert_can_modify_session(inp.actor_role)
        now = datetime.now(tz=timezone.utc)
        micro = Microcycle(
            id=uuid.uuid4(),
            organization_id=inp.organization_id,
            mesocycle_id=inp.mesocycle_id,
            week_number=inp.week_number,
            started_at=inp.started_at,
            ended_at=inp.ended_at,
            team_id=inp.team_id,
            name=inp.name,
            objective=inp.objective,
            planned_sessions_count=inp.planned_sessions_count,
            notes=inp.notes,
            created_at=now,
            updated_at=now,
        )
        micro.validate_invariants()
        return self._repo.save(micro)


class UpdateMesocycleUseCase:
    def __init__(self, repo: MesocycleRepository):
        self._repo = repo

    def execute(self, inp: UpdateMesocycleInput) -> Mesocycle:
        meso = self._repo.get_by_id(inp.id)
        if not meso:
            raise MesocycleNotFound(f"Mesociclo {inp.id} não encontrado")
        assert_can_modify_session(inp.actor_role)
        if inp.name is not None:
            meso.name = inp.name
        if inp.started_at is not None:
            meso.started_at = inp.started_at
        if inp.ended_at is not None:
            meso.ended_at = inp.ended_at
        if inp.season_id is not None:
            meso.season_id = inp.season_id
        if inp.team_id is not None:
            meso.team_id = inp.team_id
        if inp.objective is not None:
            meso.objective = inp.objective
        if inp.notes is not None:
            meso.notes = inp.notes
        meso.updated_at = datetime.now(tz=timezone.utc)
        meso.validate_invariants()
        return self._repo.save(meso)


class UpdateMicrocycleUseCase:
    def __init__(self, repo: MicrocycleRepository):
        self._repo = repo

    def execute(self, inp: UpdateMicrocycleInput) -> Microcycle:
        micro = self._repo.get_by_id(inp.id)
        if not micro:
            raise MicrocycleNotFound(f"Microciclo {inp.id} não encontrado")
        assert_can_modify_session(inp.actor_role)
        if inp.week_number is not None:
            micro.week_number = inp.week_number
        if inp.started_at is not None:
            micro.started_at = inp.started_at
        if inp.ended_at is not None:
            micro.ended_at = inp.ended_at
        if inp.team_id is not None:
            micro.team_id = inp.team_id
        if inp.name is not None:
            micro.name = inp.name
        if inp.objective is not None:
            micro.objective = inp.objective
        if inp.planned_sessions_count is not None:
            micro.planned_sessions_count = inp.planned_sessions_count
        if inp.notes is not None:
            micro.notes = inp.notes
        micro.updated_at = datetime.now(tz=timezone.utc)
        micro.validate_invariants()
        return self._repo.save(micro)
