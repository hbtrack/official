import sys
from pathlib import Path
sys.path.insert(0, str(Path('docs/scripts')))

from verify_invariants_tests import InvariantsParser

# Minimal YAML with 2 list items with anchors
yaml_test = """units:
  - unit_key: "db-column"
    class: "B"
    required: false
    description: "Database column locked_at documents the rule"
    anchors:
      db.table: "wellness_pre"
      db.column: "locked_at"
      db.comment: "pré editável até 2h antes da sessão"
  
  - unit_key: "service-validation"
    class: "C2"
    required: true
    description: "Service enforces 2h deadline with ValidationError"
    anchors:
      code.file: "app/services/wellness_pre_service.py"
      code.symbol: "_check_edit_window"
      code.lines: [93, 102, 231, 232]
      code.error_type: "ValidationError"
"""

parser = InvariantsParser()
result = parser._parse_yaml_simple(yaml_test)

print("Result:")
for i, unit in enumerate(result.get('units', [])):
    print(f"\nUnit {i}:")
    if isinstance(unit, dict):
        for key, value in unit.items():
            print(f"  {key}: {value}")
    else:
        print(f"  {unit}")
