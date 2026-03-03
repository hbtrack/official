"""
run_top10_dod.py — Executor AR_200
Roda os 10 testes COBERTO+NOT_RUN, salva saída em _reports/training/,
imprime resumo JSON para conferência.
"""
import sys
import types
import os
import subprocess
import json
from datetime import date

# Configuração de paths
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(REPO_ROOT, "Hb Track - Backend")
VENV_PYTHON = os.path.join(BACKEND_DIR, ".venv", "Scripts", "python.exe")
REPORTS_DIR = os.path.join(REPO_ROOT, "_reports", "training")
TODAY = date.today().isoformat()
AR_ID = "AR_200"

os.makedirs(REPORTS_DIR, exist_ok=True)

TESTS = [
    {
        "id": "INV-001",
        "report_id": "INV-TRAIN-001",
        "test_path": "tests/training/invariants/test_inv_train_001_focus_sum_constraint.py",
        "nome": "focus_total_max_120_pct",
        "evidence_file": "TEST-TRAIN-INV-001.md",
    },
    {
        "id": "INV-002",
        "report_id": "INV-TRAIN-002",
        "test_path": "tests/training/invariants/test_inv_train_002_wellness_pre_deadline.py",
        "nome": "wellness_pre_deadline_2h_before_session",
        "evidence_file": "TEST-TRAIN-INV-002.md",
    },
    {
        "id": "INV-003",
        "report_id": "INV-TRAIN-003",
        "test_path": "tests/training/invariants/test_inv_train_003_wellness_post_deadline.py",
        "nome": "wellness_post_edit_window_24h",
        "evidence_file": "TEST-TRAIN-INV-003.md",
    },
    {
        "id": "INV-004",
        "report_id": "INV-TRAIN-004",
        "test_path": "tests/training/invariants/test_inv_train_004_edit_window_time.py",
        "nome": "session_edit_window_by_role",
        "evidence_file": "TEST-TRAIN-INV-004.md",
    },
    {
        "id": "INV-005",
        "report_id": "INV-TRAIN-005",
        "test_path": "tests/training/invariants/test_inv_train_005_immutability_60_days.py",
        "nome": "session_immutable_after_60_days",
        "evidence_file": "TEST-TRAIN-INV-005.md",
    },
    {
        "id": "INV-008",
        "report_id": "INV-TRAIN-008",
        "test_path": "tests/training/invariants/test_inv_train_008_soft_delete_reason_pair.py",
        "nome": "soft_delete_reason_pair",
        "evidence_file": "TEST-TRAIN-INV-008.md",
    },
    {
        "id": "INV-009",
        "report_id": "INV-TRAIN-009",
        "test_path": "tests/training/invariants/test_inv_train_009_wellness_pre_uniqueness.py",
        "nome": "unique_wellness_pre_per_athlete_session",
        "evidence_file": "TEST-TRAIN-INV-009.md",
    },
    {
        "id": "INV-030",
        "report_id": "INV-TRAIN-030",
        "test_path": "tests/training/invariants/test_inv_train_030_attendance_correction_fields.py",
        "nome": "attendance_correction_requires_audit_fields",
        "evidence_file": "TEST-TRAIN-INV-030.md",
    },
    {
        "id": "INV-032",
        "report_id": "INV-TRAIN-032",
        "test_path": "tests/training/invariants/test_inv_train_032_wellness_post_rpe.py",
        "nome": "wellness_post_rpe_range",
        "evidence_file": "TEST-TRAIN-INV-032.md",
    },
    {
        "id": "CONTRACT-077-085",
        "report_id": "CONTRACT-TRAIN-077..085",
        "test_path": "tests/training/contracts/test_contract_train_077_085_alerts_suggestions.py",
        "nome": "alerts_suggestions_endpoints",
        "evidence_file": "TEST-TRAIN-CONTRACT-077-085.md",
    },
]

# Script runner que injeta o pre-patch de sys.modules
RUNNER_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "run_training_tests.py")

results = []

for t in TESTS:
    print(f"\n{'='*60}")
    print(f"Rodando: {t['report_id']} — {t['nome']}")
    print(f"  Arquivo: {t['test_path']}")

    result = subprocess.run(
        [VENV_PYTHON, RUNNER_SCRIPT, t["test_path"]],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=BACKEND_DIR,
    )

    exit_code = result.returncode
    status = "PASS" if exit_code == 0 else "FAIL"
    output = result.stdout + result.stderr
    print(f"  Status: {status} (exit {exit_code})")

    # Extrai linhas de sumário (última linha com passed/failed/error)
    summary_lines = [l for l in output.splitlines() if "passed" in l or "failed" in l or "error" in l]
    summary = summary_lines[-1] if summary_lines else "(sem sumário)"
    print(f"  Sumário: {summary}")

    # Grava evidência
    evidence_path = os.path.join(REPORTS_DIR, t["evidence_file"])
    with open(evidence_path, "w", encoding="utf-8") as f:
        f.write(f"# TEST-TRAIN-{t['id']} — Evidência de Execução\n")
        f.write(f"- Data: {TODAY}\n")
        f.write(f"- Status: {status}\n")
        f.write(f"- Comando: pytest {t['test_path']} -v\n")
        f.write(f"- AR Origem: {AR_ID}\n")
        f.write(f"\n## Output pytest\n\n```\n")
        f.write(output)
        f.write(f"\n```\n")

    results.append({
        "id": t["report_id"],
        "status": status,
        "exit_code": exit_code,
        "summary": summary,
        "evidence": t["evidence_file"],
    })

print(f"\n{'='*60}")
print("RESUMO FINAL:")
for r in results:
    mark = "✅" if r["status"] == "PASS" else "❌"
    print(f"  {mark} {r['id']:35s} {r['status']:5s} — {r['summary']}")

# Salva resumo JSON
summary_path = os.path.join(REPORTS_DIR, "_summary_ar200.json")
with open(summary_path, "w", encoding="utf-8") as f:
    json.dump({"date": TODAY, "ar": AR_ID, "results": results}, f, indent=2, ensure_ascii=False)

print(f"\nResumo salvo em: {summary_path}")
print("Evidências salvas em: _reports/training/")
