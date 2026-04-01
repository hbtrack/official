from __future__ import annotations

import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
SYNC_MANIFEST_PATH = ROOT / "docs" / "_canon" / "SYNC_MANIFEST.yaml"
SOURCE_AUTHORITY_GRAPH_PATH = ROOT / "docs" / "_canon" / "SOURCE_AUTHORITY_GRAPH.yaml"
REPORTS_IMPACT_PATH = ROOT / "generated" / "source_graph" / "reports" / "impact_report.json"


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _looks_like_glob(value: str) -> bool:
    return any(token in value for token in ("*", "?", "["))


def _resolve_ref(ref: str) -> list[Path]:
    if _looks_like_glob(ref):
        return sorted(ROOT.glob(ref))

    target = ROOT / ref
    if target.exists():
        return [target]

    return []


def _rules_by_source_master() -> dict[str, dict]:
    manifest = _load_yaml(SYNC_MANIFEST_PATH)
    return {rule["source_master"]: rule for rule in manifest["rules"]}


def test_sync_manifest_exists_and_is_active():
    assert SYNC_MANIFEST_PATH.exists(), "SYNC_MANIFEST.yaml deve existir"
    manifest = _load_yaml(SYNC_MANIFEST_PATH)

    assert manifest["artifact"] == "SYNC_MANIFEST"
    assert manifest["status"] == "active"
    assert manifest["policy"]["partial_update_policy"] == "blocked"
    assert manifest["policy"]["update_mode"] == "all_required_consumers_must_change_together"
    assert manifest["rules"], "SYNC_MANIFEST precisa declarar regras de sincronismo"


def test_sync_manifest_rules_resolve_sources_consumers_and_validations():
    manifest = _load_yaml(SYNC_MANIFEST_PATH)
    seen_source_masters: set[str] = set()

    for rule in manifest["rules"]:
        rule_id = rule["rule_id"]
        source_master = rule["source_master"]

        assert source_master not in seen_source_masters, f"source_master duplicado: {source_master}"
        seen_source_masters.add(source_master)

        assert _resolve_ref(source_master), f"{rule_id} aponta para source_master inexistente: {source_master}"

        source_inputs = rule.get("source_inputs") or []
        assert isinstance(source_inputs, list)
        for ref in source_inputs:
            assert _resolve_ref(ref), f"{rule_id} aponta para source_input inexistente: {ref}"

        change_types = rule.get("change_types") or []
        assert isinstance(change_types, list) and change_types, f"{rule_id} sem change_types"
        assert all(isinstance(item, str) and item.strip() for item in change_types), (
            f"{rule_id} possui change_types inválidos"
        )

        required_consumers = rule.get("required_consumers") or []
        assert isinstance(required_consumers, list) and required_consumers, (
            f"{rule_id} sem required_consumers"
        )
        for consumer in required_consumers:
            assert _resolve_ref(consumer), f"{rule_id} aponta para consumer inexistente: {consumer}"

        validation_commands = rule.get("validation_commands") or []
        assert isinstance(validation_commands, list) and validation_commands, (
            f"{rule_id} sem validation_commands"
        )
        assert all(isinstance(cmd, str) and cmd.strip() for cmd in validation_commands), (
            f"{rule_id} possui validation_commands inválidos"
        )


def test_sync_manifest_covers_every_source_authority_owner_source():
    graph = _load_yaml(SOURCE_AUTHORITY_GRAPH_PATH)
    expected_sources = {
        concept["owner_source"]
        for concept in graph["concepts"].values()
    }
    actual_sources = set(_rules_by_source_master().keys())

    missing = expected_sources - actual_sources
    assert not missing, f"SYNC_MANIFEST não cobre source_masters soberanos: {sorted(missing)}"


def test_sync_manifest_includes_all_graph_consumers_per_owner_source():
    graph = _load_yaml(SOURCE_AUTHORITY_GRAPH_PATH)
    expected_consumers_by_source: dict[str, set[str]] = {}
    for concept in graph["concepts"].values():
        expected_consumers_by_source.setdefault(concept["owner_source"], set()).update(
            concept.get("consumers") or []
        )

    rules = _rules_by_source_master()
    for owner_source, expected_consumers in expected_consumers_by_source.items():
        actual_consumers = set(rules[owner_source]["required_consumers"])
        missing = expected_consumers - actual_consumers
        assert not missing, (
            f"{owner_source} não cobre consumers declarados no SOURCE_AUTHORITY_GRAPH: {sorted(missing)}"
        )


def test_reports_source_graph_sync_matches_compiler_impact_report():
    impact = json.loads(REPORTS_IMPACT_PATH.read_text(encoding="utf-8"))
    rules = _rules_by_source_master()
    reports_rule = rules["docs/hbtrack/modulos/reports/graph/module_manifest.yaml"]

    expected_consumers = set(impact["impacted_docs"])
    expected_consumers |= set(impact["impacted_contracts"])
    expected_consumers |= set(impact["impacted_runtime"])
    expected_consumers |= set(impact["outputs"])

    actual_consumers = set(reports_rule["required_consumers"])
    missing = expected_consumers - actual_consumers
    assert not missing, f"REPORTS_SOURCE_GRAPH_SYNC sem consumers do impact_report: {sorted(missing)}"


def test_doc_usage_manifest_covers_sync_manifest():
    manifest = _load_yaml(ROOT / "docs" / "_canon" / "DOC_USAGE_MANIFEST.yaml")
    covered = False

    for entry in manifest.get("entries") or []:
        if "docs/_canon/SYNC_MANIFEST.yaml" in (entry.get("paths") or []):
            covered = True
            break

    assert covered, "DOC_USAGE_MANIFEST.yaml deve cobrir SYNC_MANIFEST.yaml"


def test_canon_readme_mentions_sync_manifest():
    text = (ROOT / "docs" / "_canon" / "README.md").read_text(encoding="utf-8")
    assert "SYNC_MANIFEST.yaml" in text
