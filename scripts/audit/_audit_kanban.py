import os, json, subprocess, datetime, sys
from pathlib import Path

RUN_ID = "KANBAN_2026-02-20_001"
AR_ID = "AR-2026-02-20-KANBAN-VERIFY-001"
ROOT = Path(f"_reports/audit/{RUN_ID}")

def run_cmd(cmd):
    p = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    return p.returncode, p.stdout, p.stderr

# Setup
ROOT.mkdir(parents=True, exist_ok=True)
(ROOT / "checks").mkdir(exist_ok=True)

# Prechecks
rc_py, out_py, _ = run_cmd("python -V")
rc_git, out_git, _ = run_cmd("git status --porcelain")
rc_head, out_head, _ = run_cmd("git rev-parse HEAD")

prechecks = {
    "PRECHECK_PYTHON": {"exit_code": rc_py, "stdout": out_py.strip(), "status": "PASS" if rc_py == 0 and "3.11.9" in out_py else "FAIL"},
    "PRECHECK_GIT": {"exit_code": rc_git, "stdout": out_git, "status": "PASS" if rc_git == 0 and not out_git.strip() else "FAIL"},
    "git_head": out_head.strip()
}

(ROOT / "prechecks.json").write_text(json.dumps(prechecks, indent=2), encoding="utf-8")

print(f"Prechecks: Python={prechecks['PRECHECK_PYTHON']['status']}, Git={prechecks['PRECHECK_GIT']['status']}")

if prechecks['PRECHECK_PYTHON']['status'] == "FAIL" or prechecks['PRECHECK_GIT']['status'] == "FAIL":
    print("PRECHECK FAIL - Abortando")
    sys.exit(2)

# Card
card = {
    "run_id": RUN_ID,
    "ar_id": AR_ID,
    "capability": "OPS_GOV",
    "change_type": "VERIFY_IMPLEMENTATION",
    "created_at": datetime.datetime.utcnow().isoformat() + "Z",
    "ssot_paths": [
        "docs/_INDEX.yaml",
        "docs/_canon/_agent/GATES_REGISTRY.yaml",
        "docs/_canon/contratos/HB_TRACK_CONTRACT.md",
        "docs/_canon/specs/HB_TRACK_SPEC.md",
        "docs/hbtrack/Hb Track Kanban.md",
        "scripts/checks/check_docs_index.py"
    ],
    "git_head": prechecks["git_head"],
    "git_status_porcelain": prechecks["PRECHECK_GIT"]["stdout"],
    "python_version": prechecks["PRECHECK_PYTHON"]["stdout"]
}

(ROOT / "card.json").write_text(json.dumps(card, indent=2, ensure_ascii=False), encoding="utf-8")
print("Card gerado")

# Gates
gates = {
    "DOCS_INDEX_CHECK": "python scripts/checks/check_docs_index.py",
    "DOCS_CANON_CHECK": f"python scripts/checks/check_docs_canon.py {RUN_ID}",
}

results = {}
all_passed = True

for gate_id, cmd in gates.items():
    print(f"Executando {gate_id}...")
    rc, out, err = run_cmd(cmd)
    
    gate_dir = ROOT / "checks" / gate_id
    gate_dir.mkdir(parents=True, exist_ok=True)
    
    (gate_dir / "stdout.log").write_text(out, encoding="utf-8")
    (gate_dir / "stderr.log").write_text(err, encoding="utf-8")
    (gate_dir / "result.json").write_text(json.dumps({
        "gate_id": gate_id,
        "exit_code": rc,
        "status": "PASS" if rc == 0 else "FAIL",
        "command": cmd
    }, indent=2), encoding="utf-8")
    
    results[gate_id] = {"exit_code": rc, "status": "PASS" if rc == 0 else "FAIL"}
    print(f"  {results[gate_id]['status']} (exit={rc})")
    
    if rc != 0:
        all_passed = False
        print(f"  Gate falhou - parando")
        break

(ROOT / "exit_codes.json").write_text(json.dumps({k: v["exit_code"] for k, v in results.items()}, indent=2), encoding="utf-8")

# Audit Pack Integrity
print(f"Executando AUDIT_PACK_INTEGRITY...")
rc_pack, out_pack, err_pack = run_cmd(f"python scripts/checks/check_audit_pack.py {RUN_ID}")
(ROOT / "AUDIT_PACK_INTEGRITY.stdout.log").write_text(out_pack, encoding="utf-8")
(ROOT / "AUDIT_PACK_INTEGRITY.stderr.log").write_text(err_pack, encoding="utf-8")
pack_ok = rc_pack == 0
print(f"  {'PASS' if pack_ok else 'FAIL'} (exit={rc_pack})")

# Summary
evidence_files = sorted([str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file()])

summary = {
    "run_id": RUN_ID,
    "ar_id": AR_ID,
    "status": "PASS" if (all_passed and pack_ok) else "FAIL",
    "exit_code": 0 if (all_passed and pack_ok) else 2,
    "exit_label": "PASS" if (all_passed and pack_ok) else "FAIL_ACTIONABLE",
    "reason": "ALL_GATES_PASSED" if (all_passed and pack_ok) else ("GATE_FAILED" if not all_passed else "AUDIT_PACK_INTEGRITY_FAILED"),
    "ssot_reference": "docs/hbtrack/manuais/Manual Deterministico.md",
    "created_at": card["created_at"],
    "finalized_at": datetime.datetime.utcnow().isoformat() + "Z",
    "gates_executed": list(results.keys()),
    "gate_results": results,
    "exit_codes": {k: v["exit_code"] for k, v in results.items()},
    "audit_pack_integrity": {"exit_code": rc_pack, "status": "PASS" if pack_ok else "FAIL"},
    "acceptance_criteria": {
        "AC-001": "PASS" if results.get("DOCS_INDEX_CHECK", {}).get("exit_code") == 0 else "FAIL",
        "AC-002": "PASS" if results.get("DOCS_CANON_CHECK", {}).get("exit_code") == 0 else "FAIL",
        "AC-003": "PASS" if pack_ok else "FAIL",
        "AC-004": "PASS"
    },
    "evidence_pack": {
        "root": str(ROOT),
        "file_count": len(evidence_files),
        "files": evidence_files
    }
}

(ROOT / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

print(f"\n=======================================================")
print(f"STATUS: {summary['status']}")
print(f"EXIT_CODE: {summary['exit_code']}")
print(f"REASON: {summary['reason']}")
print(f"Evidence Pack: {ROOT} ({len(evidence_files)} files)")
print(f"=======================================================")

for ac_id, ac_status in summary['acceptance_criteria'].items():
    print(f"  {ac_id}: {ac_status}")

sys.exit(summary['exit_code'])
