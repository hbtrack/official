---
id: pb_parity_gate_fail
doc_mode: HOWTO
status: CANONICAL
source_of_truth:
  - kind: runtime_evidence
    ref: docs/product/runtime/_INDEX.yaml
depends_on:
  - docs/product/runtime/parity_pipeline.md
evidence_expected: []
---

# Playbook: Parity Gate Failure

## Trigger
- `check_ci_gates_local.ps1` reports schema drift or contract drift
- Generated `schema.sql` or `openapi.json` differs from committed version
- Alembic reports multi-head

## Related runtime scenarios
- `parity_pipeline` — full SSOT regeneration and validation

## Diagnosis

1. Identify which gate failed:
```bash
pwsh scripts/checks/check_ci_gates_local.ps1 2>&1 | grep -i "fail"
```

2. For **schema drift** — compare generated vs committed:
```bash
python scripts/ssot/gen_docs_ssot.py --schema
diff docs/ssot/schema.sql docs/_generated/_core/schema.sql
```

3. For **OpenAPI drift** — compare generated vs committed:
```bash
python scripts/ssot/gen_docs_ssot.py --openapi
diff docs/ssot/openapi.json docs/_generated/_core/openapi.json
```

4. For **multi-head migration**:
```bash
cd "Hb Track - Backend"
alembic heads
```
Expected: single head. If multiple: merge needed.

## Action

| Symptom | Fix |
|---------|-----|
| Schema drift | Regenerate: `python scripts/ssot/gen_docs_ssot.py --schema` then copy to `_generated/_core/` |
| OpenAPI drift | Regenerate: `python scripts/ssot/gen_docs_ssot.py --openapi` then copy to `_generated/_core/` |
| Multi-head | `alembic merge heads -m "merge"` then `alembic upgrade head` |
| Generator import error | `pip install -r requirements.txt` in backend venv |

## Verification
Re-run the `parity_pipeline` runtime scenario. All gates must pass.
