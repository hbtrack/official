#!/usr/bin/env python3
"""
HB Track — DOCS_CANON_CHECK
Kind: CHECK (ENFORCER)
Side-effects: FS_READ
Exit codes (canônico):
  0 PASS
  2 FAIL_ACTIONABLE (violação/drift)
  3 ERROR_INFRA (erro de harness/execução)
  4 BLOCKED_INPUT (entrada/pré-requisito ausente)  [não usado aqui; reservado]
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import List


def _repo_root() -> Path:
    # scripts/checks/check_docs_canon.py -> parents[2] == repo root
    return Path(__file__).resolve().parents[2]


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def main(argv: List[str]) -> int:
    try:
        repo = _repo_root()

        manual = repo / "docs" / "hbtrack" / "manuais" / "Manual Deterministico.md"
        index_yaml = repo / "docs" / "_INDEX.yaml"
        gates_registry = repo / "docs" / "_canon" / "_agent" / "GATES_REGISTRY.yaml"
        cap_runner = repo / "scripts" / "gates" / "run_capability_gates.py"

        errors: List[str] = []

        # 1) Manual existe
        if not manual.exists():
            errors.append(f"[E001] Missing manual SSOT: {manual}")

        # 2) _INDEX referencia o manual como entrypoint
        if not index_yaml.exists():
            errors.append(f"[E002] Missing root index: {index_yaml}")
        else:
            idx = _read_text(index_yaml)
            if "docs/hbtrack/manuais/Manual Deterministico.md" not in idx:
                errors.append("[E003] docs/_INDEX.yaml does not reference docs/hbtrack/manuais/Manual Deterministico.md")

        # 3) GATES_REGISTRY reports_root == _reports
        if not gates_registry.exists():
            errors.append(f"[E004] Missing GATES_REGISTRY SSOT: {gates_registry}")
        else:
            reg = _read_text(gates_registry)
            if 'reports_root: "_reports"' not in reg and "reports_root: '_reports'" not in reg:
                errors.append('[E005] GATES_REGISTRY.yaml does not declare reports_root: "_reports"')

        # 4) Nenhum hardcode do root divergente no capability runner
        if not cap_runner.exists():
            errors.append(f"[E006] Missing capability runner: {cap_runner}")
        else:
            cr = _read_text(cap_runner)
            if "docs/ssot/_reports" in cr.replace("\\", "/"):
                errors.append("[E007] run_capability_gates.py still contains hardcoded docs/ssot/_reports")

        # 5) Tokens de "citação" (se tiverem sido gravados no YAML do repo, isso contamina SSOT)
        # (não depende de PyYAML; é verificação textual)
        suspicious_tokens = ["[cite_start]", "[cite:"]
        # checar apenas nos SSOTs agent que você mostrou como críticos
        ssot_candidates = [
            repo / "docs" / "_canon" / "_agent" / "CORRECTION_WRITE_ALLOWLIST.yaml",
            repo / "docs" / "_canon" / "_agent" / "FAILURE_TO_GATES.yaml",
            repo / "docs" / "_canon" / "_agent" / "GATES_REGISTRY.yaml",
        ]
        for p in ssot_candidates:
            if p.exists():
                txt = _read_text(p)
                for tok in suspicious_tokens:
                    if tok in txt:
                        errors.append(f"[E008] SSOT token contamination: found '{tok}' in {p}")

        # 6) Verificar política VPS no manual (PY-ONLY enforcement)
        if manual.exists():
            man = _read_text(manual)
            vps_policy_markers = ["0.3.1 Politica VPS", "somente scripts Python (.py)"]
            missing_markers = [m for m in vps_policy_markers if m not in man]
            if missing_markers:
                errors.append(f"[E009] Missing VPS .py-only policy in manual: {', '.join(missing_markers)}")

        if errors:
            print("FAIL_ACTIONABLE (2): DOCS_CANON_CHECK violations detected")
            for e in errors:
                print(e)
            return 2

        print("PASS (0): DOCS_CANON_CHECK OK")
        print(f"repo_root={repo}")
        return 0

    except Exception as ex:
        print("ERROR_INFRA (3): DOCS_CANON_CHECK crashed")
        print(repr(ex))
        return 3


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))