#!/usr/bin/env python3
"""Extract validation_command from AR and execute hb report."""
import re
import subprocess
import sys
from pathlib import Path

ar_id = "104"
ar_path = Path(f"docs/hbtrack/ars/features/AR_{ar_id}_modificar_migration_0060_para_detectar_versão_post.md")

if not ar_path.exists():
    print(f"AR file not found: {ar_path}", file=sys.stderr)
    sys.exit(1)

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

print(f"Extracted command ({len(validation_cmd)} chars)")
print(f"Running: hb report {ar_id} <command>")

result = subprocess.run(
    ["python", "scripts/run/hb_cli.py", "report", ar_id, validation_cmd],
    capture_output=False,
    text=True
)

sys.exit(result.returncode)
