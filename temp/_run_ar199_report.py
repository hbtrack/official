"""Driver: extrai validation_command do AR_199 e chama hb_cli.py report."""
import sys, re, subprocess
from pathlib import Path

ar_path = Path(
    "docs/hbtrack/ars/features/"
    "AR_199_test_matrix_\u00a79_sync_+_desbloquear_\u00a75_inv_+_\u00a78_cont.md"
)
text = ar_path.read_text(encoding="utf-8")
m = re.search(r"## Validation Command.*?```\s*\n(.*?)```", text, re.DOTALL)
if not m:
    print("ERRO: validation_command nao encontrado no AR_199")
    sys.exit(1)
validation_command = m.group(1).strip()
print(f"[driver] validation_command extraido ({len(validation_command)} chars)")
result = subprocess.run(
    [sys.executable, "scripts/run/hb_cli.py", "report", "199", validation_command],
    capture_output=False,
)
sys.exit(result.returncode)
