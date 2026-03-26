"""Testes unitários — módulo matches."""
import uuid
from datetime import datetime, timedelta

import pytest

from matches.domain.entities import Match, _VALID_STATUSES
from matches.domain.rules import (
    RoleLabel, InsufficientPrivilege, MatchStateError,
    assert_can_create_match, assert_can_patch_match,
    assert_can_edit_lineup, assert_not_completed, MAX_LINEUP,
)


def make_match(**kwargs) -> Match:
    defaults = dict(
        id=uuid.uuid4(),
        competition_id=uuid.uuid4(),
        home_team_id=uuid.uuid4(),
        away_team_id=uuid.uuid4(),
        scheduled_at=datetime(2026, 3, 15, 14, 0),
    )
    defaults.update(kwargs)
    return Match(**defaults)


# ---------------------------------------------------------------------------
# INV-MATCH-001: campos obrigatórios
# ---------------------------------------------------------------------------

class TestInvariantRequiredFields:
    def test_valid_match_passes(self):
        make_match().validate_invariants()


# ---------------------------------------------------------------------------
# INV-MATCH-002: home != away
# ---------------------------------------------------------------------------

class TestInvariantTeamsDistinct:
    def test_same_team_raises(self):
        uid = uuid.uuid4()
        with pytest.raises(ValueError, match="INV-MATCH-002"):
            make_match(home_team_id=uid, away_team_id=uid).validate_invariants()

    def test_different_teams_pass(self):
        make_match().validate_invariants()


# ---------------------------------------------------------------------------
# INV-MATCH-003: scores >= 0
# ---------------------------------------------------------------------------

class TestInvariantScores:
    def test_negative_home_score_raises(self):
        with pytest.raises(ValueError, match="INV-MATCH-003"):
            make_match(home_score=-1).validate_invariants()

    def test_negative_away_score_raises(self):
        with pytest.raises(ValueError, match="INV-MATCH-003"):
            make_match(away_score=-1).validate_invariants()

    def test_zero_scores_pass(self):
        make_match(home_score=0, away_score=0).validate_invariants()

    def test_positive_scores_pass(self):
        make_match(home_score=30, away_score=25).validate_invariants()


# ---------------------------------------------------------------------------
# INV-MATCH-004: startedAt <= endedAt
# ---------------------------------------------------------------------------

class TestInvariantTemporal:
    def test_started_after_ended_raises(self):
        now = datetime(2026, 3, 15, 15, 0)
        earlier = datetime(2026, 3, 15, 14, 0)
        with pytest.raises(ValueError, match="INV-MATCH-004"):
            make_match(started_at=now, ended_at=earlier).validate_invariants()

    def test_started_equals_ended_passes(self):
        t = datetime(2026, 3, 15, 14, 0)
        make_match(started_at=t, ended_at=t).validate_invariants()

    def test_valid_temporal_passes(self):
        s = datetime(2026, 3, 15, 14, 0)
        e = datetime(2026, 3, 15, 15, 30)
        make_match(started_at=s, ended_at=e).validate_invariants()


# ---------------------------------------------------------------------------
# INV-MATCH-005: no duplicates
# ---------------------------------------------------------------------------

class TestInvariantNoDuplicates:
    def test_duplicate_lineup_raises(self):
        uid = uuid.uuid4()
        with pytest.raises(ValueError, match="INV-MATCH-005"):
            make_match(lineup_user_ids=[uid, uid]).validate_invariants()

    def test_duplicate_referee_raises(self):
        with pytest.raises(ValueError, match="INV-MATCH-005"):
            make_match(referee_names=["João", "João"]).validate_invariants()

    def test_unique_lineup_passes(self):
        make_match(lineup_user_ids=[uuid.uuid4(), uuid.uuid4()]).validate_invariants()


# ---------------------------------------------------------------------------
# RBAC — createMatch
# ---------------------------------------------------------------------------

class TestCreateMatchRBAC:
    def test_admin_can_create(self):
        assert_can_create_match(RoleLabel.ADMIN)

    def test_coordinator_can_create(self):
        assert_can_create_match(RoleLabel.COORDINATOR)

    def test_coach_cannot_create(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_create_match(RoleLabel.COACH)

    def test_athlete_cannot_create(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_create_match(RoleLabel.ATHLETE)


# ---------------------------------------------------------------------------
# RBAC — patchMatch
# ---------------------------------------------------------------------------

class TestPatchMatchRBAC:
    def test_admin_can_patch(self):
        assert_can_patch_match(RoleLabel.ADMIN)

    def test_coach_can_patch(self):
        assert_can_patch_match(RoleLabel.COACH)

    def test_athlete_cannot_patch(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_patch_match(RoleLabel.ATHLETE)

    def test_member_cannot_patch(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_patch_match(RoleLabel.MEMBER)


# ---------------------------------------------------------------------------
# RBAC — lineup (PERM-MATCH-001/002)
# ---------------------------------------------------------------------------

class TestLineupRBAC:
    def test_coach_can_edit_scheduled(self):
        assert_can_edit_lineup(RoleLabel.COACH, "SCHEDULED")

    def test_coach_can_edit_pre_match(self):
        assert_can_edit_lineup(RoleLabel.COACH, "PRE_MATCH")

    def test_coach_cannot_edit_first_half(self):
        with pytest.raises(MatchStateError, match="PERM-MATCH-002"):
            assert_can_edit_lineup(RoleLabel.COACH, "FIRST_HALF")

    def test_athlete_cannot_edit_lineup(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_edit_lineup(RoleLabel.ATHLETE, "SCHEDULED")

    def test_completed_is_readonly(self):
        with pytest.raises(MatchStateError, match="PERM-MATCH-001"):
            assert_not_completed("COMPLETED")

    def test_scheduled_not_readonly(self):
        assert_not_completed("SCHEDULED")  # não levanta


# ---------------------------------------------------------------------------
# HBR-008: max 16 jogadores no lineup
# ---------------------------------------------------------------------------

class TestLineupLimit:
    def test_16_players_pass(self):
        ids = [uuid.uuid4() for _ in range(MAX_LINEUP)]
        make_match(lineup_user_ids=ids).validate_invariants()

    def test_17_unique_players_pass_entity(self):
        # domain entity não limita contagem (rule check é no use case)
        ids = [uuid.uuid4() for _ in range(17)]
        make_match(lineup_user_ids=ids).validate_invariants()
