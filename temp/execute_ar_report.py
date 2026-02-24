#!/usr/bin/env python3
"""Extract validation_command from AR and execute hb report."""
import re
import subprocess
import sys
from pathlib import Path

# Get AR ID from command line or use default
ar_id = sys.argv[1] if len(sys.argv) > 1 else "024"

# Find AR file
ar_files = list(Path("docs/hbtrack/ars").rglob(f"AR_{ar_id}_*.md"))
if not ar_files:
    print(f"AR file not found for AR_{ar_id}", file=sys.stderr)
    sys.exit(1)

ar_path = ar_files[0]
print(f"Found: {ar_path}")

ar_content = ar_path.read_text(encoding="utf-8")

# Extract validation_command from ## Validation Command (Contrato) section
match = re.search(
    r'## Validation Command \(Contrato\)\s*```\s*\n(.*?)\n```',
    ar_content,
    re.DOTALL
)

if not match:
    print("validation_command not found in AR", file=sys.stderr)
    sys.exit(1)

validation_cmd = match.group(1).strip()

print(f"Validation command length: {len(validation_cmd)} chars")

result = subprocess.run(
    ["python", "scripts/run/hb_cli.py", "report", ar_id, validation_cmd],
    capture_output=False,
    text=True
)

sys.exit(result.returncode)
