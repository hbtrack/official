#!/usr/bin/env python3
"""Execute AR_061 hb report using venv Python explicitly."""
import subprocess
import sys
from pathlib import Path

# Define paths
workspace_root = Path(r"C:\HB TRACK")
venv_python = workspace_root / "Hb Track - Backend" / ".venv" / "Scripts" / "python.exe"
hb_cli = workspace_root / "scripts" / "run" / "hb_cli.py"

# AR_061 details
ar_id = "061"
validation_cmd = (
    "python -c \"import pathlib; "
    "p=pathlib.Path('Hb Track - Backend/docs/ssot/alembic_state.txt'); "
    "assert p.exists(),'FAIL: alembic_state.txt nao encontrado'; "
    "c=p.read_text(encoding='utf-8'); "
    "assert '0061' in c,f'FAIL: alembic_state.txt nao menciona 0061'; "
    "assert '0059 (head)' not in c,'FAIL: ainda mostra 0059 como head'; "
    "print(f'PASS AR_061: alembic_state.txt atualizado, 0061 presente')\""
)

print(f"=== AR_061 HB REPORT (using venv Python) ===")
print(f"venv Python: {venv_python}")
print(f"hb_cli: {hb_cli}")
print(f"Comando: {venv_python} {hb_cli} report {ar_id} ...")
print()

# Execute hb report
cmd = [str(venv_python), str(hb_cli), "report", ar_id, validation_cmd]
result = subprocess.run(cmd, cwd=str(workspace_root), capture_output=True, text=True)

print("=== STDOUT ===")
print(result.stdout)
print()
print("=== STDERR ===")
print(result.stderr)
print()
print(f"=== EXIT CODE: {result.returncode} ===")

sys.exit(result.returncode)
