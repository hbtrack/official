from enum import Enum
from uuid import UUID
from .entities import AnalyticsSnapshot


class RoleLabel(str, Enum):
    ADMIN = "admin"
    COORDINATOR = "coordinator"
    COACH = "coach"
    ATHLETE = "athlete"
    MEMBER = "member"


STAFF_ROLES = {RoleLabel.ADMIN, RoleLabel.COORDINATOR, RoleLabel.COACH}


class InsufficientPrivilege(Exception):
    pass


class SnapshotNotFound(Exception):
    pass


def assert_can_create_snapshot(role: RoleLabel) -> None:
    """createAnalyticsSnapshot: admin/coordinator/coach only (PERM-ANL-002)."""
    if role not in STAFF_ROLES:
        raise InsufficientPrivilege("createAnalyticsSnapshot requires admin, coordinator or coach")


def assert_can_list_snapshots(role: RoleLabel) -> None:
    """listAnalyticsSnapshots: all except member."""
    if role == RoleLabel.MEMBER:
        raise InsufficientPrivilege("listAnalyticsSnapshots: member access denied")


def assert_can_get_snapshot(
    role: RoleLabel,
    snapshot: AnalyticsSnapshot,
    requester_id: UUID,
) -> None:
    """getAnalyticsSnapshot: athlete sees only own snapshots (PERM-ANL-001)."""
    if role == RoleLabel.MEMBER:
        raise InsufficientPrivilege("getAnalyticsSnapshot: member access denied")
    if role == RoleLabel.ATHLETE and snapshot.created_by_user_id != requester_id:
        raise InsufficientPrivilege("PERM-ANL-001: athlete can only access own snapshots")


def assert_can_list_dashboards(role: RoleLabel) -> None:
    """listAnalyticsDashboards: all except member."""
    if role == RoleLabel.MEMBER:
        raise InsufficientPrivilege("listAnalyticsDashboards: member access denied")


def assert_can_query_analytics(role: RoleLabel) -> None:
    """queryAnalyticsData: staff only (PERM-ANL-002)."""
    if role not in STAFF_ROLES:
        raise InsufficientPrivilege("queryAnalyticsData requires admin, coordinator or coach")
