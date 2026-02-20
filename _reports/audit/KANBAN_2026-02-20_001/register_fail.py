import json
import os
import subprocess
import datetime

RUN_ID = "KANBAN_2026-02-20_001"
root = f"_reports/audit/{RUN_ID}"

# Git info
git_head = subprocess.run("git rev-parse HEAD", shell=True, text=True, capture_output=True).stdout.strip()
git_status = subprocess.run("git status --porcelain", shell=True, text=True, capture_output=True).stdout
python_ver = subprocess.run("python -V", shell=True, text=True, capture_output=True).stdout.strip()

# Card com falha documentada
card = {
    "run_id": RUN_ID,
    "ar_id": "AR-2026-02-20-KANBAN-VERIFY-001",
    "created_at": datetime.datetime.utcnow().isoformat() + "Z",
    "status": "FAIL_ACTIONABLE",
    "failure_reason": "Working tree não está limpa (git status --porcelain retornou alterações)",
    "stop_condition_triggered": "git_status_clean",
    "git_head": git_head,
    "git_status_porcelain": git_status,
    "python_version": python_ver,
    "ssot_paths": [
        "docs/_INDEX.yaml",
        "docs/_canon/_agent/GATES_REGISTRY.yaml",
        "docs/_canon/contratos/HB_TRACK_CONTRACT.md",
        "docs/_canon/specs/HB_TRACK_SPEC.md",
        "docs/hbtrack/Hb Track Kanban.md",
        "scripts/checks/check_docs_index.py",
    ]
}

with open(os.path.join(root, "card.json"), "w", encoding="utf-8") as f:
    json.dump(card, f, indent=2, ensure_ascii=False)

with open(os.path.join(root, "git_status.log"), "w", encoding="utf-8") as f:
    f.write(git_status)

print("FAIL_REGISTERED")
print(f"Evidence Pack: {root}/")
