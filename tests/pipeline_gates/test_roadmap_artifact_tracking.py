from __future__ import annotations

import subprocess
from pathlib import Path

import yaml


REQUIRED_ROADMAP_ARTIFACTS = [
    "ROADMAP.md",
    ".github/skills/hb-roadmap-executor/SKILL.md",
    "tests/pipeline_gates/test_roadmap_session_boot.py",
]


def _is_tracked(path: str) -> bool:
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", path],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def test_roadmap_mode_requires_versioned_artifacts():
    with open(".contract_driven/TASK_CATALOG.yaml", "r", encoding="utf-8") as f:
        catalog = yaml.safe_load(f)

    roadmap_task = catalog["task_catalog"]["execute_roadmap_phase"]
    assert roadmap_task["status"] == "active", "execute_roadmap_phase deve permanecer ativo neste teste"

    missing = [path for path in REQUIRED_ROADMAP_ARTIFACTS if not Path(path).exists()]
    assert not missing, f"Artefatos obrigatórios do modo ROADMAP ausentes: {missing}"

    untracked = [path for path in REQUIRED_ROADMAP_ARTIFACTS if not _is_tracked(path)]
    assert not untracked, (
        "Artefatos do modo ROADMAP existem, mas não estão versionados/tracked no Git: "
        f"{untracked}. Resolva com git add/commit dos artefatos obrigatórios."
    )
