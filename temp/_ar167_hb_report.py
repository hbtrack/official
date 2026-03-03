"""
Wrapper que lê o declared_cmd da AR_167 e chama hb_cli.py report com o argumento exato.
"""
import re
import sys
import subprocess
from pathlib import Path

ar_file = Path("docs/hbtrack/ars/features/AR_167_gate_ia_coach_072-081_tests_exist_+_pytest.md")
ar_content = ar_file.read_text(encoding="utf-8")

match = re.search(r"## Validation Command \(Contrato\)\n```\n(.+?)\n```", ar_content, re.DOTALL)
if not match:
    print("ERRO: não encontrou Validation Command na AR", file=sys.stderr)
    sys.exit(1)

declared_cmd = match.group(1).strip()
print(f"[wrapper] declared_cmd extraído ({len(declared_cmd)} chars)")

python_exe = sys.executable
result = subprocess.run(
    [python_exe, "scripts/run/hb_cli.py", "report", "167", declared_cmd],
    capture_output=False,
)
sys.exit(result.returncode)
