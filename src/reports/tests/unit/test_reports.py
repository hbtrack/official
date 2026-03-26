import uuid
from datetime import datetime, timezone
import pytest

from reports.domain.entities import ReportJob
from reports.domain.rules import (
    RoleLabel, InsufficientPrivilege, ReportJobNotFound, ReportJobConflict,
    assert_can_list_jobs, assert_can_create_job, assert_can_access_job,
    assert_can_update_job, assert_can_download,
)


def make_job(**kwargs):
    defaults = dict(
        id=uuid.uuid4(),
        owner_user_id=uuid.uuid4(),
        report_type="training-summary",
        requested_at=datetime.now(timezone.utc),
        format_label="pdf",
        parameter_summary="season=2026; team=senior-male",
        source_metric_names=["Training Load Trend", "Attendance Rate"],
        retention_label="90-days",
        status_label="queued",
    )
    defaults.update(kwargs)
    return ReportJob(**defaults)


# ---- INV-RPT-001: required fields ----

def test_job_valid():
    j = make_job()
    j.validate_invariants()  # no raise


def test_job_missing_report_type():
    j = make_job(report_type="")
    with pytest.raises(ValueError, match="INV-RPT-001"):
        j.validate_invariants()


def test_job_missing_owner():
    j = make_job(owner_user_id=None)
    with pytest.raises(ValueError, match="INV-RPT-001"):
        j.validate_invariants()


# ---- INV-RPT-003: requestedAt required ----

def test_job_missing_requested_at():
    j = make_job(requested_at=None)
    with pytest.raises(ValueError, match="INV-RPT-003"):
        j.validate_invariants()


# ---- INV-RPT-002: sourceMetricNames unique ----

def test_job_duplicate_metric_names():
    j = make_job(source_metric_names=["Load", "Load"])
    with pytest.raises(ValueError, match="INV-RPT-002"):
        j.validate_invariants()


def test_job_unique_metric_names():
    j = make_job(source_metric_names=["Load", "Attendance"])
    j.validate_invariants()


# ---- INV-RPT-004: generatedArtifactRef -> retentionLabel ----

def test_artifact_ref_without_retention_fails():
    j = make_job(generated_artifact_ref="reports://2026/test.pdf", retention_label=None)
    with pytest.raises(ValueError, match="INV-RPT-004"):
        j.validate_invariants()


def test_artifact_ref_with_retention_valid():
    j = make_job(generated_artifact_ref="reports://2026/test.pdf", retention_label="30-days")
    j.validate_invariants()


# ---- can_be_cancelled ----

def test_queued_can_be_cancelled():
    j = make_job(status_label="queued")
    assert j.can_be_cancelled() is True


def test_processing_can_be_cancelled():
    j = make_job(status_label="processing")
    assert j.can_be_cancelled() is True


def test_completed_cannot_be_cancelled():
    j = make_job(status_label="completed")
    assert j.can_be_cancelled() is False


# ---- RBAC: listReportJobs ----

def test_list_jobs_admin_allowed():
    assert_can_list_jobs(RoleLabel.ADMIN)


def test_list_jobs_athlete_allowed():
    assert_can_list_jobs(RoleLabel.ATHLETE)


def test_list_jobs_member_denied():
    with pytest.raises(InsufficientPrivilege):
        assert_can_list_jobs(RoleLabel.MEMBER)


# ---- RBAC: createReportJob ----

def test_create_job_admin_allowed():
    assert_can_create_job(RoleLabel.ADMIN)


def test_create_job_athlete_allowed():
    assert_can_create_job(RoleLabel.ATHLETE)


def test_create_job_member_denied():
    with pytest.raises(InsufficientPrivilege):
        assert_can_create_job(RoleLabel.MEMBER)


# ---- RBAC: getReportJob BOLA ----

def test_get_job_admin_any():
    j = make_job()
    assert_can_access_job(RoleLabel.ADMIN, j, uuid.uuid4())


def test_get_job_coach_own():
    uid = uuid.uuid4()
    j = make_job(owner_user_id=uid)
    assert_can_access_job(RoleLabel.COACH, j, uid)


def test_get_job_coach_other_denied():
    j = make_job(owner_user_id=uuid.uuid4())
    with pytest.raises(InsufficientPrivilege, match="BOLA"):
        assert_can_access_job(RoleLabel.COACH, j, uuid.uuid4())


def test_get_job_athlete_own():
    uid = uuid.uuid4()
    j = make_job(owner_user_id=uid)
    assert_can_access_job(RoleLabel.ATHLETE, j, uid)


def test_get_job_athlete_other_denied():
    j = make_job(owner_user_id=uuid.uuid4())
    with pytest.raises(InsufficientPrivilege, match="BOLA"):
        assert_can_access_job(RoleLabel.ATHLETE, j, uuid.uuid4())


def test_get_job_member_denied():
    j = make_job()
    with pytest.raises(InsufficientPrivilege):
        assert_can_access_job(RoleLabel.MEMBER, j, uuid.uuid4())


# ---- RBAC: updateReportJob ----

def test_update_admin_any():
    j = make_job()
    assert_can_update_job(RoleLabel.ADMIN, j, uuid.uuid4())


def test_update_coordinator_any():
    j = make_job()
    assert_can_update_job(RoleLabel.COORDINATOR, j, uuid.uuid4())


def test_update_coach_own():
    uid = uuid.uuid4()
    j = make_job(owner_user_id=uid)
    assert_can_update_job(RoleLabel.COACH, j, uid)


def test_update_coach_other_denied():
    j = make_job(owner_user_id=uuid.uuid4())
    with pytest.raises(InsufficientPrivilege, match="BOLA"):
        assert_can_update_job(RoleLabel.COACH, j, uuid.uuid4())


def test_update_athlete_denied():
    uid = uuid.uuid4()
    j = make_job(owner_user_id=uid)
    with pytest.raises(InsufficientPrivilege):
        assert_can_update_job(RoleLabel.ATHLETE, j, uid)


def test_update_member_denied():
    j = make_job()
    with pytest.raises(InsufficientPrivilege):
        assert_can_update_job(RoleLabel.MEMBER, j, uuid.uuid4())


# ---- RBAC: downloadReportArtifact ----

def test_download_admin_any():
    j = make_job()
    assert_can_download(RoleLabel.ADMIN, j, uuid.uuid4())


def test_download_athlete_own():
    uid = uuid.uuid4()
    j = make_job(owner_user_id=uid)
    assert_can_download(RoleLabel.ATHLETE, j, uid)


def test_download_athlete_other_denied():
    j = make_job(owner_user_id=uuid.uuid4())
    with pytest.raises(InsufficientPrivilege, match="PERM-REP-002"):
        assert_can_download(RoleLabel.ATHLETE, j, uuid.uuid4())


def test_download_member_denied():
    j = make_job()
    with pytest.raises(InsufficientPrivilege):
        assert_can_download(RoleLabel.MEMBER, j, uuid.uuid4())
