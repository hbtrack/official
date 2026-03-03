"""Driver: extrai validation_command do AR_198 e chama hb_cli.py report."""
import sys
import re
import subprocess
from pathlib import Path

ar_path = Path("docs/hbtrack/ars/features/AR_198_ar_backlog_ar-train-022_verificado_+_add_ar-train-.md")
text = ar_path.read_text(encoding="utf-8")

m = re.search(r"## Validation Command.*?```\s*\n(.*?)```", text, re.DOTALL)
if not m:
    print("ERRO: validation_command nao encontrado no AR", file=sys.stderr)
    sys.exit(1)

validation_command = m.group(1).strip()
print(f"[driver] validation_command extraido ({len(validation_command)} chars)")

result = subprocess.run(
    [sys.executable, "scripts/run/hb_cli.py", "report", "198", validation_command],
    capture_output=False,
)
sys.exit(result.returncode)
