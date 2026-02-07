"""
TRD Verification Script - Extract Training scope operationIds from OpenAPI

Usage:
    python3 docs/scripts/trd_extract_training_openapi_ids.py

Output:
    docs/_generated/trd_training_openapi_operationIds.txt
"""

import json
from pathlib import Path

OPENAPI = Path("Hb Track - Backend/docs/_generated/openapi.json")
OUT = Path("docs/_generated/trd_training_openapi_operationIds.txt")

# Training scope - both hyphen and underscore variants
SCOPE_PREFIXES = (
    "/api/v1/training-sessions",
    "/api/v1/training_sessions",  # underscore variant used in some endpoints
    "/api/v1/wellness-pre",
    "/api/v1/wellness_pre",
    "/api/v1/wellness-post",
    "/api/v1/wellness_post",
    "/api/v1/exercises",
    "/api/v1/exercise-tags",
    "/api/v1/exercise_tags",
    "/api/v1/exercise-favorites",
    "/api/v1/exercise_favorites",
    "/api/v1/training-cycles",
    "/api/v1/training_cycles",
    "/api/v1/training-microcycles",
    "/api/v1/training_microcycles",
    "/api/v1/session-templates",
    "/api/v1/session_templates",
    "/api/v1/training/alerts-suggestions",
    "/api/v1/attendance",
    "/api/v1/analytics/wellness-rankings",
    "/api/v1/analytics/team",
)

def main():
    if not OPENAPI.exists():
        print(f"ERROR: {OPENAPI} not found")
        return 1

    spec = json.loads(OPENAPI.read_text(encoding="utf-8"))
    ids = set()

    for path, methods in spec.get("paths", {}).items():
        if not any(path.startswith(p) for p in SCOPE_PREFIXES):
            continue
        for method, op in methods.items():
            if isinstance(op, dict) and op.get("operationId"):
                ids.add(op["operationId"])

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(sorted(ids)) + "\n", encoding="utf-8")
    print(f"N={len(ids)} -> {OUT}")
    return 0

if __name__ == "__main__":
    exit(main())
