#!/usr/bin/env python3
"""Execute AR_045 report validation"""
import subprocess
from pathlib import Path

# Read the validation command from AR_045 directly
ar045_file = Path('docs/hbtrack/ars/AR_045_git_mv_docs_hbtrack_ars__→_governance_,_competitio.md')
content = ar045_file.read_text(encoding='utf-8')

# Extract validation command from markdown
# It's between "```" markers
import re
match = re.search(r'```\n(python -c .*?)\n```', content, re.DOTALL)
if match:
    validation_cmd = match.group(1)
    print(f"Found validation command in AR_045")
    print("=" * 80)
    
    # Run hb report 045
    result = subprocess.run(
        ['python', 'scripts/run/hb_cli.py', 'report', '045', validation_cmd],
        capture_output=True,
        text=True
    )
    
    print(f"Exit Code: {result.returncode}")
    print(f"\nSTDOUT:\n{result.stdout}")
    if result.stderr:
        print(f"\nSTDERR:\n{result.stderr}")
else:
    print("Could not find validation command in AR_045")
