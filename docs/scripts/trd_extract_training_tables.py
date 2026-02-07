"""
TRD Verification Script - Extract Training-related tables from schema.sql

Usage:
    python3 docs/scripts/trd_extract_training_tables.py

Output:
    docs/_generated/trd_training_schema_tables.txt
"""

import re
from pathlib import Path

SCHEMA = Path("Hb Track - Backend/docs/_generated/schema.sql")
OUT = Path("docs/_generated/trd_training_schema_tables.txt")

# Tables that belong to Training scope
TRAINING_TABLE_PATTERNS = (
    r"training_sessions",
    r"training_session_exercises",
    r"wellness_pre",
    r"wellness_post",
    r"attendance",
    r"training_cycles",
    r"training_microcycles",
    r"session_templates",
    r"exercises",
    r"exercise_tags",
    r"exercise_favorites",
    r"athlete_badges",
    r"team_wellness_rankings",
    r"training_alerts",
    r"training_suggestions",
    r"training_analytics_cache",
    r"export_jobs",
)

# Pattern to find CREATE TABLE statements
CREATE_TABLE_PATTERN = re.compile(r"CREATE TABLE (?:IF NOT EXISTS )?(?:public\.)?(\w+)")

def main():
    if not SCHEMA.exists():
        print(f"ERROR: {SCHEMA} not found")
        return 1

    content = SCHEMA.read_text(encoding="utf-8")
    all_tables = set(CREATE_TABLE_PATTERN.findall(content))

    # Filter to Training scope
    training_tables = set()
    for table in all_tables:
        if any(re.match(p, table) for p in TRAINING_TABLE_PATTERNS):
            training_tables.add(table)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(sorted(training_tables)) + "\n", encoding="utf-8")
    print(f"N={len(training_tables)} -> {OUT}")

    # Also print tables found but not in our pattern list (potential orphans)
    print(f"\nAll tables in schema: {len(all_tables)}")
    return 0

if __name__ == "__main__":
    exit(main())
