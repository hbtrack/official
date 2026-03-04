#!/usr/bin/env python3
"""
Gate: check_ops_invariants.py

Scanner de Invariantes Operacionais HB Track.

Checa um conjunto mínimo de invariantes do runtime:
  INV-OPS-001  Entrypoint único do hb_cli (tasks.json)
  INV-OPS-002  Encoding seguro (utf-8 + errors=replace) em hb_cli gate-runners
  INV-OPS-003  Registro canônico: DOC-GATE-019/020/021 em GATES_REGISTRY.yaml
  INV-OPS-010  Regras mínimas nos arquivos .agent.md
  INV-OPS-015  Todo check_*.py de gate tem test_*.py correspondente
  INV-OPS-DOC  Documento SSOT de invariantes existe no path configurado

Exit codes (canônico HB Track):
  0 = PASS
  2 = FAIL_ACTIONABLE
  3 = ERROR_INFRA
  4 = BLOCKED_INPUT

Uso:
  python scripts/gates/check_ops_invariants.py [--json] [--ops-doc <path>]

  --json      grava _reports/ops_invariants/result.json além do stdout
  --ops-doc   path relativo ao repo do doc SSOT de invariantes
              default: docs/invariantes/INVARIANTS_OPERACIONAIS_HBTRACK.md
"""
from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Tuple

EXIT_PASS = 0
EXIT_FAIL_ACTIONABLE = 2
EXIT_ERROR_INFRA = 3
EXIT_BLOCKED_INPUT = 4

MARKER = "# OPS-SCAN/V1"

DEFAULT_OPS_DOC = "docs/invariantes/INVARIANTS_OPERACIONAIS_HBTRACK.md"
GATES_REGISTRY_REL = "docs/_canon/specs/GATES_REGISTRY.yaml"


@dataclass(frozen=True)
class CheckResult:
    id: str
    ok: bool
    severity: str  # "A" | "B"
    message: str
    evidence: List[str] = field(default_factory=list)


def _repo_root() -> Path:
    """Script está em scripts/gates/ → parents[2] é o repo root."""
    return Path(__file__).resolve().parents[2]


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _write_result_json(out_path: Path, payload: dict) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


# ─────────────────────────────────────────────────────────────
# INV-OPS-DOC: doc SSOT de invariantes existe
# ─────────────────────────────────────────────────────────────

def _check_ops_doc_exists(repo: Path, ops_doc_rel: str) -> CheckResult:
    p = repo / ops_doc_rel
    if not p.exists():
        return CheckResult(
            id="INV-OPS-DOC",
            ok=False,
            severity="A",
            message=f"BLOCKED_INPUT: doc SSOT de invariantes ausente: {ops_doc_rel}",
            evidence=[str(p)],
        )
    return CheckResult(
        id="INV-OPS-DOC",
        ok=True,
        severity="A",
        message=f"OK: doc SSOT de invariantes encontrado: {ops_doc_rel}",
        evidence=[str(p)],
    )


# ─────────────────────────────────────────────────────────────
# INV-OPS-001: entrypoint hb_cli único em tasks.json
# ─────────────────────────────────────────────────────────────

def _check_tasks_point_to_single_hb_cli(repo: Path) -> CheckResult:
    tasks = repo / ".vscode" / "tasks.json"
    if not tasks.exists():
        return CheckResult(
            id="INV-OPS-001",
            ok=False,
            severity="A",
            message="BLOCKED_INPUT: .vscode/tasks.json não encontrado",
            evidence=[str(tasks)],
        )

    txt = _read_text(tasks)

    # Captura todos os valores de string que terminam em hb_cli.py dentro do JSON
    paths = set(re.findall(r'"([^"]*hb_cli\.py)"', txt, flags=re.IGNORECASE))
    if not paths:
        return CheckResult(
            id="INV-OPS-001",
            ok=False,
            severity="A",
            message="FAIL_ACTIONABLE: tasks.json não referencia hb_cli.py",
            evidence=[str(tasks)],
        )

    norm = sorted({p.replace("\\", "/") for p in paths})
    if len(norm) != 1:
        return CheckResult(
            id="INV-OPS-001",
            ok=False,
            severity="A",
            message=f"FAIL_ACTIONABLE: múltiplos paths hb_cli em tasks.json: {norm}",
            evidence=[str(tasks)],
        )

    hb_path = (repo / norm[0]).resolve()
    if not hb_path.exists():
        return CheckResult(
            id="INV-OPS-001",
            ok=False,
            severity="A",
            message=f"FAIL_ACTIONABLE: hb_cli referenciado em tasks.json não existe: {norm[0]}",
            evidence=[str(tasks), str(hb_path)],
        )

    return CheckResult(
        id="INV-OPS-001",
        ok=True,
        severity="A",
        message=f"OK: entrypoint hb_cli único = {norm[0]}",
        evidence=[str(tasks), str(hb_path)],
    )


# ─────────────────────────────────────────────────────────────
# INV-OPS-002: encoding seguro nos runners de gate em hb_cli
# ─────────────────────────────────────────────────────────────

def _check_hb_cli_gate_runner_encoding(repo: Path) -> CheckResult:
    hb = repo / "scripts" / "run" / "hb_cli.py"
    if not hb.exists():
        return CheckResult(
            id="INV-OPS-002",
            ok=False,
            severity="A",
            message="BLOCKED_INPUT: scripts/run/hb_cli.py não encontrado",
            evidence=[str(hb)],
        )

    txt = _read_text(hb)
    has_encoding = 'encoding="utf-8"' in txt or "encoding='utf-8'" in txt
    has_errors = 'errors="replace"' in txt or "errors='replace'" in txt

    if not (has_encoding and has_errors):
        missing = []
        if not has_encoding:
            missing.append('encoding="utf-8"')
        if not has_errors:
            missing.append('errors="replace"')
        return CheckResult(
            id="INV-OPS-002",
            ok=False,
            severity="A",
            message=f'FAIL_ACTIONABLE: hb_cli gate-runner sem: {", ".join(missing)}',
            evidence=[str(hb)],
        )

    return CheckResult(
        id="INV-OPS-002",
        ok=True,
        severity="A",
        message='OK: hb_cli contém encoding="utf-8" + errors="replace"',
        evidence=[str(hb)],
    )


# ─────────────────────────────────────────────────────────────
# INV-OPS-003 (registry): DOC-GATE-019/020/021 registrados
# ─────────────────────────────────────────────────────────────

def _check_gates_registry_contains(repo: Path, gate_ids: List[str]) -> CheckResult:
    reg = repo / GATES_REGISTRY_REL
    if not reg.exists():
        return CheckResult(
            id="INV-OPS-003",
            ok=False,
            severity="A",
            message=f"BLOCKED_INPUT: GATES_REGISTRY.yaml não encontrado em {GATES_REGISTRY_REL}",
            evidence=[str(reg)],
        )

    txt = _read_text(reg)
    missing = [gid for gid in gate_ids if gid not in txt]
    if missing:
        return CheckResult(
            id="INV-OPS-003",
            ok=False,
            severity="A",
            message=f"FAIL_ACTIONABLE: gate(s) ausente(s) no registry: {missing}",
            evidence=[str(reg)],
        )

    return CheckResult(
        id="INV-OPS-003",
        ok=True,
        severity="A",
        message=f"OK: GATES_REGISTRY contém {gate_ids}",
        evidence=[str(reg)],
    )


# ─────────────────────────────────────────────────────────────
# INV-OPS-010: regras mínimas nos .agent.md
# ─────────────────────────────────────────────────────────────

def _check_agent_minimum_rules(repo: Path) -> CheckResult:
    agents = repo / ".github" / "agents"
    # Needles calibrados contra o conteúdo real dos arquivos (2026-03-04)
    required = {
        "Arquiteto.agent.md": [
            "Você NÃO executa: hb report",
            "PROOF",
            "TRACE",
        ],
        "Executor.agent.md": [
            "workspace clean",
            "FAIL_ACTIONABLE",
        ],
        "Testador.agent.md": [
            "hb verify",
            "E_DOD_STRICT_WARN",
            "result.json",
        ],
    }

    missing_files = [name for name in required if not (agents / name).exists()]
    if missing_files:
        return CheckResult(
            id="INV-OPS-010",
            ok=False,
            severity="A",
            message=f"BLOCKED_INPUT: agent file(s) ausente(s): {missing_files}",
            evidence=[str(agents)],
        )

    missing_rules: List[str] = []
    evidence: List[str] = []
    for fn, needles in required.items():
        p = agents / fn
        txt = _read_text(p)
        evidence.append(str(p))
        for n in needles:
            # case-sensitive para manter determinismo com os tokens canônicos
            if n not in txt:
                missing_rules.append(f"{fn}: '{n}'")

    if missing_rules:
        return CheckResult(
            id="INV-OPS-010",
            ok=False,
            severity="B",
            message="FAIL_ACTIONABLE: regras mínimas ausentes: " + "; ".join(missing_rules),
            evidence=evidence,
        )

    return CheckResult(
        id="INV-OPS-010",
        ok=True,
        severity="B",
        message="OK: regras mínimas presentes nos .agent.md",
        evidence=evidence,
    )


# ─────────────────────────────────────────────────────────────
# INV-OPS-015: todo check_*.py tem test_*.py correspondente
# ─────────────────────────────────────────────────────────────

def _check_gate_tests_exist(repo: Path) -> CheckResult:
    gates_dir = repo / "scripts" / "gates"
    tests_dir = gates_dir / "tests"

    if not gates_dir.exists():
        return CheckResult(
            id="INV-OPS-015",
            ok=False,
            severity="A",
            message="BLOCKED_INPUT: scripts/gates/ não encontrado",
            evidence=[str(gates_dir)],
        )
    if not tests_dir.exists():
        return CheckResult(
            id="INV-OPS-015",
            ok=False,
            severity="A",
            message="FAIL_ACTIONABLE: scripts/gates/tests/ não encontrado",
            evidence=[str(tests_dir)],
        )

    check_scripts = sorted(p for p in gates_dir.glob("check_*.py") if p.is_file())
    missing_tests: List[str] = []
    for s in check_scripts:
        t = tests_dir / f"test_{s.name}"
        if not t.exists():
            missing_tests.append(s.name)

    if missing_tests:
        return CheckResult(
            id="INV-OPS-015",
            ok=False,
            severity="A",
            message=f"FAIL_ACTIONABLE: gates sem test_*.py: {missing_tests}",
            evidence=[str(tests_dir)],
        )

    return CheckResult(
        id="INV-OPS-015",
        ok=True,
        severity="A",
        message=f"OK: {len(check_scripts)} gate(s) com teste(s) correspondente(s)",
        evidence=[str(tests_dir)],
    )


# ─────────────────────────────────────────────────────────────
# Orquestrador
# ─────────────────────────────────────────────────────────────

def run_all_checks(repo: Path, ops_doc_rel: str) -> Tuple[int, List[CheckResult]]:
    checks: List[CheckResult] = []

    checks.append(_check_ops_doc_exists(repo, ops_doc_rel))
    checks.append(_check_tasks_point_to_single_hb_cli(repo))
    checks.append(_check_hb_cli_gate_runner_encoding(repo))
    checks.append(_check_gates_registry_contains(repo, ["DOC-GATE-019", "DOC-GATE-020", "DOC-GATE-021"]))
    checks.append(_check_agent_minimum_rules(repo))
    checks.append(_check_gate_tests_exist(repo))

    blocked = [c for c in checks if not c.ok and c.message.startswith("BLOCKED_INPUT")]
    fail = [c for c in checks if not c.ok and c.message.startswith("FAIL_ACTIONABLE")]
    other_bad = [c for c in checks if not c.ok]

    if blocked:
        return EXIT_BLOCKED_INPUT, checks
    if fail or other_bad:
        return EXIT_FAIL_ACTIONABLE, checks
    return EXIT_PASS, checks


def main(argv: List[str]) -> int:
    # Parsing manual de args (sem argparse para zero deps extras)
    write_json = "--json" in argv
    ops_doc_rel = DEFAULT_OPS_DOC
    if "--ops-doc" in argv:
        idx = argv.index("--ops-doc")
        if idx + 1 < len(argv):
            ops_doc_rel = argv[idx + 1]

    repo = _repo_root()
    out_path = repo / "_reports" / "ops_invariants" / "result.json"
    exit_code, checks = run_all_checks(repo, ops_doc_rel)
    ts = datetime.now(timezone.utc).isoformat()

    print(f"marker=OPS-SCAN/V1")
    print(f"repo={repo}")
    print(f"ops_doc={ops_doc_rel}")
    print(f"timestamp_utc={ts}")
    print()

    for c in checks:
        status = "PASS" if c.ok else "FAIL"
        print(f"- {c.id} [{status}] ({c.severity}) {c.message}")
        for ev in c.evidence:
            print(f"    evidence: {ev}")

    payload = {
        "marker": "OPS-SCAN/V1",
        "timestamp_utc": ts,
        "repo_root": str(repo),
        "ops_doc": ops_doc_rel,
        "exit_code": exit_code,
        "checks": [
            {
                "id": c.id,
                "ok": c.ok,
                "severity": c.severity,
                "message": c.message,
                "evidence": c.evidence,
            }
            for c in checks
        ],
    }

    print()
    if write_json:
        _write_result_json(out_path, payload)
        print(f"result_json={out_path}")

    label = "PASS" if exit_code == 0 else ("BLOCKED_INPUT" if exit_code == 4 else "FAIL_ACTIONABLE")
    print(f"exit_code={exit_code} ({label})")
    return exit_code


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except SystemExit:
        raise
    except Exception as e:
        print(f"{MARKER} ERROR_INFRA: {type(e).__name__}: {e}")
        raise SystemExit(EXIT_ERROR_INFRA)
