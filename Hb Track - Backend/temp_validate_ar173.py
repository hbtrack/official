"""Validation script for AR_173 — migração ssot lote 1/2."""
import sys
from pathlib import Path

files = [
    'tests/training/invariants/test_inv_train_008_soft_delete_reason_pair.py',
    'tests/training/invariants/test_inv_train_020_cache_invalidation_trigger.py',
    'tests/training/invariants/test_inv_train_021_internal_load_trigger.py',
    'tests/training/invariants/test_inv_train_028_focus_sum_constraint.py',
    'tests/training/invariants/test_inv_train_030_attendance_correction_fields.py',
    'tests/training/invariants/test_inv_train_031_derive_phase_focus.py',
]

errs = [f for f in files if '_generated' in Path(f).read_text(encoding='utf-8')]
if errs:
    sys.exit('FAIL _generated still found: ' + str(errs))
print('PASS lote 1: 6 files migrated')
