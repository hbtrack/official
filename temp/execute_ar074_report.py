#!/usr/bin/env python3
"""Execute AR_074 hb report."""
import subprocess
import sys
import re
from pathlib import Path

# Define paths
workspace_root = Path(r"C:\HB TRACK")
venv_python = workspace_root / "Hb Track - Backend" / ".venv" / "Scripts" / "python.exe"
hb_cli = workspace_root / "scripts" / "run" / "hb_cli.py"

# Find AR file
ar_files = list((workspace_root / "docs" / "hbtrack" / "ars").rglob("AR_074_*.md"))
if not ar_files:
    print("ERROR: AR_074 file not found")
    sys.exit(1)

ar_file = ar_files[0]
print(f"Reading AR from: {ar_file}")

# Read AR content
ar_content = ar_file.read_text(encoding="utf-8")

# Extract validation command
match = re.search(
    r"## Validation Command.*?```\s*\n(.*?)```",
    ar_content,
    re.DOTALL | re.IGNORECASE
)

if not match:
    print("ERROR: Could not extract validation command from AR file")
    sys.exit(1)

validation_cmd = match.group(1).strip()
# Normalize: remove line breaks
validation_cmd = validation_cmd.replace('\n', ' ').replace('\r', '')

print(f"Validation command: {len(validation_cmd)} chars")
print()

# Execute hb report
ar_id = "074"
cmd = [str(venv_python), str(hb_cli), "report", ar_id, validation_cmd]
result = subprocess.run(cmd, cwd=str(workspace_root), capture_output=True, text=True, encoding="utf-8", errors="replace")

print("=== STDOUT ===")
print(result.stdout)
print()
print("=== STDERR ===")
print(result.stderr)
print()
print(f"=== EXIT CODE: {result.returncode} ===")

sys.exit(result.returncode)
