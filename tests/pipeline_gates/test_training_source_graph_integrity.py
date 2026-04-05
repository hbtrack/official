from __future__ import annotations

import json
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
GRAPH_ROOT = REPO_ROOT / "docs" / "hbtrack" / "modulos" / "training" / "graph"


def _load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve(ref: str) -> Path:
    target = (GRAPH_ROOT / ref).resolve()
    assert target.exists(), f"referência ausente no source graph: {ref}"
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


def test_training_graph_files_exist_and_are_active():
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
        assert payload["module"] == "training"


def test_training_module_manifest_refs_resolve():
    manifest = _load_yaml(GRAPH_ROOT / "module_manifest.yaml")

    for section in ("module_docs", "contract_surfaces", "runtime_surfaces", "structured_ir"):
        for ref in manifest[section].values():
            _resolve(ref)

    assert manifest["phase"] == "source_graph_rollout"
    assert manifest["known_gaps"]


def test_training_entities_graph_matches_schema_and_runtime():
    entities = _load_yaml(GRAPH_ROOT / "entity_graph.yaml")["entities"]
    entity = entities["TrainingSession"]
    schema = _load_json(_resolve(entity["schema_ref"]))
    entity_file, symbol = _resolve_symbol(entity["runtime_entity_ref"])
    entity_source = entity_file.read_text(encoding="utf-8")

    assert entity_file.name == "entities.py"
    assert f"class {symbol}" in entity_source
    assert entity["schema_ref"].endswith("training_session.schema.json")

    graph_sovereign_names = [field["name"] for field in entity["sovereign_fields"]]
    assert graph_sovereign_names == list(schema["properties"].keys())

    graph_required = sorted(field["name"] for field in entity["sovereign_fields"] if field["required"])
    assert graph_required == sorted(schema["required"])

    for field in entity["sovereign_fields"]:
        assert field["runtime_name"] in entity_source


def test_training_endpoints_graph_matches_openapi_and_runtime_refs():
    endpoints = _load_yaml(GRAPH_ROOT / "endpoints.yaml")["endpoints"]
    openapi_paths = _load_yaml(REPO_ROOT / "contracts" / "openapi" / "paths" / "training.yaml")

    graph_operation_ids = [entry["operation_id"] for entry in endpoints]
    assert sorted(graph_operation_ids) == sorted(_operation_ids_from_openapi(openapi_paths))

    for entry in endpoints:
        assert entry["method"] in {"GET", "POST", "PUT", "PATCH", "DELETE"}
        assert isinstance(entry["response_codes"], list) and entry["response_codes"]
        _resolve(entry["openapi_ref"].split("#", 1)[0])

        handler_file, handler_symbol = _resolve_symbol(entry["runtime_handler_ref"])
        assert f"def {handler_symbol}" in handler_file.read_text(encoding="utf-8")

        use_case_file, use_case_symbol = _resolve_symbol(entry["use_case_ref"])
        assert f"class {use_case_symbol}" in use_case_file.read_text(encoding="utf-8")


def test_training_errors_graph_maps_to_real_exceptions_and_operations():
    errors = _load_yaml(GRAPH_ROOT / "errors.yaml")["errors"]

    for error in errors:
        assert "error_id" in error
        assert "http_status" in error
        # class_ref opcional (pode ser None para erros de transporte como 401)
        class_ref = error.get("class_ref")
        if class_ref:
            exc_file, exc_symbol = _resolve_symbol(class_ref)
            assert f"class {exc_symbol}" in exc_file.read_text(encoding="utf-8")


def test_training_test_obligations_cover_graph_contracts_and_runtime():
    obligations = _load_yaml(GRAPH_ROOT / "test_obligations.yaml")["obligations"]
    obligation_ids = {item["id"] for item in obligations}
    assert obligation_ids == {
        "TRAIN-TO-001",
        "TRAIN-TO-002",
        "TRAIN-TO-003",
        "TRAIN-TO-004",
    }

    for obligation in obligations:
        artifact = _resolve(obligation["artifact_ref"])
        assert artifact.exists()
        for evidence_ref in obligation["evidence_refs"]:
            _resolve(evidence_ref)


def test_training_module_docs_reference_source_graph():
    domain_rules = (REPO_ROOT / "docs" / "hbtrack" / "modulos" / "training" / "DOMAIN_RULES_TRAINING.md").read_text(encoding="utf-8")

    for ref in (
        "graph/entity_graph.yaml",
        "graph/endpoints.yaml",
        "graph/errors.yaml",
    ):
        assert ref in domain_rules, f"DOMAIN_RULES_TRAINING.md não referencia {ref}"
