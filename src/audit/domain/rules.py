from enum import Enum
from uuid import UUID
from typing import Optional
from .entities import AuditEntry


class RoleLabel(str, Enum):
    ADMIN = "admin"
    COORDINATOR = "coordinator"
    COACH = "coach"
    ATHLETE = "athlete"
    MEMBER = "member"


AUDIT_ROLES = {RoleLabel.ADMIN, RoleLabel.COORDINATOR}


class InsufficientPrivilege(Exception):
    pass


class AuditEntryNotFound(Exception):
    pass


def _assert_audit_access(role: RoleLabel) -> None:
    """PERM-AUD: only admin and coordinator can access audit trail."""
    if role not in AUDIT_ROLES:
        raise InsufficientPrivilege(
            "audit: requires admin or coordinator role (DEC-AUD-002=B)"
        )


def assert_coordinator_context(
    role: RoleLabel,
    team_id: Optional[str],
    organization_id: Optional[str],
) -> None:
    """PERM-AUD-001: coordinator must provide teamId or organizationId."""
    if role == RoleLabel.COORDINATOR:
        if not team_id and not organization_id:
            raise ValueError(
                "PERM-AUD-001: coordinator must provide teamId or organizationId"
            )


def assert_can_list_entries(
    role: RoleLabel,
    team_id: Optional[str] = None,
    organization_id: Optional[str] = None,
) -> None:
    _assert_audit_access(role)
    assert_coordinator_context(role, team_id, organization_id)


def assert_can_create_entry(role: RoleLabel) -> None:
    _assert_audit_access(role)


def assert_can_get_entry(role: RoleLabel) -> None:
    _assert_audit_access(role)


def assert_can_export_entries(
    role: RoleLabel,
    team_id: Optional[str] = None,
    organization_id: Optional[str] = None,
) -> None:
    _assert_audit_access(role)
    assert_coordinator_context(role, team_id, organization_id)
