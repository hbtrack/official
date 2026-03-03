"""Driver: executa hb report 187 extraindo validation_command do AR file."""
import re
import subprocess
import sys
from pathlib import Path

ar_path = Path("docs/hbtrack/ars/features/AR_187_criar_athlete_training.py_router_preview_+_fe_visa.md")
text = ar_path.read_text(encoding="utf-8")

m = re.search(r"## Validation Command \(Contrato\).*?```\s*\n(.*?)```", text, re.DOTALL)
if not m:
    print("ERRO: validation_command não encontrado no AR file", file=sys.stderr)
    sys.exit(4)

cmd = m.group(1).strip()
result = subprocess.run([sys.executable, "scripts/run/hb_cli.py", "report", "187", cmd])
sys.exit(result.returncode)
