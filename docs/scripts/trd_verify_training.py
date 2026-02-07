"""
TRD Verification Script - Compare OpenAPI vs TRD operationIds and report orphans

Usage:
    python3 docs/scripts/trd_verify_training.py

Requires running first:
    python3 docs/scripts/trd_extract_training_openapi_ids.py
    python3 docs/scripts/trd_extract_trd_operationIds.py
    python3 docs/scripts/trd_extract_training_tables.py
    python3 docs/scripts/trd_extract_trd_tables.py

Output:
    docs/_generated/trd_training_verification_report.txt
"""

from pathlib import Path
from datetime import datetime, timezone

OPENAPI_IDS = Path("docs/_generated/trd_training_openapi_operationIds.txt")
TRD_IDS = Path("docs/_generated/trd_training_trd_operationIds.txt")
SCHEMA_TABLES = Path("docs/_generated/trd_training_schema_tables.txt")
TRD_TABLES = Path("docs/_generated/trd_training_trd_tables.txt")
OUT = Path("docs/_generated/trd_training_verification_report.txt")

def load_set(path: Path) -> set:
    if not path.exists():
        return set()
    return set(line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip())

def main():
    openapi_ids = load_set(OPENAPI_IDS)
    trd_ids = load_set(TRD_IDS)
    schema_tables = load_set(SCHEMA_TABLES)
    trd_tables = load_set(TRD_TABLES)

    orphan_endpoints = openapi_ids - trd_ids
    missing_from_openapi = trd_ids - openapi_ids
    orphan_tables = schema_tables - trd_tables
    missing_tables = trd_tables - schema_tables

    report = []
    report.append(f"# TRD Training Verification Report")
    report.append(f"Generated: {datetime.now(timezone.utc).isoformat()}Z")
    report.append("")
    report.append("## Endpoint Counts")
    report.append(f"- OpenAPI (Training scope): {len(openapi_ids)}")
    report.append(f"- TRD cited: {len(trd_ids)}")
    report.append(f"- Orphan endpoints (in OpenAPI, not in TRD): {len(orphan_endpoints)}")
    report.append(f"- Missing from OpenAPI (in TRD, not in OpenAPI): {len(missing_from_openapi)}")
    report.append("")
    report.append("## Table Counts")
    report.append(f"- Schema (Training scope): {len(schema_tables)}")
    report.append(f"- TRD cited tables: {len(trd_tables)}")
    report.append(f"- Orphan tables (in schema, not in TRD): {len(orphan_tables)}")
    report.append(f"- Missing from schema (in TRD, not in schema): {len(missing_tables)}")
    report.append("")

    if orphan_endpoints:
        report.append("## Orphan Endpoints (OpenAPI -> TRD)")
        for eid in sorted(orphan_endpoints):
            report.append(f"- {eid}")
        report.append("")

    if missing_from_openapi:
        report.append("## Missing from OpenAPI (TRD -> OpenAPI)")
        for eid in sorted(missing_from_openapi):
            report.append(f"- {eid}")
        report.append("")

    if orphan_tables:
        report.append("## Orphan Tables (Schema -> TRD)")
        for table in sorted(orphan_tables):
            report.append(f"- {table}")
        report.append("")

    if missing_tables:
        report.append("## Missing Tables (TRD -> Schema)")
        for table in sorted(missing_tables):
            report.append(f"- {table}")
        report.append("")

    report.append("## Training Tables (from schema.sql)")
    for table in sorted(schema_tables):
        report.append(f"- {table}")
    report.append("")

    if trd_tables:
        report.append("## Training Tables Cited in TRD")
        for table in sorted(trd_tables):
            report.append(f"- {table}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"Report written to: {OUT}")
    print(f"\nSummary:")
    print(f"  OpenAPI endpoints: {len(openapi_ids)}")
    print(f"  TRD endpoints: {len(trd_ids)}")
    print(f"  Orphans: {len(orphan_endpoints)}")
    print(f"  Schema tables: {len(schema_tables)}")
    print(f"  TRD tables: {len(trd_tables)}")
    print(f"  Orphan tables: {len(orphan_tables)}")
    return 0

if __name__ == "__main__":
    exit(main())
