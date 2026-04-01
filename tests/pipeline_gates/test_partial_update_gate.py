from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import sys
import textwrap
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR_PATH = ROOT / "scripts" / "contracts" / "validate" / "validate_contracts.py"


def _load_validator_module():
    spec = importlib.util.spec_from_loader(
        "hb_validate_contracts_partial_module",
        importlib.machinery.SourceFileLoader(
            "hb_validate_contracts_partial_module",
            str(VALIDATOR_PATH),
        ),
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


validator = _load_validator_module()


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _base_repo(tmp_path: Path, *, invalid_blocking_subset: bool = False) -> Path:
    _write(tmp_path / "docs" / "_canon" / "SOURCE_AUTHORITY_GRAPH.yaml", "graph: true\n")
    _write(tmp_path / "docs" / "_canon" / "AGENT_INSTRUCTIONS.md", "# agent\n")
    _write(tmp_path / "scripts" / "contracts" / "validate" / "validate_contracts.py", "print('validator')\n")

    blocking_ref = "docs/_canon/NOT_DECLARED.md" if invalid_blocking_subset else "docs/_canon/AGENT_INSTRUCTIONS.md"
    if invalid_blocking_subset:
        _write(tmp_path / "docs" / "_canon" / "NOT_DECLARED.md", "# extra\n")

    _write(
        tmp_path / "docs" / "_canon" / "SYNC_MANIFEST.yaml",
        textwrap.dedent(
            f"""
        version: "1.0.0"
        artifact: "SYNC_MANIFEST"
        status: "active"
        scope: "global"
        policy:
          objective: "test"
          update_mode: "all_required_consumers_must_change_together"
          partial_update_policy: "blocked"
          missing_consumer_status: "FAIL"
          consumer_reference_modes: ["path"]
          enforcement_targets: ["test"]
        rules:
          - rule_id: graph_sync
            source_master: "docs/_canon/SOURCE_AUTHORITY_GRAPH.yaml"
            source_kind: "canon_governance"
            change_types: ["precedence_change"]
            required_consumers:
              - "docs/_canon/AGENT_INSTRUCTIONS.md"
              - "scripts/contracts/validate/validate_contracts.py"
            blocking_consumers:
              - "{blocking_ref}"
            validation_commands:
              - "python3 scripts/validate_contracts.py --profile ci"
        """
        ).lstrip(),
    )
    return tmp_path


def test_partial_update_gate_fails_when_blocking_consumer_is_missing(tmp_path: Path, monkeypatch):
    root = _base_repo(tmp_path)
    monkeypatch.setenv(
        "HB_CHANGED_PATHS_JSON",
        json.dumps(["docs/_canon/SOURCE_AUTHORITY_GRAPH.yaml"]),
    )

    result = validator._g2s_partial_update(root)

    assert result["status"] == "FAIL", result
    assert result["blocking_code"] == "BLOCKED_SYNC_PARTIAL_UPDATE"
    assert any("docs/_canon/AGENT_INSTRUCTIONS.md" in violation["message"] for violation in result["violations"])


def test_partial_update_gate_passes_when_blocking_consumers_are_updated(tmp_path: Path, monkeypatch):
    root = _base_repo(tmp_path)
    monkeypatch.setenv(
        "HB_CHANGED_PATHS_JSON",
        json.dumps(
            [
                "docs/_canon/SOURCE_AUTHORITY_GRAPH.yaml",
                "docs/_canon/AGENT_INSTRUCTIONS.md",
            ]
        ),
    )

    result = validator._g2s_partial_update(root)

    assert result["status"] == "PASS", result
    assert "propagação bloqueante completa" in result["summary"]


def test_partial_update_gate_fails_when_blocking_consumers_are_not_subset(tmp_path: Path, monkeypatch):
    root = _base_repo(tmp_path, invalid_blocking_subset=True)
    monkeypatch.setenv(
        "HB_CHANGED_PATHS_JSON",
        json.dumps(
            [
                "docs/_canon/SOURCE_AUTHORITY_GRAPH.yaml",
                "docs/_canon/NOT_DECLARED.md",
            ]
        ),
    )

    result = validator._g2s_partial_update(root)

    assert result["status"] == "FAIL", result
    assert result["blocking_code"] == "BLOCKED_SYNC_PARTIAL_UPDATE"
    assert any("subconjunto de required_consumers" in violation["message"] for violation in result["violations"])
