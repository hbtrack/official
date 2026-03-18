# HB TRACK — Refactoring Status Report
> Status: **PR2 ✅ Complete | PR3 Ready for Execution**

## Executive Summary

**Refactoring Goal:** Eliminate non-determinism from pipeline. Transform implicit defaults into explicit, machine-validated requirements across 8 phases.

**Progress:** 
- ✅ **Phase 0-1 Complete** (PR1 + PR2): SSOTs created, CLI hardened, 11/12 tests passing
- ✅ **Blocker Closed:** PIPELINE_NONDETERMINISTIC
- ⏳ **Phase 2-3 Ready:** PR3 specification ready, can execute immediately
- ⏳ **Phase 4-7 Queued:** PR4-PR6 waiting on PR3

**Key Achievement:** `hb` CLI now enforces all required arguments at runtime. No more undefined behavior.

---

## Current State (Post-PR2)

### Test Results
```
tests/pipeline_gates/test_phase_0_determinism.py
  11 PASSED (3 CLI + 8 schema validations)
  1 FAILED (hook divergence — expected for PR4)
  Exitcode: 0 for 11 tests, 1 for divergence
```

### Completed Artifacts
| File | Type | Status | Purpose |
|------|------|--------|---------|
| docs/_canon/BOOT_PROFILES.yaml | SSOT | ✅ Complete | 4 profiles + selection rules |
| docs/_canon/TASK_CATALOG.yaml | SSOT | ✅ Complete | 11 task types (9 active, 2 frozen) |
| contracts/schemas/shared/session_start.schema.json | SSOT | ✅ Complete | Deterministic validation (blocks "unknown") |
| scripts/hb | Python CLI | ✅ v2 Complete | HBCLIv2 with full validation |
| .dev/planejamento/PR1_STATUS.md | Doc | ✅ Complete | PR1 completion report |
| .dev/planejamento/PR2_STATUS.md | Doc | ✅ Complete | PR2 completion report |

### Closed Blockers
| Blocker | Closed By | Status |
|---------|-----------|--------|
| PIPELINE_NONDETERMINISTIC | PR2 | ✅ CLOSED |

### Active Blockers (4 remaining)
| Blocker | Phase | PR |
|---------|-------|-----|
| UI_DOC_VALIDATION_GATE_SEMANTIC_DRIFT | 2-3 | PR3 |
| HOOK_DIVERGENCE | 3-4 | PR4 |
| LEGACY_EVIDENCE_ACTIVE | 4-5 | PR5 |
| CONTEXT_BUDGET_OVERRUN | 6-8 | PR6 |

---

## PR3 Status: Ready To Execute

### What is PR3? 
**Goal:** Make GATES_REGISTRY.yaml the SSOT for gate metadata (blocking status, dependencies, severity)

### The Problem (Semantic Drift)
Currently in `validate_contracts.py`:
- 40+ gates hard-code their own blocking status
- GATES_REGISTRY.yaml is documentation-only, not consulted at runtime
- Example: UI_DOC_VALIDATION_GATE marked blocking=true in registry, but code returns blocking=false
- Result: Impossible to know which gates are actually blocking vs warnings

### The Solution (4 Steps)
1. **Load GATES_REGISTRY.yaml** at pipeline startup
2. **Consult registry** for blocking status in each gate (remove hard-codes)
3. **Define phase contracts** — explicit gate sets for phase 0/1/2
4. **Enforce phase semantics** — phase 0/1/2 failures always exit != 0

### Detailed Spec
→ **See:** `.dev/planejamento/PR3_SPECIFICATION.md` (19 pages, implementation-ready)

### Effort Estimate
- **Code changes:** Modify 40+ gate functions in validate_contracts.py
- **Test additions:** 5 new tests for phase contracts + registry loading
- **Estimated effort:** 2-3 hours development + testing
- **Risk level:** Low (changes localized, GATES_REGISTRY already exists)

---

## Roadmap (PR1 → PR6)

### ✅ PR1 & PR2 (Complete)
- **PR1:** Create SSOTs (BOOT_PROFILES, TASK_CATALOG, session_start.schema)
- **PR2:** Harden CLI (scripts/hb v2, validate required args, eliminate implicit defaults)

### ⏳ PR3 (Ready)
- **PR3:** Align validator with GATES_REGISTRY (resolve semantic drift)
- **Blocker to close:** UI_DOC_VALIDATION_GATE_SEMANTIC_DRIFT

### 📋 PR4 (Queued)
- **PR4:** Unify pre-commit hooks (bash vs python)
- **Blocker to close:** HOOK_DIVERGENCE (turns 1 RED test GREEN)

### 📋 PR5-PR6 (Dependent)
- **PR5:** Remove legacy evidence (old report formats)
- **PR6:** CI regression + context budget enforcement

---

## How to Execute PR3

### Option A: Guided Execution (Recommended)
```bash
# 1. Read specification
cat .dev/planejamento/PR3_SPECIFICATION.md

# 2. Read current implementation (understand hard-coding pattern)
grep -n "blocking.*True\|blocking.*False" scripts/contracts/validate/validate_contracts.py

# 3. Create checklist from PR3_SPECIFICATION.md Implementation Checklist
# 4. Implement step-by-step
# 5. Validate: run tests at each step
```

### Option B: Quick Reference
**Key files to modify:**
- `scripts/contracts/validate/validate_contracts.py` (lines ~7607, ~2429, and 40+ gate functions)
- `tests/pipeline_gates/test_phase_0_determinism.py` (add 5 new gate tests)

**Key changes:**
1. Add `_load_gates_metadata(root)` function (10 lines)
2. Change all `"blocking": True/False` → `"blocking": gates_metadata[gate_id].get("blocking", False)`
3. Add phase contract constants (3 sets of gate IDs)
4. Update exit code logic at end of run_pipeline()

---

## Success Criteria (PR3)
- [ ] GATES_REGISTRY.yaml loads at startup without error
- [ ] UI_DOC_VALIDATION_GATE reports blocking=true (from registry, not hard-coded)
- [ ] 5 new tests pass (phase contracts + registry loading)
- [ ] Exit code behavior respects phase (0/1/2 → always exit != 0 if blocking fail)
- [ ] Blocker **UI_DOC_VALIDATION_GATE_SEMANTIC_DRIFT** marked CLOSED

---

## Decision Point for User

**Question:** Ready to execute PR3?

**Options:**
1. **Yes, proceed with PR3** → Start from `.dev/planejamento/PR3_SPECIFICATION.md`
2. **Yes, I'll help guide** → I'll pair on real-time implementation
3. **No, clarify first** → Ask questions about specification
4. **No, other priority** → We can defer to next session (PR2 is checkpoint)

### What I Need From You
- Confirmation you want to proceed with PR3
- Any questions about the specification before starting
- Time estimate you have available (2-3 hours suggested)

---

## Additional Context

### Determinism Framework (Why This Matters)
The pipeline goal is: **"DONE = exitcode 0, always."**

- **Non-deterministic:** Same input → different output (implicit defaults, magic)
- **Deterministic:** Same input → always same output (explicit, validated)

PR3 moves semantics from "magic implicit blocking" to "machine-readable explicit blocking via GATES_REGISTRY".

### Impact If Skipped
- GATES_REGISTRY remains documentation-only (not SSOT)
- Future gate changes will diverge (code vs docs)
- Impossible to audit which gates are blocking at runtime
- PR4-6 become harder (hook, legacy cleanup, CI regression)

---

## Files You Should Know About

**Core Reference:**
- `.dev/planejamento/execut.md` — Original 8-phase plan (all phases defined)
- `.dev/planejamento/PR3_SPECIFICATION.md` — **Start here for PR3**
- `SESSION_HANDOFF.md` — Current status (this document's sibling)

**Code to Review:**
- `scripts/contracts/validate/validate_contracts.py` — Validator implementation
- `docs/_canon/gates/GATES_REGISTRY.yaml` — Gate metadata (SSOT)
- `scripts/hb` — CLI that will call validator

---

## Questions?
See PR3_SPECIFICATION.md §"Success Criteria" for validation checklist.

---

**Generated:** 2026-03-17 (Session: PR1 Complete → PR2 Complete → PR3 Ready)
**Next Review:** Post-PR3 execution (expected 2026-03-18)
