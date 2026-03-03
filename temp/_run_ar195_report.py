"""Helper para rodar hb report 195 com validation_command da AR_195 (AC-001)."""
import subprocess
import sys
import os

os.chdir(r"c:\HB TRACK")

# Definir PYTHONUTF8=1 nos env vars para que open() use UTF-8 por padrão
env = os.environ.copy()
env["PYTHONUTF8"] = "1"

validation_command = (
    "python -c \""
    "c=open('docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md').read(); "
    "assert 'AR-TRAIN-010B' in c, 'AR-TRAIN-010B ausente TEST_MATRIX'; "
    "s13=c[max(0,c.index('INV-TRAIN-013')-200):c.index('INV-TRAIN-013')+1000]; "
    "assert 'AR-TRAIN-010B' in s13, 'AR-TRAIN-010B nao referenciado perto de INV-TRAIN-013'; "
    "s24=c[max(0,c.index('INV-TRAIN-024')-200):c.index('INV-TRAIN-024')+1000]; "
    "assert 'AR-TRAIN-010B' in s24, 'AR-TRAIN-010B nao referenciado perto de INV-TRAIN-024'; "
    "print('OK: AC-001 PASS')\""
)

result = subprocess.run(
    [sys.executable, "scripts/run/hb_cli.py", "report", "195", validation_command],
    capture_output=False,
    text=True,
    encoding="utf-8",
    env=env,
)

sys.exit(result.returncode)
