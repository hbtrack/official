"""Helper: extrai validation_command da AR e roda hb report 164."""
import re
import subprocess
import sys
from pathlib import Path

AR_PATH = Path("docs/hbtrack/ars/features/AR_164_feedback_imediato_pos_conversacional_077.md")
ar_text = AR_PATH.read_text(encoding="utf-8")

m = re.search(r"## Validation Command \(Contrato\)\n```\n(.+?)\n```", ar_text, re.DOTALL)
if not m:
    print("ERRO: Validation Command não encontrado", file=sys.stderr)
    sys.exit(1)

validation_cmd = m.group(1).strip()
print(f"[ar164] cmd extraído ({len(validation_cmd)} chars)")

cmd = [sys.executable, "scripts/run/hb_cli.py", "report", "164", validation_cmd]
result = subprocess.run(cmd, text=True, encoding="utf-8", errors="replace")
sys.exit(result.returncode)
