"""
TRD Verification Script - Extract Training tables cited in TRD_TRAINING.md

Usage:
    python3 docs/scripts/trd_extract_trd_tables.py

Output:
    docs/_generated/trd_training_trd_tables.txt
"""

import re
from pathlib import Path

TRD = Path("docs/02-modulos/training/TRD_TRAINING.md")
OUT = Path("docs/_generated/trd_training_trd_tables.txt")

# Explicit list of Training tables (schema allowlist)
TRAINING_TABLES = {
    "training_sessions",
    "training_session_exercises",
    "wellness_pre",
    "wellness_post",
    "attendance",
    "training_cycles",
    "training_microcycles",
    "session_templates",
    "exercises",
    "exercise_tags",
    "exercise_favorites",
    "athlete_badges",
    "team_wellness_rankings",
    "training_alerts",
    "training_suggestions",
    "training_analytics_cache",
    "export_jobs",
}

# Match backticked identifiers and filter to known tables
BACKTICK_PATTERN = re.compile(r"`([a-z_]+)`")


def main() -> int:
    if not TRD.exists():
        print(f"ERROR: {TRD} not found")
        return 1

    content = TRD.read_text(encoding="utf-8")
    ids = {name for name in BACKTICK_PATTERN.findall(content) if name in TRAINING_TABLES}

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(sorted(ids)) + "\n", encoding="utf-8")
    print(f"N={len(ids)} -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
