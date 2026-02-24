"""Run hb report 033 with the corrected validation command."""
import subprocess
import sys

vc = (
    'python -c "'
    'import pathlib,re; '
    'ar_dir=pathlib.Path(\'docs/hbtrack/ars\'); '
    'idx_path=pathlib.Path(\'docs/hbtrack/_INDEX.md\'); '
    'files=[f for f in ar_dir.rglob(\'AR_*.md\') if \'_INDEX\' not in f.name]; '
    'ar_ids=set(); '
    '[ar_ids.add(m.group(1)) for f in files for m in [re.match(r\'AR_([0-9]{3}(?:\\\\.[0-9]+)?[A-Za-z]?)\',f.name)] if m]; '
    'idx=idx_path.read_text(encoding=\'utf-8\'); '
    'assert \'Auto-gerado\' in idx,\'FAIL: _INDEX.md nao e auto-gerado ou foi editado manualmente\'; '
    'missing=[i for i in sorted(ar_ids) if f\'AR_{i}\' not in idx]; '
    'assert not missing,f\'FAIL: ARs ausentes no index: {missing}\'; '
    'idx_ids=set(m.group(1) for l in idx.splitlines() for m in [re.match(r\'\\\\| AR_([0-9]+(?:\\\\.[0-9]+)?[A-Za-z]?) \',l)] if m); '
    'assert len(idx_ids)==len(ar_ids),f\'FAIL: index tem {len(idx_ids)} ARs mas disco tem {len(ar_ids)} ARs\'; '
    'print(f\'PASS: _INDEX.md completo - {len(ar_ids)} ARs sincronizados\')"'
)

result = subprocess.run(
    [sys.executable, 'scripts/run/hb_cli.py', 'report', '033', vc],
    cwd='c:\\HB TRACK',
    capture_output=True,
    text=True
)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("Exit:", result.returncode)
