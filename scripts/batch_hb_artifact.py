#!/usr/bin/env python3
"""Batch-register all staged contract files via hb artifact."""
import subprocess
import sys
from pathlib import Path

result = subprocess.run(
    ["git", "diff", "--cached", "--name-only"],
    capture_output=True, text=True, check=True
)
all_staged = result.stdout.strip().splitlines()

# Files that need hb artifact registration (in contracts/ or .contract_driven/)
to_register = [
    p for p in all_staged
    if p.startswith("contracts/") or p.startswith(".contract_driven/")
]

print(f"Files to register: {len(to_register)}")

errors = []
for path in to_register:
    r = subprocess.run(
        ["python3", "scripts/hb", "artifact", path],
        capture_output=True, text=True
    )
    if r.returncode != 0:
        print(f"  FAIL: {path}")
        print(f"    {r.stderr.strip()}")
        errors.append(path)
    else:
        print(f"  OK: {path}")

print(f"\nDone. {len(to_register) - len(errors)} OK, {len(errors)} FAIL")
if errors:
    sys.exit(1)
