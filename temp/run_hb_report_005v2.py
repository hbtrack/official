"""Run hb_cli.py report for AR_005 with updated VC."""
import subprocess
import sys
import pathlib
import re

repo_root = pathlib.Path("c:/HB TRACK")

ar_id = "005"
base = repo_root / "docs/hbtrack/ars"
files = list(base.rglob(f"AR_{ar_id}_*.md"))
ar_file = files[0]
content = ar_file.read_text(encoding="utf-8")

match = re.search(r"## Validation Command \(Contrato\)\n```\n(.+?)\n```", content, re.DOTALL)
vc = match.group(1).strip() if match else ""
print(f"VC (len={len(vc)}): {vc[:120]}...")

result = subprocess.run(
    [sys.executable, str(repo_root / "scripts/run/hb_cli.py"), "report", ar_id, vc],
    cwd=str(repo_root),
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace"
)
print(f"STDOUT: {result.stdout[:500]}")
if result.stderr:
    print(f"STDERR: {result.stderr[:300]}")
print(f"Exit: {result.returncode}")
