from __future__ import annotations

import hashlib
import pathlib
import textwrap

import yaml

from scripts.contracts.validate.api.policy_compiler import detect_global_input_recompile_gap


def _write(path: pathlib.Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")


def _sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _make_global_inputs(tmp_path: pathlib.Path) -> dict[str, pathlib.Path]:
    files = {
        ".contract_driven/templates/api/ARCHITECTURE_MATRIX.yaml": "modules: {}\n",
        ".contract_driven/templates/api/MODULE_PROFILE_REGISTRY.yaml": "modules: {}\n",
        ".contract_driven/templates/api/api_rules.yaml": "hbtrack_api_rules: {}\n",
        ".contract_driven/templates/api/CANONICAL_TYPE_REGISTRY.yaml": "base_types: {}\nderived_types: {}\n",
        ".contract_driven/DOMAIN_AXIOMS.json": "{\"domain_axioms\": {}}\n",
    }
    out: dict[str, pathlib.Path] = {}
    for relpath, content in files.items():
        path = tmp_path / relpath
        _write(path, content)
        out[relpath] = path
    return out


def _write_manifest(tmp_path: pathlib.Path, *, source_hashes: dict[str, str]) -> None:
    manifest = {
        "traceability_manifest": {
            "artifact_id": "users.sync.openapi",
            "source_inputs": [
                {"path": relpath, "sha256": sha}
                for relpath, sha in source_hashes.items()
            ],
        }
    }
    path = tmp_path / "generated" / "manifests" / "users.sync.traceability.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")


def test_detect_global_input_recompile_gap_returns_empty_when_manifests_are_fresh(tmp_path: pathlib.Path):
    inputs = _make_global_inputs(tmp_path)
    _write_manifest(tmp_path, source_hashes={relpath: _sha256(path) for relpath, path in inputs.items()})

    assert detect_global_input_recompile_gap(tmp_path) == {}


def test_detect_global_input_recompile_gap_aggregates_stale_global_source(tmp_path: pathlib.Path):
    inputs = _make_global_inputs(tmp_path)
    current_hashes = {relpath: _sha256(path) for relpath, path in inputs.items()}
    stale_hashes = dict(current_hashes)
    stale_hashes[".contract_driven/DOMAIN_AXIOMS.json"] = "0" * 64
    _write_manifest(tmp_path, source_hashes=stale_hashes)

    result = detect_global_input_recompile_gap(tmp_path)

    assert result == {
        ".contract_driven/DOMAIN_AXIOMS.json": ["generated/manifests/users.sync.traceability.yaml"],
    }
