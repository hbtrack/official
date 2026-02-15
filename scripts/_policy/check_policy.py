# HB_SCRIPT_KIND=CHECK
# HB_SCRIPT_SCOPE=docs
# HB_SCRIPT_SIDE_EFFECTS=FS_READ,FS_WRITE
# HB_SCRIPT_IDEMPOTENT=YES
# HB_SCRIPT_ENTRYPOINT=python scripts/checks/check_policy_manifest.py
# HB_SCRIPT_OUTPUTS=scripts/artifacts/checks/docs/check_policy_manifest/
# HB_SCRIPT_INPUTS=scripts/_policy/scripts.policy.yaml,scripts/_policy/scripts.policy.schema.json,scripts/_policy/policy.manifest.json
# HB_SCRIPT_RISK=LOW

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

EXIT_PASS = 0
EXIT_FAIL = 2
EXIT_HARNESS = 3

REPO_ROOT_SENTINELS = [".git", "pyproject.toml", "README.md"]


def eprint(msg: str) -> None:
    print(msg, file=sys.stderr)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().lower()


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def find_repo_root(start: Path) -> Path:
    """
    Deterministic repo root finder:
    Walk up until we find a sentinel (.git or pyproject.toml or README.md).
    Fallback: two parents up (scripts/checks/ -> scripts/ -> repo root).
    """
    cur = start.resolve()
    for _ in range(10):
        for s in REPO_ROOT_SENTINELS:
            if (cur / s).exists():
                return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    # fallback assumes location scripts/checks/check_policy_manifest.py
    return start.resolve().parents[2]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8", newline="\n")


def load_yaml(path: Path) -> Dict[str, Any]:
    try:
        import yaml  # type: ignore
    except Exception:
        raise RuntimeError("Missing dependency: PyYAML. Install with: pip install pyyaml")
    data = yaml.safe_load(read_text(path))
    if not isinstance(data, dict):
        raise ValueError("SSOT YAML root must be a mapping/object")
    return data


def maybe_validate_schema(policy: Dict[str, Any], schema_path: Path) -> Tuple[bool, str]:
    """
    Optional JSON Schema validation:
    - If jsonschema installed and schema exists => validate, return (True,"OK") or raise on fail
    - If not installed => (False,"SKIP")
    """
    if not schema_path.exists():
        return (False, "SKIP_NO_SCHEMA_FILE")

    try:
        import jsonschema  # type: ignore
    except Exception:
        return (False, "SKIP_NO_JSONSCHEMA")

    schema = json.loads(read_text(schema_path))
    jsonschema.validate(instance=policy, schema=schema)
    return (True, "OK")


def canonical_json(obj: Any) -> str:
    # Deterministic rendering: sort_keys, indent=2, ensure_ascii=False, LF, trailing newline.
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def _get(d: Dict[str, Any], path: List[str], default: Any = None) -> Any:
    cur: Any = d
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur


def build_manifest(policy: Dict[str, Any], repo_root: Path) -> Dict[str, Any]:
    """
    Build derived manifest from SSOT policy YAML.
    Expected YAML shape (preferred):
      spec: {id, version, status, scope, norm}
      determinism: {rule}
      classification:
        priority: [...]
        folders:
          checks: {kind, prefix, path, subscopes, allowed_side_effects, forbidden_side_effects, ...}
          ...
      script_surface:
        allowed_extensions: [...]
        required_header_fields: [...]
        optional_header_fields: [...]
      side_effects: {enum:[...]}
      checks_contract: {exit_codes:{...}}
    """
    spec = _get(policy, ["spec"], {}) or {}
    determinism = _get(policy, ["determinism"], {}) or {}
    classification = _get(policy, ["classification"], policy) or {}

    priority = classification.get("priority", policy.get("priority", []))
    if not isinstance(priority, list):
        raise ValueError("policy.classification.priority must be a list")

    folders = classification.get("folders", policy.get("folders", {}))
    if not isinstance(folders, dict):
        raise ValueError("policy.classification.folders must be an object")

    allowed_ext = _get(policy, ["script_surface", "allowed_extensions"], [".py", ".ps1", ".sql"])
    required_header = _get(
        policy,
        ["script_surface", "required_header_fields"],
        [
            "HB_SCRIPT_KIND",
            "HB_SCRIPT_SCOPE",
            "HB_SCRIPT_SIDE_EFFECTS",
            "HB_SCRIPT_IDEMPOTENT",
            "HB_SCRIPT_ENTRYPOINT",
            "HB_SCRIPT_OUTPUTS",
        ],
    )
    optional_header = _get(policy, ["script_surface", "optional_header_fields"], ["HB_SCRIPT_INPUTS", "HB_SCRIPT_RISK", "HB_SCRIPT_ROLLBACK"])

    side_effect_enum = _get(policy, ["side_effects", "enum"], ["NONE", "DB_READ", "DB_WRITE", "FS_READ", "FS_WRITE", "ENV_WRITE", "NET"])
    exit_codes = _get(policy, ["checks_contract", "exit_codes"], {"0": "PASS", "2": "FAIL", "3": "HARNESS_ERROR"})

    ssot_yaml_rel = "scripts/_policy/scripts.policy.yaml"
    schema_rel = "scripts/_policy/scripts.policy.schema.json"

    ssot_yaml_abs = repo_root / ssot_yaml_rel
    schema_abs = repo_root / schema_rel

    manifest: Dict[str, Any] = {
        "manifest_version": "1.0.0",
        "derived_from": {
            "ssot_policy_yaml": ssot_yaml_rel,
            "schema_json": schema_rel,
        },
        "spec": {
            "id": spec.get("id", "HB-SCRIPTS-CLASSIFICATION"),
            "version": spec.get("version", "1.0.0"),
            "status": spec.get("status", "APPROVED"),
            "scope": spec.get("scope", "scripts/**"),
            "norm": spec.get("norm", "BCP14 (RFC2119 + RFC8174)"),
        },
        "determinism": {
            "rule": determinism.get("rule", "classify_by_side_effects_then_intent"),
            "tie_break_priority": priority,
        },
        "script_surface": {
            "root": "scripts/",
            "categories": [
                "artifacts",
                "checks",
                "diagnostics",
                "fixes",
                "generate",
                "migrate",
                "ops",
                "reset",
                "run",
                "seeds",
                "temp",
            ],
            "allowed_extensions": allowed_ext,
            "required_header_fields": required_header,
            "optional_header_fields": optional_header,
        },
        "side_effects": {"enum": side_effect_enum},
        "checks_contract": {"exit_codes": exit_codes},
        "folders": {},
        "integrity": {
            "sha256": {
                "ssot_policy_yaml": sha256_file(ssot_yaml_abs) if ssot_yaml_abs.exists() else "",
                "schema_json": sha256_file(schema_abs) if schema_abs.exists() else "",
            },
            "json_render": {"sort_keys": True, "indent": 2, "ensure_ascii": False, "newline": "LF"},
        },
    }

    # Deterministic folder order: sorted keys
    for name in sorted(folders.keys()):
        manifest["folders"][name] = folders[name]

    return manifest


def compare_files(expected_text: str, actual_path: Path) -> bool:
    if not actual_path.exists():
        return False
    actual_text = read_text(actual_path)
    # Normalize newlines to LF for comparison (Windows-safe)
    expected_norm = expected_text.replace("\r\n", "\n").replace("\r", "\n")
    actual_norm = actual_text.replace("\r\n", "\n").replace("\r", "\n")
    return expected_norm == actual_norm


def write_diff_artifacts(art_dir: Path, expected_path: Path, actual_path: Path) -> None:
    """
    Deterministic minimal diff:
    - writes expected regen file already
    - writes simple line-based diff summary
    """
    exp_lines = read_text(expected_path).replace("\r\n", "\n").split("\n")
    act_lines = read_text(actual_path).replace("\r\n", "\n").split("\n") if actual_path.exists() else []

    # Find first mismatch for a stable signal
    max_len = max(len(exp_lines), len(act_lines))
    first_idx = None
    for i in range(max_len):
        a = act_lines[i] if i < len(act_lines) else "<EOF>"
        e = exp_lines[i] if i < len(exp_lines) else "<EOF>"
        if a != e:
            first_idx = i
            break

    diff_path = art_dir / "policy.manifest.diff.txt"
    out: List[str] = []
    out.append("MANIFEST_DIFF=1")
    out.append(f"EXPECTED={expected_path.as_posix()}")
    out.append(f"ACTUAL={actual_path.as_posix()}")
    out.append("")
    if first_idx is None:
        out.append("No line mismatch found (unexpected).")
    else:
        out.append(f"FIRST_MISMATCH_LINE={first_idx+1}")
        out.append("ACTUAL_LINE=" + (act_lines[first_idx] if first_idx < len(act_lines) else "<EOF>"))
        out.append("EXPECTED_LINE=" + (exp_lines[first_idx] if first_idx < len(exp_lines) else "<EOF>"))
    out.append("")
    out.append("HINT: Re-render manifest and commit:")
    out.append("  python scripts/_policy/render_policy_manifest.py")
    write_text(diff_path, "\n".join(out) + "\n")


def main() -> int:
    here = Path(__file__).resolve()
    repo_root = find_repo_root(here.parent)

    yaml_path = repo_root / "scripts/_policy/scripts.policy.yaml"
    schema_path = repo_root / "scripts/_policy/scripts.policy.schema.json"
    manifest_path = repo_root / "scripts/_policy/policy.manifest.json"

    art_dir = repo_root / "scripts/artifacts/checks/docs/check_policy_manifest"
    ensure_dir(art_dir)

    try:
        if not yaml_path.exists():
            eprint(f"[HARNESS] Missing SSOT YAML: {yaml_path}")
            return EXIT_HARNESS

        policy = load_yaml(yaml_path)

        validated, schema_msg = maybe_validate_schema(policy, schema_path)
        # Build derived manifest and write regen to artifacts for debugging
        manifest_obj = build_manifest(policy, repo_root)
        regen_text = canonical_json(manifest_obj)

        regen_path = art_dir / "policy.manifest.regen.json"
        write_text(regen_path, regen_text)

        ok = compare_files(regen_text, manifest_path)
        if not ok:
            if not manifest_path.exists():
                eprint(f"[FAIL] Missing derived manifest: {manifest_path}")
            else:
                eprint("[FAIL] policy.manifest.json drift detected (regen != committed).")
            write_diff_artifacts(art_dir, regen_path, manifest_path)
            return EXIT_FAIL

        # PASS summary line (deterministic)
        yaml_sha = sha256_file(yaml_path)
        msg = f"OK_POLICY_MANIFEST exit=0 sha256_yaml={yaml_sha}"
        if validated:
            msg += " schema=OK"
        else:
            msg += f" schema={schema_msg}"
        print(msg)
        return EXIT_PASS

    except Exception as ex:
        err_path = art_dir / "policy.manifest.error.txt"
        write_text(err_path, f"[HARNESS] {type(ex).__name__}: {ex}\n")
        eprint(f"[HARNESS] Unexpected error. See: {err_path}")
        return EXIT_HARNESS


if __name__ == "__main__":
    raise SystemExit(main())


scripts/_policy/side_effects_heuristics.yaml