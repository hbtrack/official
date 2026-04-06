from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
GRAPH_ROOT = REPO_ROOT / "docs" / "hbtrack" / "modulos" / "video" / "graph"


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


def _operation_ids_from_openapi(path_doc: dict[str, Any]) -> list[str]:
    operation_ids: list[str] = []
    for path_item in path_doc.values():
        for method_doc in path_item.values():
            if isinstance(method_doc, dict) and "operationId" in method_doc:
                operation_ids.append(method_doc["operationId"])
    return operation_ids


def test_video_graph_files_exist_and_are_active():
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
        assert payload["module"] == "video"


def test_video_module_manifest_refs_resolve():
    manifest = _load_yaml(GRAPH_ROOT / "module_manifest.yaml")

    for section in ("global_refs", "module_docs", "contract_surfaces", "runtime_surfaces", "structured_ir"):
        for ref in manifest[section].values():
            _resolve(ref)

    assert manifest["phase"] == "source_graph_rollout"
    assert manifest["known_gaps"]


def test_video_entities_graph_matches_schema_and_runtime():
    entities = _load_yaml(GRAPH_ROOT / "entity_graph.yaml")["entities"]

    entity = entities["MatchMediaSession"]
    _ = _load_json(_resolve(entity["schema_ref"]))
    entity_file, symbol = _resolve_symbol(entity["runtime_entity_ref"])
    entity_source = entity_file.read_text(encoding="utf-8")

    assert entity_file.name == "entities.py"
    assert f"class {symbol}" in entity_source

    for field in entity["sovereign_fields"]:
        assert field["runtime_name"] in entity_source


def test_video_endpoints_graph_matches_openapi_and_runtime_refs():
    endpoints = _load_yaml(GRAPH_ROOT / "endpoints.yaml")["endpoints"]
    openapi_paths = _load_yaml(REPO_ROOT / "contracts" / "openapi" / "paths" / "video.yaml")

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


def test_video_errors_graph_maps_to_real_operations_and_source_refs():
    """video/domain/rules.py usa assert_* functions — não há exception classes soberanas.
    Todos os erros referenciados via source_ref; nenhum via exception_ref.
    """
    endpoints = _load_yaml(GRAPH_ROOT / "endpoints.yaml")["endpoints"]
    operation_ids = {entry["operation_id"] for entry in endpoints}
    errors = _load_yaml(GRAPH_ROOT / "errors.yaml")["errors"]

    for error in errors:
        assert set(error["operations"]) <= operation_ids
        # video usa source_ref; exception_ref não deve estar presente
        assert "exception_ref" not in error, (
            f"ERR {error['id']}: video não usa exception classes — use source_ref"
        )
        if "source_ref" in error:
            source_file, source_symbol = _resolve_symbol(error["source_ref"])
            assert source_symbol in source_file.read_text(encoding="utf-8")


def test_video_test_obligations_cover_graph_contracts_and_runtime():
    obligations = _load_yaml(GRAPH_ROOT / "test_obligations.yaml")["obligations"]
    obligation_ids = {item["id"] for item in obligations}
    assert obligation_ids == {
        "VID-TO-001",
        "VID-TO-002",
        "VID-TO-003",
        "VID-TO-004",
    }

    for obligation in obligations:
        artifact = _resolve(obligation["artifact_ref"])
        assert artifact.exists()
        for evidence_ref in obligation["evidence_refs"]:
            _resolve(evidence_ref)


def test_video_module_docs_and_manifest_reference_source_graph():
    manifest = _load_yaml(REPO_ROOT / "docs" / "_canon" / "DOC_USAGE_MANIFEST.yaml")

    video_graph_entry = next(
        (entry for entry in manifest["entries"] if entry["rule_id"] == "HBTRACK_VIDEO_GRAPH"),
        None,
    )
    assert video_graph_entry is not None, "HBTRACK_VIDEO_GRAPH ausente do DOC_USAGE_MANIFEST"


