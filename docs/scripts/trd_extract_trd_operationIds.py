"""
TRD Verification Script - Extract operationIds cited in TRD_TRAINING.md

Usage:
    python3 docs/scripts/trd_extract_trd_operationIds.py

Output:
    docs/_generated/trd_training_trd_operationIds.txt
"""

import re
from pathlib import Path

TRD = Path("docs/02-modulos/training/TRD_TRAINING.md")
OUT = Path("docs/_generated/trd_training_trd_operationIds.txt")

# Pattern to match operationIds in backticks (full FastAPI-style operationIds)
# Example: `list_training_sessions_api_v1_training_sessions_get`
PATTERN = re.compile(r"`([a-z0-9_]+_api_v1_[a-z0-9_]+)`")

def main():
    if not TRD.exists():
        print(f"ERROR: {TRD} not found")
        return 1

    content = TRD.read_text(encoding="utf-8")
    ids = set(PATTERN.findall(content))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(sorted(ids)) + "\n", encoding="utf-8")
    print(f"N={len(ids)} -> {OUT}")
    return 0

if __name__ == "__main__":
    exit(main())
