"""Driver: extrai validation_command do AR_188 e chama hb_cli.py report."""
import sys
import re
import subprocess
from pathlib import Path

# Lê o AR file e extrai o validation_command exato
ar_path = Path("docs/hbtrack/ars/features/AR_188_test_matrix_sync_batch2_3_-_ar-train-006..014_veri.md")
text = ar_path.read_text(encoding="utf-8")

# Extrai bloco de código após "## Validation Command"
m = re.search(r"## Validation Command.*?```\s*\n(.*?)```", text, re.DOTALL)
if not m:
    print("ERRO: validation_command nao encontrado no AR", file=sys.stderr)
    sys.exit(1)

validation_command = m.group(1).strip()
print(f"[driver] validation_command extraido ({len(validation_command)} chars)")

result = subprocess.run(
    [sys.executable, "scripts/run/hb_cli.py", "report", "188", validation_command],
    capture_output=False,
)
sys.exit(result.returncode)
