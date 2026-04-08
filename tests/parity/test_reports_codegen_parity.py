from __future__ import annotations

import ast
import uuid
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest

import reports.api as manual_api
import reports.application.use_cases as manual_use_cases
import reports.generated.api as generated_api
import reports.generated.application.use_cases as generated_use_cases
import reports.generated.domain.entities as generated_entities
import reports.generated.schemas as generated_schemas
import reports.schemas as manual_schemas
from reports.domain.entities import ReportJob as ManualReportJob
from reports.domain.rules import ReportJobConflict, ReportJobNotFound, RoleLabel


REPO_ROOT = Path(__file__).resolve().parents[2]
FROZEN_JOB_ID = uuid.UUID("550e8400-e29b-41d4-a716-446655440010")
FROZEN_OWNER_ID = uuid.UUID("550e8400-e29b-41d4-a716-446655440710")
OTHER_OWNER_ID = uuid.UUID("550e8400-e29b-41d4-a716-446655440711")
FROZEN_NOW = datetime(2026, 3, 31, 15, 0, tzinfo=timezone.utc)


class FrozenDateTime:
    @classmethod
    def now(cls, tz=None):
        if tz is None:
            return FROZEN_NOW
        return FROZEN_NOW.astimezone(tz)


class InMemoryRepo:
    def __init__(self, jobs: list[Any] | None = None):
        self.jobs: dict[uuid.UUID, Any] = {}
        for job in jobs or []:
            self.jobs[job.id] = job

    def save(self, job):
        self.jobs[job.id] = job
        return job

    def get_by_id(self, job_id):
        return self.jobs.get(job_id)

    def list_jobs(
        self,
        requester_id=None,
        owner_scoped=False,
        report_type=None,
        format_label=None,
        status_label=None,
        date_from=None,
        date_to=None,
        owner_user_id=None,
        page_size=20,
        page_token=None,
    ):
        items = list(self.jobs.values())
        if owner_scoped and requester_id:
            items = [job for job in items if job.owner_user_id == requester_id]
        if owner_user_id:
            items = [job for job in items if job.owner_user_id == owner_user_id]
        if report_type:
            items = [job for job in items if job.report_type == report_type]
        if format_label:
            items = [job for job in items if job.format_label == format_label]
        if status_label:
            items = [job for job in items if job.status_label == status_label]
        if date_from:
            items = [job for job in items if job.requested_at.date().isoformat() >= date_from]
        if date_to:
            items = [job for job in items if job.requested_at.date().isoformat() <= date_to]
        items = sorted(items, key=lambda job: job.requested_at, reverse=True)
        offset = int(page_token) if page_token and str(page_token).isdigit() else 0
        selected = items[offset: offset + page_size]
        next_token = str(offset + page_size) if (offset + page_size) < len(items) else None
        return selected, next_token


def _make_manual_job(**overrides) -> ManualReportJob:
    payload = {
        "id": FROZEN_JOB_ID,
        "owner_user_id": FROZEN_OWNER_ID,
        "report_type": "training-summary",
        "requested_at": FROZEN_NOW,
        "format_label": "pdf",
        "parameter_summary": "season=2026; team=senior-male",
        "source_metric_names": ["Training Load Trend", "Attendance Rate"],
        "generated_artifact_ref": None,
        "retention_label": "90-days",
        "status_label": "queued",
        "completed_at": None,
        "error_message": None,
    }
    payload.update(overrides)
    return ManualReportJob(**payload)


def _make_generated_job(**overrides) -> generated_entities.ReportJob:
    payload = {
        "id": FROZEN_JOB_ID,
        "owner_user_id": FROZEN_OWNER_ID,
        "report_type": "training-summary",
        "requested_at": FROZEN_NOW,
        "format_label": "pdf",
        "parameter_summary": "season=2026; team=senior-male",
        "source_metric_names": ["Training Load Trend", "Attendance Rate"],
        "generated_artifact_ref": None,
        "retention_label": "90-days",
        "status_label": "queued",
        "completed_at": None,
        "error_message": None,
    }
    payload.update(overrides)
    return generated_entities.ReportJob(**payload)


def _schema_dump(schema_obj: Any) -> dict[str, Any]:
    if hasattr(schema_obj, "model_dump"):
        return schema_obj.model_dump()
    return schema_obj.dict()


def _job_snapshot(job: Any) -> dict[str, Any]:
    return asdict(job)


def _route_surface(path: Path) -> list[dict[str, Any]]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    routes: list[dict[str, Any]] = []
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call):
                continue
            if not isinstance(decorator.func, ast.Attribute):
                continue
            if not isinstance(decorator.func.value, ast.Name) or decorator.func.value.id != "router":
                continue
            route = ast.literal_eval(decorator.args[0])
            responses = {}
            for keyword in decorator.keywords:
                if keyword.arg != "response" or not isinstance(keyword.value, ast.Dict):
                    continue
                for key, value in zip(keyword.value.keys, keyword.value.values):
                    responses[ast.literal_eval(key)] = getattr(value, "id", None)
            routes.append(
                {
                    "function": node.name,
                    "method": decorator.func.attr.upper(),
                    "route": route,
                    "params": [arg.arg for arg in node.args.args[1:]],
                    "responses": responses,
                }
            )
    return routes


def _freeze_codegen_time_and_uuid(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(manual_use_cases.uuid, "uuid4", lambda: FROZEN_JOB_ID)
    monkeypatch.setattr(generated_use_cases.uuid, "uuid4", lambda: FROZEN_JOB_ID)
    monkeypatch.setattr(manual_use_cases, "datetime", FrozenDateTime)
    monkeypatch.setattr(generated_use_cases, "datetime", FrozenDateTime)


def test_reports_codegen_http_surface_matches_manual_api():
    manual_routes = _route_surface(REPO_ROOT / "src" / "reports" / "api.py")
    generated_routes = _route_surface(REPO_ROOT / "src" / "reports" / "generated" / "api.py")
    assert generated_routes == manual_routes


def test_reports_codegen_schema_serialization_matches_manual_schema():
    manual_payload = _schema_dump(manual_schemas.ReportJobOut.from_domain(_make_manual_job()))
    generated_payload = _schema_dump(generated_schemas.ReportJobOut.from_domain(_make_generated_job()))
    assert generated_payload == manual_payload


def test_reports_codegen_create_and_list_use_cases_match_manual(monkeypatch: pytest.MonkeyPatch):
    _freeze_codegen_time_and_uuid(monkeypatch)

    manual_repo = InMemoryRepo()
    generated_repo = InMemoryRepo()
    manual_create = manual_use_cases.CreateReportJob(manual_repo)
    generated_create = generated_use_cases.CreateReportJob(generated_repo)

    manual_job = manual_create.execute(
        role=RoleLabel.COACH,
        requester_id=FROZEN_OWNER_ID,
        report_type="training-summary",
        format_label="pdf",
        parameter_summary="season=2026; team=senior-male",
        source_metric_names=["Training Load Trend", "Attendance Rate"],
        retention_label="90-days",
    )
    generated_job = generated_create.execute(
        role=RoleLabel.COACH,
        requester_id=FROZEN_OWNER_ID,
        report_type="training-summary",
        format_label="pdf",
        parameter_summary="season=2026; team=senior-male",
        source_metric_names=["Training Load Trend", "Attendance Rate"],
        retention_label="90-days",
    )

    assert _job_snapshot(generated_job) == _job_snapshot(manual_job)

    manual_repo.save(_make_manual_job(id=uuid.uuid4(), owner_user_id=OTHER_OWNER_ID, requested_at=FROZEN_NOW.replace(hour=14)))
    generated_repo.save(
        _make_generated_job(id=uuid.uuid4(), owner_user_id=OTHER_OWNER_ID, requested_at=FROZEN_NOW.replace(hour=14))
    )

    manual_list = manual_use_cases.ListReportJobs(manual_repo)
    generated_list = generated_use_cases.ListReportJobs(generated_repo)

    manual_jobs, manual_next = manual_list.execute(
        role=RoleLabel.COACH,
        requester_id=FROZEN_OWNER_ID,
        page_size=10,
    )
    generated_jobs, generated_next = generated_list.execute(
        role=RoleLabel.COACH,
        requester_id=FROZEN_OWNER_ID,
        page_size=10,
    )

    assert [_job_snapshot(job) for job in generated_jobs] == [_job_snapshot(job) for job in manual_jobs]
    assert generated_next == manual_next


def test_reports_codegen_get_and_update_positive_paths_match_manual(monkeypatch: pytest.MonkeyPatch):
    _freeze_codegen_time_and_uuid(monkeypatch)

    manual_repo = InMemoryRepo([_make_manual_job()])
    generated_repo = InMemoryRepo([_make_generated_job()])

    manual_get = manual_use_cases.GetReportJob(manual_repo)
    generated_get = generated_use_cases.GetReportJob(generated_repo)
    assert _job_snapshot(generated_get.execute(RoleLabel.COACH, FROZEN_OWNER_ID, FROZEN_JOB_ID)) == _job_snapshot(
        manual_get.execute(RoleLabel.COACH, FROZEN_OWNER_ID, FROZEN_JOB_ID)
    )

    manual_update = manual_use_cases.UpdateReportJob(manual_repo)
    generated_update = generated_use_cases.UpdateReportJob(generated_repo)

    manual_updated = manual_update.execute(
        role=RoleLabel.COACH,
        requester_id=FROZEN_OWNER_ID,
        job_id=FROZEN_JOB_ID,
        status_label="cancelled",
    )
    generated_updated = generated_update.execute(
        role=RoleLabel.COACH,
        requester_id=FROZEN_OWNER_ID,
        job_id=FROZEN_JOB_ID,
        status_label="cancelled",
    )

    assert _job_snapshot(generated_updated) == _job_snapshot(manual_updated)


def test_reports_codegen_negative_paths_match_manual():
    manual_repo = InMemoryRepo([_make_manual_job(status_label="completed")])
    generated_repo = InMemoryRepo([_make_generated_job(status_label="completed")])

    manual_update = manual_use_cases.UpdateReportJob(manual_repo)
    generated_update = generated_use_cases.UpdateReportJob(generated_repo)

    with pytest.raises(ReportJobConflict) as manual_exc:
        manual_update.execute(RoleLabel.COACH, FROZEN_OWNER_ID, FROZEN_JOB_ID, status_label="cancelled")
    with pytest.raises(ReportJobConflict) as generated_exc:
        generated_update.execute(RoleLabel.COACH, FROZEN_OWNER_ID, FROZEN_JOB_ID, status_label="cancelled")
    assert str(generated_exc.value) == str(manual_exc.value)

    with pytest.raises(ReportJobNotFound) as manual_not_found:
        manual_use_cases.GetReportJob(InMemoryRepo()).execute(RoleLabel.ADMIN, FROZEN_OWNER_ID, FROZEN_JOB_ID)
    with pytest.raises(ReportJobNotFound) as generated_not_found:
        generated_use_cases.GetReportJob(InMemoryRepo()).execute(RoleLabel.ADMIN, FROZEN_OWNER_ID, FROZEN_JOB_ID)
    assert str(generated_not_found.value) == str(manual_not_found.value)

    with pytest.raises(ReportJobConflict) as manual_download_exc:
        manual_use_cases.DownloadReportArtifact(InMemoryRepo([_make_manual_job(status_label="queued")])).execute(
            RoleLabel.COACH,
            FROZEN_OWNER_ID,
            FROZEN_JOB_ID,
        )
    with pytest.raises(ReportJobConflict) as generated_download_exc:
        generated_use_cases.DownloadReportArtifact(InMemoryRepo([_make_generated_job(status_label="queued")])).execute(
            RoleLabel.COACH,
            FROZEN_OWNER_ID,
            FROZEN_JOB_ID,
        )
    assert str(generated_download_exc.value) == str(manual_download_exc.value)
