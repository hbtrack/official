from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


GENERATOR_NAME = "hbtrack_backend_codegen"
GENERATOR_VERSION = "0.1.0"
SUPPORTED_MODULES = {"reports"}
REPORTS_REQUIRED_RUNTIME_FIELDS = ("requestedAt",)
REPORTS_CANCELLABLE_STATUSES = ("queued", "processing")


@dataclass(frozen=True)
class ExpectedFile:
    relpath: str
    content: str


class BackendCodegenError(RuntimeError):
    def __init__(self, summary: str):
        super().__init__(summary)
        self.summary = summary


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / ".git").exists():
            return parent
        if (parent / "docs").exists() and (parent / ".contract_driven").exists():
            return parent
    return here.parents[2]


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise BackendCodegenError(f"Arquivo YAML ausente: {path}")
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise BackendCodegenError(f"YAML inválido (esperado objeto): {path}")
    return payload


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise BackendCodegenError(f"Arquivo JSON ausente: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise BackendCodegenError(f"JSON inválido (esperado objeto): {path}")
    return payload


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _render_list_literal(values: list[str] | tuple[str, ...]) -> str:
    return ", ".join(f'"{value}"' for value in values)


def _python_type(field_type: str) -> str:
    mapping = {
        "uuid_v4": "UUID",
        "timestamp_utc": "datetime",
        "string": "str",
        "string[]": "List[str]",
        "enum": "str",
    }
    try:
        return mapping[field_type]
    except KeyError as exc:
        raise BackendCodegenError(f"Tipo não suportado no codegen backend: {field_type}") from exc


def _python_type_from_json_schema(schema: dict[str, Any]) -> str:
    schema_type = schema.get("type")
    schema_format = schema.get("format")
    if schema_format == "uuid":
        return "UUID"
    if schema_format in {"date-time", "date"}:
        return "str"
    if schema_type == "string":
        return "str"
    if schema_type == "integer":
        return "int"
    if schema_type == "number":
        return "float"
    if schema_type == "boolean":
        return "bool"
    if schema_type == "array":
        item_schema = schema.get("items") or {}
        return f"List[{_python_type_from_json_schema(item_schema)}]"
    raise BackendCodegenError(f"Tipo OpenAPI não suportado: {schema}")


def _format_output_field_lines(
    sovereign_fields: list[dict[str, Any]],
    runtime_fields: list[dict[str, Any]],
    runtime_required_names: set[str],
) -> list[str]:
    lines: list[str] = []
    for field in sovereign_fields:
        field_name = field["runtime_name"]
        annotation = _python_type(field["type"])
        if field["name"] in REPORTS_REQUIRED_RUNTIME_FIELDS or field.get("required"):
            lines.append(f"    {field_name}: {annotation}")
        else:
            lines.append(f"    {field_name}: Optional[{annotation}] = None")
    for field in runtime_fields:
        field_name = field["runtime_name"]
        annotation = _python_type(field["type"])
        if field["name"] in runtime_required_names:
            lines.append(f"    {field_name}: {annotation}")
        else:
            lines.append(f"    {field_name}: Optional[{annotation}] = None")
    return lines


def _format_domain_field_lines(
    sovereign_fields: list[dict[str, Any]],
    runtime_fields: list[dict[str, Any]],
    runtime_required_names: set[str],
) -> list[str]:
    required_lines: list[str] = []
    optional_lines: list[str] = []
    for field in sovereign_fields:
        field_name = field["runtime_name"]
        annotation = _python_type(field["type"])
        if field["name"] in REPORTS_REQUIRED_RUNTIME_FIELDS or field.get("required"):
            required_lines.append(f"    {field_name}: {annotation}")
        elif field["type"] == "string[]":
            optional_lines.append(f"    {field_name}: {annotation} = field(default_factory=list)")
        else:
            optional_lines.append(f"    {field_name}: Optional[{annotation}] = None")
    for field in runtime_fields:
        field_name = field["runtime_name"]
        annotation = _python_type(field["type"])
        if field["name"] == "statusLabel":
            default = field.get("allowed_values", ["queued"])[0]
            optional_lines.append(f'    {field_name}: {annotation} = "{default}"')
        elif field["name"] in runtime_required_names:
            required_lines.append(f"    {field_name}: {annotation}")
        else:
            optional_lines.append(f"    {field_name}: Optional[{annotation}] = None")
    return required_lines + optional_lines


def _format_from_domain_lines(
    sovereign_fields: list[dict[str, Any]],
    runtime_fields: list[dict[str, Any]],
) -> list[str]:
    lines: list[str] = []
    for field in sovereign_fields:
        lines.append(f"            {field['runtime_name']}=job.{field['runtime_name']},")
    for field in runtime_fields:
        lines.append(f"            {field['runtime_name']}=job.{field['runtime_name']},")
    return lines


def _load_codegen_inputs(root: Path, module: str) -> dict[str, Any]:
    if module not in SUPPORTED_MODULES:
        raise BackendCodegenError(
            f"Módulo `{module}` não suportado por {GENERATOR_NAME}. "
            f"Suportados nesta fase: {sorted(SUPPORTED_MODULES)}."
        )

    source_graph_root = root / "generated" / "source_graph" / module
    bundle = _load_yaml(source_graph_root / f"{module}.bundle.yaml")
    schema_view = _load_yaml(source_graph_root / f"{module}.schema_contract_view.yaml")
    openapi_view = _load_yaml(source_graph_root / f"{module}.openapi_contract_view.yaml")
    impact_report = _load_json(source_graph_root / "impact_report.json")
    openapi_paths = _load_yaml(root / openapi_view["openapi_paths_ref"])

    if schema_view.get("module") != module or openapi_view.get("module") != module:
        raise BackendCodegenError("Artefatos compilados do source graph divergentes do módulo alvo.")

    return {
        "bundle": bundle,
        "schema_view": schema_view,
        "openapi_view": openapi_view,
        "impact_report": impact_report,
        "openapi_paths": openapi_paths,
    }


def _runtime_required_names(openapi_paths: dict[str, Any]) -> set[str]:
    required_names: set[str] = set()
    for path_item in openapi_paths.values():
        if not isinstance(path_item, dict):
            continue
        for operation in path_item.values():
            if not isinstance(operation, dict):
                continue
            for response in (operation.get("responses") or {}).values():
                content = ((response or {}).get("content") or {}).get("application/json")
                schema = (content or {}).get("schema")
                if not isinstance(schema, dict):
                    continue
                for item in schema.get("allOf", []):
                    if isinstance(item, dict):
                        for name in item.get("required", []) or []:
                            required_names.add(name)
    return required_names


def _render_header(*, module: str, source_fingerprint: str) -> list[str]:
    return [
        "# Auto-generated by scripts/generate/backend_codegen.py.",
        "# DO NOT EDIT MANUALLY.",
        f"# generator: {GENERATOR_NAME}@{GENERATOR_VERSION}",
        f"# module: {module}",
        f"# source_fingerprint: {source_fingerprint}",
        "",
    ]


def _build_reports_schemas(inputs: dict[str, Any]) -> str:
    schema_view = inputs["schema_view"]
    openapi_paths = inputs["openapi_paths"]
    source_fingerprint = inputs["impact_report"]["source_fingerprint"]
    report_path = openapi_paths["/reports/jobs"]
    create_schema = report_path["post"]["requestBody"]["content"]["application/json"]["schema"]
    update_schema = openapi_paths["/reports/jobs/{jobId}"]["patch"]["requestBody"]["content"]["application/json"]["schema"]

    runtime_required_names = _runtime_required_names(openapi_paths)
    output_lines = _format_output_field_lines(
        schema_view["sovereign_fields"],
        schema_view["runtime_extension_fields"],
        runtime_required_names,
    )
    from_domain_lines = _format_from_domain_lines(
        schema_view["sovereign_fields"],
        schema_view["runtime_extension_fields"],
    )

    create_lines: list[str] = []
    for name, field_schema in create_schema["properties"].items():
        annotation = _python_type_from_json_schema(field_schema)
        required = name in set(create_schema.get("required") or [])
        if required and "default" not in field_schema:
            create_lines.append(f"    {name}: {annotation}")
        elif "default" in field_schema:
            create_lines.append(f'    {name}: {annotation} = "{field_schema["default"]}"')
        else:
            create_lines.append(f"    {name}: Optional[{annotation}] = None")

    update_lines: list[str] = []
    for name, field_schema in update_schema["properties"].items():
        annotation = _python_type_from_json_schema(field_schema)
        update_lines.append(f"    {name}: Optional[{annotation}] = None")

    lines = _render_header(module="reports", source_fingerprint=source_fingerprint)
    lines += [
        "from __future__ import annotations",
        "",
        "from datetime import datetime",
        "from typing import List, Optional",
        "from uuid import UUID",
        "",
        "from ninja import Schema",
        "",
        "",
        "class ReportJobOut(Schema):",
        *output_lines,
        "",
        '    @classmethod',
        '    def from_domain(cls, job) -> "ReportJobOut":',
        "        return cls(",
        *from_domain_lines,
        "        )",
        "",
        "",
        "class ReportJobListOut(Schema):",
        "    data: List[ReportJobOut]",
        "    nextPageToken: Optional[str] = None",
        "",
        "",
        "class CreateReportJobIn(Schema):",
        *create_lines,
        "",
        "",
        "class UpdateReportJobIn(Schema):",
        *update_lines,
        "",
        "",
        "class ErrorOut(Schema):",
        "    detail: str",
        "",
    ]
    return "\n".join(lines)


def _build_reports_entities(inputs: dict[str, Any]) -> str:
    schema_view = inputs["schema_view"]
    openapi_paths = inputs["openapi_paths"]
    source_fingerprint = inputs["impact_report"]["source_fingerprint"]
    runtime_required_names = _runtime_required_names(openapi_paths)
    format_values = tuple(
        openapi_paths["/reports/jobs"]["post"]["requestBody"]["content"]["application/json"]["schema"]["properties"]["formatLabel"]["enum"]
    )
    status_values = tuple(schema_view["runtime_extension_fields"][0]["allowed_values"])

    lines = _render_header(module="reports", source_fingerprint=source_fingerprint)
    lines += [
        "from __future__ import annotations",
        "",
        "from dataclasses import dataclass, field",
        "from datetime import datetime",
        "from typing import List, Optional",
        "from uuid import UUID",
        "",
        f"VALID_FORMATS = frozenset([{_render_list_literal(format_values)}])",
        f"VALID_STATUSES = frozenset([{_render_list_literal(status_values)}])",
        f"CANCELLABLE_STATUSES = frozenset([{_render_list_literal(REPORTS_CANCELLABLE_STATUSES)}])",
        "",
        "",
        "@dataclass",
        "class ReportJob:",
        *_format_domain_field_lines(
            schema_view["sovereign_fields"],
            schema_view["runtime_extension_fields"],
            runtime_required_names,
        ),
        "",
        "    def validate_invariants(self) -> None:",
        "        if not self.id:",
        '            raise ValueError("INV-RPT-001: id is required")',
        "        if not self.owner_user_id:",
        '            raise ValueError("INV-RPT-001: ownerUserId is required")',
        "        if not self.report_type:",
        '            raise ValueError("INV-RPT-001: reportType is required")',
        "        if not self.requested_at:",
        '            raise ValueError("INV-RPT-003: requestedAt is required")',
        "        if len(self.source_metric_names) != len(set(self.source_metric_names)):",
        '            raise ValueError("INV-RPT-002: sourceMetricNames must be unique")',
        "        if self.generated_artifact_ref and not self.retention_label:",
        '            raise ValueError("INV-RPT-004: retentionLabel required when generatedArtifactRef is set")',
        "",
        "    def can_be_cancelled(self) -> bool:",
        "        return self.status_label in CANCELLABLE_STATUSES",
        "",
        "    def can_be_updated(self) -> bool:",
        '        return self.status_label == "queued"',
        "",
    ]
    return "\n".join(lines)


def _build_reports_repository(inputs: dict[str, Any]) -> str:
    source_fingerprint = inputs["impact_report"]["source_fingerprint"]
    lines = _render_header(module="reports", source_fingerprint=source_fingerprint)
    lines += [
        "from __future__ import annotations",
        "",
        "from typing import List, Optional, Tuple",
        "from uuid import UUID",
        "",
        "from ...infrastructure.models import ReportJobModel",
        "from ..domain.entities import ReportJob",
        "",
        "",
        "def _job_from_model(model: ReportJobModel) -> ReportJob:",
        "    return ReportJob(",
        "        id=model.id,",
        "        owner_user_id=model.owner_user_id,",
        "        report_type=model.report_type,",
        "        format_label=model.format_label,",
        "        parameter_summary=model.parameter_summary,",
        "        source_metric_names=model.source_metric_names or [],",
        "        generated_artifact_ref=model.generated_artifact_ref,",
        "        retention_label=model.retention_label,",
        "        status_label=model.status_label,",
        "        requested_at=model.requested_at,",
        "        completed_at=model.completed_at,",
        "        error_message=model.error_message,",
        "    )",
        "",
        "",
        "class ReportJobRepository:",
        "    def save(self, job: ReportJob) -> ReportJob:",
        "        obj, _ = ReportJobModel.objects.update_or_create(",
        "            id=job.id,",
        "            defaults={",
        '                "owner_user_id": job.owner_user_id,',
        '                "report_type": job.report_type,',
        '                "format_label": job.format_label,',
        '                "parameter_summary": job.parameter_summary,',
        '                "source_metric_names": job.source_metric_names,',
        '                "generated_artifact_ref": job.generated_artifact_ref,',
        '                "retention_label": job.retention_label,',
        '                "status_label": job.status_label,',
        '                "requested_at": job.requested_at,',
        '                "completed_at": job.completed_at,',
        '                "error_message": job.error_message,',
        "            },",
        "        )",
        "        return _job_from_model(obj)",
        "",
        "    def get_by_id(self, job_id: UUID) -> Optional[ReportJob]:",
        "        try:",
        "            return _job_from_model(ReportJobModel.objects.get(id=job_id))",
        "        except ReportJobModel.DoesNotExist:",
        "            return None",
        "",
        "    def list_jobs(",
        "        self,",
        "        requester_id: Optional[UUID] = None,",
        "        owner_scoped: bool = False,",
        "        report_type: Optional[str] = None,",
        "        format_label: Optional[str] = None,",
        "        status_label: Optional[str] = None,",
        "        date_from: Optional[str] = None,",
        "        date_to: Optional[str] = None,",
        "        owner_user_id: Optional[UUID] = None,",
        "        page_size: int = 20,",
        "        page_token: Optional[str] = None,",
        "    ) -> Tuple[List[ReportJob], Optional[str]]:",
        "        qs = ReportJobModel.objects.all()",
        "        if owner_scoped and requester_id:",
        "            qs = qs.filter(owner_user_id=requester_id)",
        "        if owner_user_id:",
        "            qs = qs.filter(owner_user_id=owner_user_id)",
        "        if report_type:",
        "            qs = qs.filter(report_type=report_type)",
        "        if format_label:",
        "            qs = qs.filter(format_label=format_label)",
        "        if status_label:",
        "            qs = qs.filter(status_label=status_label)",
        "        if date_from:",
        "            qs = qs.filter(requested_at__date__gte=date_from)",
        "        if date_to:",
        "            qs = qs.filter(requested_at__date__lte=date_to)",
        "",
        "        offset = 0",
        "        if page_token:",
        "            try:",
        "                offset = int(page_token)",
        "            except ValueError:",
        "                offset = 0",
        "",
        "        total = qs.count()",
        "        items = qs[offset: offset + page_size]",
        "        jobs = [_job_from_model(model) for model in items]",
        '        next_token = str(offset + page_size) if (offset + page_size) < total else None',
        "        return jobs, next_token",
        "",
    ]
    return "\n".join(lines)


def _build_reports_use_cases(inputs: dict[str, Any]) -> str:
    source_fingerprint = inputs["impact_report"]["source_fingerprint"]
    lines = _render_header(module="reports", source_fingerprint=source_fingerprint)
    lines += [
        "from __future__ import annotations",
        "",
        "import uuid",
        "from datetime import datetime, timezone",
        "from typing import List, Optional, Tuple",
        "from uuid import UUID",
        "",
        "from ...domain.rules import (",
        "    MANAGER_ROLES,",
        "    InsufficientPrivilege,",
        "    ReportJobConflict,",
        "    ReportJobNotFound,",
        "    RoleLabel,",
        "    assert_can_access_job,",
        "    assert_can_create_job,",
        "    assert_can_download,",
        "    assert_can_list_jobs,",
        "    assert_can_update_job,",
        ")",
        "from ..domain.entities import ReportJob",
        "from ..infrastructure.repository import ReportJobRepository",
        "",
        "",
        "class ListReportJobs:",
        "    def __init__(self, repo: ReportJobRepository):",
        "        self.repo = repo",
        "",
        "    def execute(",
        "        self,",
        "        role: RoleLabel,",
        "        requester_id: UUID,",
        "        report_type: Optional[str] = None,",
        "        format_label: Optional[str] = None,",
        "        status_label: Optional[str] = None,",
        "        date_from: Optional[str] = None,",
        "        date_to: Optional[str] = None,",
        "        owner_user_id: Optional[UUID] = None,",
        "        page_size: int = 20,",
        "        page_token: Optional[str] = None,",
        "    ) -> Tuple[List[ReportJob], Optional[str]]:",
        "        assert_can_list_jobs(role)",
        "        owner_scoped = role not in MANAGER_ROLES",
        "        resolved_owner = owner_user_id if role in MANAGER_ROLES else None",
        "        return self.repo.list_jobs(",
        "            requester_id=requester_id,",
        "            owner_scoped=owner_scoped,",
        "            report_type=report_type,",
        "            format_label=format_label,",
        "            status_label=status_label,",
        "            date_from=date_from,",
        "            date_to=date_to,",
        "            owner_user_id=resolved_owner,",
        "            page_size=page_size,",
        "            page_token=page_token,",
        "        )",
        "",
        "",
        "class CreateReportJob:",
        "    def __init__(self, repo: ReportJobRepository):",
        "        self.repo = repo",
        "",
        "    def execute(",
        "        self,",
        "        role: RoleLabel,",
        "        requester_id: UUID,",
        "        report_type: str,",
        "        format_label: str,",
        "        parameter_summary: str,",
        "        source_metric_names: Optional[List[str]] = None,",
        '        retention_label: str = "90-days",',
        "    ) -> ReportJob:",
        "        assert_can_create_job(role)",
        "        job = ReportJob(",
        "            id=uuid.uuid4(),",
        "            owner_user_id=requester_id,",
        "            report_type=report_type,",
        "            format_label=format_label,",
        "            parameter_summary=parameter_summary,",
        "            source_metric_names=source_metric_names or [],",
        "            retention_label=retention_label,",
        '            status_label="queued",',
        "            requested_at=datetime.now(timezone.utc),",
        "        )",
        "        job.validate_invariants()",
        "        return self.repo.save(job)",
        "",
        "",
        "class GetReportJob:",
        "    def __init__(self, repo: ReportJobRepository):",
        "        self.repo = repo",
        "",
        "    def execute(self, role: RoleLabel, requester_id: UUID, job_id: UUID) -> ReportJob:",
        "        job = self.repo.get_by_id(job_id)",
        "        if job is None:",
        '            raise ReportJobNotFound(f"ReportJob {job_id} not found")',
        "        assert_can_access_job(role, job, requester_id)",
        "        return job",
        "",
        "",
        "class UpdateReportJob:",
        "    def __init__(self, repo: ReportJobRepository):",
        "        self.repo = repo",
        "",
        "    def execute(",
        "        self,",
        "        role: RoleLabel,",
        "        requester_id: UUID,",
        "        job_id: UUID,",
        "        status_label: Optional[str] = None,",
        "        retention_label: Optional[str] = None,",
        "    ) -> ReportJob:",
        "        job = self.repo.get_by_id(job_id)",
        "        if job is None:",
        '            raise ReportJobNotFound(f"ReportJob {job_id} not found")',
        "        assert_can_update_job(role, job, requester_id)",
        '        if status_label == "cancelled":',
        "            if not job.can_be_cancelled():",
        "                raise ReportJobConflict(",
        '                    f"PERM-REP-003: job in status \'{job.status_label}\' cannot be cancelled"',
        "                )",
        '            job.status_label = "cancelled"',
        "            job.completed_at = datetime.now(timezone.utc)",
        "        if retention_label is not None:",
        "            job.retention_label = retention_label",
        "        job.validate_invariants()",
        "        return self.repo.save(job)",
        "",
        "",
        "class DownloadReportArtifact:",
        "    def __init__(self, repo: ReportJobRepository):",
        "        self.repo = repo",
        "",
        "    def execute(self, role: RoleLabel, requester_id: UUID, job_id: UUID) -> ReportJob:",
        "        job = self.repo.get_by_id(job_id)",
        "        if job is None:",
        '            raise ReportJobNotFound(f"ReportJob {job_id} not found")',
        "        assert_can_download(role, job, requester_id)",
        '        if job.status_label != "completed":',
        "            raise ReportJobConflict(",
        '                "downloadReportArtifact: artifact only available for completed jobs"',
        "            )",
        "        return job",
        "",
    ]
    return "\n".join(lines)


def _build_reports_api(inputs: dict[str, Any]) -> str:
    source_fingerprint = inputs["impact_report"]["source_fingerprint"]
    lines = _render_header(module="reports", source_fingerprint=source_fingerprint)
    lines += [
        "from __future__ import annotations",
        "",
        "from typing import Optional",
        "from uuid import UUID",
        "",
        "from django.http import HttpRequest",
        "from ninja import Router",
        "from ninja.errors import HttpError",
        "",
        "from ..domain.rules import InsufficientPrivilege, ReportJobConflict, ReportJobNotFound, RoleLabel",
        "from .application.use_cases import (",
        "    CreateReportJob,",
        "    DownloadReportArtifact,",
        "    GetReportJob,",
        "    ListReportJobs,",
        "    UpdateReportJob,",
        ")",
        "from .infrastructure.repository import ReportJobRepository",
        "from .schemas import CreateReportJobIn, ErrorOut, ReportJobListOut, ReportJobOut, UpdateReportJobIn",
        "",
        "router = Router()",
        "_repo = ReportJobRepository()",
        "_list_uc = ListReportJobs(_repo)",
        "_create_uc = CreateReportJob(_repo)",
        "_get_uc = GetReportJob(_repo)",
        "_update_uc = UpdateReportJob(_repo)",
        "_download_uc = DownloadReportArtifact(_repo)",
        "",
        "",
        "def _role(request: HttpRequest) -> RoleLabel:",
        '    """Extrai RoleLabel do JWT validado."""',
        '    role = getattr(request, "_actor_role", None)',
        "    if role:",
        "        try:",
        "            return RoleLabel(role)",
        "        except ValueError:",
        "            return RoleLabel.MEMBER",
        '    raise HttpError(401, "Unauthenticated")',
        "",
        "",
        "def _uid(request: HttpRequest) -> UUID:",
        '    """Extrai actor_id do JWT validado."""',
        '    actor_id = getattr(request, "_actor_id", None)',
        "    if actor_id:",
        "        return UUID(str(actor_id))",
        '    raise HttpError(401, "Unauthenticated")',
        "",
        "",
        "@router.get('/jobs', response={200: ReportJobListOut, 401: ErrorOut, 403: ErrorOut, 422: ErrorOut})",
        "def list_report_jobs(",
        "    request: HttpRequest,",
        "    reportType: Optional[str] = None,",
        "    formatLabel: Optional[str] = None,",
        "    statusLabel: Optional[str] = None,",
        "    dateFrom: Optional[str] = None,",
        "    dateTo: Optional[str] = None,",
        "    ownerUserId: Optional[UUID] = None,",
        "    pageSize: int = 20,",
        "    pageToken: Optional[str] = None,",
        "):",
        "    try:",
        "        role = _role(request)",
        "        requester_id = _uid(request)",
        "        jobs, next_token = _list_uc.execute(",
        "            role=role,",
        "            requester_id=requester_id,",
        "            report_type=reportType,",
        "            format_label=formatLabel,",
        "            status_label=statusLabel,",
        "            date_from=dateFrom,",
        "            date_to=dateTo,",
        "            owner_user_id=ownerUserId,",
        "            page_size=pageSize,",
        "            page_token=pageToken,",
        "        )",
        "        return 200, ReportJobListOut(",
        "            data=[ReportJobOut.from_domain(job) for job in jobs],",
        "            nextPageToken=next_token,",
        "        )",
        "    except InsufficientPrivilege as exc:",
        "        return 403, ErrorOut(detail=str(exc))",
        "    except ValueError as exc:",
        "        return 422, ErrorOut(detail=str(exc))",
        "",
        "",
        "@router.post('/jobs', response={201: ReportJobOut, 400: ErrorOut, 401: ErrorOut, 403: ErrorOut, 422: ErrorOut})",
        "def create_report_job(request: HttpRequest, payload: CreateReportJobIn):",
        "    try:",
        "        role = _role(request)",
        "        requester_id = _uid(request)",
        "        job = _create_uc.execute(",
        "            role=role,",
        "            requester_id=requester_id,",
        "            report_type=payload.reportType,",
        "            format_label=payload.formatLabel,",
        "            parameter_summary=payload.parameterSummary,",
        "            source_metric_names=payload.sourceMetricNames,",
        "            retention_label=payload.retentionLabel,",
        "        )",
        "        return 201, ReportJobOut.from_domain(job)",
        "    except InsufficientPrivilege as exc:",
        "        return 403, ErrorOut(detail=str(exc))",
        "    except ValueError as exc:",
        "        return 422, ErrorOut(detail=str(exc))",
        "",
        "",
        "@router.get('/jobs/{job_id}', response={200: ReportJobOut, 401: ErrorOut, 403: ErrorOut, 404: ErrorOut})",
        "def get_report_job(request: HttpRequest, job_id: UUID):",
        "    try:",
        "        role = _role(request)",
        "        requester_id = _uid(request)",
        "        job = _get_uc.execute(role=role, requester_id=requester_id, job_id=job_id)",
        "        return 200, ReportJobOut.from_domain(job)",
        "    except ReportJobNotFound as exc:",
        "        return 404, ErrorOut(detail=str(exc))",
        "    except InsufficientPrivilege as exc:",
        "        return 403, ErrorOut(detail=str(exc))",
        "",
        "",
        "@router.patch('/jobs/{job_id}', response={200: ReportJobOut, 400: ErrorOut, 401: ErrorOut, 403: ErrorOut, 404: ErrorOut, 409: ErrorOut, 422: ErrorOut})",
        "def update_report_job(request: HttpRequest, job_id: UUID, payload: UpdateReportJobIn):",
        "    try:",
        "        role = _role(request)",
        "        requester_id = _uid(request)",
        "        job = _update_uc.execute(",
        "            role=role,",
        "            requester_id=requester_id,",
        "            job_id=job_id,",
        "            status_label=payload.statusLabel,",
        "            retention_label=payload.retentionLabel,",
        "        )",
        "        return 200, ReportJobOut.from_domain(job)",
        "    except ReportJobNotFound as exc:",
        "        return 404, ErrorOut(detail=str(exc))",
        "    except ReportJobConflict as exc:",
        "        return 409, ErrorOut(detail=str(exc))",
        "    except InsufficientPrivilege as exc:",
        "        return 403, ErrorOut(detail=str(exc))",
        "    except ValueError as exc:",
        "        return 422, ErrorOut(detail=str(exc))",
        "",
        "",
        "@router.get('/jobs/{job_id}/download', response={200: ReportJobOut, 401: ErrorOut, 403: ErrorOut, 404: ErrorOut, 409: ErrorOut})",
        "def download_report_artifact(request: HttpRequest, job_id: UUID):",
        "    try:",
        "        role = _role(request)",
        "        requester_id = _uid(request)",
        "        job = _download_uc.execute(role=role, requester_id=requester_id, job_id=job_id)",
        "        return 200, ReportJobOut.from_domain(job)",
        "    except ReportJobNotFound as exc:",
        "        return 404, ErrorOut(detail=str(exc))",
        "    except ReportJobConflict as exc:",
        "        return 409, ErrorOut(detail=str(exc))",
        "    except InsufficientPrivilege as exc:",
        "        return 403, ErrorOut(detail=str(exc))",
        "",
    ]
    return "\n".join(lines)


def _build_reports_generated_test(inputs: dict[str, Any]) -> str:
    source_fingerprint = inputs["impact_report"]["source_fingerprint"]
    lines = _render_header(module="reports", source_fingerprint=source_fingerprint)
    lines += [
        "from __future__ import annotations",
        "",
        "import uuid",
        "from datetime import datetime, timezone",
        "",
        "import pytest",
        "",
        "from reports.generated.domain.entities import ReportJob",
        "from reports.generated.schemas import ReportJobOut",
        "",
        "",
        "def _make_job(**overrides):",
        "    payload = {",
        '        "id": uuid.uuid4(),',
        '        "owner_user_id": uuid.uuid4(),',
        '        "report_type": "training-summary",',
        '        "requested_at": datetime.now(timezone.utc),',
        '        "completed_at": datetime.now(timezone.utc),',
        '        "format_label": "pdf",',
        '        "parameter_summary": "season=2026; team=senior-male",',
        '        "source_metric_names": ["Training Load Trend", "Attendance Rate"],',
        '        "retention_label": "90-days",',
        '        "status_label": "queued",',
        "    }",
        "    payload.update(overrides)",
        "    return ReportJob(**payload)",
        "",
        "",
        "def test_generated_report_job_validates_invariants():",
        "    job = _make_job()",
        "    job.validate_invariants()",
        "",
        "",
        "def test_generated_report_job_rejects_duplicate_metrics():",
        '    job = _make_job(source_metric_names=["Load", "Load"])',
        '    with pytest.raises(ValueError, match="INV-RPT-002"):',
        "        job.validate_invariants()",
        "",
        "",
        "def test_generated_report_job_out_from_domain_maps_runtime_extensions():",
        '    job = _make_job(status_label="completed", error_message="none")',
        "    payload = ReportJobOut.from_domain(job)",
        "    assert payload.id == job.id",
        '    assert payload.status_label == "completed"',
        '    assert payload.error_message == "none"',
        "",
    ]
    return "\n".join(lines)


def _expected_files(root: Path, module: str) -> list[ExpectedFile]:
    inputs = _load_codegen_inputs(root, module)
    return [
        ExpectedFile(
            relpath=f"src/{module}/generated/schemas.py",
            content=_build_reports_schemas(inputs),
        ),
        ExpectedFile(
            relpath=f"src/{module}/generated/api.py",
            content=_build_reports_api(inputs),
        ),
        ExpectedFile(
            relpath=f"src/{module}/generated/domain/entities.py",
            content=_build_reports_entities(inputs),
        ),
        ExpectedFile(
            relpath=f"src/{module}/generated/application/use_cases.py",
            content=_build_reports_use_cases(inputs),
        ),
        ExpectedFile(
            relpath=f"src/{module}/generated/infrastructure/repository.py",
            content=_build_reports_repository(inputs),
        ),
        ExpectedFile(
            relpath=f"src/{module}/generated/tests/test_codegen_contract.py",
            content=_build_reports_generated_test(inputs),
        ),
    ]


def _materialize(root: Path, expected_files: list[ExpectedFile], check: bool) -> dict[str, Any]:
    drifts: list[dict[str, Any]] = []
    files: list[dict[str, str]] = []

    for expected in expected_files:
        target = root / expected.relpath
        existing = target.read_text(encoding="utf-8") if target.exists() else None
        file_sha = _sha256_text(expected.content)
        files.append({"relpath": expected.relpath, "sha256": file_sha})

        if check:
            if existing != expected.content:
                drifts.append({"relpath": expected.relpath, "expected_sha256": file_sha})
            continue

        target.parent.mkdir(parents=True, exist_ok=True)
        if existing != expected.content:
            target.write_text(expected.content, encoding="utf-8")

    return {"files": files, "drifts": drifts}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Deterministic backend codegen for HB Track pilot modules.")
    parser.add_argument("--module", required=True, help="Target module. Current pilot: reports.")
    parser.add_argument("--check", action="store_true", help="Validate generated files without rewriting.")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="Output format.")
    args = parser.parse_args(argv)

    root = _repo_root()

    try:
        expected = _expected_files(root, args.module)
        materialized = _materialize(root, expected, check=args.check)
    except BackendCodegenError as exc:
        if args.format == "json":
            print(json.dumps({"status": "FAIL", "summary": exc.summary}, ensure_ascii=False, indent=2))
        else:
            print(f"[FAIL] {exc.summary}")
        return 1

    combined_hash = _sha256_text(
        "\n".join(f"{item['relpath']}:{item['sha256']}" for item in materialized["files"])
    )
    summary = {
        "status": "PASS" if not materialized["drifts"] else "FAIL",
        "module": args.module,
        "check": args.check,
        "generator": GENERATOR_NAME,
        "generator_version": GENERATOR_VERSION,
        "combined_sha256": combined_hash,
        "files": materialized["files"],
        "drifts": materialized["drifts"],
    }

    if args.format == "json":
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        verb = "validated" if args.check else "generated"
        print(f"[PASS] backend code {verb} for module `{args.module}`")
        print(f"combined_sha256={combined_hash}")
        for item in materialized["files"]:
            print(f" - {item['relpath']} :: {item['sha256']}")

    return 0 if not materialized["drifts"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
