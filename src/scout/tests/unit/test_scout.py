import pytest
from uuid import uuid4
from datetime import datetime, timezone

from scout.domain.entities import ScoutEvent, VALID_EVENT_LABELS, VALID_TAG_LABELS
from scout.domain.rules import (
    RoleLabel, InsufficientPrivilege,
    assert_can_create_event, assert_can_read_event,
    assert_can_list_events, assert_can_complete_session,
    assert_can_get_aggregations,
)


def _now():
    return datetime.now(timezone.utc)


def _valid_event(**kwargs):
    defaults = dict(
        id=uuid4(),
        match_id=uuid4(),
        event_label="GOAL",
        recorded_at=_now(),
    )
    defaults.update(kwargs)
    return ScoutEvent(**defaults)


# ─────────────────── INV-SCOUT-001 ───────────────────

class TestInvScout001:
    def test_valid_event_passes(self):
        e = _valid_event()
        e.validate_invariants()

    def test_missing_event_label_raises(self):
        e = _valid_event(event_label="")
        with pytest.raises(ValueError, match="eventLabel"):
            e.validate_invariants()

    def test_missing_match_id_raises(self):
        e = _valid_event()
        e.match_id = None
        with pytest.raises(ValueError, match="matchId"):
            e.validate_invariants()

    def test_missing_recorded_at_raises(self):
        e = _valid_event()
        e.recorded_at = None
        with pytest.raises(ValueError, match="recordedAt"):
            e.validate_invariants()


# ─────────────────── INV-SCOUT-002 ───────────────────

class TestInvScout002:
    def test_duplicate_tag_labels_raises(self):
        e = _valid_event(tag_labels=["left-wing", "left-wing"])
        with pytest.raises(ValueError, match="tagLabels"):
            e.validate_invariants()

    def test_duplicate_clip_refs_raises(self):
        e = _valid_event(clip_asset_refs=["clip-1", "clip-1"])
        with pytest.raises(ValueError, match="clipAssetRefs"):
            e.validate_invariants()

    def test_unique_tags_and_clips_ok(self):
        e = _valid_event(
            tag_labels=["left-wing", "right-wing"],
            clip_asset_refs=["clip-1", "clip-2"],
        )
        e.validate_invariants()


# ─────────────────── INV-SCOUT-003 ───────────────────

class TestInvScout003:
    def test_invalid_event_label_raises(self):
        e = _valid_event(event_label="INVALID_LABEL")
        with pytest.raises(ValueError, match="taxonomia"):
            e.validate_invariants()

    def test_all_valid_event_labels_pass(self):
        for label in list(VALID_EVENT_LABELS)[:5]:
            e = _valid_event(event_label=label)
            e.validate_invariants()

    def test_invalid_tag_label_raises(self):
        e = _valid_event(tag_labels=["invalid-tag"])
        with pytest.raises(ValueError, match="taxonomia"):
            e.validate_invariants()

    def test_valid_tag_labels_pass(self):
        e = _valid_event(tag_labels=["left-wing", "first-half"])
        e.validate_invariants()

    def test_valid_coding_schema_pass(self):
        e = _valid_event(coding_schema_label="match-event-v1")
        e.validate_invariants()

    def test_invalid_coding_schema_raises(self):
        e = _valid_event(coding_schema_label="invalid-schema")
        with pytest.raises(ValueError, match="taxonomia"):
            e.validate_invariants()


# ─────────────────── PERM-SCOUT-001 ───────────────────

class TestPermScout001:
    def test_coordinator_without_team_id_raises(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_list_events(RoleLabel.COORDINATOR, team_id=None)

    def test_coach_without_team_id_raises(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_list_events(RoleLabel.COACH, team_id=None)

    def test_coordinator_with_team_id_ok(self):
        assert_can_list_events(RoleLabel.COORDINATOR, team_id=uuid4())

    def test_coach_with_team_id_ok(self):
        assert_can_list_events(RoleLabel.COACH, team_id=uuid4())

    def test_admin_without_team_id_ok(self):
        assert_can_list_events(RoleLabel.ADMIN, team_id=None)

    def test_athlete_without_team_id_ok(self):
        assert_can_list_events(RoleLabel.ATHLETE, team_id=None)

    def test_member_raises_always(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_list_events(RoleLabel.MEMBER, team_id=uuid4())


# ─────────────────── PERM-SCOUT-002 (BOLA) ───────────────────

class TestPermScout002:
    def test_admin_reads_any_event(self):
        assert_can_read_event(
            RoleLabel.ADMIN, actor_id=uuid4(),
            event_athlete_user_id=uuid4(), event_team_id=uuid4()
        )

    def test_athlete_reads_own_event(self):
        aid = uuid4()
        assert_can_read_event(
            RoleLabel.ATHLETE, actor_id=aid,
            event_athlete_user_id=aid, event_team_id=uuid4()
        )

    def test_athlete_cannot_read_others_event(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_read_event(
                RoleLabel.ATHLETE, actor_id=uuid4(),
                event_athlete_user_id=uuid4(), event_team_id=uuid4()
            )

    def test_member_always_denied(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_read_event(
                RoleLabel.MEMBER, actor_id=uuid4(),
                event_athlete_user_id=uuid4(), event_team_id=uuid4()
            )

    def test_coach_reads_event_in_own_team(self):
        team_id = uuid4()
        assert_can_read_event(
            RoleLabel.COACH, actor_id=uuid4(),
            event_athlete_user_id=uuid4(), event_team_id=team_id,
            actor_team_ids=[team_id]
        )

    def test_coach_cannot_read_other_team_event(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_read_event(
                RoleLabel.COACH, actor_id=uuid4(),
                event_athlete_user_id=uuid4(), event_team_id=uuid4(),
                actor_team_ids=[uuid4()]
            )


# ─────────────────── PERM-SCOUT-005 ───────────────────

class TestPermScout005:
    def test_admin_can_create(self):
        assert_can_create_event(RoleLabel.ADMIN)

    def test_coordinator_can_create(self):
        assert_can_create_event(RoleLabel.COORDINATOR)

    def test_coach_can_create(self):
        assert_can_create_event(RoleLabel.COACH)

    def test_athlete_cannot_create(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_create_event(RoleLabel.ATHLETE)

    def test_member_cannot_create(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_create_event(RoleLabel.MEMBER)

    def test_admin_can_complete_session(self):
        assert_can_complete_session(RoleLabel.ADMIN)

    def test_athlete_cannot_complete_session(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_complete_session(RoleLabel.ATHLETE)

    def test_member_cannot_complete_session(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_complete_session(RoleLabel.MEMBER)
