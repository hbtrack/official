---
id: parity_pipeline
doc_mode: HOWTO
status: CANONICAL
source_of_truth:
  - kind: ssot_factual
    ref: docs/_canon/HB_TRACK_PROFILE.yaml
depends_on:
  - docs/product/ARCHITECTURE.md
evidence_expected:
  - docs/_generated/_reports/tasks/parity_pipeline.log
  - docs/ssot/schema.sql
  - docs/ssot/openapi.json
---

# Runtime Scenario: Parity Pipeline (SSOT Generation + Validation)

## Goal
Regenerate SSOT artifacts (schema.sql, openapi.json) and validate consistency between code, DB, and documentation.

## Preconditions
- PostgreSQL running with current migrations applied
- Backend dependencies installed
- Python available with PyYAML

## Steps

1. Apply latest migrations:
```bash
cd "Hb Track - Backend"
alembic upgrade head
alembic current
```
Expected: All migrations applied, single head.

2. Generate SSOT artifacts:
```bash
cd "/c/HB TRACK"
python scripts/ssot/gen_docs_ssot.py --all
```
Expected: Files generated in docs/ssot/ (schema.sql, openapi.json, alembic_state.txt, manifest.json).

4. Run L0/L1 gate:
```bash
python scripts/checks/check_hb_track_profile.py
```
Expected: PASS.

5. Run local CI gates:
```bash
pwsh scripts/checks/check_ci_gates_local.ps1 -SkipDocsIndex
```
Expected: All gates pass (or known non-blocking failures documented).

## Expected outcomes
- schema.sql reflects current Alembic state
- openapi.json matches running FastAPI app
- No migration multi-head (single head only)
- Gates produce deterministic PASS/FAIL with exit codes

## Failure modes
- **Multi-head migration:** `alembic heads` shows >1 head; merge required
- **Schema drift:** Generated schema.sql differs from last committed version; investigate new migration
- **OpenAPI drift:** Endpoint signatures changed; update contract tests
- **Generator import error:** Missing dependencies; check `requirements.txt`

## Rollback
SSOT artifacts are derived — regenerate from source at any time. No destructive state.
