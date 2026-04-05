from __future__ import annotations

import json
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
GRAPH_ROOT = REPO_ROOT / "docs" / "hbtrack" / "modulos" / "audit" / "graph"


def _load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve(ref: str) -> Path:
    target = (GRAPH_ROOT / ref).resolve()
    assert target.exists(), f"referência ausente: {ref}"
    return target


def _resolve_symbol(ref: str) -> tuple[Path, str]:
    path_str, symbol = ref.split("#", 1)
    return _resolve(path_str), symbol


def _operation_ids_from_openapi(path_doc: dict) -> list[str]:
    operation_ids: list[str] = []
    for path_item in path_doc.values():
        for method_doc in path_item.values():
            if isinstance(method_doc, dict) and "operationId" in method_doc:
                operation_ids.append(method_doc["operationId"])
    return operation_ids


def test_audit_graph_files_exist_and_are_active():
    expected = {
        "module_manifest.yaml",
        "entity_graph.yaml",
        "endpoints.yaml",
        "errors.yaml",
        "test_obligations.yaml",
    }
    present = {path.name for path in GRAPH_ROOT.glob("*.yaml")}
    assert expected <= present

    for filename in expected:
        payload = _load_yaml(GRAPH_ROOT / filename)
        assert payload["status"] == "active"
        assert payload["module"] == "audit"


def test_audit_module_manifest_refs_resolve():
    manifest = _load_yaml(GRAPH_ROOT / "module_manifest.yaml")

    for section in ("module_docs", "contract_surfaces", "runtime_surfaces", "structured_ir"):
        for ref in manifest[section].values():
            _resolve(ref)

    assert manifest["phase"] == "source_graph_rollout"
    assert manifest["known_gaps"]


def test_audit_entities_graph_matches_schema_and_runtime():
    entities = _load_yaml(GRAPH_ROOT / "entity_graph.yaml")["entities"]
    entity = entities["AuditEntry"]
    schema = _load_json(_resolve(entity["schema_ref"]))
    entity_file, symbol = _resolve_symbol(entity["runtime_entity_ref"])
    entity_source = entity_file.read_text(encoding="utf-8")

    assert entity_file.name == "entities.py"
    assert f"class {symbol}" in entity_source
    assert entity["schema_ref"].endswith("audit_entry.schema.json")

    graph_sovereign_names = [field["name"] for field in entity["sovereign_fields"]]
    assert graph_sovereign_names == list(schema["properties"].keys())

    graph_required = sorted(field["name"] for field in entity["sovereign_fields"] if field["required"])
    assert graph_required == sorted(schema["required"])

    for field in entity["sovereign_fields"]:
        assert field["runtime_name"] in entity_source


def test_audit_endpoints_graph_matches_openapi_and_runtime_refs():
    endpoints = _load_yaml(GRAPH_ROOT / "endpoints.yaml")["endpoints"]
    openapi_paths = _load_yaml(REPO_ROOT / "contracts" / "openapi" / "paths" / "audit.yaml")

    graph_operation_ids = [entry["operation_id"] for entry in endpoints]
    assert sorted(graph_operation_ids) == sorted(_operation_ids_from_openapi(openapi_paths))

    for entry in endpoints:
        assert entry["method"] in {"GET", "POST", "PATCH", "DELETE"}
        assert isinstance(entry["response_codes"], list) and entry["response_codes"]
        _resolve(entry["openapi_ref"].split("#", 1)[0])

        handler_file, handler_symbol = _resolve_symbol(entry["runtime_handler_ref"])
        assert f"def {handler_symbol}" in handler_file.read_text(encoding="utf-8")

        use_case_file, use_case_symbol = _resolve_symbol(entry["use_case_ref"])
        assert f"class {use_case_symbol}" in use_case_file.read_text(encoding="utf-8")


def test_audit_errors_graph_maps_to_real_exceptions_and_operations():
    endpoints = _load_yaml(GRAPH_ROOT / "endpoints.yaml")["endpoints"]
    operation_ids = {entry["operation_id"] for entry in endpoints}
    errors = _load_yaml(GRAPH_ROOT / "errors.yaml")["errors"]

    for error in errors:
        assert set(error["operations"]) <= operation_ids
        if "exception_ref" in error:
            exc_file, exc_symbol = _resolve_symbol(error["exception_ref"])
            assert f"class {exc_symbol}" in exc_file.read_text(encoding="utf-8")
        if "source_ref" in error:
            src_file, src_symbol = _resolve_symbol(error["source_ref"])
            assert src_symbol in src_file.read_text(encoding="utf-8")


def test_audit_test_obligations_cover_graph_contracts_and_runtime():
    obligations = _load_yaml(GRAPH_ROOT / "test_obligations.yaml")["obligations"]
    obligation_ids = {item["id"] for item in obligations}
    assert obligation_ids == {
        "AUD-TO-001",
        "AUD-TO-002",
        "AUD-TO-003",
        "AUD-TO-004",
    }

    for obligation in obligations:
        artifact = _resolve(obligation["artifact_ref"])
        assert artifact.exists()
        for evidence_ref in obligation["evidence_refs"]:
            _resolve(evidence_ref)


def test_audit_module_docs_and_manifest_reference_source_graph():
    readme = (REPO_ROOT / "docs" / "hbtrack" / "modulos" / "audit" / "README.md").read_text(encoding="utf-8")
    domain_rules = (REPO_ROOT / "docs" / "hbtrack" / "modulos" / "audit" / "DOMAIN_RULES_AUDIT.md").read_text(encoding="utf-8")
    test_matrix = (REPO_ROOT / "docs" / "hbtrack" / "modulos" / "audit" / "TEST_MATRIX_AUDIT.md").read_text(encoding="utf-8")
    manifest = _load_yaml(REPO_ROOT / "docs" / "_canon" / "DOC_USAGE_MANIFEST.yaml")

    for ref in (
        "graph/module_manifest.yaml",
        "graph/entity_graph.yaml",
        "graph/endpoints.yaml",
        "graph/errors.yaml",
        "graph/test_obligations.yaml",
    ):
        assert ref in readme

    assert "graph/entity_graph.yaml" in domain_rules
    assert "graph/endpoints.yaml" in domain_rules
    assert "graph/errors.yaml" in domain_rules
    assert "graph/test_obligations.yaml" in test_matrix

    audit_graph_entry = next(entry for entry in manifest["entries"] if entry["rule_id"] == "HBTRACK_AUDIT_GRAPH")
    covered = set()
    for pattern in audit_graph_entry["path_globs"]:
        covered |= {
            path.relative_to(REPO_ROOT).as_posix()
            for path in REPO_ROOT.glob(pattern)
            if path.is_file()
        }
    assert covered == {
        "docs/hbtrack/modulos/audit/graph/module_manifest.yaml",
        "docs/hbtrack/modulos/audit/graph/entity_graph.yaml",
        "docs/hbtrack/modulos/audit/graph/endpoints.yaml",
        "docs/hbtrack/modulos/audit/graph/errors.yaml",
        "docs/hbtrack/modulos/audit/graph/test_obligations.yaml",
    }
