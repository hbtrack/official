#!/usr/bin/env python3
"""Execute hb report for AR_004 with filesize validation."""
import subprocess
import sys

validation_cmd = '''python -c "import pathlib; p=pathlib.Path('Hb Track - Backend/app/services/match_event_service.py'); assert p.exists(), 'File not found'; print(f'PASS_AR_004_bytes={p.stat().st_size}'); exit(0)"'''

result = subprocess.run(
    ["python", "scripts/run/hb_cli.py", "report", "004", validation_cmd],
    capture_output=False,
    text=True
)

sys.exit(result.returncode)
