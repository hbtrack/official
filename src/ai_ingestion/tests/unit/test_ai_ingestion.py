import uuid
from datetime import datetime, timezone, timedelta
import pytest

from ai_ingestion.domain.entities import IngestionJob
from ai_ingestion.domain.rules import (
    RoleLabel,
    InsufficientPrivilege,
    IngestionJobNotFound,
    IngestionJobConflict,
    assert_can_list_jobs,
    assert_can_create_job,
    assert_can_get_job,
    assert_can_retry_job,
)
from ai_ingestion.application.use_cases import (
    ListIngestionJobs,
    CreateIngestionJob,
    GetIngestionJob,
    RetryIngestionJob,
)


def make_job(**kwargs):
    now = datetime.now(timezone.utc)
    defaults = dict(
        id=uuid.uuid4(),
        source_label="video-pipeline",
        ingestion_mode="automated",
        received_at=now,
        status_label="queued",
    )
    defaults.update(kwargs)
    return IngestionJob(**defaults)


# ---- INV-ING-001: required fields ----

def test_job_valid():
    j = make_job()
    j.validate_invariants()


def test_job_missing_source_label():
    j = make_job(source_label="")
    with pytest.raises(ValueError, match="INV-ING-001"):
        j.validate_invariants()


def test_job_missing_ingestion_mode():
    j = make_job(ingestion_mode="")
    with pytest.raises(ValueError, match="INV-ING-001"):
        j.validate_invariants()


def test_job_missing_received_at():
    j = make_job(received_at=None)
    with pytest.raises(ValueError, match="INV-ING-001"):
        j.validate_invariants()


# ---- INV-ING-002: completedAt >= receivedAt ----

def test_completed_at_before_received_at_fails():
    now = datetime.now(timezone.utc)
    j = make_job(received_at=now, completed_at=now - timedelta(seconds=1))
    with pytest.raises(ValueError, match="INV-ING-002"):
        j.validate_invariants()


def test_completed_at_equal_received_at_ok():
    now = datetime.now(timezone.utc)
    j = make_job(received_at=now, completed_at=now)
    j.validate_invariants()


def test_completed_at_after_received_at_ok():
    now = datetime.now(timezone.utc)
    j = make_job(received_at=now, completed_at=now + timedelta(seconds=10))
    j.validate_invariants()


# ---- INV-ING-003: payloadSchemaRef and mappingProfile both present or both absent ----

def test_payload_schema_ref_without_mapping_profile_fails():
    j = make_job(payload_schema_ref="schema://v1/jobs", mapping_profile=None)
    with pytest.raises(ValueError, match="INV-ING-003"):
        j.validate_invariants()


def test_mapping_profile_without_payload_schema_ref_fails():
    j = make_job(payload_schema_ref=None, mapping_profile="profile://standard")
    with pytest.raises(ValueError, match="INV-ING-003"):
        j.validate_invariants()


def test_both_present_ok():
    j = make_job(payload_schema_ref="schema://v1/jobs", mapping_profile="profile://standard")
    j.validate_invariants()


def test_both_absent_ok():
    j = make_job(payload_schema_ref=None, mapping_profile=None)
    j.validate_invariants()


# ---- can_be_retried ----

def test_can_be_retried_failed():
    j = make_job(status_label="failed")
    assert j.can_be_retried() is True


def test_cannot_be_retried_queued():
    j = make_job(status_label="queued")
    assert j.can_be_retried() is False


def test_cannot_be_retried_completed():
    j = make_job(status_label="completed")
    assert j.can_be_retried() is False


def test_cannot_be_retried_processing():
    j = make_job(status_label="processing")
    assert j.can_be_retried() is False


# ---- PERM-AI-001: only admin/coordinator ----

def test_assert_list_admin_ok():
    assert_can_list_jobs(RoleLabel.ADMIN)


def test_assert_list_coordinator_ok():
    assert_can_list_jobs(RoleLabel.COORDINATOR)


def test_assert_list_coach_forbidden():
    with pytest.raises(InsufficientPrivilege):
        assert_can_list_jobs(RoleLabel.COACH)


def test_assert_list_athlete_forbidden():
    with pytest.raises(InsufficientPrivilege):
        assert_can_list_jobs(RoleLabel.ATHLETE)


def test_assert_list_member_forbidden():
    with pytest.raises(InsufficientPrivilege):
        assert_can_list_jobs(RoleLabel.MEMBER)


def test_assert_create_coach_forbidden():
    with pytest.raises(InsufficientPrivilege):
        assert_can_create_job(RoleLabel.COACH)


def test_assert_get_athlete_forbidden():
    with pytest.raises(InsufficientPrivilege):
        assert_can_get_job(RoleLabel.ATHLETE)


# ---- PERM-AI-003: retry only for failed ----

def test_assert_retry_failed_admin_ok():
    j = make_job(status_label="failed")
    assert_can_retry_job(RoleLabel.ADMIN, j)


def test_assert_retry_queued_raises_conflict():
    j = make_job(status_label="queued")
    with pytest.raises(IngestionJobConflict, match="PERM-AI-003"):
        assert_can_retry_job(RoleLabel.ADMIN, j)


def test_assert_retry_completed_raises_conflict():
    j = make_job(status_label="completed")
    with pytest.raises(IngestionJobConflict):
        assert_can_retry_job(RoleLabel.COORDINATOR, j)


def test_assert_retry_coach_forbidden():
    j = make_job(status_label="failed")
    with pytest.raises(InsufficientPrivilege):
        assert_can_retry_job(RoleLabel.COACH, j)


# ---- Fake repo for use case tests ----

class FakeRepo:
    def __init__(self, jobs=None):
        self._jobs = {j.id: j for j in (jobs or [])}
        self._by_key = {j.idempotency_key: j for j in (jobs or []) if j.idempotency_key}

    def save(self, job):
        self._jobs[job.id] = job
        if job.idempotency_key:
            self._by_key[job.idempotency_key] = job
        return job

    def get_by_id(self, job_id):
        return self._jobs.get(job_id)

    def get_by_idempotency_key(self, key):
        return self._by_key.get(key)

    def list_jobs(self, source_label=None, ingestion_mode=None, status_label=None, page=1, page_size=20):
        items = list(self._jobs.values())
        if source_label:
            items = [j for j in items if j.source_label == source_label]
        if status_label:
            items = [j for j in items if j.status_label == status_label]
        total = len(items)
        offset = (page - 1) * page_size
        return items[offset:offset + page_size], total


# ---- ListIngestionJobs ----

def test_list_returns_dict():
    j1 = make_job()
    result = ListIngestionJobs(FakeRepo([j1])).execute(role=RoleLabel.ADMIN)
    assert isinstance(result, dict)
    assert result["total"] == 1
    assert result["data"][0].id == j1.id


def test_list_forbidden_for_coach():
    with pytest.raises(InsufficientPrivilege):
        ListIngestionJobs(FakeRepo()).execute(role=RoleLabel.COACH)


def test_list_filter_by_status():
    j1 = make_job(status_label="failed")
    j2 = make_job(status_label="queued")
    result = ListIngestionJobs(FakeRepo([j1, j2])).execute(role=RoleLabel.ADMIN, status_label="failed")
    assert result["total"] == 1
    assert result["data"][0].status_label == "failed"


# ---- CreateIngestionJob ----

def test_create_new_job():
    repo = FakeRepo()
    job, is_dup = CreateIngestionJob(repo).execute(
        role=RoleLabel.ADMIN,
        source_label="video-pipeline",
        ingestion_mode="automated",
    )
    assert is_dup is False
    assert job.status_label == "queued"


def test_create_idempotency_duplicate():
    existing = make_job(idempotency_key="key-abc")
    repo = FakeRepo([existing])
    job, is_dup = CreateIngestionJob(repo).execute(
        role=RoleLabel.ADMIN,
        source_label="video-pipeline",
        ingestion_mode="automated",
        idempotency_key="key-abc",
    )
    assert is_dup is True
    assert job.id == existing.id


def test_create_forbidden_for_athlete():
    with pytest.raises(InsufficientPrivilege):
        CreateIngestionJob(FakeRepo()).execute(
            role=RoleLabel.ATHLETE,
            source_label="s",
            ingestion_mode="m",
        )


# ---- GetIngestionJob ----

def test_get_job_found():
    j = make_job()
    result = GetIngestionJob(FakeRepo([j])).execute(role=RoleLabel.ADMIN, job_id=j.id)
    assert result.id == j.id


def test_get_job_not_found():
    with pytest.raises(IngestionJobNotFound):
        GetIngestionJob(FakeRepo()).execute(role=RoleLabel.ADMIN, job_id=uuid.uuid4())


def test_get_job_forbidden():
    j = make_job()
    with pytest.raises(InsufficientPrivilege):
        GetIngestionJob(FakeRepo([j])).execute(role=RoleLabel.MEMBER, job_id=j.id)


# ---- RetryIngestionJob ----

def test_retry_failed_creates_new_job():
    original = make_job(status_label="failed")
    repo = FakeRepo([original])
    new_job = RetryIngestionJob(repo).execute(role=RoleLabel.ADMIN, job_id=original.id)
    assert new_job.id != original.id
    assert new_job.origin_job_id == original.id
    assert new_job.status_label == "queued"
    assert new_job.idempotency_key is None


def test_retry_queued_raises_conflict():
    j = make_job(status_label="queued")
    with pytest.raises(IngestionJobConflict):
        RetryIngestionJob(FakeRepo([j])).execute(role=RoleLabel.ADMIN, job_id=j.id)


def test_retry_not_found():
    with pytest.raises(IngestionJobNotFound):
        RetryIngestionJob(FakeRepo()).execute(role=RoleLabel.ADMIN, job_id=uuid.uuid4())


def test_retry_forbidden_for_coach():
    j = make_job(status_label="failed")
    with pytest.raises(InsufficientPrivilege):
        RetryIngestionJob(FakeRepo([j])).execute(role=RoleLabel.COACH, job_id=j.id)
