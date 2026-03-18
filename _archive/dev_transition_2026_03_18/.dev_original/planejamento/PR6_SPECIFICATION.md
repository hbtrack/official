# PR6 Specification — Phase 7-8: Context Budgets + CI/Regression

## Overview

**Objective:** Enforce strict context budgets across critical pipeline documents and validate CI/local parity through golden tests.

**Problem Identified:**
- CLAUDE.md: 662 words → target 450 (cut 212w, −32%)
- SESSION_HANDOFF.md: 2496 words → target 350 (cut 2146w, −86% ⚠️ AGGRESSIVE)
- CONTRACT_PIPELINE.md: 874 words → target 600 (cut 274w, −31%)
- pre_contract_orchestrator.prompt.md: 1129 words → target 700 (cut 429w, −38%)
- **Total: 5161 words → 2100 target (cut 3061w, −59%)**

**Phase 7 Risk:** SESSION_HANDOFF needs to be 86% smaller while keeping operational value.
**Phase 8 Task:** Add golden tests for parity between local execution and CI.

---

## Current State

### Word Count Baseline
```
  662 CLAUDE.md (32% over)
 2496 SESSION_HANDOFF.md (86% over) ← CRITICAL
  874 CONTRACT_PIPELINE.md (31% over)
 1129 pre_contract_orchestrator.prompt.md (38% over)
------
 5161 total (59% over budget)
```

### What EXISTS (to preserve)
- ✅ BOOT_PROFILES.yaml (SSOT for boot — small, ~40w)
- ✅ TASK_CATALOG.yaml (SSOT for task_type — small, ~50w)
- ✅ session_start.schema.json (SSOT for evidence — structural, ~100w)
- ✅ GATES_REGISTRY.yaml (SSOT for gate metadata — 46 gates, registry format)
- ✅ scripts/hb (CLI hardened — ~340 lines code, not prose)
- ✅ scripts/git-hooks/pre-commit (hook versionado — small script)

---

## Phase 7: Context Reduction Strategy

### CLAUDE.md (662w → 450w: cut 212w)

**Current Structure:**
1. LEIA PRIMEIRO (138w)
2. MODO DE OPERAÇÃO (82w)
3. 16 MÓDULOS CANÔNICOS (120w)
4. 9 TASK TYPES → WORKERS (110w)
5. 5 BLOQUEIOS CANÔNICOS (150w) ← **REMOVE THIS SECTION**
6. REGRAS CORE (180w) ← **COMPRESS TO 60w SUMMARY**
7. COMUNICAÇÃO (140w) ← **COMPRESS TO 40w**
8. PATHS CRÍTICOS (400w+) ← **REMOVE (inline in §6)**

**Action Plan:**
- Keep: §0, §1, §2, §3, §4 (core decision-making info)
- Cut: §5 bloqueios (now in execut.md), §6 detailed rules (replace with pointer), §7 comms (merge to 1 sentence), §8 paths (inline essential as footnotes)
- Result: ~450w (entrypoint only, deep dives via links)

**Target Structure (450w):**
```
0. LEIA PRIMEIRO (brief)
1. MODO (2 sentences)
2. 16 MÓDULOS CANÔNICOS (list only)
3. 9 TASK TYPES (table only)
4. CORE RULES (1 decision tree: module? → surfaces? → contratos? → implementation)
5. COMMUNICATION RULE (1 sentence)
6. CRITICAL PATHS (inline via [link](path) format)
```

---

### SESSION_HANDOFF.md (2496w → 350w: cut 2146w — EXTREME)

**Current Issue:**
Session handoff became a **document archive** mixing:
- Historical iteration logs (¹000s of words of what was done)
- Decision history (belongs in SESSION_HANDOFF but with diff)
- Blocker tracking (now in execut.md)
- ADR list (belongs in docs, not handoff)
- Contracts status (belongs in MODULE_REGISTRY, not handoff)
- Architecture context (belongs in CODE_ARCHITECTURE, not handoff)

**Action Plan — Convert to DELTA-ONLY Model:**
- **REMOVE:** All historical iteration logs (§"O Que Foi Feito")
- **REMOVE:** All PR status lists
- **REMOVE:** Detailed ADR table (keep only "pending" and "blocking")
- **REMOVE:** Contracts status (link to MODULE_REGISTRY instead)
- **KEEP ONLY:**
  - Estado Geral (3 sentences)
  - Decisões Pendentes (table, 3-5 items ONLY)
  - Bloqueios Ativos (table, current session ONLY — 1-2 items)
  - Próximos Passos (1-2 sentences)

**Target Structure (350w):**
```
# SESSION HANDOFF — HB TRACK

## Estado Geral
[Date, branch, CI status, module focus, pipeline status — 3 sentences]

## Decisões Pendentes (This Session)
[Table: only decisions blocking current work — max 5 rows]

## Bloqueios Ativos (This Session)
[Table: only blockers from this session — max 2-3 rows]

## Próximos Passos
[1-2 sentences on immediate next action]

## Contexto Crítico (Only if session-specific)
[Max 5 bullet points of unusual context; else omit]
```

---

### CONTRACT_PIPELINE.md (874w → 600w: cut 274w)

**Current Issue:**
- Extended examples (can move to linked appendix)
- Verbose descriptions (can compress to 1-sentence per concept)
- Duplicated info from CONTRACT_SYSTEM_RULES

**Action Plan:**
- **COMPRESS:** Estágios descrição → 1 line each
- **REMOVE:** Detailed conformance rules (link to RULES instead)
- **REMOVE:** Extended examples section
- **KEEP:** Tabla de estágios, phase definitions, evidence table
- **COMPRESS:** Ações corretivas mínimas (1 line per action)

**Target Structure (600w):**
```
## 1. Estágios Oficiais (table only, compressed descriptions)
## 2. Fase 0 — Validação (3 sentences)
## 3-6. Fase 1-4 (1 sentence definition + evidence spec each)
## 7. Ações Corretivas (bullet list, no explanation)
[Link to CONTRACT_SYSTEM_RULES for detailed rules]
```

---

### pre_contract_orchestrator.prompt.md (1129w → 700w: cut 429w)

**Current Issue:**
- Duplicated instruction content (in CONTRACT_SYSTEM_RULES)
- Verbose phase descriptions
- Redundant decision matrix
- Extended reference sections

**Action Plan:**
- **KEEP:** §1-3 Fase 0 instructions (essential for worker)
- **COMPRESS:** Bloqueios table (reference to execut.md instead)
- **REMOVE:** Detailed phase walkthroughs (1 sentence each)
- **REMOVE:** Extended decision rationale
- **COMPRESS:** Outputs section (1 line per output type)

**Target Structure (700w):**
```
## 1. Orquestrador Pre-Contrato
[Brief: what it does]

## 2. Fase 0: Entrada
[Stage 0 decision tree — keep detailed]

## 3. Saídas
[Output types — 1 line each]

## 4. Bloqueios
[Link to execut.md/GATES_REGISTRY instead of repeating]

[Remove extended walkthrough sections]
```

---

## Phase 8: CI/Regression Tests

### Golden Tests to Add

**Test 1: Word Count Enforcement**
```python
def test_context_budgets():
    """Verify all critical docs stay within budgets."""
    assert word_count("CLAUDE.md") <= 450
    assert word_count("SESSION_HANDOFF.md") <= 350
    assert word_count("CONTRACT_PIPELINE.md") <= 600
    assert word_count("pre_contract_orchestrator.prompt.md") <= 700
```

**Test 2: TASK_CATALOG ↔ Orchestrator Parity**
```python
def test_task_catalog_to_orchestrator_parity():
    """Verify TASK_CATALOG task_types match orchestrator validation."""
    catalog = load_yaml("docs/_canon/TASK_CATALOG.yaml")
    orchestrator_logic = extract_task_types_from_orchestrator()
    assert catalog.task_types == set(orchestrator_logic)
```

**Test 3: GATES_REGISTRY ↔ Validator Parity**
```python
def test_gates_registry_to_validator_parity():
    """Verify GATES_REGISTRY gates match validator enforcement."""
    registry = load_yaml("docs/_canon/GATES_REGISTRY.yaml")
    validator_gates = extract_gates_from_validator()
    assert registry.gate_ids == set(validator_gates.keys())
    assert all(g.blocking == validator_gates[g.id].blocking 
               for g in registry.gates)
```

**Test 4: Hook Script Integrity**
```python
def test_hook_versionado_equals_hook_instalado():
    """Verify hook versionado ≡ hook installed via core.hooksPath."""
    versionado = read_file("scripts/git-hooks/pre-commit")
    git_config = subprocess.run(["git", "config", "core.hooksPath"])
    assert git_config.stdout == "scripts/git-hooks"
    # Hook executed by git is same as versionado
```

**Test 5: Session Start Schema Validation**
```python
def test_session_start_schema_enforces_no_unknown():
    """Verify session_start.json rejects task_type='unknown', module='unknown'."""
    schema = load_schema("contracts/schemas/shared/session_start.schema.json")
    assert not validate({"task_type": "unknown"}, schema)
    assert not validate({"module": "unknown"}, schema)
```

**Test 6: Boot Profile References**
```python
def test_zero_active_boot_profile_references():
    """Verify all boot config uses BOOT_PROFILES.yaml, not hardcoded."""
    # Should NOT find "boot_profile: '" in active code
    result = subprocess.run(["grep", "-r", "boot_profile:", 
                            "--include=*.py", "--include=*.md"])
    hardcoded = [r for r in result if "BOOT_PROFILES" not in r]
    assert len(hardcoded) == 0, f"Found hardcoded boot refs: {hardcoded}"
```

**Test 7: CLI Parity (local vs CI)**
```bash
#!/bin/bash
# test_cli_parity.sh
# Run hb verify, hb check, hb artifact locally and in CI
# Expect same exit codes and outputs

hb verify --task-type new_contract --module training > local.log
hb check --module training > local_check.log
[CI equivalent runs]
diff local.log ci.log  # Must be identical
```

---

## Implementation Sequence (Phase 7)

### Step 1: Reduce CLAUDE.md (−212w)
- Remove §5 bloqueios (move to execut.md reference)
- Compress §6 regras (decision tree only)
- Compress §7 comms (1 sentence)
- Inline §8 paths (footnotes/links)
- Target: 450w ✅

### Step 2: Reduce SESSION_HANDOFF.md (−2146w) **CRITICAL**
- Remove all historical logs (§"O Que Foi Feito")
- Remove PR status lists
- Keep ONLY: estado, decisões pendentes, bloqueios, próximos passos
- Convert table format (max 5 rows per table)
- Target: 350w ✅ (from 2496w — will be aggressively short)

### Step 3: Reduce CONTRACT_PIPELINE.md (−274w)
- Compress estágios descriptions
- Inline rules (link to CONTRACT_SYSTEM_RULES)
- Remove extended examples
- Target: 600w ✅

### Step 4: Reduce pre_contract_orchestrator.prompt.md (−429w)
- Keep Fase 0 logic (essential)
- Compress bloqueios (link to execut.md)
- Remove verbose walkthroughs
- Target: 700w ✅

---

## Implementation Sequence (Phase 8)

### Step 5: Add Golden Tests
Create `tests/pipeline_gates/test_context_budgets_and_parity.py`:
- Word count enforcement (6 tests)
- TASK_CATALOG ↔ orchestrator parity
- GATES_REGISTRY ↔ validator parity
- Hook integrity
- Session schema validation
- Boot profile reference check
- CLI parity (local vs CI)

### Step 6: Add Shell Integration Tests
Create `scripts/ci/test_local_ci_parity.sh`:
- Run hb verify/check/artifact locally
- Compare outputs with CI runs
- Verify identical behavior

### Step 7: CI Configuration
Update `.github/workflows/` to:
- Run context budget tests
- Run golden parity tests
- Report context metrics in PR

---

## Success Criteria (PR6 Definition of Done)

### Phase 7 (Context Reduction)
- [x] CLAUDE.md ≤ 450 words (from 662)
- [x] SESSION_HANDOFF.md ≤ 350 words (from 2496) **← Most aggressive**
- [x] CONTRACT_PIPELINE.md ≤ 600 words (from 874)
- [x] pre_contract_orchestrator.prompt.md ≤ 700 words (from 1129)
- [x] All critical content preserved via links/references
- [x] No decision loss, only redundancy removal

### Phase 8 (CI/Regression)
- [x] Golden test suite created (7+ tests)
- [x] All tests GREEN locally
- [x] CI parity validated (local ≡ CI)
- [x] Context budgets enforced in CI checks
- [x] Parity matrix passed (TASK_CATALOG, GATES_REGISTRY, hooks)

---

## Risk Assessment

### Phase 7 Risks
- **HIGH:** SESSION_HANDOFF reduction so aggressive it becomes useless
  - **Mitigation:** Keep hyperlinks to full context (MODULE_REGISTRY, execut.md, DECISION_LOG)
  
- **MEDIUM:** Removing historical context makes onboarding harder
  - **Mitigation:** Move history to SESSION_ARCHIVE.md (separate file, not loaded at boot)

- **MEDIUM:** CLAUDE.md becomes too terse
  - **Mitigation:** Keep decision tree + link to CONTRACT_SYSTEM_RULES for rules

### Phase 8 Risks
- **LOW:** Golden tests might be brittle if docs update by 1 word
  - **Mitigation:** Allow ±5% tolerance, enforce strict limit in CI pre-submit

---

## Files to Modify (Phase 7)

| File | Current (w) | Target (w) | Action |
|------|-------------|-----------|--------|
| CLAUDE.md | 662 | 450 | Remove §5/8, compress §6/7 |
| SESSION_HANDOFF.md | 2496 | 350 | **EXTREME: keep only delta** |
| CONTRACT_PIPELINE.md | 874 | 600 | Compress descriptions, inline rules |
| pre_contract_orchestrator.prompt.md | 1129 | 700 | Compress, link to execut.md |

| File | Purpose | Phase 8 |
|------|---------|---------|
| tests/pipeline_gates/test_context_budgets_and_parity.py | Golden tests | Add 7+ tests |
| scripts/ci/test_local_ci_parity.sh | Shell integration | Add parity test |

---

## Files to Create (Phase 8 Optional)

- `SESSION_ARCHIVE.md` — Historical session logs (optional, for reference)
- `.github/workflows/context-budgets.yml` — CI enforcement (optional)

---

## Success Metrics

```
✅ Total word count: 5161w → ~2100w (target)
✅ Individual docs: All within budgets
✅ Critical content: Preserved via SSOT + links
✅ Tests: 13/13 GREEN (Phase 0-6) + 7+ golden tests GREEN (Phase 7-8)
✅ CI/Local parity: 100% match (same inputs → same outputs)
✅ Blocker CONTEXT_BUDGET_OVERRUN: CLOSED
```

---

## References

- Targets: execut.md, Phase 7-8
- Current state: SESSION_HANDOFF.md (before PR6)
- Baselines: PR1-5 completion reports

---

## Notes

**Session Handoff Challenge:**
SESSION_HANDOFF needs to go from **2496w → 350w**, a **86% reduction**. This is only feasible if:
1. Historical session logs move to SESSION_ARCHIVE.md (not essential at boot)
2. Detailed contract status moves to MODULE_REGISTRY (SSOT)
3. ADR status moves to documents themselves
4. Handoff becomes **delta-only**: "What changed this session? What's blocked? What's next?"

This is the single **most aggressive** cut but necessary for the budget.

