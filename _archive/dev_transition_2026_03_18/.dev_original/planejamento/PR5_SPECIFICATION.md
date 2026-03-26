# PR5 Specification — Phase 6: Legacy Cleanup

## Overview
**Objective:** Remove old evidence model (`boot_resolution_report.json`, `agent_execution/latest.json`) from active pipeline and consolidate on `session_start.json` as sole evidence source.

**Problem Identified:**
- Old evidence model: `_reports/evidence/boot_resolution_report.json` and `_reports/agent_execution/latest.json`
- New evidence model: `_reports/session_start.json` (prova real)
- Dual model: Both old and new in pipeline, causing confusion and divergence
- References scattered in: pre_contract_orchestrator.prompt.md, CONTRACT_PIPELINE.md, TOOLCHAIN_HEALTH_POLICY.md

**Impact:**
- Pipeline carries two evidence models (confusing, conflicting)
- Old report format no longer actively used
- Cleanup streamlines evidence to single source
- Makes SESSION_HANDOFF and reporting cleaner

---

## Current State (Dual Model)

### Old Evidence (Legacy — to be removed)
- `_reports/evidence/boot_resolution_report.json` — Old format (no longer active)
- `_reports/agent_execution/latest.json` — Old format (superseded by session_start.json)
- Referenced in: pre_contract_orchestrator, CONTRACT_PIPELINE, TOOLCHAIN_HEALTH_POLICY

### New Evidence (Current — to be single source)
- `_reports/session_start.json` — New format (active, validated)
- Schema: session_id, task_type, module, stage, artifacts with SHA-256, exit codes
- Actively used by: scripts/hb CLI, validate_contracts.py, SESSION_HANDOFF

---

## PR5 Solution Architecture

### Phase 1: Identify All References
```bash
grep -r "boot_resolution_report\|agent_execution/latest" . --include="*.py" --include="*.md" --include="*.yaml"
```

**Files with references:**
- `.contract_driven/agent_prompts/pre_contract_orchestrator.prompt.md` (line 172)
- `docs/_canon/CONTRACT_PIPELINE.md` (line 64)
- `docs/_canon/TOOLCHAIN_HEALTH_POLICY.md` (line 99)
- `SESSION_HANDOFF.md` (mentions in context)

### Phase 2: Remove References
1. **pre_contract_orchestrator.prompt.md** — Remove line mentioning boot_resolution_report publication
2. **CONTRACT_PIPELINE.md** — Remove boot_resolution_report from evidence list
3. **TOOLCHAIN_HEALTH_POLICY.md** — Remove old evidence references
4. **SESSION_HANDOFF.md** — Update to reference only session_start.json

### Phase 3: Update Documentation
- Update CONTRACT_PIPELINE.md to show session_start.json as sole evidence source
- Update TOOLCHAIN_HEALTH_POLICY.md to reference only active evidence model
- Update pre_contract_orchestrator to handle only session_start.json

### Phase 4: Validation
Verify no references remain:
```bash
grep -r "boot_resolution_report\|agent_execution/latest" . --include="*.py" --include="*.md" --include="*.yaml"
# Should return: 0 matches (only in git history/disabled files)
```

---

## Implementation Steps

### Step 1: Remove from pre_contract_orchestrator.prompt.md
**Location:** Line 172  
**Current:**
```markdown
Publicar `_reports/evidence/boot_resolution_report.json` ao final.
```
**Change to:**
```markdown
Publicar `_reports/session_start.json` com resultado do orchestrator (PASS/BLOCKED/SKIP).
```

### Step 2: Update CONTRACT_PIPELINE.md
**Location:** Line 64 — Remove old evidence references  
**Current:** Lists both `_reports/agent_execution/*.json` and `_reports/evidence/boot_resolution_report.json`  
**Change to:** Single evidence: `_reports/session_start.json`

### Step 3: Update TOOLCHAIN_HEALTH_POLICY.md
**Location:** Line 99  
**Current:** References old evidence format  
**Change to:** Reference only session_start.json

### Step 4: Update SESSION_HANDOFF.md
**Location:** Evidence section  
**Update:** Clarify that session_start.json is sole active evidence

---

## Phase Contract

**What Phase 6 (PR5) Validates:**
- No references to boot_resolution_report.json in active pipeline
- No references to agent_execution/latest.json in active pipeline
- All evidence consolidated to session_start.json
- Documentation updated to reflect single evidence model

**Exit Criteria:**
- grep returns 0 active references to legacy evidence
- Documentation updated
- SESSION_HANDOFF reflects new model
- Tests pass (if any new ones added)

---

## Test Plan (PR5)

### Validation Test
```bash
grep -r "boot_resolution_report\|agent_execution/latest" \
  --include="*.py" --include="*.md" --include="*.yaml" \
  --exclude-dir=.git --exclude-dir=.venv \
  .contract_driven .docs _reports scripts
# Expected: 0 matches (except in disabled files/history)
```

### Documentation Validation
- [ ] pre_contract_orchestrator.prompt.md cleaned
- [ ] CONTRACT_PIPELINE.md shows session_start.json as sole evidence
- [ ] TOOLCHAIN_HEALTH_POLICY.md updated
- [ ] SESSION_HANDOFF.md consistent with new model

---

## Success Criteria

### Definition of Done (PR5)
1. ✅ All references to boot_resolution_report.json removed from active code/docs
2. ✅ All references to agent_execution/latest.json removed from active code/docs
3. ✅ Evidence model consolidated: session_start.json is sole source
4. ✅ Documentation updated and consistent
5. ✅ grep validation returns 0 legacy references
6. ✅ Blocker LEGACY_EVIDENCE_ACTIVE closed
7. ✅ Tests pass (existing + validation)

### Verification
```bash
# 1. Check for legacy references
grep -r "boot_resolution_report\|agent_execution/latest" \
  --include="*.py" --include="*.md" --include="*.yaml" \
  . 2>/dev/null | grep -v ".git" | wc -l
# Expected: 0

# 2. Verify session_start.json mentioned as evidence
grep -n "session_start.json" docs/_canon/CONTRACT_PIPELINE.md
# Expected: Found

# 3. Run tests
pytest tests/pipeline_gates/test_phase_0_determinism.py -v
# Expected: 13 PASSED
```

---

## Dependencies & Sequencing
- **Depends on:** PR1-4 (SSOTs, CLI, Validator, Hook all complete)
- **Blocks:** PR6 (CI/context budgets)
- **Parallel:** None

---

## Risk Assessment

### Low Risk
- Changes are documentation/reference updates
- No code behavior changes
- session_start.json already active and tested
- Can restore old files if needed (git history)

### No Logic Impact
- Evidence reading already uses session_start.json
- Old evidence not actively read
- Just removing stale references

---

## Architecture Benefit

### Before PR5
```
Evidence sources (dual model):
  - session_start.json (new, active)
  - boot_resolution_report.json (old, referenced)
  - agent_execution/latest.json (old, referenced)
Result: Confusion about which is authoritative
```

### After PR5
```
Evidence sources:
  - session_start.json (sole source, authoritative)
Result: Clear single source, no confusion
```

---

## Next Actions (Post-PR5)
1. ✅ PR5 COMPLETE → LEGACY_EVIDENCE_ACTIVE blocker closed
2. PR6 starts: CI regression + context budgets

---

## Files to Modify

| File | Action | Lines |
|------|--------|-------|
| `.contract_driven/agent_prompts/pre_contract_orchestrator.prompt.md` | Remove boot_resolution_report publication | ~172 |
| `docs/_canon/CONTRACT_PIPELINE.md` | Update evidence column | ~64 |
| `docs/_canon/TOOLCHAIN_HEALTH_POLICY.md` | Remove legacy evidence | ~99 |
| `SESSION_HANDOFF.md` | Update context section | varies |

---

## References
- Original execut.md: `.dev/planejamento/execut.md` (Phase 6)
- Current evidence: `_reports/session_start.json`
- Legacy evidence: `_reports/evidence/boot_resolution_report.json` (to be removed from refs)
