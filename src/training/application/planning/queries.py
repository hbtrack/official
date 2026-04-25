from __future__ import annotations

from ...domain.entities.planning import Mesocycle, Microcycle
from ...domain.rules import MesocycleNotFound, MicrocycleNotFound
from ...infrastructure.repository.planning import MesocycleRepository, MicrocycleRepository
from .dto import GetMesocycleInput, GetMicrocycleInput, ListMesocyclesInput, ListMicrocyclesInput


class ListMesocyclesUseCase:
    def __init__(self, repo: MesocycleRepository):
        self._repo = repo

    def execute(self, inp: ListMesocyclesInput) -> list[Mesocycle]:
        return self._repo.list(organization_id=inp.organization_id)


class GetMesocycleUseCase:
    def __init__(self, repo: MesocycleRepository):
        self._repo = repo

    def execute(self, inp: GetMesocycleInput) -> Mesocycle:
        meso = self._repo.get_by_id(inp.id)
        if not meso:
            raise MesocycleNotFound(f"Mesociclo {inp.id} não encontrado")
        return meso


class ListMicrocyclesUseCase:
    def __init__(self, repo: MicrocycleRepository):
        self._repo = repo

    def execute(self, inp: ListMicrocyclesInput) -> list[Microcycle]:
        return self._repo.list(
            organization_id=inp.organization_id,
            mesocycle_id=inp.mesocycle_id,
        )


class GetMicrocycleUseCase:
    def __init__(self, repo: MicrocycleRepository):
        self._repo = repo

    def execute(self, inp: GetMicrocycleInput) -> Microcycle:
        micro = self._repo.get_by_id(inp.id)
        if not micro:
            raise MicrocycleNotFound(f"Microciclo {inp.id} não encontrado")
        return micro
