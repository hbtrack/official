"""
Orchestrator: regenerate canonical docs and verify TRD vs OpenAPI/Schema for Training.

Usage:
    python docs/scripts/run_training_docs_checks.py

Exit code:
    1 if any step fails.
"""

from __future__ import annotations

import hashlib
import shutil
import subprocess
import sys
from pathlib import Path
import re


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    backend_script = repo_root / "Hb Track - Backend" / "scripts" / "generate_docs.py"
    docs_scripts = repo_root / "docs" / "scripts"
    invariants_status = repo_root / "docs" / "_generated" / "training_invariants_status.md"

    python_cmd = None
    for candidate in ("python", "python3"):
        if shutil.which(candidate):
            python_cmd = candidate
            break
    if python_cmd is None:
        python_cmd = sys.executable

    required = [
        backend_script,
        docs_scripts / "trd_extract_training_openapi_ids.py",
        docs_scripts / "trd_extract_trd_operationIds.py",
        docs_scripts / "trd_extract_training_tables.py",
        docs_scripts / "trd_extract_trd_tables.py",
        docs_scripts / "trd_extract_training_permissions_report.py",
        docs_scripts / "trd_verify_training.py",
        docs_scripts / "generate_training_invariants_status.py",
    ]

    missing = [str(path) for path in required if not path.exists()]
    if missing:
        print("ERROR: missing required scripts:")
        for path in missing:
            print(f"- {path}")
        return 1

    steps = [
        ([python_cmd, str(backend_script), "--all"], "generate_docs.py --all"),
        ([python_cmd, str(docs_scripts / "trd_extract_training_openapi_ids.py")],
         "trd_extract_training_openapi_ids.py"),
        ([python_cmd, str(docs_scripts / "trd_extract_trd_operationIds.py")],
         "trd_extract_trd_operationIds.py"),
        ([python_cmd, str(docs_scripts / "trd_extract_training_tables.py")],
         "trd_extract_training_tables.py"),
        ([python_cmd, str(docs_scripts / "trd_extract_trd_tables.py")],
         "trd_extract_trd_tables.py"),
        ([python_cmd, str(docs_scripts / "trd_extract_training_permissions_report.py")],
         "trd_extract_training_permissions_report.py"),
        ([python_cmd, str(docs_scripts / "trd_verify_training.py")],
         "trd_verify_training.py"),
        ([python_cmd, str(docs_scripts / "generate_training_invariants_status.py")],
         "generate_training_invariants_status.py"),
    ]

    for cmd, label in steps:
        print(f"[RUN] {label}")
        subprocess.run(cmd, check=True, cwd=repo_root)

    if not invariants_status.exists():
        print(f"ERROR: expected generated file missing: {invariants_status}")
        return 1

    with open(invariants_status, "rb") as handle:
        current_hash = hashlib.sha256(handle.read()).hexdigest()

    regenerate_cmd = [python_cmd, str(docs_scripts / "generate_training_invariants_status.py")]
    subprocess.run(
        regenerate_cmd,
        check=True,
        cwd=repo_root,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )

    with open(invariants_status, "rb") as handle:
        regenerated_hash = hashlib.sha256(handle.read()).hexdigest()

    if current_hash != regenerated_hash:
        print("ERROR: training_invariants_status.md out of sync with INVARIANTS_TRAINING.md")
        print(f"Current hash: {current_hash}")
        print(f"Regenerated hash: {regenerated_hash}")
        print("Re-run: python docs/scripts/generate_training_invariants_status.py")
        return 1

    legacy_pattern = re.compile(r"INV-TRAIN-[PI]\\d{3}")
    skip_dirs = {
        ".git",
        "node_modules",
        "venv",
        "__pycache__",
        ".pytest_cache",
    }
    skip_exts = {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".exe", ".dll", ".so"}

    for path in repo_root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in skip_dirs for part in path.parts):
            continue
        if path.suffix.lower() in skip_exts:
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except Exception:
            continue
        for line in content.splitlines():
            if legacy_pattern.search(line) and "Legacy ID:" not in line:
                print("ERROR: legacy invariant ID found outside Legacy ID field")
                print(f"File: {path}")
                print(f"Line: {line.strip()}")
                return 1

    print("[OK] Training docs checks complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
