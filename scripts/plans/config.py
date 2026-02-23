#!/usr/bin/env python3
"""
Configuration for HB Track Plans System
=========================================
Centralizes all path constants used by the Architect-Executor flow scripts.
All paths are absolute to ensure scripts work regardless of execution directory.
"""

from pathlib import Path


def find_project_root(start: Path) -> Path:
    """
    Discover project root by searching for .git directory.
    Falls back to 2 levels up if .git not found (original behavior).
    """
    for p in [start, *start.parents]:
        if (p / ".git").exists():
            return p
    # Fallback: mantém comportamento original
    return start.parent.parent


# Root da estrutura de scripts de planos
SCRIPTS_PLANS_ROOT = Path(__file__).resolve().parent

# Root do projeto (descoberto via .git ou fallback)
PROJECT_ROOT = find_project_root(SCRIPTS_PLANS_ROOT)

# Diretórios da estrutura encapsulada
DOCS_ROOT = SCRIPTS_PLANS_ROOT / "docs"
PLANS_DIR = DOCS_ROOT / "plans"
IMPLEMENTED_DIR = DOCS_ROOT / "implemented"
CONTEXT_DIR = DOCS_ROOT / "context"
METRICS_DIR = DOCS_ROOT / "metrics"

# Arquivos específicos
METRICS_FILE = METRICS_DIR / "executor_metrics.json"
LOCKS_FILE = DOCS_ROOT / "file_locks.yaml"

# Diretórios do projeto HB TRACK (para generate_context_snapshot)
# Com fallback para variações de nome
HB_BACKEND_DIR = PROJECT_ROOT / "Hb Track - Backend"
if not HB_BACKEND_DIR.exists():
    HB_BACKEND_DIR = PROJECT_ROOT / "HB Track - Backend"

HB_FRONTEND_DIR = PROJECT_ROOT / "Hb Track - Frontend"
if not HB_FRONTEND_DIR.exists():
    HB_FRONTEND_DIR = PROJECT_ROOT / "HB Track - Frontend"

# Diretórios importantes do backend
BACKEND_APP_DIR = HB_BACKEND_DIR / "app"
BACKEND_MODELS_DIR = BACKEND_APP_DIR / "models"
BACKEND_ROUTERS_DIR = BACKEND_APP_DIR / "routers"
BACKEND_SCHEMAS_DIR = BACKEND_APP_DIR / "schemas"
BACKEND_SERVICES_DIR = BACKEND_APP_DIR / "services"
BACKEND_TESTS_DIR = HB_BACKEND_DIR / "tests"

# Arquivos de configuração do backend
BACKEND_REQUIREMENTS = HB_BACKEND_DIR / "requirements.txt"
BACKEND_PYPROJECT = HB_BACKEND_DIR / "pyproject.toml"
BACKEND_ALEMBIC_DIR = HB_BACKEND_DIR / "alembic"


def resolve_plan_path(path_arg: str) -> Path:
    """
    Resolve plan path intelligently:
    1. If absolute, use as-is
    2. If relative, try CWD first
    3. Fallback to PLANS_DIR if not found in CWD
    
    This allows users to pass short names like "TESTE-001.md" 
    without needing full paths.
    """
    p = Path(path_arg).expanduser()
    
    if not p.is_absolute():
        # Try relative to CWD first
        cand_cwd = (Path.cwd() / p).resolve()
        
        # Fallback: relative to PLANS_DIR (by name only)
        cand_plans = (PLANS_DIR / p.name).resolve()
        
        if cand_cwd.exists():
            return cand_cwd
        elif cand_plans.exists():
            return cand_plans
        else:
            # Return CWD candidate even if doesn't exist (let caller handle error)
            return cand_cwd
    else:
        return p.resolve()
