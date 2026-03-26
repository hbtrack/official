"""
Use Cases — módulo seasons.
Um use case por operationId do contrato OpenAPI.
Contrato: contracts/openapi/paths/seasons.yaml
Features: FT-018..023
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID

from ..domain.entities import Season, SeasonStatus
from ..domain.rules import (
    RoleLabel,
    assert_can_manage_season,
    assert_can_patch_season,
    assert_can_remove_team,
    assert_date_range,
    assert_team_not_in_season,
    assert_valid_status_transition,
)

if TYPE_CHECKING:
    from ..infrastructure.repository import SeasonsRepository


# ---------------------------------------------------------------------------
# FT-018 — listSeasons
# ---------------------------------------------------------------------------

@dataclass
class ListSeasonsInput:
    actor_role: RoleLabel
    status_label: str | None = None  # filtro opcional: draft/active/archived
    page: int = 1
    page_size: int = 20


@dataclass
class ListSeasonsOutput:
    data: list[Season]
    page: int
    page_size: int
    total: int


class ListSeasonsUseCase:
    """
    Feature: FT-018 — listSeasons
    Contrato: GET /seasons
    PERM-SEA-003: leitura pública (todos os roles).
    OWASP API4:2023: pageSize máximo 100.
    """
    def __init__(self, repository: "SeasonsRepository") -> None:
        self._repo = repository

    def execute(self, inp: ListSeasonsInput) -> ListSeasonsOutput:
        effective_page_size = min(max(inp.page_size, 1), 100)
        effective_page = min(max(inp.page, 1), 10_000)  # cap: previne overflow de OFFSET no PostgreSQL

        # Normaliza filtro de status para uppercase (entidade usa DRAFT/ACTIVE/ARCHIVED)
        status_filter = inp.status_label.upper() if inp.status_label else None

        data, total = self._repo.list_seasons(
            status_label=status_filter,
            page=effective_page,
            page_size=effective_page_size,
        )
        return ListSeasonsOutput(
            data=data,
            page=effective_page,
            page_size=effective_page_size,
            total=total,
        )


# ---------------------------------------------------------------------------
# FT-019 — createSeason
# ---------------------------------------------------------------------------

@dataclass
class CreateSeasonInput:
    actor_role: RoleLabel
    name: str
    start_date: date
    end_date: date
    organization_id: UUID | None = None
    sport_cycle_label: str | None = None
    phase_labels: list[str] = field(default_factory=list)


class CreateSeasonUseCase:
    """
    Feature: FT-019 — createSeason
    Contrato: POST /seasons
    DR-SEAS-001, DR-SEAS-002, INV-SEAS-001, INV-SEAS-002, PERM-SEA: admin/coordinator.
    """
    def __init__(self, repository: "SeasonsRepository") -> None:
        self._repo = repository

    def execute(self, inp: CreateSeasonInput) -> Season:
        # BFLA: apenas admin/coordinator criam temporadas
        assert_can_manage_season(inp.actor_role)

        # INV-SEAS-002: startDate <= endDate
        assert_date_range(inp.start_date, inp.end_date)

        # INV-SEAS-003: phaseLabels sem duplicidade (preservando ordem)
        unique_phases = list(dict.fromkeys(inp.phase_labels))

        season = Season(
            id=uuid.uuid4(),
            name=inp.name.strip(),
            start_date=inp.start_date,
            end_date=inp.end_date,
            status_label=SeasonStatus.DRAFT,
            organization_id=inp.organization_id,
            sport_cycle_label=inp.sport_cycle_label,
            phase_labels=unique_phases,
            team_ids=[],
            competition_ids=[],
        )
        season.validate_invariants()
        return self._repo.save(season)


# ---------------------------------------------------------------------------
# FT-020 — getSeason
# ---------------------------------------------------------------------------

@dataclass
class GetSeasonInput:
    actor_role: RoleLabel
    season_id: UUID


class GetSeasonUseCase:
    """
    Feature: FT-020 — getSeason
    Contrato: GET /seasons/{seasonId}
    PERM-SEA-003: leitura pública (todos os roles).
    """
    def __init__(self, repository: "SeasonsRepository") -> None:
        self._repo = repository

    def execute(self, inp: GetSeasonInput) -> Season:
        return self._repo.get_by_id(inp.season_id)


# ---------------------------------------------------------------------------
# FT-021 — patchSeason
# ---------------------------------------------------------------------------

@dataclass
class PatchSeasonInput:
    actor_role: RoleLabel
    season_id: UUID
    name: str | None = None
    sport_cycle_label: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    status_label: str | None = None
    phase_labels: list[str] | None = None


class PatchSeasonUseCase:
    """
    Feature: FT-021 — patchSeason
    Contrato: PATCH /seasons/{seasonId}
    PERM-SEA-002: patches em ARCHIVED somente admin.
    DR-SEAS-002: phaseLabels substituem o array completo.
    INV-SEAS-002: startDate <= endDate após patch.
    """
    def __init__(self, repository: "SeasonsRepository") -> None:
        self._repo = repository

    def execute(self, inp: PatchSeasonInput) -> Season:
        season = self._repo.get_by_id(inp.season_id)

        # PERM-SEA-002 + BFLA
        assert_can_patch_season(inp.actor_role, season.status_label.value)

        # Aplicar patches
        if inp.name is not None:
            season.name = inp.name.strip()
        if inp.sport_cycle_label is not None:
            season.sport_cycle_label = inp.sport_cycle_label
        if inp.start_date is not None:
            season.start_date = inp.start_date
        if inp.end_date is not None:
            season.end_date = inp.end_date
        if inp.phase_labels is not None:
            # DR-SEAS-002: substitui array completo; INV-SEAS-003: sem duplicatas
            season.phase_labels = list(dict.fromkeys(inp.phase_labels))
        if inp.status_label is not None:
            new_status = inp.status_label.upper()
            assert_valid_status_transition(season.status_label.value, new_status)
            season.status_label = SeasonStatus(new_status)

        # Revalida invariantes após patch
        season.validate_invariants()
        return self._repo.update(season)


# ---------------------------------------------------------------------------
# FT-022 — addTeamToSeason
# ---------------------------------------------------------------------------

@dataclass
class AddTeamToSeasonInput:
    actor_role: RoleLabel
    season_id: UUID
    team_id: UUID


class AddTeamToSeasonUseCase:
    """
    Feature: FT-022 — addTeamToSeason
    Contrato: POST /seasons/{seasonId}/teams/{teamId}
    DR-SEAS-003: associação explícita, canônica.
    INV-SEAS-003: rejeita duplicatas.
    PERM-SEA: admin/coordinator.
    """
    def __init__(self, repository: "SeasonsRepository") -> None:
        self._repo = repository

    def execute(self, inp: AddTeamToSeasonInput) -> None:
        assert_can_manage_season(inp.actor_role)

        season = self._repo.get_by_id(inp.season_id)

        # INV-SEAS-003: equipe não pode ser duplicada
        assert_team_not_in_season(inp.team_id, season.team_ids)

        season.team_ids = list(season.team_ids) + [inp.team_id]
        self._repo.update(season)


# ---------------------------------------------------------------------------
# FT-023 — removeTeamFromSeason
# ---------------------------------------------------------------------------

@dataclass
class RemoveTeamFromSeasonInput:
    actor_role: RoleLabel
    season_id: UUID
    team_id: UUID


class RemoveTeamFromSeasonUseCase:
    """
    Feature: FT-023 — removeTeamFromSeason
    Contrato: DELETE /seasons/{seasonId}/teams/{teamId}
    PERM-SEA-001: temporadas ACTIVE — somente admin remove times.
    DR-SEAS-003: vínculo removido explicitamente.
    """
    def __init__(self, repository: "SeasonsRepository") -> None:
        self._repo = repository

    def execute(self, inp: RemoveTeamFromSeasonInput) -> None:
        season = self._repo.get_by_id(inp.season_id)

        # PERM-SEA-001: coordinator não pode remover times de temporada ACTIVE
        assert_can_remove_team(inp.actor_role, season.status_label.value)

        if inp.team_id not in season.team_ids:
            from ..domain.rules import SeasonNotFound
            raise SeasonNotFound(
                f"Associação equipe {inp.team_id} não encontrada na temporada {inp.season_id}."
            )

        season.team_ids = [tid for tid in season.team_ids if tid != inp.team_id]
        self._repo.update(season)
