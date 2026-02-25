#!/usr/bin/env python3
"""Extract and execute AR_059 validation command"""
import subprocess
import sys
import re
from pathlib import Path

# Read AR file
ar_path = Path("docs/hbtrack/ars/features/AR_059_criar_context_map.md_-_mapa_temático_de_ars_por_do.md")
ar_content = ar_path.read_text(encoding="utf-8")

# Extract validation command from markdown code block
match = re.search(
    r"## Validation Command \(Contrato\)\s*```\s*(.+?)\s*```",
    ar_content,
    re.DOTALL
)

if not match:
    print("❌ ERROR: Could not extract validation_command from AR")
    sys.exit(1)

validation_cmd = match.group(1).strip()

print(f"Extracted validation command ({len(validation_cmd)} chars)")
print(f"First 100 chars: {validation_cmd[:100]}")
print(f"Last 50 chars: {validation_cmd[-50:]}")
print()

# Execute hb report
cmd = ["python", "scripts/run/hb_cli.py", "report", "059", validation_cmd]

print("Executing: hb report 059")
result = subprocess.run(cmd, capture_output=False, text=True)
sys.exit(result.returncode)
