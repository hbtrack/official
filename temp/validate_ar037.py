#!/usr/bin/env python3
"""
Validation script for AR_037: Competition.points_per_draw + Competition.points_per_loss model fields

Validation criteria:
- Competition model has points_per_draw attribute
- Competition model has points_per_loss attribute
- No import errors
"""

import sys
from pathlib import Path

# Adicionar o Backend ao sys.path
backend_path = Path(__file__).parent.parent / "Hb Track - Backend"
sys.path.insert(0, str(backend_path))

try:
    from app.models.competition import Competition
    
    fields = ['points_per_draw', 'points_per_loss']
    missing = [f for f in fields if not hasattr(Competition, f)]
    
    if missing:
        print(f"[FAIL] Missing fields in Competition model: {missing}")
        sys.exit(1)
    
    print(f"[PASS] AR_037 objective achieved: {fields} present in Competition")
    sys.exit(0)
    
except ImportError as e:
    print(f"[FAIL] Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"[FAIL] Validation error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
