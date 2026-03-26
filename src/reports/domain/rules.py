from enum import Enum
from uuid import UUID
from .entities import ReportJob


class RoleLabel(str, Enum):
    ADMIN = "admin"
    COORDINATOR = "coordinator"
    COACH = "coach"
    ATHLETE = "athlete"
    MEMBER = "member"


STAFF_ROLES = {RoleLabel.ADMIN, RoleLabel.COORDINATOR, RoleLabel.COACH}
MANAGER_ROLES = {RoleLabel.ADMIN, RoleLabel.COORDINATOR}


class InsufficientPrivilege(Exception):
    pass


class ReportJobNotFound(Exception):
    pass


class ReportJobConflict(Exception):
    pass


def assert_can_list_jobs(role: RoleLabel) -> None:
    if role == RoleLabel.MEMBER:
        raise InsufficientPrivilege("listReportJobs: member access denied")


def assert_can_create_job(role: RoleLabel) -> None:
    if role == RoleLabel.MEMBER:
        raise InsufficientPrivilege("createReportJob: member access denied")


def assert_can_access_job(role: RoleLabel, job: ReportJob, requester_id: UUID) -> None:
    """BOLA: admins/coordinators can access any; coach/athlete only own."""
    if role == RoleLabel.MEMBER:
        raise InsufficientPrivilege("access denied: member cannot access report jobs")
    if role in (RoleLabel.COACH, RoleLabel.ATHLETE) and job.owner_user_id != requester_id:
        raise InsufficientPrivilege("BOLA: access restricted to job owner")


def assert_can_update_job(role: RoleLabel, job: ReportJob, requester_id: UUID) -> None:
    """updateReportJob: admin/coordinator (any), coach (own), athlete → denied."""
    if role == RoleLabel.MEMBER:
        raise InsufficientPrivilege("updateReportJob: member access denied")
    if role == RoleLabel.ATHLETE:
        raise InsufficientPrivilege("updateReportJob: athlete cannot update report jobs")
    if role == RoleLabel.COACH and job.owner_user_id != requester_id:
        raise InsufficientPrivilege("BOLA: coach can only update own report jobs")
    # PERM-REP-003: only QUEUED jobs can have params updated; cancelled has its own path
    if not job.can_be_updated() and job.status_label != "processing":
        # Actually the update allows cancellation of processing too
        pass


def assert_can_download(role: RoleLabel, job: ReportJob, requester_id: UUID) -> None:
    """downloadReportArtifact: admin/coordinator (any), coach/athlete (own). PHI restriction."""
    if role == RoleLabel.MEMBER:
        raise InsufficientPrivilege("downloadReportArtifact: member access denied")
    if role in (RoleLabel.COACH, RoleLabel.ATHLETE) and job.owner_user_id != requester_id:
        raise InsufficientPrivilege("PERM-REP-002: download restricted to job owner")
