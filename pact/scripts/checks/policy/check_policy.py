# HB_SCRIPT_KIND: CHECK
# HB_SCRIPT_SCOPE: POLICY
# HB_SCRIPT_SIDE_EFFECTS: FS_READ
# HB_SCRIPT_ID: CHECK_POLICY_FILES_CONSISTENCY
#
# Exit codes (HB Track canonical):
# 0 PASS
# 2 FAIL_ACTIONABLE (violation/drift)
# 3 ERROR_INFRA (harness error)
# 4 BLOCKED_INPUT (missing required prereq)

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

REPO_POLICY_DIR = Path("scripts") / "_policy"

# SSOT explícito: o check só aceita essas “policy artifacts” canônicas.
# Se você adicionar uma policy nova no futuro, isso DEVE ser atualizado aqui (por design).
REQUIRED_CANONICAL = [
    "scripts.policy.yaml",
    "scripts.policy.schema.json",
    "side_effects_heuristics.yaml",
    "python_layout.policy.yaml",
]

# Além dos required, existem arquivos “esperados” no mesmo diretório (não-policy-data),
# mas que não entram na regra de “confusable names” porque não são policy artifacts.
ALLOWED_NON_POLICY_FILES = {
    "policy_lib.py",
    "check_path_constants.py",
    "generate_manifest.py",
    "render_policy_md.py",
    "policy.manifest.json",
    "requirements.txt",
    "CONTRACT.md",
    "README.md",
    "__init__.py",
}

POLICY_LIKE_PATTERNS = [
    re.compile(r".*policy.*\.ya?ml$", re.IGNORECASE),
    re.compile(r".*\.schema\.json$", re.IGNORECASE),
    re.compile(r".*heuristics.*\.ya?ml$", re.IGNORECASE),
]

def _norm_confusable(name: str) -> str:
    # Remove caracteres não alfanuméricos e baixa o case:
    # "scripts.policy.yaml" ~ "scripts_policy.yaml" ~ "Scripts-Policy.yml"
    return re.sub(r"[^a-z0-9]", "", name.lower())

def _git_ls_files(dir_rel: Path) -> Tuple[int, List[str], str]:
    try:
        p = subprocess.run(
            ["git", "ls-files", str(dir_rel).replace("\\", "/")],
            check=False,
            capture_output=True,
            text=True,
        )
    except Exception as e:
        return 3, [], f"ERROR_INFRA: git invocation failed: {e!r}"
    if p.returncode != 0:
        return 3, [], f"ERROR_INFRA: git ls-files failed (rc={p.returncode}): {p.stderr.strip()}"
    files = [line.strip() for line in p.stdout.splitlines() if line.strip()]
    return 0, files, ""

def main() -> int:
    if not REPO_POLICY_DIR.exists() or not REPO_POLICY_DIR.is_dir():
        print(f"BLOCKED_INPUT: missing directory '{REPO_POLICY_DIR.as_posix()}'")
        return 4

    rc, tracked, err = _git_ls_files(REPO_POLICY_DIR)
    if rc != 0:
        print(err)
        return rc

    basenames = [Path(p).name for p in tracked]
    basename_set = set(basenames)

    # 1) Required canonical files MUST exist (exact casing).
    missing = [f for f in REQUIRED_CANONICAL if f not in basename_set]
    if missing:
        print("BLOCKED_INPUT: required policy artifacts missing:")
        for f in missing:
            print(f" - {f}")
        return 4

    # 2) Detect same-file-different-casing issues (Windows hazard).
    lower_map: Dict[str, List[str]] = {}
    for b in basenames:
        lower_map.setdefault(b.lower(), []).append(b)

    casing_conflicts = []
    for canonical in REQUIRED_CANONICAL:
        variants = lower_map.get(canonical.lower(), [])
        if variants and canonical not in variants:
            casing_conflicts.append((canonical, variants))

    if casing_conflicts:
        print("FAIL_ACTIONABLE: casing conflict detected for canonical required files:")
        for canonical, variants in casing_conflicts:
            print(f" - canonical: {canonical} | present variants: {variants}")
        return 2

    # 3) Detect “confusable duplicates” among policy-like files.
    policy_like = []
    for b in basenames:
        if b in ALLOWED_NON_POLICY_FILES:
            continue
        if any(pat.match(b) for pat in POLICY_LIKE_PATTERNS):
            policy_like.append(b)

    by_norm: Dict[str, List[str]] = {}
    for b in policy_like:
        by_norm.setdefault(_norm_confusable(b), []).append(b)

    confusable = [(k, v) for k, v in by_norm.items() if len(set(v)) > 1]
    if confusable:
        print("FAIL_ACTIONABLE: confusable policy filenames detected (normalize-collision):")
        for k, v in sorted(confusable, key=lambda x: x[0]):
            print(f" - key={k}: {sorted(set(v))}")
        return 2

    # 4) Unknown policy artifacts that “look like policy” but are not explicitly allowed.
    allowed_policy_like = set(REQUIRED_CANONICAL)
    allowed_policy_like |= {f for f in ALLOWED_NON_POLICY_FILES if any(p.match(f) for p in POLICY_LIKE_PATTERNS)}

    unknown_policy_like = [b for b in policy_like if b not in allowed_policy_like]
    if unknown_policy_like:
        print("FAIL_ACTIONABLE: unknown policy-like artifacts present in scripts/_policy (must be explicitly allowlisted):")
        for b in sorted(unknown_policy_like):
            print(f" - {b}")
        return 2

    print("PASS: policy artifacts naming is canonical, unique, and non-confusable.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
