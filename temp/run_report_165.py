"""Extrai o validation_command da AR_165 e executa hb report."""
import re
import subprocess
import sys
from pathlib import Path

ar_file = Path("docs/hbtrack/ars/features/AR_165_reconhecimento_sem_vazamento_intimo_079.md")
content = ar_file.read_text(encoding="utf-8")

m = re.search(r"## Validation Command \(Contrato\)\n```\n(.+?)\n```", content, re.DOTALL)
if not m:
    print("ERRO: validation_command não encontrado na AR")
    sys.exit(1)

declared_cmd = m.group(1).strip()
print(f"[DEBUG] Declared cmd (primeiros 80 chars): {declared_cmd[:80]!r}")

result = subprocess.run(
    [sys.executable, "scripts/run/hb_cli.py", "report", "165", declared_cmd],
    capture_output=False,
)
sys.exit(result.returncode)
