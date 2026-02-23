#!/usr/bin/env python3
"""Execute AR_045 report with proper command"""
import subprocess
import sys

# Read AR_045 to get the validation command
ar045_path = 'docs/hbtrack/ars/AR_045_git_mv_docs_hbtrack_ars__→_governance_,_competitio.md'

try:
    with open(ar045_path, 'r', encoding='utf-8') as f:
        content = f.read()
except FileNotFoundError:
    print(f"ERROR: AR_045 not found at {ar045_path}")
    sys.exit(1)

# Extract validation command
import re
match = re.search(r'## Validation Command.*?\n```\n(.*?)\n```', content, re.DOTALL)

if not match:
    print("ERROR: Could not find validation command in AR_045")
    sys.exit(1)

validation_cmd = match.group(1).strip()

print("=== Running AR_045 Report ===")
print(f"Validation command extracted from AR_045\n")

# Execute hb report 045 with the validation command
result = subprocess.run(
    ['python', 'scripts/run/hb_cli.py', 'report', '045', validation_cmd],
    capture_output=False,
    text=True
)

print(f"\nExit Code: {result.returncode}")
if result.returncode == 0:
    print("✅ AR_045 PASSED")
else:
    print("❌ AR_045 FAILED")

sys.exit(result.returncode)
