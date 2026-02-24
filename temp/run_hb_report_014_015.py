"""Run hb_cli.py report for AR_014 and AR_015."""
import subprocess
import sys
import pathlib
import re

repo_root = pathlib.Path("c:/HB TRACK")

def run_report(ar_id: str) -> int:
    base = repo_root / "docs/hbtrack/ars"
    files = list(base.rglob(f"AR_{ar_id}_*.md"))
    if not files:
        print(f"ERROR: AR_{ar_id} not found")
        return 1
    
    ar_file = files[0]
    content = ar_file.read_text(encoding="utf-8")
    
    match = re.search(r"## Validation Command \(Contrato\)\n```\n(.+?)\n```", content, re.DOTALL)
    vc = match.group(1).strip() if match else ""
    print(f"\n=== AR_{ar_id} VC ({len(vc)} chars) ===")
    print(vc[:100] + "...")
    
    if not vc:
        print(f"ERROR: no VC found for AR_{ar_id}")
        return 1
    
    result = subprocess.run(
        [sys.executable, str(repo_root / "scripts/run/hb_cli.py"), "report", ar_id, vc],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )
    print(f"STDOUT: {result.stdout[:300]}")
    if result.stderr:
        print(f"STDERR: {result.stderr[:300]}")
    print(f"Exit: {result.returncode}")
    return result.returncode

r1 = run_report("014")
r2 = run_report("015")
print(f"\nSummary: AR_014={'OK' if r1==0 else 'FAIL'}, AR_015={'OK' if r2==0 else 'FAIL'}")
