#!/usr/bin/env python3
"""
Stop Hook — ADVISORY (não-bloqueante)
Avisa o agente quando existem artefatos canônicos não commitados antes de encerrar.

CLASSIFICAÇÃO: advisory / informational — sempre sai com exit(0).
Não é um guard, não bloqueia, não é enforcement.
Registrado em .claude/settings.local.json como "Stop" hook advisory.
Ver HBCONTROL.md Onda 0 para contexto.

Usa apenas stdlib.
"""
import json
import subprocess
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent.parent

# Prefixos canônicos que exigem commit ao final de uma sessão CDD
CANONICAL_PREFIXES = [
    "contracts/",
    "docs/hbtrack/",
    "docs/_canon/",
    "SESSION_HANDOFF",
]


def main():
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            cwd=WORKSPACE,
        )
        if result.returncode != 0:
            sys.exit(0)

        uncommitted = []
        for line in result.stdout.splitlines():
            if len(line) < 4:
                continue
            path = line[3:].strip()
            if any(path.startswith(p) for p in CANONICAL_PREFIXES):
                uncommitted.append(path)

        if not uncommitted:
            sys.exit(0)

        preview = "\n  ".join(uncommitted[:6])
        if len(uncommitted) > 6:
            preview += f"\n  ... e {len(uncommitted) - 6} arquivo(s) adicional(is)"

        message = (
            f"⚠️  FASE 6 PENDENTE — {len(uncommitted)} artefato(s) canônico(s) sem commit.\n\n"
            f"Arquivos modificados:\n"
            f"  {preview}\n\n"
            f"Execute antes de encerrar a sessão:\n"
            f"  git add <artefatos> SESSION_HANDOFF.md\n"
            f"  git commit -m \"feat(contract): <module> — <task_type> pipeline PASS\"\n\n"
            f"Sem commit: o pre-commit hook não executa e o trabalho não é rastreável "
            f"(conforme AGENT_INSTRUCTIONS.md §5, Regra de ouro #8)."
        )

        print(json.dumps({"systemMessage": message}))
        sys.exit(0)

    except Exception as e:
        print(f"advisory_session_commit warning: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
