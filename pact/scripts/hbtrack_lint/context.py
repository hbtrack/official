"""
ValidationContext — contexto compartilhado entre todos os checkers.

SSOT: docs/hbtrack/modulos/atletas/MOTORES.md
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ValidationContext:
    """Contexto passado a cada checker durante a execução do planner."""
    repo_root: Path
    module_root: Path
    contracts: dict

    # Campos opcionais (preenchidos progressivamente pelo hb_plan.py)
    handoff: dict | None = None
    anchor_manifest: dict | None = None
    original_files_dir: Path | None = None
    working_files_dir: Path | None = None
