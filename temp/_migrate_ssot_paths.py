"""Migra '_generated' para 'ssot' em 11 test files TRAINING (AR_173 + AR_174)."""
from pathlib import Path

BASE = Path(__file__).parent.parent / "Hb Track - Backend"

files = [
    # Lote 1 (AR_173)
    "tests/training/invariants/test_inv_train_008_soft_delete_reason_pair.py",
    "tests/training/invariants/test_inv_train_020_cache_invalidation_trigger.py",
    "tests/training/invariants/test_inv_train_021_internal_load_trigger.py",
    "tests/training/invariants/test_inv_train_028_focus_sum_constraint.py",
    "tests/training/invariants/test_inv_train_030_attendance_correction_fields.py",
    "tests/training/invariants/test_inv_train_031_derive_phase_focus.py",
    # Lote 2 (AR_174)
    "tests/training/invariants/test_inv_train_035_session_templates_unique_name.py",
    "tests/training/invariants/test_inv_train_036_wellness_rankings_unique.py",
    "tests/training/invariants/test_inv_train_037_cycle_dates.py",
    "tests/training/invariants/test_inv_train_072_ai_suggestion_not_order.py",
    "tests/training/invariants/test_inv_train_077_immediate_virtual_coach_feedback.py",
]

for rel in files:
    p = BASE / rel
    if not p.exists():
        print(f"MISSING: {rel}")
        continue
    t = p.read_text(encoding="utf-8")
    new_t = t.replace('"_generated"', '"ssot"')
    if new_t != t:
        p.write_text(new_t, encoding="utf-8")
        count = t.count('"_generated"')
        print(f"UPDATED ({count} subs): {rel}")
    else:
        print(f"UNCHANGED: {rel}")

print("\nDone.")
