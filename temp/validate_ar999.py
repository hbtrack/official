"""
AR_999 validation wrapper - Windows-compatible pytest runner with deterministic output
"""
import subprocess
import sys
from pathlib import Path

# Change to backend directory
backend_dir = Path(__file__).parent.parent / "Hb Track - Backend"

# Run pytest
result = subprocess.run(
    [sys.executable, "-m", "pytest", 
     "tests/models/test_person.py::test_birthdate_field", "-v", "-q"],
    cwd=backend_dir,
    capture_output=True,
    text=True
)

# Deterministic output: print only PASS/FAIL
if result.returncode == 0:
    print("[PASS] test_birthdate_field: Person.birth_date exists and works correctly")
else:
    print("[FAIL] test_birthdate_field")
    print(result.stdout, end='')
    print(result.stderr, end='', file=sys.stderr)

sys.exit(result.returncode)
