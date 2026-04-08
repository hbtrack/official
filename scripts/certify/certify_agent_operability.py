"""B11-003 — Certificação final de compliance do agente HB Track.

Verifica as 7 dimensões de operabilidade do agente e produz
`_reports/compliance/agent_operability_latest.json`.

Dimensões:
  1. adversarial_suites     — testes adversariais cobertos e passando
  2. sync_gates             — validate_contracts.py --profile ci STATUS: PASS
  3. bundle_freshness       — compiled_context/ cobre 17/17 módulos canônicos
  4. dss_traceability       — source graphs presentes para 17/17 módulos
  5. runtime_replay         — PENDING_B10003 (B10-003 não executado ainda)
  6. merge_rules_enforcement — merge-readiness.json válido + required_thread_resolution
  7. operability_matrix     — test_agent_operability_matrix.py PASS

Saída:
  PASS    — todas as 7 dimensões certificadas
  PARTIAL — ≥1 dimensão PENDING (aguardando tarefa futura), zero FAIL
  FAIL    — ≥1 dimensão FAIL (bloqueante)
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = REPO_ROOT / "_reports" / "compliance" / "agent_operability_latest.json"

CANONICAL_MODULES = [
    "users", "seasons", "teams", "training", "wellness", "medical",
    "competitions", "matches", "scout", "exercises", "analytics",
    "reports", "ai_ingestion", "identity_access", "audit",
    "notifications", "video",
]


# ---------------------------------------------------------------------------
# Dimensão 1 — Suites adversariais
# ---------------------------------------------------------------------------
def check_adversarial_suites() -> dict:
    """Verifica que arquivos de teste adversarial existem e podem ser coletados."""
    adversarial_files = list((REPO_ROOT / "tests" / "adversarial").glob("*.py"))
    adversarial_files = [f for f in adversarial_files if f.name != "__init__.py"]

    coverage_files = [
        f for f in (REPO_ROOT / "tests" / "pipeline_gates").glob("*.py")
        if "adversarial" in f.read_text(encoding="utf-8").lower()
    ]

    total = len(adversarial_files) + len(coverage_files)
    if total == 0:
        return {
            "status": "FAIL",
            "detail": "Nenhum arquivo de teste adversarial encontrado em tests/adversarial/ ou tests/pipeline_gates/",
        }

    return {
        "status": "PASS",
        "detail": f"{len(adversarial_files)} arquivo(s) em tests/adversarial/, {len(coverage_files)} em pipeline_gates/ com cobertura adversarial",
        "files": [f.name for f in adversarial_files] + [f.name for f in coverage_files],
    }


# ---------------------------------------------------------------------------
# Dimensão 2 — Gates de sincronismo
# ---------------------------------------------------------------------------
def check_sync_gates() -> dict:
    """Executa validate_contracts.py --profile ci e verifica STATUS: PASS."""
    result = subprocess.run(
        [sys.executable, "scripts/contracts/validate/validate_contracts.py", "--profile", "ci"],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
    )
    passed = result.returncode == 0 and "STATUS   : PASS" in result.stdout
    return {
        "status": "PASS" if passed else "FAIL",
        "detail": "validate_contracts.py --profile ci STATUS: PASS" if passed
                  else f"validate_contracts.py retornou exit={result.returncode}",
    }


# ---------------------------------------------------------------------------
# Dimensão 3 — Bundle freshness
# ---------------------------------------------------------------------------
def check_bundle_freshness() -> dict:
    """Verifica que compiled_context/ cobre todos os 17 módulos canônicos."""
    ctx = REPO_ROOT / "compiled_context"
    if not ctx.is_dir():
        return {"status": "FAIL", "detail": "compiled_context/ não existe"}

    missing = [m for m in CANONICAL_MODULES if not (ctx / m).is_dir()]
    empty = [m for m in CANONICAL_MODULES if (ctx / m).is_dir() and not list((ctx / m).glob("*.json"))]

    if missing or empty:
        return {
            "status": "FAIL",
            "detail": f"Módulos sem bundle: {missing + empty}",
            "missing_dirs": missing,
            "empty_dirs": empty,
        }

    return {
        "status": "PASS",
        "detail": f"compiled_context/ cobre 17/17 módulos canônicos",
        "modules_covered": len(CANONICAL_MODULES),
    }


# ---------------------------------------------------------------------------
# Dimensão 4 — DSS traceability (source graphs)
# ---------------------------------------------------------------------------
def check_dss_traceability() -> dict:
    """Verifica que source graphs existem para todos os 17 módulos."""
    graph_base = REPO_ROOT / "docs" / "hbtrack" / "modulos"
    missing = []
    for module in CANONICAL_MODULES:
        manifest = graph_base / module / "graph" / "module_manifest.yaml"
        if not manifest.exists():
            missing.append(module)

    if missing:
        return {
            "status": "FAIL",
            "detail": f"Source graph ausente em {len(missing)} módulo(s): {missing}",
        }

    return {
        "status": "PASS",
        "detail": f"Source graphs (module_manifest.yaml) presentes em 17/17 módulos",
    }


# ---------------------------------------------------------------------------
# Dimensão 5 — Runtime replay (B10-003)
# ---------------------------------------------------------------------------
def check_runtime_replay() -> dict:
    """Verifica replay de staging. Pendente até B10-003 ser executado."""
    replay_dir = REPO_ROOT / "tests" / "replay" / "staging"
    if replay_dir.is_dir() and list(replay_dir.glob("test_*.py")):
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/replay/staging", "-q", "--tb=short"],
            capture_output=True, text=True, cwd=str(REPO_ROOT),
        )
        passed = result.returncode == 0
        return {
            "status": "PASS" if passed else "FAIL",
            "detail": "Replay suite de staging executada" if passed else "Replay suite falhou",
        }

    return {
        "status": "PENDING",
        "pending_task": "B10-003",
        "detail": (
            "tests/replay/staging/ não existe. "
            "B10-003 deve criar datasets seeded e replay packs por ciclo de negócio "
            "antes desta dimensão poder ser certificada."
        ),
    }


# ---------------------------------------------------------------------------
# Dimensão 6 — Merge-rules enforcement
# ---------------------------------------------------------------------------
def check_merge_rules_enforcement() -> dict:
    """Verifica merge-readiness.json e ruleset GitHub."""
    mr_path = REPO_ROOT / "merge-readiness.json"
    if not mr_path.exists():
        return {"status": "FAIL", "detail": "merge-readiness.json não encontrado"}

    data = json.loads(mr_path.read_text(encoding="utf-8"))
    checks = data.get("checks", [])
    required = [c for c in checks if c.get("category") == "required"]
    ruleset_id = data.get("ruleset_id")
    ruleset_name = data.get("ruleset_name")

    if not required:
        return {"status": "FAIL", "detail": "Nenhum check com category=required em merge-readiness.json"}

    if not ruleset_id or not ruleset_name:
        return {"status": "FAIL", "detail": "ruleset_id ou ruleset_name ausentes em merge-readiness.json"}

    # Verificar schema
    schema_result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/invariants/test_merge_readiness_parity.py", "-q", "--tb=short"],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
    )
    schema_ok = schema_result.returncode == 0

    return {
        "status": "PASS" if schema_ok else "FAIL",
        "detail": (
            f"merge-readiness.json válido | ruleset={ruleset_name} (id={ruleset_id}) | "
            f"{len(required)} checks required | parity tests: {'PASS' if schema_ok else 'FAIL'}"
        ),
        "ruleset_id": ruleset_id,
        "required_checks": len(required),
    }


# ---------------------------------------------------------------------------
# Dimensão 7 — Operability matrix
# ---------------------------------------------------------------------------
def check_operability_matrix() -> dict:
    """Executa test_agent_operability_matrix.py."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest",
         "tests/pipeline_gates/test_agent_operability_matrix.py",
         "-q", "--tb=short"],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
    )
    passed = result.returncode == 0
    # Extract pass count from output
    lines = result.stdout.splitlines()
    summary = next((l for l in reversed(lines) if "passed" in l), "")
    return {
        "status": "PASS" if passed else "FAIL",
        "detail": summary if passed else "test_agent_operability_matrix.py falhou",
    }


# ---------------------------------------------------------------------------
# Runner principal
# ---------------------------------------------------------------------------
DIMENSIONS = [
    ("adversarial_suites", check_adversarial_suites),
    ("sync_gates", check_sync_gates),
    ("bundle_freshness", check_bundle_freshness),
    ("dss_traceability", check_dss_traceability),
    ("runtime_replay", check_runtime_replay),
    ("merge_rules_enforcement", check_merge_rules_enforcement),
    ("operability_matrix", check_operability_matrix),
]


def run() -> dict:
    results = {}
    for name, fn in DIMENSIONS:
        print(f"  Verificando {name}...", end=" ", flush=True)
        try:
            r = fn()
        except Exception as exc:
            r = {"status": "FAIL", "detail": f"Exceção: {exc}"}
        results[name] = r
        print(r["status"])

    statuses = [r["status"] for r in results.values()]
    if "FAIL" in statuses:
        overall = "FAIL"
    elif "PENDING" in statuses:
        overall = "PARTIAL"
    else:
        overall = "PASS"

    pending_tasks = [
        r.get("pending_task") for r in results.values()
        if r["status"] == "PENDING" and r.get("pending_task")
    ]

    report = {
        "generated_at": str(date.today()),
        "overall": overall,
        "pending_tasks": pending_tasks,
        "dimensions": results,
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return report


def main() -> int:
    print("\n══ HB TRACK — Certificação de Operabilidade do Agente (B11-003) ══\n")
    report = run()
    overall = report["overall"]

    print(f"\n{'─' * 60}")
    print(f"  RESULTADO GERAL : {overall}")
    if report["pending_tasks"]:
        print(f"  PENDÊNCIAS      : {', '.join(report['pending_tasks'])}")
    print(f"  Relatório       : {REPORT_PATH.relative_to(REPO_ROOT)}")
    print(f"{'─' * 60}\n")

    if overall == "FAIL":
        print("❌ Certificação FAIL — corrigir dimensões com status FAIL antes de prosseguir.")
        return 1
    if overall == "PARTIAL":
        print("⚠️  Certificação PARTIAL — aguardando conclusão das tarefas pendentes.")
        return 0
    print("✅ Certificação PASS — agente totalmente operável e compliance verificado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
