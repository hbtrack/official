---
id: pb_migrations_drift
doc_mode: HOWTO
status: CANONICAL
source_of_truth:
  - kind: runtime_evidence
    ref: docs/product/runtime/_INDEX.yaml
depends_on:
  - docs/product/runtime/parity_pipeline.md
evidence_expected: []
---

# Playbook: Migrations Drift

## Trigger
- `alembic upgrade head` fails
- `alembic current` shows revision different from expected head
- New model fields not reflected in DB
- Tests fail with "column does not exist" errors

## Related runtime scenarios
- `parity_pipeline` — includes migration state verification

## Diagnosis

1. Check current migration state:
```bash
cd "Hb Track - Backend"
alembic current
alembic heads
alembic history --verbose -r current:head
```

2. Check for unapplied migrations:
```bash
alembic upgrade head --sql  # Preview SQL without applying
```

3. Check for model/schema mismatch:
```bash
alembic check  # Auto-detect model changes not in migrations
```

4. Check if DB is reachable:
```bash
cd "Hb Track - Backend"
python -c "from app.core.config import settings; print(settings.DATABASE_URL)"
```

## Action

| Symptom | Fix |
|---------|-----|
| Unapplied migrations | `alembic upgrade head` |
| Multi-head | `alembic merge heads -m "merge branches"` then `alembic upgrade head` |
| Model changes without migration | `alembic revision --autogenerate -m "description"` then review and apply |
| Corrupted alembic_version | Fix manually: `UPDATE alembic_version SET version_num = '<correct_head>'` |
| DB unreachable | Check `DATABASE_URL` in `.env`, verify PostgreSQL container is running |

## Verification

1. `alembic current` matches `alembic heads` (single head)
2. `alembic check` reports no pending changes
3. Regenerate schema.sql and confirm no unexpected diff:
```bash
python scripts/ssot/gen_docs_ssot.py --schema
```
