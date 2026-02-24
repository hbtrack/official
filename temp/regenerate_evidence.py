#!/usr/bin/env python3
"""Regenerate evidence for ARs 004, 069, and 056-068."""
import subprocess
import sys
import pathlib
import re

def extract_validation_command(ar_path: str) -> str:
    """Extract validation_command from AR markdown file."""
    with open(ar_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    match = re.search(
        r'## Validation Command \(Contrato\)\n```\n(.*?)\n```',
        content,
        re.DOTALL
    )
    
    if not match:
        raise ValueError(f"Validation Command not found in {ar_path}")
    
    return match.group(1).strip()

def run_hb_report(ar_id: str) -> tuple[int, str]:
    """Run hb report for an AR and return exit code and output."""
    # Find AR file
    ar_files = list(pathlib.Path("docs/hbtrack/ars").rglob(f"AR_{ar_id}*.md"))
    
    if not ar_files:
        return (1, f"AR_{ar_id} not found")
    
    ar_file = ar_files[0]
    print(f"Processing: {ar_file.name}")
    
    # Extract validation command
    try:
        validation_cmd = extract_validation_command(str(ar_file))
    except Exception as e:
        return (1, f"Failed to extract validation command: {e}")
    
    # Execute hb report
    result = subprocess.run(
        ["python", "scripts/run/hb_cli.py", "report", ar_id, validation_cmd],
        capture_output=True,
        text=True
    )
    
    return (result.returncode, result.stdout + result.stderr)

if __name__ == "__main__":
    ars_to_process = [
        "004",  # Critical
        "069",  # Infrastructure
        "056", "057", "058", "059", "060", "061", "062", "063", "068"  # STUB batch
    ]
    
    results = {}
    for ar_id in ars_to_process:
        print(f"\n{'='*60}")
        print(f"AR_{ar_id}")
        print('='*60)
        exit_code, output = run_hb_report(ar_id)
        results[ar_id] = exit_code
        print(f"Exit Code: {exit_code}")
        if exit_code != 0 and ar_id not in ["056", "057", "058", "059", "060", "061", "062", "063", "068"]:
            print(f"ERROR: {output}")
    
    print(f"\n{'='*60}")
    print("SUMMARY")
    print('='*60)
    for ar_id, exit_code in results.items():
        status = "✅ PASS" if exit_code == 0 else ("⚠️ EXPECTED FAIL" if ar_id in ["056", "057", "058", "059", "060", "061", "062", "063", "068"] else "❌ FAIL")
        print(f"AR_{ar_id}: {status}")
    
    # Check critical ARs
    critical_ars = ["004", "069"]
    all_critical_passed = all(results.get(ar_id, 1) == 0 for ar_id in critical_ars)
    
    sys.exit(0 if all_critical_passed else 1)
