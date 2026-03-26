from enum import Enum
from uuid import UUID
from .entities import IngestionJob


class RoleLabel(str, Enum):
    ADMIN = "admin"
    COORDINATOR = "coordinator"
    COACH = "coach"
    ATHLETE = "athlete"
    MEMBER = "member"


MANAGER_ROLES = {RoleLabel.ADMIN, RoleLabel.COORDINATOR}


class InsufficientPrivilege(Exception):
    pass


class IngestionJobNotFound(Exception):
    pass


class IngestionJobConflict(Exception):
    pass


def _assert_manager(role: RoleLabel) -> None:
    """PERM-AI-001: only admin and coordinator can access ai_ingestion."""
    if role not in MANAGER_ROLES:
        raise InsufficientPrivilege("ai_ingestion: requires admin or coordinator role (PERM-AI-001)")


def assert_can_list_jobs(role: RoleLabel) -> None:
    _assert_manager(role)


def assert_can_create_job(role: RoleLabel) -> None:
    _assert_manager(role)


def assert_can_get_job(role: RoleLabel) -> None:
    _assert_manager(role)


def assert_can_retry_job(role: RoleLabel, job: IngestionJob) -> None:
    _assert_manager(role)
    # PERM-AI-003: only FAILED or ERROR jobs can be retried
    if not job.can_be_retried():
        raise IngestionJobConflict(
            f"PERM-AI-003: job in status '{job.status_label}' cannot be retried (requires failed)"
        )
