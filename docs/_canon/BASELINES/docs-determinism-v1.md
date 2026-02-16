# Baseline Snapshot — docs-determinism-v1

**Version:** 1.0  
**Date:** 2026-02-16  
**Status:** FROZEN  
**Git Commit:** `c4c4a79e3b8786a81abe47ba90da9aa5993018ba`

---

## 1. Writer Command (Single Source of Truth)

```powershell
pwsh docs/_ssot/update_gen.ps1
```

**Location:** `docs/_ssot/update_gen.ps1`  
**Purpose:** Generates schema.sql, openapi.json, alembic_state.txt and updates integrity manifest.

---

## 2. Integrity SSOT

**File:** `docs/_ssot/_manifest.yaml`

```
83664a1eb17c5757405f72cb5b1608d797b3062895b64d7827b9d06c7b1f9a49  schema.sql
aaf8ec0960ea2a37ce01e414d34d648b560c0d0b9ede4b317d49835bc9c91455  openapi.json
d52276f724b68be0c6dbe2e5f9f5fb9a08717c62affb0854fc45d51b3faffdaf  alembic_state.txt
```

**Algorithm:** SHA256

---

## 3. Gates Status

| Layer | Status | Notes |
|-------|--------|-------|
| L0 Structure | ✅ PASS | YAML/JSON/SQL files present and valid |
| L1 Schema | ✅ PASS | Schema consistency across artifacts |
| L2 Integrity | ✅ PASS | Checksums match manifest |
| L3 Evidence | ⏳ Not started | Reserved for future |
| L4 Runtime | ⏳ Not started | Reserved for future |

---

## 4. Invariants Enforced

- **Single-writer invariant:** Only `pwsh docs/_ssot/update_gen.ps1` may update artifacts
- **Bundle-integrity invariant:** All checksums must match `_manifest.yaml`
- **Deterministic-regeneration invariant:** Same input produces identical output

---

## 5. Threat Model Coverage

| Threat | Protected |
|--------|-----------|
| Silent manual edits | ✅ Checksum mismatch triggers gate failure |
| Parallel writers | ✅ Single-writer command enforced |
| Structural drift | ✅ Schema validation gates |
| Agent hallucination | ✅ SSOT with verifiable integrity |

---

## 6. Drift Detection

To detect drift from this baseline:

```powershell
# Compare current checksums with baseline
diff (Get-Content docs/_canon/BASELINES/docs-determin) ...
ism-v1.md```

---

**This baseline is frozen. Any changes require a new baseline version.**
