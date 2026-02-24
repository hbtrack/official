"""Run hb_cli.py report 033 with the correct VC via subprocess args list."""
import subprocess
import sys
import pathlib

repo_root = pathlib.Path("c:/HB TRACK")

# Read the exact VC from the AR file to pass it correctly
ar_file = list((repo_root / "docs/hbtrack/ars").rglob("AR_033_*.md"))[0]
content = ar_file.read_text(encoding="utf-8")

import re
match = re.search(r"## Validation Command \(Contrato\)\n```\n(.+?)\n```", content, re.DOTALL)
vc = match.group(1).strip() if match else ""
print(f"VC found ({len(vc)} chars): {vc[:80]}...")

if not vc:
    print("ERROR: Could not extract VC from AR file")
    sys.exit(1)

result = subprocess.run(
    [sys.executable, str(repo_root / "scripts/run/hb_cli.py"), "report", "033", vc],
    cwd=str(repo_root),
    capture_output=True,
    text=True
)
print("=== STDOUT ===")
print(result.stdout)
if result.stderr:
    print("=== STDERR ===")
    print(result.stderr[:1000])
print(f"Exit: {result.returncode}")
