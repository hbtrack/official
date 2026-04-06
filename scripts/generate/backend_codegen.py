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
SUPPORTED_MODULES = {
    "reports", "analytics", "exercises", "notifications", "wellness",
    "medical", "ai_ingestion", "seasons", "teams", "competitions",
    "users", "matches", "scout", "video", "audit", "identity_access",
    "training",
}
_REPORTS_ONLY_MODULE = "reports"
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
        "uuid_v4|null": "UUID",
        "timestamp_utc": "datetime",
        "timestamp_utc|null": "datetime",
        "datetime": "datetime",
        "datetime_utc": "datetime",
        "datetime_iso8601": "datetime",
        "string": "str",
        "string[]": "List[str]",
        "enum": "str",
        "string_enum": "str",
        "integer": "int",
        "number": "float",
        "decimal": "Decimal",
        "float": "float",
        "boolean": "bool",
        "date": "date",
        "date_only": "date",
        "array_of_string": "List[str]",
        "array_of_uuid": "List[UUID]",
        "object": "Dict[str, Any]",
    }
    try:
        return mapping[field_type]
    except KeyError as exc:
        raise BackendCodegenError(f"Tipo não suportado no codegen backend: {field_type}") from exc


def _is_nullable_type(field_type: str) -> bool:
    return field_type.endswith("|null")


def _to_snake_case(name: str) -> str:
    """PascalCase → snake_case: 'ReportJob' → 'report_job'."""
    import re
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def _to_class_name(module: str) -> str:
    """Module name → PascalCase class prefix: 'ai_ingestion' → 'AiIngestion'."""
    return "".join(part.capitalize() for part in module.split("_"))


def _needs_import(types_used: set[str]) -> dict[str, bool]:
    return {
        "UUID": any(t in types_used for t in ("UUID", "List[UUID]")),
        "datetime": "datetime" in types_used,
        "date": "date" in types_used,
        "Decimal": "Decimal" in types_used,
        "List": any(t.startswith("List[") for t in types_used),
        "Optional": True,
        "Dict": any(t.startswith("Dict[") for t in types_used),
        "Any": any(t.startswith("Dict[") for t in types_used),
    }


def _python_type_from_json_schema(schema: dict[str, Any]) -> str:
    # Handle $ref as opaque string (unresolved refs default to str)
    if "$ref" in schema and "type" not in schema:
        return "str"
    schema_type = schema.get("type")
    schema_format = schema.get("format")
    # Handle nullable type arrays: {"type": ["string", "null"]}
    if isinstance(schema_type, list):
        non_null = [t for t in schema_type if t != "null"]
        schema_type = non_null[0] if non_null else "string"
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
    if schema_type == "object":
        return "dict"
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

    # Load entity_graph.yaml for invariants (generic modules)
    entity_graph_path = root / "docs" / "hbtrack" / "modulos" / module / "graph" / "entity_graph.yaml"
    entity_graph = _load_yaml(entity_graph_path) if entity_graph_path.exists() else {}

    return {
        "bundle": bundle,
        "schema_view": schema_view,
        "openapi_view": openapi_view,
        "impact_report": impact_report,
        "openapi_paths": openapi_paths,
        "entity_graph": entity_graph,
        "module": module,
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


# ---------------------------------------------------------------------------
# Generic build functions (all modules except reports)
# ---------------------------------------------------------------------------

def _generic_output_field_lines(
    sovereign_fields: list[dict[str, Any]],
    runtime_fields: list[dict[str, Any]],
) -> list[str]:
    """Generate Schema field lines for EntityOut — generic version."""
    lines: list[str] = []
    for field in sovereign_fields:
        name = field["runtime_name"]
        raw_type = field["type"]
        annotation = _python_type(raw_type)
        if field.get("required"):
            lines.append(f"    {name}: {annotation}")
        elif _is_nullable_type(raw_type):
            lines.append(f"    {name}: Optional[{annotation}] = None")
        else:
            lines.append(f"    {name}: Optional[{annotation}] = None")
    for field in runtime_fields:
        name = field["runtime_name"]
        annotation = _python_type(field["type"])
        lines.append(f"    {name}: Optional[{annotation}] = None")
    return lines


def _generic_domain_field_lines(
    sovereign_fields: list[dict[str, Any]],
    runtime_fields: list[dict[str, Any]],
) -> list[str]:
    """Generate dataclass field lines for entity — generic version."""
    required_lines: list[str] = []
    optional_lines: list[str] = []
    for field in sovereign_fields:
        name = field["runtime_name"]
        raw_type = field["type"]
        annotation = _python_type(raw_type)
        if field.get("required"):
            required_lines.append(f"    {name}: {annotation}")
        elif raw_type in ("string[]", "array_of_string"):
            optional_lines.append(f"    {name}: List[str] = field(default_factory=list)")
        elif raw_type == "array_of_uuid":
            optional_lines.append(f"    {name}: List[UUID] = field(default_factory=list)")
        elif raw_type == "object":
            optional_lines.append(f"    {name}: Dict[str, Any] = field(default_factory=dict)")
        else:
            optional_lines.append(f"    {name}: Optional[{annotation}] = None")
    for field in runtime_fields:
        name = field["runtime_name"]
        raw_type = field["type"]
        annotation = _python_type(raw_type)
        if raw_type == "enum" and field.get("allowed_values"):
            default = field["allowed_values"][0]
            optional_lines.append(f'    {name}: {annotation} = "{default}"')
        else:
            optional_lines.append(f"    {name}: Optional[{annotation}] = None")
    return required_lines + optional_lines


def _generic_from_domain_lines(
    sovereign_fields: list[dict[str, Any]],
    runtime_fields: list[dict[str, Any]],
    var_name: str = "entity",
) -> list[str]:
    lines: list[str] = []
    for field in sovereign_fields:
        lines.append(f"            {field['runtime_name']}={var_name}.{field['runtime_name']},")
    for field in runtime_fields:
        lines.append(f"            {field['runtime_name']}={var_name}.{field['runtime_name']},")
    return lines


def _collect_types_used(
    sovereign_fields: list[dict[str, Any]],
    runtime_fields: list[dict[str, Any]],
) -> set[str]:
    types: set[str] = set()
    for f in sovereign_fields + runtime_fields:
        types.add(_python_type(f["type"]))
    return types


def _generic_imports_block(types_used: set[str]) -> list[str]:
    """Build import lines based on which types are actually used."""
    lines = ["from __future__ import annotations", ""]
    stdlib: list[str] = []
    if "date" in types_used:
        stdlib.append("date")
    if "datetime" in types_used:
        stdlib.append("datetime")
    if "Decimal" in types_used:
        stdlib.append("Decimal")
    if stdlib:
        if "date" in stdlib and "datetime" in stdlib:
            lines.append("from datetime import date, datetime")
        elif "datetime" in stdlib:
            lines.append("from datetime import datetime")
        elif "date" in stdlib:
            lines.append("from datetime import date")
        if "Decimal" in stdlib:
            lines.append("from decimal import Decimal")

    typing_parts: list[str] = []
    needs = _needs_import(types_used)
    if needs["Any"]:
        typing_parts.append("Any")
    if needs["Dict"]:
        typing_parts.append("Dict")
    if needs["List"]:
        typing_parts.append("List")
    typing_parts.append("Optional")
    if typing_parts:
        lines.append(f"from typing import {', '.join(sorted(typing_parts))}")
    if needs["UUID"]:
        lines.append("from uuid import UUID")
    return lines


def _build_generic_schemas(inputs: dict[str, Any]) -> str:
    schema_view = inputs["schema_view"]
    openapi_view = inputs["openapi_view"]
    openapi_paths = inputs["openapi_paths"]
    source_fingerprint = inputs["impact_report"]["source_fingerprint"]
    module = inputs["module"]
    entity_name = schema_view["primary_entity"]
    sovereign_fields = schema_view["sovereign_fields"]
    runtime_fields = schema_view.get("runtime_extension_fields") or []

    types_used = _collect_types_used(sovereign_fields, runtime_fields)
    output_lines = _generic_output_field_lines(sovereign_fields, runtime_fields)
    from_domain_lines = _generic_from_domain_lines(sovereign_fields, runtime_fields)

    # Find POST / PATCH operations for Create/Update schemas
    create_lines: list[str] = []
    update_lines: list[str] = []
    for op in openapi_view.get("operations", []):
        method = op["method"].upper()
        path = op["path"]
        path_key = path if path in openapi_paths else None
        if path_key is None:
            # Try without leading module prefix — normalize path
            for k in openapi_paths:
                if k.rstrip("/") == path.rstrip("/"):
                    path_key = k
                    break
        if path_key is None:
            continue
        path_item = openapi_paths.get(path_key, {})
        operation = path_item.get(method.lower(), {})
        req_body = (
            operation.get("requestBody", {})
            .get("content", {})
            .get("application/json", {})
            .get("schema", {})
        )
        if not req_body.get("properties"):
            continue
        if method == "POST" and not create_lines:
            required_set = set(req_body.get("required") or [])
            for name, field_schema in req_body["properties"].items():
                annotation = _python_type_from_json_schema(field_schema)
                types_used.add(annotation)
                if name in required_set and "default" not in field_schema:
                    create_lines.append(f"    {name}: {annotation}")
                elif "default" in field_schema:
                    default = field_schema["default"]
                    if isinstance(default, str):
                        create_lines.append(f'    {name}: {annotation} = "{default}"')
                    else:
                        create_lines.append(f"    {name}: {annotation} = {default}")
                else:
                    create_lines.append(f"    {name}: Optional[{annotation}] = None")
        elif method == "PATCH" and not update_lines:
            for name, field_schema in req_body["properties"].items():
                annotation = _python_type_from_json_schema(field_schema)
                types_used.add(annotation)
                update_lines.append(f"    {name}: Optional[{annotation}] = None")

    lines = _render_header(module=module, source_fingerprint=source_fingerprint)
    lines += _generic_imports_block(types_used)
    lines += [
        "",
        "from ninja import Schema",
        "",
        "",
        f"class {entity_name}Out(Schema):",
        *output_lines,
        "",
        "    @classmethod",
        f'    def from_domain(cls, entity) -> "{entity_name}Out":',
        "        return cls(",
        *from_domain_lines,
        "        )",
        "",
        "",
        f"class {entity_name}ListOut(Schema):",
        f"    data: List[{entity_name}Out]",
        "    nextPageToken: Optional[str] = None",
    ]
    if create_lines:
        lines += [
            "",
            "",
            f"class Create{entity_name}In(Schema):",
            *create_lines,
        ]
    if update_lines:
        lines += [
            "",
            "",
            f"class Update{entity_name}In(Schema):",
            *update_lines,
        ]
    lines += [
        "",
        "",
        "class ErrorOut(Schema):",
        "    detail: str",
        "",
    ]
    return "\n".join(lines)


def _build_generic_entities(inputs: dict[str, Any]) -> str:
    schema_view = inputs["schema_view"]
    entity_graph = inputs.get("entity_graph", {})
    source_fingerprint = inputs["impact_report"]["source_fingerprint"]
    module = inputs["module"]
    entity_name = schema_view["primary_entity"]
    sovereign_fields = schema_view["sovereign_fields"]
    runtime_fields = schema_view.get("runtime_extension_fields") or []

    types_used = _collect_types_used(sovereign_fields, runtime_fields)
    domain_field_lines = _generic_domain_field_lines(sovereign_fields, runtime_fields)

    # Extract enum values from sovereign_fields + runtime_fields
    enum_defs: list[str] = []
    for field in sovereign_fields + runtime_fields:
        values = field.get("allowed_values") or field.get("values")
        if values and isinstance(values, list):
            const_name = f"VALID_{field['runtime_name'].upper()}S"
            enum_defs.append(f"{const_name} = frozenset([{_render_list_literal(values)}])")

    # Extract invariants from entity_graph
    invariants: list[dict[str, str]] = []
    for ent in entity_graph.get("entities", []):
        if isinstance(ent, dict):
            ent_name = ent.get("name", "")
            if ent_name == entity_name:
                invariants = ent.get("invariants", []) or []
                break

    lines = _render_header(module=module, source_fingerprint=source_fingerprint)
    lines += _generic_imports_block(types_used)
    if "field(default_factory" in "\n".join(domain_field_lines):
        lines.append("from dataclasses import dataclass, field")
    else:
        lines.append("from dataclasses import dataclass")
    lines += ["", ""]
    if enum_defs:
        lines += enum_defs
        lines += ["", ""]
    lines += [
        "@dataclass",
        f"class {entity_name}:",
        *domain_field_lines,
        "",
        "    def validate_invariants(self) -> None:",
        '        """Validate domain invariants from entity graph."""',
    ]
    # Generate basic required-field invariant checks
    required_fields = [f for f in sovereign_fields if f.get("required")]
    if required_fields:
        for f in required_fields:
            rn = f["runtime_name"]
            lines.append(f"        if not self.{rn}:")
            lines.append(f'            raise ValueError("{entity_name}: {rn} is required")')
    else:
        lines.append("        pass  # No invariants to validate")
    lines.append("")
    return "\n".join(lines)


def _build_generic_repository(inputs: dict[str, Any]) -> str:
    schema_view = inputs["schema_view"]
    source_fingerprint = inputs["impact_report"]["source_fingerprint"]
    module = inputs["module"]
    entity_name = schema_view["primary_entity"]
    snake_entity = _to_snake_case(entity_name)
    model_name = f"{entity_name}Model"
    sovereign_fields = schema_view["sovereign_fields"]
    runtime_fields = schema_view.get("runtime_extension_fields") or []
    all_fields = sovereign_fields + runtime_fields
    types_used = _collect_types_used(sovereign_fields, runtime_fields)

    # Build from_model mapping lines
    from_model_lines: list[str] = []
    for f in all_fields:
        rn = f["runtime_name"]
        ft = f["type"]
        if ft in ("string[]", "array_of_string"):
            from_model_lines.append(f"        {rn}=model.{rn} or [],")
        elif ft == "array_of_uuid":
            from_model_lines.append(f"        {rn}=model.{rn} or [],")
        elif ft == "object":
            from_model_lines.append(f"        {rn}=model.{rn} or {{}},")
        else:
            from_model_lines.append(f"        {rn}=model.{rn},")

    # Build save defaults dict
    save_defaults: list[str] = []
    for f in all_fields:
        if f["runtime_name"] == "id":
            continue
        rn = f["runtime_name"]
        save_defaults.append(f'            "{rn}": {snake_entity}.{rn},')

    # Build list filter fields (optional string/enum/uuid fields good for filtering)
    filter_fields: list[str] = []
    for f in sovereign_fields:
        if f.get("required") and f["runtime_name"] != "id":
            continue
        if f["type"] in ("string", "enum", "string_enum", "uuid_v4"):
            filter_fields.append(f["runtime_name"])

    lines = _render_header(module=module, source_fingerprint=source_fingerprint)
    lines += _generic_imports_block(types_used)
    lines += [
        "from typing import List, Tuple",
        "",
        f"from ...infrastructure.models import {model_name}",
        f"from ..domain.entities import {entity_name}",
        "",
        "",
        f"def _{snake_entity}_from_model(model: {model_name}) -> {entity_name}:",
        f"    return {entity_name}(",
        *from_model_lines,
        "    )",
        "",
        "",
        f"class {entity_name}Repository:",
        f"    def save(self, {snake_entity}: {entity_name}) -> {entity_name}:",
        f"        obj, _ = {model_name}.objects.update_or_create(",
        f"            id={snake_entity}.id,",
        "            defaults={",
        *save_defaults,
        "            },",
        "        )",
        f"        return _{snake_entity}_from_model(obj)",
        "",
        f"    def get_by_id(self, entity_id: UUID) -> Optional[{entity_name}]:",
        "        try:",
        f"            return _{snake_entity}_from_model({model_name}.objects.get(id=entity_id))",
        f"        except {model_name}.DoesNotExist:",
        "            return None",
        "",
        f"    def list_entities(",
        "        self,",
        "        page_size: int = 20,",
        "        page_token: Optional[str] = None,",
        f"    ) -> Tuple[List[{entity_name}], Optional[str]]:",
        f"        qs = {model_name}.objects.all()",
        "        offset = 0",
        "        if page_token:",
        "            try:",
        "                offset = int(page_token)",
        "            except ValueError:",
        "                offset = 0",
        "        total = qs.count()",
        "        items = qs[offset: offset + page_size]",
        f"        entities = [_{snake_entity}_from_model(m) for m in items]",
        '        next_token = str(offset + page_size) if (offset + page_size) < total else None',
        "        return entities, next_token",
        "",
    ]
    return "\n".join(lines)


def _build_generic_use_cases(inputs: dict[str, Any]) -> str:
    schema_view = inputs["schema_view"]
    openapi_view = inputs["openapi_view"]
    source_fingerprint = inputs["impact_report"]["source_fingerprint"]
    module = inputs["module"]
    entity_name = schema_view["primary_entity"]
    snake_entity = _to_snake_case(entity_name)

    operations = openapi_view.get("operations", [])

    lines = _render_header(module=module, source_fingerprint=source_fingerprint)
    lines += [
        "from __future__ import annotations",
        "",
        "import uuid",
        "from typing import List, Optional, Tuple",
        "from uuid import UUID",
        "",
        f"from ..domain.entities import {entity_name}",
        f"from ..infrastructure.repository import {entity_name}Repository",
        "",
    ]

    for op in operations:
        op_id = op["operation_id"]
        class_name = "".join(part.capitalize() for part in op_id.replace("-", "_").split("_"))
        # Filter out sub-path operations for stub safety (e.g. addTeamToSeason, lineup ops)
        # Only generate stubs for primary CRUD operations
        method = op["method"].upper()

        lines += [
            "",
            f"class {class_name}:",
            f"    def __init__(self, repo: {entity_name}Repository):",
            "        self.repo = repo",
            "",
        ]

        if method == "GET" and "{" not in op["path"].split("/")[-1]:
            # List operation
            lines += [
                "    def execute(",
                "        self,",
                "        requester_id: UUID,",
                "        page_size: int = 20,",
                "        page_token: Optional[str] = None,",
                f"    ) -> Tuple[List[{entity_name}], Optional[str]]:",
                "        return self.repo.list_entities(page_size=page_size, page_token=page_token)",
                "",
            ]
        elif method == "GET":
            # Get by ID
            lines += [
                "    def execute(self, requester_id: UUID, entity_id: UUID) -> {entity_name}:".format(entity_name=entity_name),
                "        entity = self.repo.get_by_id(entity_id)",
                "        if entity is None:",
                f'            raise ValueError(f"{entity_name} {{entity_id}} not found")',
                "        return entity",
                "",
            ]
        elif method == "POST":
            lines += [
                "    def execute(self, requester_id: UUID, **kwargs) -> {entity_name}:".format(entity_name=entity_name),
                f"        entity = {entity_name}(id=uuid.uuid4(), **kwargs)",
                "        entity.validate_invariants()",
                "        return self.repo.save(entity)",
                "",
            ]
        elif method in ("PATCH", "PUT"):
            lines += [
                "    def execute(self, requester_id: UUID, entity_id: UUID, **kwargs) -> {entity_name}:".format(entity_name=entity_name),
                "        entity = self.repo.get_by_id(entity_id)",
                "        if entity is None:",
                f'            raise ValueError(f"{entity_name} {{entity_id}} not found")',
                "        for key, value in kwargs.items():",
                "            if value is not None:",
                "                setattr(entity, key, value)",
                "        entity.validate_invariants()",
                "        return self.repo.save(entity)",
                "",
            ]
        elif method == "DELETE":
            lines += [
                "    def execute(self, requester_id: UUID, entity_id: UUID) -> None:",
                "        entity = self.repo.get_by_id(entity_id)",
                "        if entity is None:",
                f'            raise ValueError(f"{entity_name} {{entity_id}} not found")',
                "        # Delete logic delegated to repository",
                "        pass",
                "",
            ]
        else:
            lines += [
                "    def execute(self, requester_id: UUID, **kwargs):",
                f'        raise NotImplementedError("{class_name}.execute")',
                "",
            ]
    return "\n".join(lines)


def _build_generic_api(inputs: dict[str, Any]) -> str:
    schema_view = inputs["schema_view"]
    openapi_view = inputs["openapi_view"]
    source_fingerprint = inputs["impact_report"]["source_fingerprint"]
    module = inputs["module"]
    entity_name = schema_view["primary_entity"]

    operations = openapi_view.get("operations", [])

    # Collect use case class names
    uc_classes: list[str] = []
    for op in operations:
        class_name = "".join(
            part.capitalize() for part in op["operation_id"].replace("-", "_").split("_")
        )
        uc_classes.append(class_name)

    # Determine which schema classes exist
    has_create = any(op["method"].upper() == "POST" for op in operations)
    has_update = any(op["method"].upper() in ("PATCH", "PUT") for op in operations)

    schema_imports: list[str] = [f"{entity_name}ListOut", f"{entity_name}Out", "ErrorOut"]
    if has_create:
        schema_imports.append(f"Create{entity_name}In")
    if has_update:
        schema_imports.append(f"Update{entity_name}In")

    lines = _render_header(module=module, source_fingerprint=source_fingerprint)
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
        "from .application.use_cases import (",
    ]
    for cls in uc_classes:
        lines.append(f"    {cls},")
    lines += [
        ")",
        "from .infrastructure.repository import {entity_name}Repository".format(entity_name=entity_name),
        "from .schemas import {imports}".format(imports=", ".join(sorted(set(schema_imports)))),
        "",
        "router = Router()",
        f"_repo = {entity_name}Repository()",
    ]

    # Instantiate use cases
    for op in operations:
        class_name = "".join(
            part.capitalize() for part in op["operation_id"].replace("-", "_").split("_")
        )
        var_name = f"_{_to_snake_case(class_name)}_uc"
        lines.append(f"{var_name} = {class_name}(_repo)")
    lines.append("")

    lines += [
        "",
        "def _role(request: HttpRequest) -> str:",
        '    role = getattr(request, "_actor_role", None)',
        "    if role:",
        "        return str(role)",
        '    raise HttpError(401, "Unauthenticated")',
        "",
        "",
        "def _uid(request: HttpRequest) -> UUID:",
        '    actor_id = getattr(request, "_actor_id", None)',
        "    if actor_id:",
        "        return UUID(str(actor_id))",
        '    raise HttpError(401, "Unauthenticated")',
        "",
    ]

    # Generate handler stubs for each operation
    for op in operations:
        op_id = op["operation_id"]
        method = op["method"].upper()
        path = op["path"]
        handler_name = _to_snake_case(op_id)
        class_name = "".join(
            part.capitalize() for part in op_id.replace("-", "_").split("_")
        )
        var_name = f"_{_to_snake_case(class_name)}_uc"

        # Build response map from response_codes
        response_codes = op.get("response_codes", [])
        resp_parts: list[str] = []
        for code in sorted(response_codes):
            if code in (200, 201):
                resp_parts.append(f"{code}: {entity_name}Out")
            elif code in (401, 403, 404, 409, 422):
                resp_parts.append(f"{code}: ErrorOut")
        resp_str = ", ".join(resp_parts) if resp_parts else f"200: {entity_name}Out"

        # Derive path relative to module prefix
        # e.g. /reports/jobs → /jobs, /seasons/{seasonId} → /{seasonId}
        module_prefixes = [f"/{module}", f"/{module.replace('_', '-')}"]
        api_path = path
        for prefix in module_prefixes:
            if path.startswith(prefix):
                api_path = path[len(prefix):] or "/"
                break
        # Also handle special prefixes like /auth, /ingestion, etc.
        if api_path == path:
            # Keep as-is for modules with non-standard prefixes
            api_path = path

        lines += [
            "",
            f"@router.{method.lower()}('{api_path}', response={{{resp_str}}})",
            f"def {handler_name}(request: HttpRequest):",
            "    try:",
            "        uid = _uid(request)",
        ]
        if method == "GET" and "{" not in path.split("/")[-1]:
            lines += [
                f"        entities, token = {var_name}.execute(requester_id=uid)",
                f"        return 200, {entity_name}ListOut(",
                f"            data=[{entity_name}Out.from_domain(e) for e in entities],",
                "            nextPageToken=token,",
                "        )",
            ]
        elif method == "GET":
            lines += [
                f"        # TODO: extract path param",
                f"        raise NotImplementedError('{handler_name}')",
            ]
        elif method == "POST":
            lines += [
                f"        # TODO: parse payload → {var_name}.execute()",
                f"        raise NotImplementedError('{handler_name}')",
            ]
        elif method in ("PATCH", "PUT"):
            lines += [
                f"        # TODO: parse payload → {var_name}.execute()",
                f"        raise NotImplementedError('{handler_name}')",
            ]
        elif method == "DELETE":
            lines += [
                f"        # TODO: implement delete",
                f"        raise NotImplementedError('{handler_name}')",
            ]
        else:
            lines += [
                f"        raise NotImplementedError('{handler_name}')",
            ]
        lines += [
            "    except ValueError as exc:",
            "        return 422, ErrorOut(detail=str(exc))",
            "",
        ]
    return "\n".join(lines)


def _build_generic_test(inputs: dict[str, Any]) -> str:
    schema_view = inputs["schema_view"]
    source_fingerprint = inputs["impact_report"]["source_fingerprint"]
    module = inputs["module"]
    entity_name = schema_view["primary_entity"]
    snake_entity = _to_snake_case(entity_name)
    sovereign_fields = schema_view["sovereign_fields"]
    runtime_fields = schema_view.get("runtime_extension_fields") or []

    # Build factory defaults
    factory_lines: list[str] = []
    for f in sovereign_fields:
        rn = f["runtime_name"]
        ft = f["type"]
        if ft in ("uuid_v4", "uuid_v4|null"):
            factory_lines.append(f'        "{rn}": uuid.uuid4(),')
        elif ft in ("timestamp_utc", "timestamp_utc|null", "datetime", "datetime_utc", "datetime_iso8601"):
            factory_lines.append(f'        "{rn}": datetime.now(timezone.utc),')
        elif ft in ("date", "date_only"):
            factory_lines.append(f'        "{rn}": date.today(),')
        elif ft in ("string", "enum", "string_enum"):
            if f.get("allowed_values") or f.get("values"):
                vals = f.get("allowed_values") or f.get("values")
                factory_lines.append(f'        "{rn}": "{vals[0]}",')
            else:
                factory_lines.append(f'        "{rn}": "test-{rn}",')
        elif ft == "integer":
            factory_lines.append(f'        "{rn}": 1,')
        elif ft in ("number", "float", "decimal"):
            factory_lines.append(f'        "{rn}": 1.0,')
        elif ft == "boolean":
            factory_lines.append(f'        "{rn}": True,')
        elif ft in ("string[]", "array_of_string"):
            factory_lines.append(f'        "{rn}": ["item-1"],')
        elif ft == "array_of_uuid":
            factory_lines.append(f'        "{rn}": [uuid.uuid4()],')
        elif ft == "object":
            factory_lines.append(f'        "{rn}": {{"key": "value"}},')
        else:
            factory_lines.append(f'        "{rn}": None,')
    for f in runtime_fields:
        rn = f["runtime_name"]
        ft = f["type"]
        if ft == "enum" and f.get("allowed_values"):
            factory_lines.append(f'        "{rn}": "{f["allowed_values"][0]}",')
        elif ft in ("uuid_v4",):
            factory_lines.append(f'        "{rn}": uuid.uuid4(),')
        elif ft in ("timestamp_utc", "datetime"):
            factory_lines.append(f'        "{rn}": datetime.now(timezone.utc),')
        elif ft == "string":
            factory_lines.append(f'        "{rn}": "test-{rn}",')
        else:
            factory_lines.append(f'        "{rn}": None,')

    lines = _render_header(module=module, source_fingerprint=source_fingerprint)
    lines += [
        "from __future__ import annotations",
        "",
        "import uuid",
        "from datetime import date, datetime, timezone",
        "",
        "import pytest",
        "",
        f"from {module}.generated.domain.entities import {entity_name}",
        f"from {module}.generated.schemas import {entity_name}Out",
        "",
        "",
        f"def _make_{snake_entity}(**overrides):",
        "    payload = {",
        *factory_lines,
        "    }",
        "    payload.update(overrides)",
        f"    return {entity_name}(**payload)",
        "",
        "",
        f"def test_generated_{snake_entity}_validates_invariants():",
        f"    entity = _make_{snake_entity}()",
        "    entity.validate_invariants()",
        "",
        "",
        f"def test_generated_{snake_entity}_out_from_domain():",
        f"    entity = _make_{snake_entity}()",
        f"    payload = {entity_name}Out.from_domain(entity)",
        "    assert payload.id == entity.id",
        "",
    ]
    return "\n".join(lines)


def _build_generic_init() -> str:
    return ""


def _expected_files(root: Path, module: str) -> list[ExpectedFile]:
    inputs = _load_codegen_inputs(root, module)
    if module == _REPORTS_ONLY_MODULE:
        return _expected_files_reports(inputs, module)
    return _expected_files_generic(inputs, module)


def _expected_files_reports(inputs: dict[str, Any], module: str) -> list[ExpectedFile]:
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


def _expected_files_generic(inputs: dict[str, Any], module: str) -> list[ExpectedFile]:
    return [
        ExpectedFile(
            relpath=f"src/{module}/generated/__init__.py",
            content=_build_generic_init(),
        ),
        ExpectedFile(
            relpath=f"src/{module}/generated/schemas.py",
            content=_build_generic_schemas(inputs),
        ),
        ExpectedFile(
            relpath=f"src/{module}/generated/api.py",
            content=_build_generic_api(inputs),
        ),
        ExpectedFile(
            relpath=f"src/{module}/generated/domain/__init__.py",
            content=_build_generic_init(),
        ),
        ExpectedFile(
            relpath=f"src/{module}/generated/domain/entities.py",
            content=_build_generic_entities(inputs),
        ),
        ExpectedFile(
            relpath=f"src/{module}/generated/application/__init__.py",
            content=_build_generic_init(),
        ),
        ExpectedFile(
            relpath=f"src/{module}/generated/application/use_cases.py",
            content=_build_generic_use_cases(inputs),
        ),
        ExpectedFile(
            relpath=f"src/{module}/generated/infrastructure/__init__.py",
            content=_build_generic_init(),
        ),
        ExpectedFile(
            relpath=f"src/{module}/generated/infrastructure/repository.py",
            content=_build_generic_repository(inputs),
        ),
        ExpectedFile(
            relpath=f"src/{module}/generated/tests/__init__.py",
            content=_build_generic_init(),
        ),
        ExpectedFile(
            relpath=f"src/{module}/generated/tests/test_codegen_contract.py",
            content=_build_generic_test(inputs),
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
