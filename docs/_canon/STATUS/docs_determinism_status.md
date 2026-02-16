# Determinism Maturity Status

**Project:** HB Track Documentation Determinism  
**Last Updated:** 2026-02-16  
**Model:** B — Derived Promoted to SSOT with Verifiable Integrity

---

## Maturity Matrix

| Layer | Name | Status | Description |
|-------|------|--------|-------------|
| **L0** | Structure | ✅ COMPLETE | Files exist, valid YAML/JSON format |
| **L1** | Schema | ✅ COMPLETE | Schema consistency across artifacts |
| **L2** | Integrity | ✅ COMPLETE | SHA-256 checksum verification |
| **L3** | Evidence | ⏳ NOT STARTED | Audit trail, commit binding |
| **L4** | Runtime | ⏳ NOT STARTED | Runtime determinism validation |

---

## Layer Definitions

### L0 — Structure
- Validates that all required files exist
- Validates YAML/JSON/SQL syntax
- **Status:** PASS

### L1 — Schema
- Validates schema consistency between schema.sql, openapi.json
- Ensures no structural drift between generated artifacts
- **Status:** PASS

### L2 — Integrity
- SHA-256 checksum verification against `_manifest.yaml`
- Single-writer enforcement
- **Status:** PASS

### L3 — Evidence (Reserved)
- Commit binding (checksum → git commit)
- Evidence packs for audit
- Baseline diffing
- **Trigger:** When multi-contributor or CI-driven generation begins

### L4 — Runtime (Reserved)
- Runtime determinism validation
- Automated regeneration verification
- **Trigger:** When agents autonomously modify documentation

---

## Decision Gate: When to Advance?

**DO NOT advance to L3/L4 unless one of these triggers appears:**

- [ ] Multiple contributors generating snapshots
- [ ] CI/CD pipelines driving documentation regeneration
- [ ] Need for audit trail in PRs
- [ ] Autonomous agents modifying documentation

**Rationale:** Determinism needs "exposure time" to prove stability. Premature abstraction adds complexity without proportional benefit.

---

## Current Capabilities

| Capability | Enabled |
|------------|---------|
| Single-writer enforcement | ✅ |
| Cryptographic integrity | ✅ |
| Deterministic regeneration | ✅ |
| Automated gate validation | ✅ |
| Baseline freezing | ✅ |
| Audit trail | ⏳ |
| Commit binding | ⏳ |
| Evidence packs | ⏳ |

---

## Recommendation

**Stay at L2 for now.** Use the system in production. Let real usage reveal whether L3 is necessary.

---

## References

- Baseline: `docs/_canon/BASELINES/docs-determinism-v1.md`
- Spec: `docs/_canon/SPECS/SPEC_MODEL_B_DERIVED_PROMOTED_SSOT.md`
- Writer: `docs/_ssot/update_gen.ps1`
- Gate: `scripts/checks/check_hb_track_profile.py`

---

*This status document is updated manually when maturity layer changes occur.*
