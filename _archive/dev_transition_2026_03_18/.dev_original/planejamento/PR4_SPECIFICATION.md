# PR4 Specification — Phase 5: Hook Unified and Strong

## Overview
**Objective:** Unify pre-commit hook via `git config core.hooksPath` and eliminate divergence between versionado (bash) and instalado (python) hooks.

**Problem Identified:**
- scripts/git-hooks/pre-commit (bash, versionado)
- .git/hooks/pre-commit (python, instalado locally)
- Divergence: code in repo ≠ code running locally
- Result: 1 RED test (test_git_hook_divergence) demonstrating loophole

**Impact:**
- Impossible to track hook changes (no single source)
- Local changes to hook don't sync to repository
- Test unification failing

---

## Current State (Broken)

### Two Hook Sources
```
scripts/git-hooks/pre-commit        ← Versionado no git (bash)
.git/hooks/pre-commit               ← Instalado localmente (python)
                                     ← Diferentes = problema
```

### Problem Mechanism
1. Developer modifies hook in repo (scripts/git-hooks/pre-commit)
2. Git doesn't pick up changes (uses .git/hooks/pre-commit)
3. Outdated python hook runs instead of new bash version
4. Test fails: `assert versionado == instalado`

---

## PR4 Solution Architecture

### Phase 1: Configure git core.hooksPath
```bash
# Configure git to look for hooks in scripts/git-hooks/
git config core.hooksPath scripts/git-hooks
```

**Effect:** Git now reads hooks from scripts/git-hooks/ instead of .git/hooks/

### Phase 2: Remove Divergence
```bash
# Remove (or leave empty) .git/hooks/pre-commit
rm .git/hooks/pre-commit
# OR keep it empty as fallback
```

### Phase 3: Single Source of Truth
```
scripts/git-hooks/pre-commit  ← ONLY source
                               ← Git reads here via core.hooksPath
                               ← Always synchronized with repo
```

---

## Implementation Steps

### Step 1: Configure git in repository
```bash
cd /home/davis/HB-TRACK
git config core.hooksPath scripts/git-hooks
# Verify
git config core.hooksPath
# Output: scripts/git-hooks
```

### Step 2: Remove .git/hooks/pre-commit
```bash
rm -f .git/hooks/pre-commit
# Or verify it will be ignored now
ls -la .git/hooks/pre-commit  # Should fail or be empty
```

### Step 3: Make scripts/git-hooks/pre-commit executable
```bash
chmod +x scripts/git-hooks/pre-commit
```

### Step 4: Test Hook Execution
```bash
# Make a dummy change
echo "test" >> /tmp/test_file
git add /tmp/test_file

# Commit (hook should run from scripts/git-hooks/)
git commit -m "Test hook execution"

# Hook should execute and validate
# If pass: commit succeeds
# If fail: commit blocked with error
```

### Step 5: Run Test Suite
```bash
pytest tests/pipeline_gates/test_phase_0_determinism.py::TestPhase0Determinism::test_git_hook_divergence -v
# Expected: PASS (was RED, now GREEN)
```

---

## Phase Contract

**What Phase 5 (PR4) Validates:**
- Single hook source (scripts/git-hooks/pre-commit)
- Git reads hooks from configured path
- No divergence between versionado and instalado
- Hook changes immediately reflected (no local copy stale)

**Exit Criteria:**
- test_git_hook_divergence turns FROM RED TO GREEN
- Hook correctly reads from scripts/git-hooks/
- core.hooksPath set and verified

---

## Test Plan (PR4)

### Existing Test (Will Turn GREEN)
- test_git_hook_divergence: versionado == instalado

### New Validations
- [ ] git config core.hooksPath returns scripts/git-hooks
- [ ] .git/hooks/pre-commit doesn't exist (or is empty)
- [ ] Hook executes from scripts/git-hooks/ path
- [ ] Changes to scripts/git-hooks/pre-commit are immediately used

---

## Success Criteria

### Definition of Done (PR4)
1. ✅ git config core.hooksPath = scripts/git-hooks
2. ✅ .git/hooks/pre-commit removed or empty
3. ✅ scripts/git-hooks/pre-commit is executable
4. ✅ test_git_hook_divergence turns GREEN
5. ✅ All other tests remain GREEN (11 existing + new)
6. ✅ Blocker HOOK_DIVERGENCE closed
7. ✅ Hook changes sync immediately (single source)

### Verification
```bash
# 1. Check config
git config core.hooksPath
# Output: scripts/git-hooks

# 2. Verify single source
ls -la scripts/git-hooks/pre-commit
# Should be executable bash script

# 3. Run tests
pytest tests/pipeline_gates/test_phase_0_determinism.py -v
# Expected: 13 PASSED, 0 FAILED (hook test now GREEN)
```

---

## Dependencies & Sequencing
- **Depends on:** PR1 (SSOTs), PR2 (CLI), PR3 (Validator)
- **Blocks:** PR5 (Legacy cleanup), PR6 (CI/budgets)
- **Parallel:** None (linear sequence)

---

## Risk Assessment

### Low Risk
- git config is local to repo (reversible)
- core.hooksPath is standard git feature (stable)
- Only affects hook path, not hook logic

### No Logic Changes
- Hook code stays identical
- Only path resolution changes
- Functionality preserved

### Fallback
- If core.hooksPath fails, revert: `git config --unset core.hooksPath`
- Restore .git/hooks/pre-commit if needed

---

## Architecture Benefit

### Before PR4
```
Operator edits:   scripts/git-hooks/pre-commit
Git reads from:   .git/hooks/pre-commit
Result:           Changes invisible to git commits
                  Stale hook keeps running
```

### After PR4
```
Operator edits:   scripts/git-hooks/pre-commit
Git reads from:   scripts/git-hooks/pre-commit (via core.hooksPath)
Result:           Changes take effect immediately
                  Single source guaranteed
                  Test passes
```

---

## Next Actions (Post-PR4)
1. ✅ PR4 COMPLETE → HOOK_DIVERGENCE blocker closed
2. PR5 starts: Legacy cleanup (remove boot_resolution_report.json, etc.)
3. PR6 starts: CI regression + context budgets

---

## References
- Git config core.hooksPath: https://git-scm.com/docs/githooks#_location
- Current hook location: scripts/git-hooks/pre-commit
- Test file: tests/pipeline_gates/test_phase_0_determinism.py
- Original execut.md: .dev/planejamento/execut.md (Phase 5)
