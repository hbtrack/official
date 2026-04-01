from __future__ import annotations

from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).parents[2]
GRAPH_PATH = REPO_ROOT / "docs" / "_canon" / "SOURCE_AUTHORITY_GRAPH.yaml"


def _load_graph() -> dict:
    with open(GRAPH_PATH, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def test_source_authority_graph_exists_and_loads():
    assert GRAPH_PATH.exists(), "SOURCE_AUTHORITY_GRAPH.yaml deve existir"
    data = _load_graph()
    assert data["artifact"] == "SOURCE_AUTHORITY_GRAPH"
    assert data["status"] == "active"
    assert isinstance(data.get("concepts"), dict) and data["concepts"], "grafo deve declarar conceitos"


def test_source_authority_graph_declares_required_classifications():
    data = _load_graph()
    vocab = data["policy"]["classification_vocab"]
    assert set(vocab.keys()) == {"sovereign", "derived", "bridge", "runtime_extension"}


def test_source_authority_graph_owner_sources_resolve():
    data = _load_graph()
    for concept_id, concept in data["concepts"].items():
        owner = concept.get("owner_source")
        assert owner, f"{concept_id} sem owner_source"
        if owner == "self":
            continue
        target = REPO_ROOT / owner
        assert target.exists(), f"{concept_id} aponta para owner_source inexistente: {owner}"


def test_source_authority_graph_artifacts_resolve():
    data = _load_graph()
    for concept_id, concept in data["concepts"].items():
        for artifact in concept.get("artifacts", []):
            target = REPO_ROOT / artifact
            assert target.exists(), f"{concept_id} referencia artefato inexistente: {artifact}"


def test_source_authority_graph_is_cited_by_canonical_authorities():
    expected_ref = "SOURCE_AUTHORITY_GRAPH.yaml"
    for rel in [
        "docs/_canon/AGENT_INSTRUCTIONS.md",
        "docs/_canon/CONTRACT_PIPELINE.md",
        ".contract_driven/CONTRACT_SYSTEM_RULES.md",
    ]:
        text = (REPO_ROOT / rel).read_text(encoding="utf-8")
        assert expected_ref in text, f"{rel} deve citar SOURCE_AUTHORITY_GRAPH.yaml"


def test_doc_usage_manifest_covers_source_authority_graph():
    manifest = yaml.safe_load((REPO_ROOT / "docs" / "_canon" / "DOC_USAGE_MANIFEST.yaml").read_text(encoding="utf-8"))
    entries = manifest.get("entries") or []
    covered = False
    for entry in entries:
        if "docs/_canon/SOURCE_AUTHORITY_GRAPH.yaml" in (entry.get("paths") or []):
            covered = True
            break
    assert covered, "DOC_USAGE_MANIFEST.yaml deve cobrir SOURCE_AUTHORITY_GRAPH.yaml"
