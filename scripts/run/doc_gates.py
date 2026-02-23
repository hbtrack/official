#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HB Track — Doc Gates Runner (Determinístico)
Path: scripts/run/doc_gates.py
Versão: v1.2.0
Objetivo: Executar DOC_GATES (auditoria de documentação) em um único comando
          com exit codes determinísticos e evidence pack em docs/hbtrack/evidence/AR_<id>/.

Exit codes (determinístico):
  0 = PASS
  2 = FAIL_ACTIONABLE (gate falhou; ação humana/correção de docs)
  3 = ERROR_INFRA (dependência/erro de execução)
  4 = BLOCKED_INPUT (input inválido/ausente)

Evidence pack:
  docs/hbtrack/evidence/AR_<ar_id>/doc_gates.log

Changelog v1.2.0:
  - Adicionado DOC-GATE-017: Global scan de tokens proibidos em docs/ (exceto _legacy/)
  - Adicionado DOC-GATE-018: Architect scope protection (P3.1) - planos não referenciam backend/Frontend
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

# -------------------------
# Deterministic exit codes
# -------------------------
EXIT_PASS = 0
EXIT_FAIL_ACTIONABLE = 2
EXIT_ERROR_INFRA = 3
EXIT_BLOCKED_INPUT = 4

# -------------------------
# Error codes (deterministic)
# -------------------------
E_USAGE = "E_USAGE"
E_REPO_ROOT = "E_REPO_ROOT"
E_AR_ID_INVALID = "E_AR_ID_INVALID"
E_IO_READ = "E_IO_READ"
E_IO_WRITE = "E_IO_WRITE"
E_DEP_PYYAML = "E_DEP_PYYAML"
E_JSON_PARSE = "E_JSON_PARSE"

# Gate-level codes (actionable)
E_DOC_GATE_FAIL = "E_DOC_GATE_FAIL"

# -------------------------
# Repo root
# -------------------------
def get_repo_root() -> Path:
    # scripts/run/doc_gates.py -> repo root is 3 parents up
    return Path(__file__).resolve().parent.parent.parent

REPO_ROOT = get_repo_root()

# -------------------------
# Logging helpers
# -------------------------
def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def run_cmd(args: List[str]) -> Tuple[int, str, str]:
    import subprocess
    p = subprocess.run(
        args,
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return p.returncode, p.stdout, p.stderr

def fail(code: str, msg: str, exit_code: int) -> None:
    print(f"❌ {code}: {msg}", file=sys.stderr)
    sys.exit(exit_code)

def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception as e:
        raise IOError(f"read_text failed for {path.as_posix()}: {e}")

def write_text(path: Path, content: str) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    except Exception as e:
        raise IOError(f"write_text failed for {path.as_posix()}: {e}")

# -------------------------
# Gate model
# -------------------------
@dataclass(frozen=True)
class GateResult:
    gate_id: str
    target: str
    passed: bool
    details: str = ""
    severity: str = "ACTIONABLE"  # ACTIONABLE | INFRA

@dataclass(frozen=True)
class Gate:
    gate_id: str
    target: str
    description: str
    fn: Callable[[], GateResult]

# -------------------------
# Gate implementations (mirror DOC_GATES.md checks)
# -------------------------
def gate_001_devflow() -> GateResult:
    p = REPO_ROOT / "docs/_canon/contratos/Dev Flow.md"
    if not p.exists():
        return GateResult("DOC-GATE-001", p.as_posix(), False, "arquivo ausente")
    t = read_text(p)
    req = [
        "v1.2.0",
        "hb seal",
        "✅ SUCESSO",
        "🔴 REJEITADO",
        "⏸️ BLOQUEADO_INFRA",
        "Kanban NÃO libera commit",
        "schema_version",
        "executor_main.log",
        "behavior_hash",
    ]
    miss = [x for x in req if x not in t]
    return GateResult("DOC-GATE-001", p.as_posix(), not miss, f"missing={miss}" if miss else "")

def gate_002_schema() -> GateResult:
    p = REPO_ROOT / "docs/_canon/contratos/ar_contract.schema.json"
    if not p.exists():
        return GateResult("DOC-GATE-002", p.as_posix(), False, "arquivo ausente")
    raw = read_text(p)
    try:
        d = json.loads(raw)
    except Exception as e:
        return GateResult("DOC-GATE-002", p.as_posix(), False, f"{E_JSON_PARSE}: {e}", severity="INFRA")
    if d.get("schema_version") != "1.2.0":
        return GateResult("DOC-GATE-002", p.as_posix(), False, f"schema_version esperado=1.2.0 got={d.get('schema_version')}")
    req = ["schema_version", "\"1.2.0\"", "executor_main.log", "rollback_plan", "git checkout --", "git clean -fd", "psql -c"]
    miss = [x for x in req if x not in raw]
    return GateResult("DOC-GATE-002", p.as_posix(), not miss, f"missing={miss}" if miss else "")

def gate_003_governed_roots() -> GateResult:
    p = REPO_ROOT / "docs/_canon/specs/GOVERNED_ROOTS.yaml"
    if not p.exists():
        return GateResult("DOC-GATE-003", p.as_posix(), False, "arquivo ausente")
    try:
        import yaml  # PyYAML
    except ImportError:
        return GateResult("DOC-GATE-003", p.as_posix(), False, f"{E_DEP_PYYAML}: PyYAML não instalado", severity="INFRA")
    d = yaml.safe_load(read_text(p)) or {}
    roots = d.get("roots")
    if not isinstance(roots, list) or not roots:
        return GateResult("DOC-GATE-003", p.as_posix(), False, "roots deve ser lista não-vazia")
    if not all(isinstance(r, str) and r.strip() for r in roots):
        return GateResult("DOC-GATE-003", p.as_posix(), False, "roots contém item inválido (não-string/vazio)")
    return GateResult("DOC-GATE-003", p.as_posix(), True)

def _gate_contract_common(gate_id: str, rel_path: str, required: List[str]) -> GateResult:
    p = REPO_ROOT / rel_path
    if not p.exists():
        return GateResult(gate_id, p.as_posix(), False, "arquivo ausente")
    t = read_text(p)
    miss = [x for x in required if x not in t]
    return GateResult(gate_id, p.as_posix(), not miss, f"missing={miss}" if miss else "")

def gate_004_arquiteto_contract() -> GateResult:
    req = ["v2.2.0", "Protocol v1.2.0", "schema_version", "1.2.0", "hb seal", "executor_main.log", "rollback_plan", "git checkout --", "Kanban", "não libera commit", "_INDEX.md", "MUST NOT"]
    return _gate_contract_common("DOC-GATE-004", "docs/_canon/contratos/Arquiteto Contract.md", req)

def gate_005_executor_contract() -> GateResult:
    p = REPO_ROOT / "docs/_canon/contratos/Executor Contract.md"
    if not p.exists():
        return GateResult("DOC-GATE-005", p.as_posix(), False, "arquivo ausente")
    t = read_text(p)
    req = ["v2.1.0", "Protocol v1.2.0", "schema_version", "1.2.0", "hb report", "executor_main.log", "hb seal"]
    miss = [x for x in req if x not in t]
    if "_reports/audit" in t:
        miss.append("_reports/audit (proibido)")
    return GateResult("DOC-GATE-005", p.as_posix(), not miss, f"missing={miss}" if miss else "")

def gate_006_testador_contract() -> GateResult:
    req = [
        "v2.1.0", "Protocol v1.2.0", "schema_version", "1.2.0",
        "hb verify", "✅ SUCESSO", "🔴 REJEITADO", "⏸️ BLOQUEADO_INFRA",
        "hb seal", "behavior_hash", "exit_code + stdout_norm + stderr_norm",
        "AH-12", "PASS", "FAIL", "executor_evidence_timestamp_utc", "verify_start_timestamp_utc"
    ]
    return _gate_contract_common("DOC-GATE-006", "docs/_canon/contratos/Testador Contract.md", req)

def gate_007_arch_agent() -> GateResult:
    req = ["Protocol v1.2.0", "schema_version", "1.2.0", "hb seal", "executor_main.log", "GOVERNED_ROOTS.yaml", "GATES_REGISTRY.yaml", "Kanban"]
    return _gate_contract_common("DOC-GATE-007", ".github/agents/architect.agent.md", req)

def gate_008_exec_agent() -> GateResult:
    p = REPO_ROOT / ".github/agents/executor.agent.md"
    if not p.exists():
        return GateResult("DOC-GATE-008", p.as_posix(), False, "arquivo ausente")
    t = read_text(p)
    req = ["Protocol v1.2.0", "schema_version", "1.2.0", "hb report", "executor_main.log", "hb seal"]
    miss = [x for x in req if x not in t]
    if "_reports/audit" in t:
        miss.append("_reports/audit (proibido)")
    return GateResult("DOC-GATE-008", p.as_posix(), not miss, f"missing={miss}" if miss else "")

def gate_009_testador_agent() -> GateResult:
    req = ["Protocol v1.2.0", "hb verify", "✅ SUCESSO", "🔴 REJEITADO", "⏸️ BLOQUEADO_INFRA", "MUST NOT write ✅ VERIFICADO", "behavior_hash", "AH-12", "executor_main.log", "_reports/testador"]
    return _gate_contract_common("DOC-GATE-009", ".github/agents/testador.agent.md", req)

def gate_010_agents_readme() -> GateResult:
    req = ["SSOT", "DERIVED", "Kanban NÃO libera commit", "hb seal", "executor_main.log", "_reports/testador", "_INDEX.md"]
    return _gate_contract_common("DOC-GATE-010", ".github/agents/README.md", req)

def gate_011_hb_cli_spec() -> GateResult:
    candidates = [
        REPO_ROOT / "docs/_canon/specs/Hb cli.md",
        REPO_ROOT / "docs/_canon/specs/Hb cli Spec.md",
    ]
    p = next((x for x in candidates if x.exists()), None)
    if p is None:
        return GateResult("DOC-GATE-011", "docs/_canon/specs/Hb cli.md|Hb cli Spec.md", False, "nenhum spec encontrado")
    t = read_text(p)
    req = ["hb seal", "schema_version", "executor_main.log", "behavior_hash", "hb verify", "hb report"]
    miss = [x for x in req if x not in t]
    return GateResult("DOC-GATE-011", p.as_posix(), not miss, f"missing={miss}" if miss else "")

def gate_012_kanban_rule() -> GateResult:
    p = REPO_ROOT / "docs/hbtrack/Hb Track Kanban.md"
    if not p.exists():
        return GateResult("DOC-GATE-012", p.as_posix(), False, "arquivo ausente")
    t = read_text(p)
    ok = ("não libera commit" in t) or ("NÃO libera commit" in t)
    return GateResult("DOC-GATE-012", p.as_posix(), ok, "" if ok else "falta regra: Kanban não libera commit")

def gate_013_index_derived() -> GateResult:
    p = REPO_ROOT / "docs/hbtrack/_INDEX.md"
    if not p.exists():
        return GateResult("DOC-GATE-013", p.as_posix(), False, "arquivo ausente")
    t = read_text(p)
    req = ["Auto-gerado", "NÃO editar", "| ID |", "| Status |"]
    miss = [x for x in req if x not in t]
    return GateResult("DOC-GATE-013", p.as_posix(), not miss, f"missing={miss}" if miss else "")

def gate_014_hb_watch_automation() -> GateResult:
    """
    DOC-GATE-014 — Watcher existe e está alinhado com automação determinística:
    - usa _INDEX.md
    - respeita .hb_lock
    - usa dispatch files (_reports/dispatch)
    - usa git diff --cached (evidence staged -> trigger testador)
    - não usa status legado '🔬 EM TESTE'
    """
    p = REPO_ROOT / "scripts/run/hb_watch.py"
    if not p.exists():
        return GateResult("DOC-GATE-014", p.as_posix(), False, "arquivo ausente")

    t = read_text(p)

    required = [
        "docs/hbtrack/_INDEX.md",
        ".hb_lock",
        "_reports/dispatch",
        "git",
        "--cached",
        "--name-only",
    ]
    missing = [x for x in required if x not in t]
    if missing:
        return GateResult("DOC-GATE-014", p.as_posix(), False, f"missing={missing}")

    # Proibir status legado que não existe no v1.2.0
    forbidden = ["🔬 EM TESTE", "EM TESTE"]
    bad = [x for x in forbidden if x in t]
    if bad:
        return GateResult("DOC-GATE-014", p.as_posix(), False, f"forbidden_tokens={bad}")

    return GateResult("DOC-GATE-014", p.as_posix(), True)


def gate_015_devflow_documents_automation() -> GateResult:
    """
    DOC-GATE-015 — Dev Flow SSOT documenta automação + selo humano explícito:
    - menciona hb_watch.py (ou watcher canônico)
    - menciona dispatch inbox files (_reports/dispatch)
    - afirma: Testador só com evidence STAGED
    - afirma: hb seal é manual e último gate
    """
    p = REPO_ROOT / "docs/_canon/contratos/Dev Flow.md"
    if not p.exists():
        return GateResult("DOC-GATE-015", p.as_posix(), False, "arquivo ausente")

    t = read_text(p)

    required = [
        "hb_watch.py",
        "_reports/dispatch",
        "hb seal",
        "último gate",
        "evidence",
        "STAGED",
    ]
    missing = [x for x in required if x not in t]
    if missing:
        return GateResult("DOC-GATE-015", p.as_posix(), False, f"missing={missing}")

    # Garantir que a doc não atribui ao Testador o ✅ VERIFICADO (proibido pós I3)
    forbidden = ["hb verify + ✅ VERIFICADO", "Testador", "✅ VERIFICADO"]
    # Aqui não proibimos a palavra VERIFICADO globalmente (o doc deve falar do selo humano).
    # Proibimos apenas a combinação "Testador" perto de "✅ VERIFICADO" em um trecho curto.
    if "Testador" in t and "✅ VERIFICADO" in t:
        # Heurística determinística: exige que a doc também contenha "hb seal" e "Humano" (evita falso positivo)
        if "Humano" not in t or "hb seal" not in t:
            return GateResult("DOC-GATE-015", p.as_posix(), False, "potencial contradição: Testador/VERIFICADO sem menção clara de hb seal/Humano")

    return GateResult("DOC-GATE-015", p.as_posix(), True)


def gate_016_agents_readme_documents_automation() -> GateResult:
    """
    DOC-GATE-016 — .github/agents/README.md documenta automação (watcher + inbox) e precedência:
    - menciona hb_watch.py
    - menciona _reports/dispatch/*.todo
    - reforça: Kanban NÃO libera commit
    - reforça: hb seal manual como último gate
    """
    p = REPO_ROOT / ".github/agents/README.md"
    if not p.exists():
        return GateResult("DOC-GATE-016", p.as_posix(), False, "arquivo ausente")

    t = read_text(p)

    required = [
        "hb_watch.py",
        "_reports/dispatch",
        "executor.todo",
        "testador.todo",
        "humano.todo",
        "Kanban NÃO libera commit",
        "hb seal",
    ]
    missing = [x for x in required if x not in t]
    if missing:
        return GateResult("DOC-GATE-016", p.as_posix(), False, f"missing={missing}")

    return GateResult("DOC-GATE-016", p.as_posix(), True)

def gate_017_forbidden_tokens_global() -> GateResult:
    """
    DOC-GATE-017: Global scan for forbidden tokens (v1.2.0).
    
    Escaneiam-se todos arquivos de texto relevantes em docs/ (exceto _legacy/, evidence/, _reports/).
    Falha se encontrar:
    - "_reports/audit"
    - "🔬 EM TESTE"
    
    Tokens obsoletos devem estar apenas em docs/_legacy/DEPRECATED_PATTERNS.md.
    """
    FORBIDDEN_TOKENS = [
        "_reports/audit",
        "🔬 EM TESTE",
    ]
    
    SCAN_EXTENSIONS = {".md", ".yaml", ".yml", ".json", ".txt", ".py"}
    EXCLUDE_DIRS = {"_legacy", "evidence", "_reports", "__pycache__", ".git"}
    
    docs_root = REPO_ROOT / "docs"
    if not docs_root.exists():
        return GateResult("DOC-GATE-017", docs_root.as_posix(), False, f"docs/ não encontrado", severity="INFRA")
    
    violations: List[str] = []
    
    for root_dir, dirs, files in os.walk(docs_root):
        # Excluir diretórios do scan in-place (modifica dirs para prunning)
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        for file in files:
            if Path(file).suffix not in SCAN_EXTENSIONS:
                continue
            
            file_path = Path(root_dir) / file
            try:
                content = read_text(file_path)
                for token in FORBIDDEN_TOKENS:
                    if token in content:
                        rel_path = file_path.relative_to(REPO_ROOT).as_posix()
                        violations.append(f"{rel_path} contains '{token}'")
            except Exception as e:
                # Arquivo não pode ser lido (binário, permissões, etc.) - pula
                continue
    
    if violations:
        details = f"found {len(violations)} violations; sample: {violations[0]}"
        return GateResult("DOC-GATE-017", "docs/**", False, details)
    
    return GateResult("DOC-GATE-017", "docs/**", True)

def gate_018_architect_scope_clean() -> GateResult:
    """P3.1: Nenhum plano em _canon/planos/ referencia backend/ ou Frontend/ em campos de execução."""
    planos_dir = REPO_ROOT / "docs/_canon/planos"
    violations = []
    for plan_file in planos_dir.rglob("*.json"):
        try:
            text = plan_file.read_text(encoding="utf-8")
            if '"backend/' in text or '"Hb Track - Frontend/' in text:
                violations.append(plan_file.relative_to(REPO_ROOT).as_posix())
        except Exception:
            continue
    if violations:
        return GateResult("DOC-GATE-018", planos_dir.as_posix(), False,
                          f"Planos referenciam pastas de produto: {violations[:3]}")
    return GateResult("DOC-GATE-018", planos_dir.as_posix(), True, "OK")

# -------------------------
# Evidence pack
# -------------------------
def evidence_path(ar_id: str) -> Path:
    # evidence pack under docs/hbtrack/evidence/AR_<id>/
    return REPO_ROOT / "docs/hbtrack/evidence" / f"AR_{ar_id}" / "doc_gates.log"

def git_head() -> str:
    rc, out, _ = run_cmd(["git", "rev-parse", "HEAD"])
    return out.strip() if rc == 0 and out.strip() else "N/A"

def python_version() -> str:
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

def write_evidence(ar_id: str, run_id: str, exit_code: int, results: List[GateResult]) -> None:
    head = git_head()
    ts = now_utc_iso()

    passed = [r for r in results if r.passed]
    failed = [r for r in results if not r.passed and r.severity != "INFRA"]
    infra = [r for r in results if not r.passed and r.severity == "INFRA"]

    lines: List[str] = []
    lines.append(f"RUN_ID: {run_id}")
    lines.append(f"Timestamp UTC: {ts}")
    lines.append(f"Git HEAD: {head}")
    lines.append(f"Python Version: {python_version()}")
    lines.append(f"Exit Code: {exit_code}")
    lines.append("")
    lines.append(f"SUMMARY: PASS={len(passed)} FAIL_ACTIONABLE={len(failed)} ERROR_INFRA={len(infra)}")
    lines.append("")
    lines.append("RESULTS:")
    for r in results:
        status = "PASS" if r.passed else ("ERROR_INFRA" if r.severity == "INFRA" else "FAIL")
        lines.append(f"- {r.gate_id} [{status}] target={r.target}")
        if r.details:
            lines.append(f"  details: {r.details}")
    lines.append("")

    ev = evidence_path(ar_id)
    write_text(ev, "\n".join(lines))

# -------------------------
# Main runner
# -------------------------
def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--ar-id", required=True, help="AR id (3 dígitos) para evidence pack: docs/hbtrack/evidence/AR_<id>/doc_gates.log")
    return ap.parse_args()

def validate_inputs(ar_id: str) -> None:
    if not REPO_ROOT.exists() or not (REPO_ROOT / ".git").exists():
        fail(E_REPO_ROOT, f"repo_root inválido: {REPO_ROOT.as_posix()} (rode a partir de um repo git)", EXIT_BLOCKED_INPUT)
    if not re.match(r"^[0-9]{3}$", ar_id):
        fail(E_AR_ID_INVALID, f"--ar-id inválido: '{ar_id}' (esperado 3 dígitos, ex: 001)", EXIT_BLOCKED_INPUT)
    if ar_id == "000":
        fail(E_AR_ID_INVALID, "--ar-id=000 é proibido; use 001..999", EXIT_BLOCKED_INPUT)

def build_gates() -> List[Gate]:
    return [
        Gate("DOC-GATE-001", "docs/_canon/contratos/Dev Flow.md", "Dev Flow SSOT v1.2.0 + hb seal + Kanban rule", gate_001_devflow),
        Gate("DOC-GATE-002", "docs/_canon/contratos/ar_contract.schema.json", "Schema v1.2.0 + rollback whitelist + evidence path", gate_002_schema),
        Gate("DOC-GATE-003", "docs/_canon/specs/GOVERNED_ROOTS.yaml", "Governed roots SSOT parseable + roots non-empty", gate_003_governed_roots),
        Gate("DOC-GATE-004", "docs/_canon/contratos/Arquiteto Contract.md", "Arquiteto contract aligned", gate_004_arquiteto_contract),
        Gate("DOC-GATE-005", "docs/_canon/contratos/Executor Contract.md", "Executor contract aligned (no _reports/audit)", gate_005_executor_contract),
        Gate("DOC-GATE-006", "docs/_canon/contratos/Testador Contract.md", "Testador contract aligned (no auto VERIFIED, AH-12)", gate_006_testador_contract),
        Gate("DOC-GATE-007", ".github/agents/architect.agent.md", "Architect agent file aligned", gate_007_arch_agent),
        Gate("DOC-GATE-008", ".github/agents/executor.agent.md", "Executor agent file aligned", gate_008_exec_agent),
        Gate("DOC-GATE-009", ".github/agents/testador.agent.md", "Testador agent file aligned", gate_009_testador_agent),
        Gate("DOC-GATE-010", ".github/agents/README.md", "Agents README aligned (SSOT vs DERIVED)", gate_010_agents_readme),
        Gate("DOC-GATE-011", "docs/_canon/specs/Hb cli.md|Hb cli Spec.md", "hb cli spec aligned", gate_011_hb_cli_spec),
        Gate("DOC-GATE-012", "docs/hbtrack/Hb Track Kanban.md", "Kanban contains 'não libera commit'", gate_012_kanban_rule),
        Gate("DOC-GATE-013", "docs/hbtrack/_INDEX.md", "_INDEX is derived and warns not to edit", gate_013_index_derived),
        Gate("DOC-GATE-014", "scripts/run/hb_watch.py", "Watcher automation aligned (index+lock+dispatch+staged evidence)", gate_014_hb_watch_automation),
        Gate("DOC-GATE-015", "docs/_canon/contratos/Dev Flow.md", "Dev Flow documents automation + manual seal gate", gate_015_devflow_documents_automation),
        Gate("DOC-GATE-016", ".github/agents/README.md", "Agents README documents automation (watcher+dispatch)", gate_016_agents_readme_documents_automation),
        Gate("DOC-GATE-017", "docs/**", "Global scan: forbidden tokens in docs/ (except _legacy/)", gate_017_forbidden_tokens_global),
        Gate("DOC-GATE-018", "docs/_canon/planos/*.json", "Architect scope protection (P3.1)", gate_018_architect_scope_clean),
    ]

def main() -> None:
    args = parse_args()
    validate_inputs(args.ar_id)

    head = git_head()
    ts = now_utc_iso()
    run_id = f"DOC_GATES-AR_{args.ar_id}-{(head[:7] if head != 'N/A' else 'NOHEAD')}-{ts.replace(':','').replace('.','')}"
    gates = build_gates()

    results: List[GateResult] = []
    infra_errors = 0
    actionable_fails = 0

    try:
        for g in gates:
            try:
                r = g.fn()
            except IOError as e:
                r = GateResult(g.gate_id, g.target, False, f"{E_IO_READ}: {e}", severity="INFRA")
            except Exception as e:
                r = GateResult(g.gate_id, g.target, False, f"UNHANDLED: {e}", severity="INFRA")
            results.append(r)
            if not r.passed:
                if r.severity == "INFRA":
                    infra_errors += 1
                else:
                    actionable_fails += 1

        if infra_errors > 0:
            exit_code = EXIT_ERROR_INFRA
        elif actionable_fails > 0:
            exit_code = EXIT_FAIL_ACTIONABLE
        else:
            exit_code = EXIT_PASS

        # Evidence pack (sempre escreve, inclusive FAIL)
        try:
            write_evidence(args.ar_id, run_id, exit_code, results)
        except IOError as e:
            fail(E_IO_WRITE, str(e), EXIT_ERROR_INFRA)

        # stdout summary
        print(f"RUN_ID={run_id}")
        print(f"Exit={exit_code} | PASS={len([r for r in results if r.passed])} | FAIL={actionable_fails} | INFRA={infra_errors}")
        print(f"Evidence={evidence_path(args.ar_id).as_posix()}")
        for r in results:
            if not r.passed:
                tag = "INFRA" if r.severity == "INFRA" else "FAIL"
                print(f"- {r.gate_id} [{tag}] target={r.target} details={r.details}")

        sys.exit(exit_code)

    except KeyboardInterrupt:
        fail("E_INTERRUPT", "interrompido pelo usuário", EXIT_ERROR_INFRA)

if __name__ == "__main__":
    main()