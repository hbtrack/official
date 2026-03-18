# PR3 Specification — Phase 4: Validator Deterministic

## Overview
**Objective:** Align `scripts/contracts/validate/validate_contracts.py` with `docs/_canon/gates/GATES_REGISTRY.yaml`

**Problem Identified:** 
- GATES_REGISTRY.yaml is SSOT for gate metadata (blocking status, dependencies, order, etc.)
- validate_contracts.py hard-codes blocking logic without consulting GATES_REGISTRY
- Result: semantic divergence — registry says blocking=true, code may execute as non-blocking
- Example: `UI_DOC_VALIDATION_GATE` marked blocking=true in registry, but code returns _skip() when no UI

**Impact:** 
- Gates execute with incorrect blocking semantics
- GATES_REGISTRY becomes documentation-only, not SSOT
- Impossible to know at runtime which gates are blocking vs warning

---

## Semantic Drift Analysis

### Current State (Broken)
```python
# validate_contracts.py — hard-codes blocking logic
def _g14_ui_doc_validation(root: pathlib.Path) -> dict:
    # No consultation of GATES_REGISTRY
    # Returns _skip() when no UI contracts (same as non-blocking)
    # but GATES_REGISTRY says blocking: true
    return _pg(gate_id, "PASS", False, None, ...)  # blocking=False hard-coded
```

### GATES_REGISTRY Truth
```yaml
- gate_id: UI_DOC_VALIDATION_GATE
  order: 14
  name: "UI Documentation Validation Gate"
  blocking: true                          # ← SSOT says blocking=true
  severity: HIGH
  parallelizable: true
  applies_when: ui_documentation_present
  depends_on: [CROSS_SPEC_ALIGNMENT_GATE]
  description: "Executa `storybook build` quando houver UI documentada."
  blocking_codes: [UI_DOC_BUILD_FAILED]
  status: active
```

### Divergence Mechanism
1. **Code reads gate result from `_g14_ui_doc_validation()`**
   - Hard-codes `blocking=False` in return dict
   - No runtime consultation of GATES_REGISTRY.yaml

2. **Pipeline logic checks blocking status**
   ```python
   blocking_fails = [g for g in gates if g.get("blocking") and g.get("status") == "FAIL"]
   if blocking_fails:
       overall = "FAIL"
       exit_code = 3  # or 2
   ```

3. **Result:** Even if GATES_REGISTRY says blocking=true, gate execution doesn't honor it

---

## PR3 Solution Architecture

### Phase 1: Load GATES_REGISTRY.yaml at Startup
```python
def run_pipeline(...):
    # NEW: Load GATES_REGISTRY as SSOT
    registry_path = root / "docs" / "_canon" / "gates" / "GATES_REGISTRY.yaml"
    gates_registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    gates_metadata = {g["gate_id"]: g for g in gates_registry["gates"]}
    # gates_metadata["UI_DOC_VALIDATION_GATE"]["blocking"] == True
```

### Phase 2: Lookup Blocking Status Before Returning
```python
def _g14_ui_doc_validation(root, gates_metadata):  # Pass registry as param
    # ... validation logic ...
    blocking = gates_metadata.get("UI_DOC_VALIDATION_GATE", {}).get("blocking", False)
    return _pg(gate_id, status, blocking, blocking_code, ...)  # Use registry value
```

### Phase 3: Define Phase Contracts
Each stage (Fase 0/1/2) must explicitly define which gates validate what:

**Fase 0: SESSION_BOOT (--stage session-start)**
- Validates: Session state machine initialization
- Gates: AXIOM_INTEGRITY_GATE, HANDOFF_COHERENCE_GATE, MODULE_STATUS_COHERENCE_GATE
- Result: session_start.json must be created with _reports/session_start.json

**Fase 1: PRE_AUTHORING (--stage pre-authoring)**
- Validates: Module readiness before contract authoring
- Gates: AXIOM_INTEGRITY_GATE, MODULE_REGISTRY_GATE, REQUIRED_ARTIFACT_PRESENCE_GATE, ADVERSARIAL_ANALYSIS_GATE, CROSS_MODULE_BOUNDARY_GATE
- Result: Module contract meta-structure validated

**Fase 2: ARTIFACT (--stage artifact)**
- Validates: Individual artifact validity (OpenAPI, JSON Schema, AsyncAPI, Arazzo, UI)
- Gates: AXIOM_INTEGRITY_GATE, PATH_CANONICALITY_GATE, PLACEHOLDER_RESIDUE_GATE, JSON_SCHEMA_VALIDATION_GATE, UI_DOC_VALIDATION_GATE, CROSS_MODULE_BOUNDARY_GATE, OPENAPI_ROOT_STRUCTURE_GATE
- Result: Artifact hash stored in session, gate violations recorded

### Phase 4: Enforce Phase-Specific Fail Semantics
```python
def run_pipeline(stage=None, ...):
    # NEW: Phase-specific fail handling
    if stage in ("session-start", "pre-authoring", "artifact"):
        # FAIL in phase 0/1/2 is ALWAYS blocking, ALWAYS exit != 0
        blocking_fails = [g for g in gates if g.get("blocking") and g.get("status") == "FAIL"]
        if blocking_fails:
            overall = "FAIL"
            exit_code = 2  # or specific code per phase
            return report, exit_code
    else:
        # Full CI pipeline: FAIL only if blocking_fail
        blocking_fails = [g for g in gates if g.get("blocking") and g.get("status") == "FAIL"]
        if blocking_fails:
            overall = "FAIL"
            exit_code = 3
```

---

## Implementation Checklist

### Step 1: Load GATES_REGISTRY.yaml
- [ ] Add `import yaml` to imports (or use existing JSON parser)
- [ ] Create `_load_gates_metadata(root)` function
- [ ] Call in `run_pipeline()` before phase-specific gate filtering
- [ ] Validate registry structure (all gate_ids, blocking field present)

### Step 2: Update Each Gate to Use Registry
- [ ] _g1_path_canonicality() → consult gates_metadata["PATH_CANONICALITY_GATE"].blocking
- [ ] _g14_ui_doc_validation() → consult gates_metadata["UI_DOC_VALIDATION_GATE"].blocking
- [ ] (Apply to all 40+ gates)
- [ ] Update `_pg()` calls to use correct blocking value

### Step 3: Define Phase Contracts in Code
- [ ] Create constants for phase gate sets:
  ```python
  _PHASE0_GATES = {"AXIOM_INTEGRITY_GATE", "HANDOFF_COHERENCE_GATE", ...}
  _PHASE1_GATES = {"AXIOM_INTEGRITY_GATE", "MODULE_REGISTRY_GATE", ...}
  _PHASE2_GATES = {"AXIOM_INTEGRITY_GATE", "PATH_CANONICALITY_GATE", ...}
  ```
- [ ] Update `_maybe()` to consult phase gates from code (not registry)
- [ ] Document phase contracts in docstring

### Step 4: Enforce Phase-Specific Fail Semantics
- [ ] Modify exit_code logic to respect phase (0/1/2 = always exit != 0 if blocking fail)
- [ ] Update `overall` status assignment
- [ ] Add comment explaining phase semantics

### Step 5: Test & Validate
- [ ] Verify GATES_REGISTRY loads without error
- [ ] Check UI_DOC_VALIDATION_GATE returns blocking=true (from registry)
- [ ] Verify gate blocking status matches registry at runtime
- [ ] Confirm phase contracts match phase execution

---

## Code Regions to Modify

### File: `scripts/contracts/validate/validate_contracts.py`

**Region 1: Imports (line ~1-50)**
- Add YAML loader if not present

**Region 2: run_pipeline() function (line ~7607)**
- Add gates_metadata loading after axioms loading
- Pass gates_metadata to all gate functions
- Update phase-specific handling

**Region 3: _pg() helper (line ~2429)**
- Already has `blocking` parameter — no change needed

**Region 4: Each gate function (lines _g1_, _g2_, ... _g14_, etc.)**
- Change `"blocking": True` → `"blocking": gates_metadata["GATE_ID"].get("blocking", False)`
- Change `"blocking": False` → `"blocking": gates_metadata["GATE_ID"].get("blocking", False)`

**Region 5: Blocking fail logic (line ~7893)**
```python
# OLD
blocking_fails = [g for g in gates if g.get("blocking") and g.get("status") == "FAIL"]

# NEW
blocking_fails = [g for g in gates if g.get("blocking") and g.get("status") == "FAIL"]
if stage in ("session-start", "pre-authoring", "artifact"):
    # Phase 0/1/2: any blocking fail → FAIL + exit != 0
    exit_code = 2 if blocking_fails else 0
else:
    # Full CI: same semantics
    exit_code = 3 if blocking_fails else 0
```

---

## Test Plan (PR3)

### Existing Tests (Will Configure to Green)
- Test that GATES_REGISTRY loads without error ✅
- Test that UI_DOC_VALIDATION_GATE has blocking=true at runtime ✅
- Test that gate blocking status comes from registry (not hard-coded) ✅

### New Tests (Will Create)
- [ ] test_gates_registry_loaded_successfully
- [ ] test_ui_doc_validation_gate_blocking_true_from_registry
- [ ] test_phase0_all_blocking_gates_cause_exit_nonzero
- [ ] test_phase1_gate_set_matches_registry
- [ ] test_phase2_gate_set_matches_registry

### Validation
- Run: `python scripts/contracts/validate/validate_contracts.py --stage artifact --artifact <PATH>`
- Expect: Gate blocking status from GATES_REGISTRY
- Validate with: `jq '.gates[] | select(.gate_id=="UI_DOC_VALIDATION_GATE") | .blocking' _reports/contract_gates/latest.json`

---

## Success Criteria

### Definition of Done (PR3)
1. ✅ GATES_REGISTRY.yaml is loaded at pipeline startup
2. ✅ All 40+ gates consult registry for blocking status (no hard-coding)
3. ✅ Phase contracts explicitly defined (phase 0/1/2 gate sets)
4. ✅ Phase-specific fail semantics enforced (0/1/2 → exit != 0 if blocking fail)
5. ✅ Blocker closed: UI_DOC_VALIDATION_GATE_SEMANTIC_DRIFT
6. ✅ Tests validate gate blocking status comes from GATES_REGISTRY
7. ✅ Documentation in code explains phase semantics
8. ✅ Exit code behavior documented in `--help`

### Verification
```bash
# Should show blocking=true from registry
python scripts/contracts/validate/validate_contracts.py --stage artifact --artifact contracts/openapi/openapi.yaml 2>&1 | jq '.gates[] | select(.gate_id=="UI_DOC_VALIDATION_GATE") | {gate_id, blocking, status}'

# Output:
# {
#   "gate_id": "UI_DOC_VALIDATION_GATE",
#   "blocking": true,
#   "status": "PASS"
# }
```

---

## Dependencies & Sequencing
- **Depends on:** PR1 (SSOTs must exist), PR2 (CLI must load SSOTs)
- **Blocks:** PR4 (hook unification), PR5 (legacy cleanup)
- **Parallel:** None (linear PR sequence)

---

## Risk Assessment

### Low Risk
- Changes are localized to validate_contracts.py
- GATES_REGISTRY already exists and is valid YAML
- Gate implementations don't change (only blocking source)

### Medium Risk
- All 40+ gate functions must be updated
- Easy to miss a gate and leave hard-coded blocking
- Must test all phases (0/1/2)

### Mitigation
- Use regex to find all hard-coded blocking values
- Add linter rule: no `"blocking": True/False` in gate functions (must use registry)
- Run full test suite for each phase

---

## Rollback Plan
If PR3 fails:
1. Revert changes to validate_contracts.py
2. Return to hard-coded blocking values
3. Keep GATES_REGISTRY as documentation-only (not SSOT until PR3 valid)
4. Schedule re-attempt with code review

---

## Next Actions (Post-PR3)
1. ✅ PR3 COMPLETA → UI_DOC_VALIDATION_GATE_SEMANTIC_DRIFT blocker closed
2. PR4 starts: Hook divergence (bash vs python)
3. PR5 starts: Legacy evidence cleanup
4. PR6 starts: CI regression + context budgets

---

## References
- GATES_REGISTRY.yaml: `docs/_canon/gates/GATES_REGISTRY.yaml`
- Validator: `scripts/contracts/validate/validate_contracts.py`
- Phase contracts: This document (§Phase 3)
- Original execut.md: `.dev/planejamento/execut.md` (Phase 4)
