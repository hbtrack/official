"""
Use Cases — módulo teams.
Um use case por operationId do contrato OpenAPI.
Contrato: contracts/openapi/paths/teams.yaml
Features: FT-024..031
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import UUID

from ..domain.entities import Team, TeamStatus
from ..domain.rules import (
    RoleLabel,
    assert_can_create_team,
    assert_can_manage_athlete,
    assert_can_manage_staff,
    assert_can_patch_team,
    assert_can_read_team,
    assert_valid_status_transition,
)

if TYPE_CHECKING:
    from ..infrastructure.repository import TeamsRepository


# ---------------------------------------------------------------------------
# FT-024 — listTeams
# ---------------------------------------------------------------------------

@dataclass
class ListTeamsInput:
    actor_role: RoleLabel
    actor_team_ids: list[UUID] = field(default_factory=list)
    organization_id: UUID | None = None
    season_id: UUID | None = None
    category_label: str | None = None
    status_label: str | None = None
    page: int = 1
    page_size: int = 20


@dataclass
class ListTeamsOutput:
    data: list[Team]
    page: int
    page_size: int
    total: int


class ListTeamsUseCase:
    """
    Feature: FT-024 — listTeams
    Contrato: GET /teams
    BOLA: coach vê apenas times vinculados; athlete vê apenas os próprios times.
    admin/coordinator: acesso irrestrito.
    OWASP API4:2023: pageSize máximo 100.
    """
    def __init__(self, repository: "TeamsRepository") -> None:
        self._repo = repository

    def execute(self, inp: ListTeamsInput) -> ListTeamsOutput:
        effective_page_size = min(max(inp.page_size, 1), 100)
        effective_page = max(inp.page, 1)

        # BOLA: filtrar equipes por vínculo do ator
        team_ids_filter: list[UUID] | None = None
        if inp.actor_role in (RoleLabel.COACH, RoleLabel.ATHLETE):
            team_ids_filter = list(inp.actor_team_ids)
        elif inp.actor_role == RoleLabel.MEMBER:
            # member não acessa listagem
            return ListTeamsOutput(data=[], page=effective_page, page_size=effective_page_size, total=0)

        status_filter = inp.status_label.upper() if inp.status_label else None

        data, total = self._repo.list_teams(
            organization_id=inp.organization_id,
            season_id=inp.season_id,
            category_label=inp.category_label,
            status_label=status_filter,
            team_ids_filter=team_ids_filter,
            page=effective_page,
            page_size=effective_page_size,
        )
        return ListTeamsOutput(data=data, page=effective_page, page_size=effective_page_size, total=total)


# ---------------------------------------------------------------------------
# FT-025 — createTeam
# ---------------------------------------------------------------------------

@dataclass
class CreateTeamInput:
    actor_role: RoleLabel
    organization_id: UUID
    name: str
    category_label: str
    season_id: UUID | None = None
    short_name: str | None = None
    athlete_ids: list[UUID] = field(default_factory=list)
    staff_user_ids: list[UUID] = field(default_factory=list)
    roster_notes: str | None = None


class CreateTeamUseCase:
    """
    Feature: FT-025 — createTeam
    Contrato: POST /teams
    DR-TEAM-001..005, INV-TEAM-001..004, PERM: admin/coordinator.
    """
    def __init__(self, repository: "TeamsRepository") -> None:
        self._repo = repository

    def execute(self, inp: CreateTeamInput) -> Team:
        assert_can_create_team(inp.actor_role)

        team = Team(
            id=uuid.uuid4(),
            organization_id=inp.organization_id,
            name=inp.name.strip(),
            category_label=inp.category_label.strip(),
            status_label=TeamStatus.DRAFT,
            season_id=inp.season_id,
            short_name=inp.short_name,
            athlete_ids=list(dict.fromkeys(inp.athlete_ids)),
            staff_user_ids=list(dict.fromkeys(inp.staff_user_ids)),
            roster_notes=inp.roster_notes,
        )
        team.validate_invariants()
        return self._repo.save(team)


# ---------------------------------------------------------------------------
# FT-026 — getTeam
# ---------------------------------------------------------------------------

@dataclass
class GetTeamInput:
    actor_role: RoleLabel
    actor_team_ids: list[UUID]
    team_id: UUID


class GetTeamUseCase:
    """
    Feature: FT-026 — getTeam
    Contrato: GET /teams/{teamId}
    BOLA: coach e athlete veem apenas equipes vinculadas (PERM-TEAM-001/003).
    """
    def __init__(self, repository: "TeamsRepository") -> None:
        self._repo = repository

    def execute(self, inp: GetTeamInput) -> Team:
        assert_can_read_team(inp.actor_role, inp.actor_team_ids, inp.team_id)
        return self._repo.get_by_id(inp.team_id)


# ---------------------------------------------------------------------------
# FT-027 — patchTeam
# ---------------------------------------------------------------------------

@dataclass
class PatchTeamInput:
    actor_role: RoleLabel
    actor_team_ids: list[UUID]
    team_id: UUID
    name: str | None = None
    short_name: str | None = None
    category_label: str | None = None
    status_label: str | None = None
    season_id: str | None = None  # "null" = desvincula; UUID = vincula; None = não altera
    athlete_ids: list[UUID] | None = None
    staff_user_ids: list[UUID] | None = None
    roster_notes: str | None = None


class PatchTeamUseCase:
    """
    Feature: FT-027 — patchTeam
    Contrato: PATCH /teams/{teamId}
    PERM-TEAM-001: coach edita apenas o próprio time.
    athleteIds/staffUserIds substituem arrays completos (DR-TEAM-002).
    """
    def __init__(self, repository: "TeamsRepository") -> None:
        self._repo = repository

    def execute(self, inp: PatchTeamInput) -> Team:
        assert_can_patch_team(inp.actor_role, inp.actor_team_ids, inp.team_id)

        team = self._repo.get_by_id(inp.team_id)

        if inp.name is not None:
            team.name = inp.name.strip()
        if inp.short_name is not None:
            team.short_name = inp.short_name
        if inp.category_label is not None:
            team.category_label = inp.category_label.strip()
        if inp.season_id is not None:
            team.season_id = UUID(inp.season_id) if inp.season_id != "null" else None
        if inp.status_label is not None:
            new_status = inp.status_label.upper()
            assert_valid_status_transition(team.status_label.value, new_status)
            team.status_label = TeamStatus(new_status)
        if inp.athlete_ids is not None:
            team.athlete_ids = list(dict.fromkeys(inp.athlete_ids))
        if inp.staff_user_ids is not None:
            team.staff_user_ids = list(dict.fromkeys(inp.staff_user_ids))
        if inp.roster_notes is not None:
            team.roster_notes = inp.roster_notes

        team.validate_invariants()
        return self._repo.update(team)


# ---------------------------------------------------------------------------
# FT-028 — addAthleteToTeam (idempotente)
# ---------------------------------------------------------------------------

@dataclass
class AddAthleteToTeamInput:
    actor_role: RoleLabel
    actor_team_ids: list[UUID]
    team_id: UUID
    athlete_user_id: UUID


class AddAthleteToTeamUseCase:
    """
    Feature: FT-028 — addAthleteToTeam
    Contrato: POST /teams/{teamId}/athletes/{athleteUserId}
    DR-TEAM-002: vínculo explícito; INV-TEAM-002: idempotente (sem erro se já existe).
    PERM-TEAM-001: coach só gerencia o próprio time.
    """
    def __init__(self, repository: "TeamsRepository") -> None:
        self._repo = repository

    def execute(self, inp: AddAthleteToTeamInput) -> Team:
        assert_can_manage_athlete(inp.actor_role, inp.actor_team_ids, inp.team_id)
        team = self._repo.get_by_id(inp.team_id)
        if inp.athlete_user_id not in team.athlete_ids:
            team.athlete_ids = list(team.athlete_ids) + [inp.athlete_user_id]
        return self._repo.update(team)


# ---------------------------------------------------------------------------
# FT-029 — removeAthleteFromTeam (idempotente)
# ---------------------------------------------------------------------------

@dataclass
class RemoveAthleteFromTeamInput:
    actor_role: RoleLabel
    actor_team_ids: list[UUID]
    team_id: UUID
    athlete_user_id: UUID


class RemoveAthleteFromTeamUseCase:
    """
    Feature: FT-029 — removeAthleteFromTeam
    Contrato: DELETE /teams/{teamId}/athletes/{athleteUserId}
    Idempotente: sem erro se atleta já não estiver no elenco.
    """
    def __init__(self, repository: "TeamsRepository") -> None:
        self._repo = repository

    def execute(self, inp: RemoveAthleteFromTeamInput) -> Team:
        assert_can_manage_athlete(inp.actor_role, inp.actor_team_ids, inp.team_id)
        team = self._repo.get_by_id(inp.team_id)
        team.athlete_ids = [aid for aid in team.athlete_ids if aid != inp.athlete_user_id]
        return self._repo.update(team)


# ---------------------------------------------------------------------------
# FT-030 — addStaffToTeam (idempotente)
# ---------------------------------------------------------------------------

@dataclass
class AddStaffToTeamInput:
    actor_role: RoleLabel
    team_id: UUID
    staff_user_id: UUID


class AddStaffToTeamUseCase:
    """
    Feature: FT-030 — addStaffToTeam
    Contrato: POST /teams/{teamId}/staff/{staffUserId}
    DR-TEAM-002: vínculo explícito; idempotente.
    PERM: apenas admin/coordinator (BFLA).
    """
    def __init__(self, repository: "TeamsRepository") -> None:
        self._repo = repository

    def execute(self, inp: AddStaffToTeamInput) -> Team:
        assert_can_manage_staff(inp.actor_role)
        team = self._repo.get_by_id(inp.team_id)
        if inp.staff_user_id not in team.staff_user_ids:
            team.staff_user_ids = list(team.staff_user_ids) + [inp.staff_user_id]
        return self._repo.update(team)


# ---------------------------------------------------------------------------
# FT-031 — removeStaffFromTeam (idempotente)
# ---------------------------------------------------------------------------

@dataclass
class RemoveStaffFromTeamInput:
    actor_role: RoleLabel
    team_id: UUID
    staff_user_id: UUID


class RemoveStaffFromTeamUseCase:
    """
    Feature: FT-031 — removeStaffFromTeam
    Contrato: DELETE /teams/{teamId}/staff/{staffUserId}
    Idempotente: sem erro se staff já não estiver vinculado.
    PERM: apenas admin/coordinator (BFLA).
    """
    def __init__(self, repository: "TeamsRepository") -> None:
        self._repo = repository

    def execute(self, inp: RemoveStaffFromTeamInput) -> Team:
        assert_can_manage_staff(inp.actor_role)
        team = self._repo.get_by_id(inp.team_id)
        team.staff_user_ids = [sid for sid in team.staff_user_ids if sid != inp.staff_user_id]
        return self._repo.update(team)
