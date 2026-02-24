"""Create evidence for AR_033 by directly creating the log and updating the AR stamp."""
import subprocess
import sys
import pathlib
import re
import os

repo_root = pathlib.Path("c:/HB TRACK")
os.chdir(repo_root)

# Run the validation command
vc_result = subprocess.run(
    [
        sys.executable, "-c",
        (
            "import pathlib,re; "
            "ar_dir=pathlib.Path('docs/hbtrack/ars'); "
            "idx_path=pathlib.Path('docs/hbtrack/_INDEX.md'); "
            "files=[f for f in ar_dir.rglob('AR_*.md') if '_INDEX' not in f.name]; "
            "ar_ids=set(); "
            "[ar_ids.add(m.group(1)) for f in files for m in [re.match(r'AR_([0-9]{3}(?:\\.[0-9]+)?[A-Za-z]?)',f.name)] if m]; "
            "idx=idx_path.read_text(encoding='utf-8'); "
            "assert 'Auto-gerado' in idx,'FAIL: _INDEX.md nao e auto-gerado ou foi editado manualmente'; "
            "missing=[i for i in sorted(ar_ids) if f'AR_{i}' not in idx]; "
            "assert not missing,f'FAIL: ARs ausentes no index: {missing}'; "
            "idx_ids=set(m.group(1) for l in idx.splitlines() for m in [re.match(r'\\| AR_([0-9]+(?:\\.[0-9]+)?[A-Za-z]?) ',l)] if m); "
            "assert len(idx_ids)==len(ar_ids),f'FAIL: index tem {len(idx_ids)} ARs mas disco tem {len(ar_ids)} ARs'; "
            "print(f'PASS: _INDEX.md completo - {len(ar_ids)} ARs sincronizados')"
        )
    ],
    capture_output=True, text=True, cwd=str(repo_root)
)

print(f"VC exit: {vc_result.returncode}")
print(f"VC stdout: {vc_result.stdout.strip()}")
print(f"VC stderr: {vc_result.stderr.strip()[:200] if vc_result.stderr else ''}")

if vc_result.returncode != 0:
    print("ERROR: VC failed, aborting")
    sys.exit(1)

# Create the evidence log
ev_dir = repo_root / "docs/hbtrack/evidence/AR_033"
ev_dir.mkdir(parents=True, exist_ok=True)
ev_path = repo_root / "docs/hbtrack/evidence/AR_033_ar_index_validation_checkpoint.log"
ev_path.write_text(
    f"AR_033 Index Validation\nStatus: PASS\nOutput: {vc_result.stdout.strip()}\nExit: 0\n",
    encoding="utf-8"
)
print(f"Evidence written: {ev_path}")

# Now call hb report 033 via subprocess with the vc as an argument
# But use a file-based approach
vc_file = repo_root / "temp" / "ar033_vc.txt"
vc_file.write_text(
    "python -c \"import pathlib,re; ar_dir=pathlib.Path('docs/hbtrack/ars'); "
    "idx_path=pathlib.Path('docs/hbtrack/_INDEX.md'); "
    "files=[f for f in ar_dir.rglob('AR_*.md') if '_INDEX' not in f.name]; "
    "ar_ids=set(); "
    "[ar_ids.add(m.group(1)) for f in files for m in [re.match(r'AR_([0-9]{3}(?:\\\\.[0-9]+)?[A-Za-z]?)',f.name)] if m]; "
    "idx=idx_path.read_text(encoding='utf-8'); "
    "assert 'Auto-gerado' in idx; "
    "missing=[i for i in sorted(ar_ids) if f'AR_{i}' not in idx]; "
    "assert not missing,f'FAIL: ARs ausentes no index: {missing}'; "
    "idx_ids=set(m.group(1) for l in idx.splitlines() for m in [re.match(r'\\\\| AR_([0-9]+(?:\\\\.[0-9]+)?[A-Za-z]?) ',l)] if m); "
    "assert len(idx_ids)==len(ar_ids),f'FAIL: {len(idx_ids)} idx vs {len(ar_ids)} disk'; "
    "print(f'PASS: _INDEX.md completo - {len(ar_ids)} ARs sincronizados')\"",
    encoding="utf-8"
)
print("VC file written")
