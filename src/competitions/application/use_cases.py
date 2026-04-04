"""
Use cases — módulo competitions.
Fonte: PERMISSIONS_COMPETITIONS.md, DOMAIN_RULES_COMPETITIONS.md, INVARIANTS_COMPETITIONS.md
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import date
from typing import List, Optional

from competitions.domain.entities import Competition, CompetitionStatus
from competitions.domain.rules import (
    CompetitionNotFound,
    RoleLabel,
    TeamAlreadyRegistered,
    TeamNotRegistered,
    assert_can_create_competition,
    assert_can_list_competitions,
    assert_can_patch_competition,
    assert_can_read_competition,
    assert_can_register_team,
    assert_can_unregister_team,
    assert_team_not_registered,
    assert_team_registered,
    assert_valid_transition,
)
from competitions.infrastructure.repository import CompetitionRepository


# ---------------------------------------------------------------------------
# listCompetitions
# ---------------------------------------------------------------------------

@dataclass
class ListCompetitionsInput:
    actor_role: RoleLabel
    season_id: Optional[uuid.UUID] = None
    organization_id: Optional[uuid.UUID] = None
    status_label: Optional[str] = None
    page: int = 1
    page_size: int = 20


@dataclass
class ListCompetitionsOutput:
    data: List[Competition]
    page: int
    page_size: int
    total: int


class ListCompetitions:
    def __init__(self, repo: CompetitionRepository):
        self._repo = repo

    def execute(self, inp: ListCompetitionsInput) -> ListCompetitionsOutput:
        assert_can_list_competitions(inp.actor_role)
        page_size = min(max(inp.page_size, 1), 100)
        items, total = self._repo.list_competitions(
            season_id=inp.season_id,
            organization_id=inp.organization_id,
            status_label=inp.status_label,
            page=inp.page,
            page_size=page_size,
        )
        return ListCompetitionsOutput(data=items, page=inp.page, page_size=page_size, total=total)


# ---------------------------------------------------------------------------
# createCompetition
# ---------------------------------------------------------------------------

@dataclass
class CreateCompetitionInput:
    actor_role: RoleLabel
    season_id: uuid.UUID
    name: str
    start_date: date
    organization_id: Optional[uuid.UUID] = None
    end_date: Optional[date] = None
    format_label: Optional[str] = None
    stage_labels: List[str] = None
    calendar_entry_ids: List[uuid.UUID] = None
    registration_team_ids: List[uuid.UUID] = None

    def __post_init__(self):
        if self.stage_labels is None:
            self.stage_labels = []
        if self.calendar_entry_ids is None:
            self.calendar_entry_ids = []
        if self.registration_team_ids is None:
            self.registration_team_ids = []


class CreateCompetition:
    def __init__(self, repo: CompetitionRepository):
        self._repo = repo

    def execute(self, inp: CreateCompetitionInput) -> Competition:
        assert_can_create_competition(inp.actor_role)
        competition = Competition(
            id=uuid.uuid4(),
            season_id=inp.season_id,
            organization_id=inp.organization_id,
            name=inp.name,
            start_date=inp.start_date,
            end_date=inp.end_date,
            format_label=inp.format_label,
            status_label=CompetitionStatus.DRAFT,
            stage_labels=list(inp.stage_labels),
            calendar_entry_ids=list(inp.calendar_entry_ids),
            registration_team_ids=list(inp.registration_team_ids),
        )
        competition.validate_invariants()
        return self._repo.save(competition)


# ---------------------------------------------------------------------------
# getCompetition
# ---------------------------------------------------------------------------

class GetCompetition:
    def __init__(self, repo: CompetitionRepository):
        self._repo = repo

    def execute(self, actor_role: RoleLabel, competition_id: uuid.UUID) -> Competition:
        assert_can_read_competition(actor_role)
        comp = self._repo.get_by_id(competition_id)
        if comp is None:
            raise CompetitionNotFound(f"Competição {competition_id} não encontrada.")
        return comp


# ---------------------------------------------------------------------------
# patchCompetition
# ---------------------------------------------------------------------------

@dataclass
class PatchCompetitionInput:
    actor_role: RoleLabel
    competition_id: uuid.UUID
    name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    format_label: Optional[str] = None
    status_label: Optional[str] = None
    stage_labels: Optional[List[str]] = None
    standings_summary: Optional[str] = None


class PatchCompetition:
    def __init__(self, repo: CompetitionRepository):
        self._repo = repo

    def execute(self, inp: PatchCompetitionInput) -> Competition:
        comp = self._repo.get_by_id(inp.competition_id)
        if comp is None:
            raise CompetitionNotFound(f"Competição {inp.competition_id} não encontrada.")
        assert_can_patch_competition(inp.actor_role, comp.status_label)

        if inp.name is not None:
            comp.name = inp.name
        if inp.start_date is not None:
            comp.start_date = inp.start_date
        if inp.end_date is not None:
            comp.end_date = inp.end_date
        if inp.format_label is not None:
            comp.format_label = inp.format_label
        if inp.status_label is not None:
            target = CompetitionStatus(inp.status_label)
            assert_valid_transition(comp.status_label, target)
            comp.status_label = target
        if inp.stage_labels is not None:
            comp.stage_labels = list(inp.stage_labels)
        if inp.standings_summary is not None:
            comp.standings_summary = inp.standings_summary

        comp.validate_invariants()
        return self._repo.save(comp)


# ---------------------------------------------------------------------------
# registerTeamInCompetition / unregisterTeamFromCompetition
# ---------------------------------------------------------------------------

class RegisterTeamInCompetition:
    def __init__(self, repo: CompetitionRepository):
        self._repo = repo

    def execute(
        self,
        actor_role: RoleLabel,
        competition_id: uuid.UUID,
        team_id: uuid.UUID,
    ) -> None:
        assert_can_register_team(actor_role)
        comp = self._repo.get_by_id(competition_id)
        if comp is None:
            raise CompetitionNotFound(f"Competição {competition_id} não encontrada.")
        assert_team_not_registered(comp.registration_team_ids, team_id)
        comp.registration_team_ids.append(team_id)
        comp.validate_invariants()
        self._repo.save(comp)


class UnregisterTeamFromCompetition:
    def __init__(self, repo: CompetitionRepository):
        self._repo = repo

    def execute(
        self,
        actor_role: RoleLabel,
        competition_id: uuid.UUID,
        team_id: uuid.UUID,
    ) -> None:
        assert_can_unregister_team(actor_role)
        comp = self._repo.get_by_id(competition_id)
        if comp is None:
            raise CompetitionNotFound(f"Competição {competition_id} não encontrada.")
        assert_team_registered(comp.registration_team_ids, team_id)
        comp.registration_team_ids.remove(team_id)
        self._repo.save(comp)
