from __future__ import annotations

import json
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
COMPONENT_PATH = REPO_ROOT / "contracts" / "openapi" / "components" / "schemas" / "reports" / "report_job.yaml"
PATHS_PATH = REPO_ROOT / "contracts" / "openapi" / "paths" / "reports.yaml"
SCHEMA_PATH = REPO_ROOT / "contracts" / "schemas" / "reports" / "report_job.schema.json"
GRAPH_MANIFEST = REPO_ROOT / "docs" / "hbtrack" / "modulos" / "reports" / "graph" / "module_manifest.yaml"
SCHEMA_VIEW = REPO_ROOT / "generated" / "source_graph" / "reports" / "reports.schema_contract_view.yaml"


def _load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _response_schema(path_doc: dict, path_key: str, method: str, status: str) -> dict:
    return path_doc[path_key][method]["responses"][status]["content"]["application/json"]["schema"]


def test_reports_component_is_direct_ref_to_sovereign_schema():
    component = _load_yaml(COMPONENT_PATH)
    assert component == {"$ref": "../../../../schemas/reports/report_job.schema.json"}


def test_reports_component_matches_source_graph_schema_view():
    schema = _load_json(SCHEMA_PATH)
    schema_view = _load_yaml(SCHEMA_VIEW)

    assert schema_view["primary_schema_ref"] == "contracts/schemas/reports/report_job.schema.json"
    assert schema_view["openapi_projection_ref"] == "contracts/openapi/components/schemas/reports/report_job.yaml"
    assert [field["name"] for field in schema_view["sovereign_fields"]] == list(schema["properties"].keys())
    assert sorted(schema_view["required"]) == sorted(schema["required"])


def test_reports_paths_extend_base_shape_only_with_runtime_fields():
    paths_doc = _load_yaml(PATHS_PATH)

    list_schema = _response_schema(paths_doc, "/reports/jobs", "get", "200")
    create_schema = _response_schema(paths_doc, "/reports/jobs", "post", "201")
    get_schema = _response_schema(paths_doc, "/reports/jobs/{jobId}", "get", "200")
    update_schema = _response_schema(paths_doc, "/reports/jobs/{jobId}", "patch", "200")

    for schema in (list_schema["properties"]["data"]["items"], create_schema, get_schema, update_schema):
        assert schema["allOf"][0]["$ref"] == "../components/schemas/reports/report_job.yaml"

    runtime_only_keys = {"statusLabel", "completedAt", "errorMessage"}

    list_overlay = list_schema["properties"]["data"]["items"]["allOf"][1]
    get_overlay = get_schema["allOf"][1]
    update_overlay = update_schema["allOf"][1]
    create_overlay = create_schema["allOf"][1]

    for overlay in (list_overlay, get_overlay, update_overlay):
        assert overlay["required"] == ["statusLabel"]
        assert set(overlay["properties"]) <= runtime_only_keys
        assert overlay["properties"]["statusLabel"]["enum"] == ["queued", "processing", "completed", "failed", "cancelled"]
        assert "completedAt" in overlay["properties"]
        assert "errorMessage" in overlay["properties"]

    assert create_overlay["required"] == ["statusLabel"]
    assert set(create_overlay["properties"]) == {"statusLabel"}
    assert create_overlay["properties"]["statusLabel"]["enum"] == ["queued"]


def test_reports_openapi_no_longer_uses_legacy_projection_fields():
    raw_component = COMPONENT_PATH.read_text(encoding="utf-8")
    raw_paths = PATHS_PATH.read_text(encoding="utf-8")

    assert "jobId:" not in raw_component
    assert "createdAt:" not in raw_component
    assert "\n  status:\n" not in raw_component
    assert "required: [statusLabel, completedAt]" not in raw_paths


def test_reports_module_manifest_known_gap_matches_b3_state():
    manifest = _load_yaml(GRAPH_MANIFEST)
    assert manifest["known_gaps"]
    assert "shape base do OpenAPI agora referencia o schema soberano" in manifest["known_gaps"][0]
