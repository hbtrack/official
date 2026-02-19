from __future__ import annotations
import json
import os
import subprocess
import sys
from typing import Any, Dict, Optional

ALLOWED_EXIT = {0, 2, 3, 4}

def _load_json(path: str) -> Optional[Dict[str, Any]]:
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def _reports_root() -> str:
    # Prefer config.py (regra do seu ambiente), fallback determinístico.
    try:
        import config  # type: ignore
        root = getattr(config, "REPORTS_ROOT", None)
        if isinstance(root, str) and root.strip():
            return root.strip()
    except Exception:
        pass
    return "_reports"

def main() -> int:
    # Args minimalistas (sem PyYAML). Formato:
    # python scripts/audit/run_gate_via_capability.py <GATE_ID> <CAPABILITY> <RUN_ID>
    if len(sys.argv) < 4:
        print("ERROR: usage: run_gate_via_capability.py <GATE_ID> <CAPABILITY> <RUN_ID>")
        return 4

    gate_id = sys.argv[1].strip()
    capability = sys.argv[2].strip()
    run_id = sys.argv[3].strip()

    if not gate_id or not capability or not run_id:
        print("ERROR: gate_id/capability/run_id required")
        return 4

    # 1) Executa a capability runner (SSOT operacional)
    cmd = [
        sys.executable,
        "scripts/gates/run_capability_gates.py",
        "--capability",
        capability,
        "--run-id",
        run_id,
    ]
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")

    # 2) Procura o result.json do gate desejado
    root = _reports_root()
    res_path = os.path.join(root, "audit", run_id, "checks", gate_id, "result.json")
    res = _load_json(res_path)

    if not res:
        print(f"BLOCKED_INPUT: missing/invalid result.json for gate={gate_id} in run_id={run_id}")
        # Debug controlado (não “prova”, mas ajuda): stdout/stderr da harness
        if p.stdout:
            print("HARNESS_STDOUT:\n" + p.stdout)
        if p.stderr:
            print("HARNESS_STDERR:\n" + p.stderr)
        return 4

    raw_exit = res.get("exit_code", 2)
    try:
        raw_exit = int(raw_exit)
    except Exception:
        raw_exit = 2

    # 3) Normaliza para {0,2,3,4}
    if raw_exit not in ALLOWED_EXIT:
        raw_exit = 2

    return raw_exit

if __name__ == "__main__":
    sys.exit(main())
