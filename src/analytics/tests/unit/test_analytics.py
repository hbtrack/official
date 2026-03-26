import uuid
from datetime import datetime, timezone
import pytest

from analytics.domain.entities import (
    AnalyticsSnapshot, AnalyticsQueryRequest,
    VALID_METRIC_KEYS, VALID_SOURCE_MODULES,
)
from analytics.domain.rules import (
    RoleLabel, InsufficientPrivilege, SnapshotNotFound,
    assert_can_create_snapshot, assert_can_list_snapshots,
    assert_can_get_snapshot, assert_can_list_dashboards,
    assert_can_query_analytics,
)


def make_snapshot(**kwargs):
    defaults = dict(
        id=uuid.uuid4(),
        metric_key="READINESS_SCORE",
        computed_at=datetime.now(timezone.utc),
        created_by_user_id=uuid.uuid4(),
        source_module_labels=["TRAINING", "WELLNESS"],
        time_window_label="LAST_28_DAYS",
        granularity_label="WEEKLY",
        refresh_mode_label="scheduled",
    )
    defaults.update(kwargs)
    return AnalyticsSnapshot(**defaults)


# ---- INV-ANL-001: required fields ----

def test_snapshot_valid():
    s = make_snapshot()
    s.validate_invariants()  # no raise


def test_snapshot_missing_metric_key():
    s = make_snapshot(metric_key="")
    with pytest.raises(ValueError, match="INV-ANL-001"):
        s.validate_invariants()


# ---- INV-ANL-005: closed metric catalog ----

def test_snapshot_invalid_metric_key():
    s = make_snapshot(metric_key="INVENTED_METRIC")
    with pytest.raises(ValueError, match="INV-ANL-005"):
        s.validate_invariants()


def test_all_valid_metric_keys():
    for key in VALID_METRIC_KEYS:
        s = make_snapshot(metric_key=key)
        s.validate_invariants()


# ---- INV-ANL-002: sourceModuleLabels unique ----

def test_snapshot_duplicate_source_modules():
    s = make_snapshot(source_module_labels=["TRAINING", "TRAINING"])
    with pytest.raises(ValueError, match="INV-ANL-002"):
        s.validate_invariants()


def test_snapshot_single_source_module():
    s = make_snapshot(source_module_labels=["TRAINING"])
    s.validate_invariants()


# ---- DR-ANL-009: only TRAINING/WELLNESS ----

def test_snapshot_invalid_source_module():
    s = make_snapshot(source_module_labels=["MATCHES"])
    with pytest.raises(ValueError, match="DR-ANL-009"):
        s.validate_invariants()


# ---- RBAC: createAnalyticsSnapshot ----

def test_create_snapshot_admin_allowed():
    assert_can_create_snapshot(RoleLabel.ADMIN)


def test_create_snapshot_coordinator_allowed():
    assert_can_create_snapshot(RoleLabel.COORDINATOR)


def test_create_snapshot_coach_allowed():
    assert_can_create_snapshot(RoleLabel.COACH)


def test_create_snapshot_athlete_denied():
    with pytest.raises(InsufficientPrivilege):
        assert_can_create_snapshot(RoleLabel.ATHLETE)


def test_create_snapshot_member_denied():
    with pytest.raises(InsufficientPrivilege):
        assert_can_create_snapshot(RoleLabel.MEMBER)


# ---- RBAC: listAnalyticsSnapshots ----

def test_list_snapshots_admin_allowed():
    assert_can_list_snapshots(RoleLabel.ADMIN)


def test_list_snapshots_athlete_allowed():
    assert_can_list_snapshots(RoleLabel.ATHLETE)


def test_list_snapshots_member_denied():
    with pytest.raises(InsufficientPrivilege):
        assert_can_list_snapshots(RoleLabel.MEMBER)


# ---- RBAC: getAnalyticsSnapshot BOLA ----

def test_get_snapshot_admin_any():
    s = make_snapshot()
    assert_can_get_snapshot(RoleLabel.ADMIN, s, uuid.uuid4())


def test_get_snapshot_athlete_own():
    uid = uuid.uuid4()
    s = make_snapshot(created_by_user_id=uid)
    assert_can_get_snapshot(RoleLabel.ATHLETE, s, uid)


def test_get_snapshot_athlete_other_denied():
    s = make_snapshot(created_by_user_id=uuid.uuid4())
    with pytest.raises(InsufficientPrivilege, match="PERM-ANL-001"):
        assert_can_get_snapshot(RoleLabel.ATHLETE, s, uuid.uuid4())


def test_get_snapshot_member_denied():
    s = make_snapshot()
    with pytest.raises(InsufficientPrivilege):
        assert_can_get_snapshot(RoleLabel.MEMBER, s, uuid.uuid4())


# ---- RBAC: listAnalyticsDashboards ----

def test_list_dashboards_coach_allowed():
    assert_can_list_dashboards(RoleLabel.COACH)


def test_list_dashboards_athlete_allowed():
    assert_can_list_dashboards(RoleLabel.ATHLETE)


def test_list_dashboards_member_denied():
    with pytest.raises(InsufficientPrivilege):
        assert_can_list_dashboards(RoleLabel.MEMBER)


# ---- RBAC: queryAnalyticsData ----

def test_query_admin_allowed():
    assert_can_query_analytics(RoleLabel.ADMIN)


def test_query_athlete_denied():
    with pytest.raises(InsufficientPrivilege):
        assert_can_query_analytics(RoleLabel.ATHLETE)


def test_query_member_denied():
    with pytest.raises(InsufficientPrivilege):
        assert_can_query_analytics(RoleLabel.MEMBER)


# ---- INV-ANL-006: CUSTOM timeWindow ----

def make_query(**kwargs):
    defaults = dict(
        scope="TEAM",
        source_modules=["TRAINING"],
        metric_keys=["READINESS_SCORE"],
        time_window="LAST_28_DAYS",
        granularity="WEEKLY",
        filters={"teamIds": [str(uuid.uuid4())]},
    )
    defaults.update(kwargs)
    return AnalyticsQueryRequest(**defaults)


def test_query_custom_requires_dates():
    q = make_query(time_window="CUSTOM")
    with pytest.raises(ValueError, match="INV-ANL-006"):
        q.validate_invariants()


def test_query_custom_with_dates_valid():
    q = make_query(time_window="CUSTOM", date_from="2026-01-01", date_to="2026-03-01")
    q.validate_invariants()


def test_query_non_custom_with_dates_rejected():
    q = make_query(time_window="LAST_7_DAYS", date_from="2026-01-01")
    with pytest.raises(ValueError, match="INV-ANL-006"):
        q.validate_invariants()


# ---- INV-ANL-007: scope filter consistency ----

def test_query_team_scope_without_teamids():
    q = make_query(scope="TEAM", filters={"athleteIds": [str(uuid.uuid4())]})
    with pytest.raises(ValueError, match="INV-ANL-007"):
        q.validate_invariants()


def test_query_athlete_scope_without_athleteids():
    q = make_query(scope="ATHLETE", filters={"teamIds": [str(uuid.uuid4())]})
    with pytest.raises(ValueError, match="INV-ANL-007"):
        q.validate_invariants()


def test_query_athlete_scope_with_athleteids_valid():
    q = make_query(scope="ATHLETE", filters={"athleteIds": [str(uuid.uuid4())]})
    q.validate_invariants()


# ---- INV-ANL-005 in query ----

def test_query_invalid_metric_key():
    q = make_query(metric_keys=["FAKE_METRIC"])
    with pytest.raises(ValueError, match="INV-ANL-005"):
        q.validate_invariants()


# ---- DR-ANL-009 in query ----

def test_query_invalid_source_module():
    q = make_query(source_modules=["MATCHES"])
    with pytest.raises(ValueError, match="DR-ANL-009"):
        q.validate_invariants()
