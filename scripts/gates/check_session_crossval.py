#!/usr/bin/env python3
"""
Cross-validation gate: session_start.json ↔ SESSION_HANDOFF.md

Detecta divergências entre os dois arquivos de estado de sessão:
- branch ativo
- boot_profile_id
- task_type
- module/modulo_foco
- modo de operação (CDD/ROADMAP)

Exit codes:
  0 — PASS (estado coerente ou um dos arquivos ausente)
  2 — FAIL_ACTIONABLE (divergência detectada)
  4 — BLOCKED_INPUT (arquivo malformado)

Usa apenas stdlib (sem dependências externas).
"""
import json
import re
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent.parent
SESSION_START = WORKSPACE / "_reports" / "session_start.json"
SESSION_HANDOFF = WORKSPACE / "SESSION_HANDOFF.md"


def parse_handoff_frontmatter(text: str) -> dict:
    """Extrai front matter YAML de SESSION_HANDOFF.md via regex (sem PyYAML)."""
    match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return {}
    fm = {}
    for line in match.group(1).splitlines():
        m = re.match(r"^(\w+)\s*:\s*(.+)$", line.strip())
        if m:
            key = m.group(1).strip()
            val = m.group(2).strip().strip('"').strip("'")
            # Parse integer values
            if re.match(r"^\d+$", val):
                fm[key] = int(val)
            else:
                fm[key] = val
    return fm


def load_session_start() -> dict:
    """Carrega _reports/session_start.json."""
    try:
        return json.loads(SESSION_START.read_text())
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return {"_error": str(e)}


def cross_validate(start: dict, handoff: dict) -> list[dict]:
    """Retorna lista de divergências encontradas."""
    divergences = []

    # Map session_start fields → handoff fields
    checks = [
        ("branch", "branch_ativo", "Branch ativo"),
        ("boot_profile_id", "boot_profile_id", "Boot profile ID"),
        ("task_type", "task_type", "Task type"),
    ]

    for start_key, handoff_key, label in checks:
        sv = start.get(start_key)
        hv = handoff.get(handoff_key)
        if sv is not None and hv is not None and str(sv) != str(hv):
            divergences.append({
                "field": label,
                "session_start": sv,
                "session_handoff": hv,
                "severity": "high",
            })

    # module vs modulo_foco
    sm = start.get("module") or start.get("module_focus")
    hm = handoff.get("modulo_foco")
    if sm is not None and hm is not None and str(sm) != str(hm):
        divergences.append({
            "field": "Módulo foco",
            "session_start": sm,
            "session_handoff": hm,
            "severity": "high",
        })

    # operation_mode vs modo_operacao
    so = start.get("operation_mode")
    ho = handoff.get("modo_operacao")
    if so is not None and ho is not None and str(so) != str(ho):
        divergences.append({
            "field": "Modo de operação",
            "session_start": so,
            "session_handoff": ho,
            "severity": "critical",
        })

    return divergences


def main() -> int:
    json_output = "--json" in sys.argv

    if not SESSION_START.exists():
        if json_output:
            print(json.dumps({"status": "SKIP", "reason": "session_start.json not found"}))
        else:
            print("⏭️  session_start.json não encontrado — skip")
        return 0

    if not SESSION_HANDOFF.exists():
        if json_output:
            print(json.dumps({"status": "SKIP", "reason": "SESSION_HANDOFF.md not found"}))
        else:
            print("⏭️  SESSION_HANDOFF.md não encontrado — skip")
        return 0

    start = load_session_start()
    if "_error" in start:
        if json_output:
            print(json.dumps({"status": "BLOCKED_INPUT", "error": start["_error"]}))
        else:
            print(f"❌ session_start.json malformado: {start['_error']}")
        return 4

    try:
        handoff_text = SESSION_HANDOFF.read_text()
    except Exception as e:
        if json_output:
            print(json.dumps({"status": "BLOCKED_INPUT", "error": str(e)}))
        else:
            print(f"❌ SESSION_HANDOFF.md ilegível: {e}")
        return 4

    handoff = parse_handoff_frontmatter(handoff_text)
    if not handoff:
        if json_output:
            print(json.dumps({"status": "BLOCKED_INPUT", "error": "No YAML front matter in SESSION_HANDOFF.md"}))
        else:
            print("❌ SESSION_HANDOFF.md sem front matter YAML")
        return 4

    divergences = cross_validate(start, handoff)

    if not divergences:
        if json_output:
            print(json.dumps({"status": "PASS", "divergences": []}))
        else:
            print("✅ Cross-validation PASS — session_start.json ↔ SESSION_HANDOFF.md coerentes")
        return 0

    if json_output:
        print(json.dumps({"status": "FAIL", "divergences": divergences}, indent=2))
    else:
        print(f"❌ Cross-validation FAIL — {len(divergences)} divergência(s) detectada(s):\n")
        for d in divergences:
            print(f"  [{d['severity'].upper()}] {d['field']}:")
            print(f"    session_start.json: {d['session_start']}")
            print(f"    SESSION_HANDOFF.md: {d['session_handoff']}")
            print()

    return 2


if __name__ == "__main__":
    sys.exit(main())
