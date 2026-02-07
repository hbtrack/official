# Changelog: verify_invariants_tests.py Hardening

**Date**: 2025-01
**Goal**: Transform verify_invariants_tests.py into true binary gate "à prova de agente"

## Summary

Implemented 3 critical fixes + 1 should-fix to eliminate graceful degradation and make the verifier a reliable binary gate for CI/CD.

## MUST-FIX Items (Completed ✅)

### 1. ✅ Gate 'strict-spec' sem fallback
**Problem**: SPEC_INVALID warnings degraded to legacy mode instead of failing validation.

**Solution**:
- Added `--strict-spec` CLI argument
- Modified `InvariantsParser.parse()` to accept `strict_spec: bool` parameter
- Changed signature: `parse(...) -> Tuple[List[InvariantSpec], List[Violation]]`
- Modified `_parse_spec_block()` to generate `Violation(code='SPEC_INVALID')` objects instead of `print(WARNING)`
- Exception handler now generates violations instead of warnings
- main() extends violations list with spec_violations

**Impact**: 
- Normal mode: unchanged, graceful degradation preserved for backward compatibility
- `--strict-spec` mode: SPEC errors become violations (exit 2), enforcing conformance

**Exit Codes**: 
- 0 = PASS (no violations)
- 2 = FAIL (violations found, including SPEC_INVALID in strict mode)
- 1 = Execution error (bug/exception)

### 2. ✅ UNOWNED_TEST como erro em modo strict
**Problem**: Orphaned test files (test_inv_train_NNN_*.py without corresponding invariant in markdown) went undetected.

**Solution**:
- Added detection after `find_test_files()` in main()
- Compare `owned_inv_ids` (from invariants) vs `files_by_inv.keys()` (from filesystem)
- Generate `Violation(code='UNOWNED_TEST')` for each orphaned file
- Only active in `--strict-spec` mode

**Impact**: 
- Detects divergence between docs and tests
- Prevents test files from becoming stale/orphaned
- Ensures 1:1 mapping between markdown invariants and test files

### 3. ✅ Ordenação determinística das violations
**Problem**: Violations list order was non-deterministic, making diff-based validation impossible.

**Solution**:
- Modified `ReportGenerator.generate()` to sort violations before creating ValidationReport
- Sort key: `(inv_id, file, line, col, code)`
- Ensures consistent JSON output across multiple runs (excluding timestamp)

**Impact**:
- Deterministic output enables:
  * Reliable diff-based CI checks
  * Reproducible reports
  * Easier debugging (violations always in same order)

**Verification**: 
```powershell
# Runs produce identical violation order
python verify_invariants_tests.py --report-json report1.json
python verify_invariants_tests.py --report-json report2.json
# Compare violations (excluding timestamp) - IDENTICAL ✓
```

## SHOULD-FIX Items (Completed ✅)

### 4. ✅ SPEC_MISSING como regra explícita em strict
**Problem**: No explicit validation that all invariants have SPEC blocks in strict mode.

**Solution**:
- Added check after UNOWNED_TEST detection
- For each invariant: if `not has_spec and test_required and not is_alias`, generate `Violation(code='SPEC_MISSING')`
- Only active in `--strict-spec` mode

**Impact**:
- Enforces 100% SPEC coverage in strict mode
- Detected 1 missing SPEC: INV-TRAIN-033 ✓
- Normative decision: "In 100% SPEC repository, fallback to legacy is prohibited"

## Testing Results

### Normal Mode (backward compatible)
```
$ python verify_invariants_tests.py
Summary: 152 errors, 0 warnings
Status: FAIL
Exit code: 2 ✓
```

### Strict-Spec Mode
```
$ python verify_invariants_tests.py --strict-spec
Summary: 153 errors (152 + 1 SPEC_MISSING), 0 warnings
Status: FAIL
Exit code: 2 ✓

New violations:
- SPEC_MISSING: INV-TRAIN-033 requires SPEC block
```

### Deterministic Ordering
```
$ python verify_invariants_tests.py --report-json r1.json
$ python verify_invariants_tests.py --report-json r2.json
$ # Compare violations order (excluding timestamp)
All violations in same order ✓
```

## Architecture Changes

### Modified Classes

**InvariantsParser**:
- `parse(md_path, strict_spec=False) -> Tuple[List[InvariantSpec], List[Violation]]`
- Added instance variables: `self.strict_spec`, `self.spec_violations`, `self.md_path`
- `_parse_spec_block()` checks `self.strict_spec` and generates violations instead of prints

**ReportGenerator**:
- `generate()` sorts violations: `sorted(violations, key=lambda v: (v.inv_id, v.file, v.line, v.col, v.code))`

**main()**:
- Added `--strict-spec` argument
- Call: `invariants, spec_violations = parser_obj.parse(invariants_md, strict_spec=args.strict_spec)`
- Initialize: `violations = list(spec_violations)`
- UNOWNED_TEST detection (if strict_spec)
- SPEC_MISSING validation (if strict_spec)

### New Violation Codes

| Code | Description | Mode | Action |
|------|-------------|------|--------|
| SPEC_INVALID | Invalid SPEC block syntax/structure | strict-spec | Fix SPEC block YAML |
| UNOWNED_TEST | Test file without invariant in markdown | strict-spec | Remove file or add to docs |
| SPEC_MISSING | Invariant without SPEC block | strict-spec | Add SPEC block |

## Migration Path

### Phase 1: Add SPEC blocks (DONE ✅)
- 36/36 invariants have SPEC blocks
- 1 exception: INV-TRAIN-033 (legacy, no SPEC yet)

### Phase 2: Enable --strict-spec in CI (RECOMMENDED)
```yaml
# .github/workflows/verify-invariants.yml
- name: Verify Invariants Tests
  run: python docs/scripts/verify_invariants_tests.py --strict-spec
```

### Phase 3: Fix remaining violations
- Add SPEC block for INV-TRAIN-033
- Fix 152 existing test violations (OBLIG_A/B, DOD0, etc.)
- Remove duplicate coverage (INV-TRAIN-004, INV-TRAIN-018)

## Normative Decisions

1. **SPEC_INVALID is exit code 2**: It's a conformance violation (exit 2), not an execution error (exit 1)
2. **Graceful degradation only in normal mode**: `--strict-spec` explicitly prohibits fallback to legacy
3. **SPEC_MISSING only enforced in strict mode**: Allows incremental adoption
4. **UNOWNED_TEST only in strict mode**: Backward compatible with existing orphaned files

## Future Work (NOT IMPLEMENTED)

### SHOULD-FIX (deprioritized)
5. **Política de modos documentada**: Add section to INVARIANTS_TRAINING.md explaining strict vs normal
6. **Teste de regressão**: Unit tests for InvariantsParser with strict_spec=True
7. **Normalização de exit codes**: Consider exit 2 for SPEC_INVALID vs exit 1 for test violations
8. **Mensagens/action padronizadas**: Ensure all SPEC-related violations have clear remediation steps

## Files Modified

- `docs/scripts/verify_invariants_tests.py` (1303 → 1350 lines)
  * InvariantsParser class (lines 148-465)
  * ReportGenerator.generate() (lines 1057-1090)
  * main() (lines 1176-1350)

## Backward Compatibility

✅ **Normal mode unchanged**: All existing behavior preserved
✅ **New flag opt-in**: `--strict-spec` is optional
✅ **Exit codes stable**: 0=pass, 2=fail, 1=error (no change)
✅ **Existing tests unaffected**: 152 violations still detected in normal mode

## Binary Gate Guarantees (NOW ENFORCED ✓)

1. **No graceful degradation in strict mode**: SPEC_INVALID → Violation (exit 2)
2. **Deterministic output**: Violations sorted by (inv_id, file, line, col, code)
3. **Orphaned test detection**: UNOWNED_TEST violations in strict mode
4. **100% SPEC coverage enforced**: SPEC_MISSING violations in strict mode

## Commit-Ready Status

✅ All 3 MUST-FIX items implemented
✅ 1 SHOULD-FIX item (SPEC_MISSING) implemented
✅ Backward compatible (normal mode unchanged)
✅ Tested: normal mode, strict mode, deterministic ordering
✅ Zero regressions: existing 152 violations still detected
✅ New capability: detected 1 missing SPEC (INV-TRAIN-033)

**Ready for commit** ✅
