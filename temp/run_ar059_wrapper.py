#!/usr/bin/env python3
"""Execute AR_059 report"""
import subprocess
import sys
from pathlib import Path

# Read validation command from file
cmd_file = Path("temp/ar059_cmd.txt")
validation_cmd = cmd_file.read_text(encoding="utf-8").strip()

# Execute hb report
args = [sys.executable, "scripts/run/hb_cli.py", "report", "059", validation_cmd]

print(f"Executing: python scripts/run/hb_cli.py report 059 <validation_cmd>")
print(f"Validation command: {len(validation_cmd)} chars")
print()

result = subprocess.run(args, cwd="C:\\HB TRACK")
sys.exit(result.returncode)
