from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
GRAPH_DIR = ROOT / "docs" / "_canon" / "graph"


def _load(rel: str) -> dict:
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8"))


def test_global_source_graph_files_exist_and_are_active():
    expected = {
        "global_rules.yaml": "GLOBAL_RULES_IR",
        "global_policies.yaml": "GLOBAL_POLICIES_IR",
        "lifecycle.yaml": "GLOBAL_LIFECYCLE_IR",
        "source_map.yaml": "GLOBAL_SOURCE_MAP_IR",
    }

    for filename, artifact in expected.items():
        path = GRAPH_DIR / filename
        assert path.exists(), f"{filename} deve existir"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert data["artifact"] == artifact
        assert data["status"] == "active"


def test_global_policies_precedence_matches_source_authority_graph():
    policies = _load("docs/_canon/graph/global_policies.yaml")
    source_graph = _load("docs/_canon/SOURCE_AUTHORITY_GRAPH.yaml")

    assert (
        policies["policies"]["precedence"]["precedence_order"]
        == source_graph["policy"]["conflict_resolution"]["precedence_order"]
    )


def test_lifecycle_ir_matches_module_registry_status_order():
    lifecycle = _load("docs/_canon/graph/lifecycle.yaml")
    registry = _load("docs/_canon/MODULE_REGISTRY.yaml")

    assert lifecycle["module_status_order"] == registry["policy"]["status_order"]


def test_source_map_points_to_existing_ir_files_and_sources():
    source_map = _load("docs/_canon/graph/source_map.yaml")

    for concept_id, entry in source_map["concepts"].items():
        ir_file = entry["ir_file"]
        assert (ROOT / ir_file).exists(), f"{concept_id} aponta para IR inexistente: {ir_file}"
        for ref in entry.get("source_refs", []):
            assert (ROOT / ref).exists(), f"{concept_id} aponta para source_ref inexistente: {ref}"


def test_agent_instructions_and_contract_pipeline_cite_structured_ir():
    for rel in ("docs/_canon/AGENT_INSTRUCTIONS.md", "docs/_canon/CONTRACT_PIPELINE.md"):
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "docs/_canon/graph/global_rules.yaml" in text
        assert "docs/_canon/graph/global_policies.yaml" in text
        assert "docs/_canon/graph/lifecycle.yaml" in text
        assert "docs/_canon/graph/source_map.yaml" in text


def test_doc_usage_manifest_covers_global_graph_ir():
    manifest = _load("docs/_canon/DOC_USAGE_MANIFEST.yaml")
    covered = False
    expected = {
        "docs/_canon/graph/global_rules.yaml",
        "docs/_canon/graph/global_policies.yaml",
        "docs/_canon/graph/lifecycle.yaml",
        "docs/_canon/graph/source_map.yaml",
    }

    for entry in manifest.get("entries") or []:
        paths = set(entry.get("paths") or [])
        if expected.issubset(paths):
            covered = True
            break

    assert covered, "DOC_USAGE_MANIFEST.yaml deve cobrir todos os arquivos do IR global"


def test_canon_readme_authorizes_graph_subdirectory():
    text = (ROOT / "docs" / "_canon" / "README.md").read_text(encoding="utf-8")
    assert "`graph/`" in text
