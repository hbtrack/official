#!/usr/bin/env python3
"""Debug script para testar _parse_yaml_simple"""

import sys
sys.path.insert(0, 'docs/scripts')
from verify_invariants_tests import InvariantsParser

yaml_text = """spec_version: "1.0"
id: "INV-TRAIN-033"
status: "CONFIRMADA"
test_required: true

units:
  - unit_key: "main"
    class: "A"
    required: true
    description: "Horas de sono deve estar entre 0 e 24"
    anchors:
      db.table: "wellness_pre"
      db.constraint: "ck_wellness_pre_sleep_hours"
      db.sqlstate: "23514"

tests:
  primary: "tests/training/invariants/test_inv_train_033_wellness_pre_sleep_hours.py"
  node: "TestInvTrain033WellnessPreSleepHours"
"""

parser = InvariantsParser()
result = parser._parse_yaml_simple(yaml_text)

print("Parsed result:")
print(result)
print()
print("units:")
for u in result.get('units', []):
    print(f"  {u}")
    if 'anchors' in u:
        print(f"    anchors: {u['anchors']}")
