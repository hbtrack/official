from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Tuple

from matches.domain.entities import Match, _MAX_LINEUP_PER_TEAM
from matches.domain.rules import (
    RoleLabel, MatchNotFound, InsufficientPrivilege, MatchStateError,
    assert_can_create_match, assert_can_patch_match,
    assert_can_edit_lineup, assert_not_completed, MAX_LINEUP,
)
from matches.infrastructure.repository import MatchRepository


@dataclass
class CreateMatchInput:
    actor_role: RoleLabel
    competition_id: uuid.UUID
    home_team_id: uuid.UUID
    away_team_id: uuid.UUID
    scheduled_at: datetime
    venue_label: Optional[str] = None
    referee_names: List[str] = field(default_factory=list)


@dataclass
class PatchMatchInput:
    actor_role: RoleLabel
    venue_label: Optional[str] = None
    status_label: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    referee_names: Optional[List[str]] = None
    official_incident_ids: Optional[List[uuid.UUID]] = None


@dataclass
class ListMatchesInput:
    competition_id: Optional[uuid.UUID] = None
    status_label: Optional[str] = None
    home_team_id: Optional[uuid.UUID] = None
    away_team_id: Optional[uuid.UUID] = None
    page: int = 1
    page_size: int = 20


# ---------------------------------------------------------------------------
# Use cases
# ---------------------------------------------------------------------------

class CreateMatch:
    def __init__(self, repo: MatchRepository):
        self._repo = repo

    def execute(self, inp: CreateMatchInput) -> Match:
        assert_can_create_match(inp.actor_role)
        match = Match(
            id=uuid.uuid4(),
            competition_id=inp.competition_id,
            home_team_id=inp.home_team_id,
            away_team_id=inp.away_team_id,
            scheduled_at=inp.scheduled_at,
            venue_label=inp.venue_label,
            referee_names=list(dict.fromkeys(inp.referee_names)),  # deduplicate
        )
        match.validate_invariants()
        return self._repo.save(match)


class ListMatches:
    def __init__(self, repo: MatchRepository):
        self._repo = repo

    def execute(self, inp: ListMatchesInput) -> Tuple[List[Match], int]:
        return self._repo.list_matches(
            competition_id=inp.competition_id,
            status_label=inp.status_label,
            home_team_id=inp.home_team_id,
            away_team_id=inp.away_team_id,
            page=inp.page,
            page_size=inp.page_size,
        )


class GetMatch:
    def __init__(self, repo: MatchRepository):
        self._repo = repo

    def execute(self, match_id: uuid.UUID) -> Match:
        match = self._repo.get_by_id(match_id)
        if match is None:
            raise MatchNotFound(f"Partida {match_id} não encontrada.")
        return match


class PatchMatch:
    def __init__(self, repo: MatchRepository):
        self._repo = repo

    def execute(self, match_id: uuid.UUID, inp: PatchMatchInput) -> Match:
        assert_can_patch_match(inp.actor_role)
        match = self._repo.get_by_id(match_id)
        if match is None:
            raise MatchNotFound(f"Partida {match_id} não encontrada.")
        assert_not_completed(match.status_label)

        if inp.venue_label is not None:
            match.venue_label = inp.venue_label
        if inp.status_label is not None:
            match.status_label = inp.status_label
        if inp.scheduled_at is not None:
            match.scheduled_at = inp.scheduled_at
        if inp.started_at is not None:
            match.started_at = inp.started_at
        if inp.ended_at is not None:
            match.ended_at = inp.ended_at
        if inp.home_score is not None:
            match.home_score = inp.home_score
        if inp.away_score is not None:
            match.away_score = inp.away_score
        if inp.referee_names is not None:
            match.referee_names = list(dict.fromkeys(inp.referee_names))
        if inp.official_incident_ids is not None:
            match.official_incident_ids = list(dict.fromkeys(inp.official_incident_ids))

        match.validate_invariants()
        return self._repo.save(match)


class AddPlayerToLineup:
    def __init__(self, repo: MatchRepository):
        self._repo = repo

    def execute(self, role: RoleLabel, match_id: uuid.UUID, user_id: uuid.UUID) -> Match:
        match = self._repo.get_by_id(match_id)
        if match is None:
            raise MatchNotFound(f"Partida {match_id} não encontrada.")
        assert_can_edit_lineup(role, match.status_label)
        if user_id in match.lineup_user_ids:
            raise MatchStateError(f"Atleta {user_id} já está no lineup.")
        if len(match.lineup_user_ids) >= MAX_LINEUP:
            raise MatchStateError(f"HBR-008: limite de {MAX_LINEUP} jogadores no lineup atingido.")
        match.lineup_user_ids.append(user_id)
        match.validate_invariants()
        return self._repo.save(match)


class RemovePlayerFromLineup:
    def __init__(self, repo: MatchRepository):
        self._repo = repo

    def execute(self, role: RoleLabel, match_id: uuid.UUID, user_id: uuid.UUID) -> Match:
        match = self._repo.get_by_id(match_id)
        if match is None:
            raise MatchNotFound(f"Partida {match_id} não encontrada.")
        assert_can_edit_lineup(role, match.status_label)
        if user_id not in match.lineup_user_ids:
            raise MatchStateError(f"Atleta {user_id} não está no lineup.")
        match.lineup_user_ids.remove(user_id)
        return self._repo.save(match)
