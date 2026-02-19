#!/usr/bin/env python3
"""
Gate: Capability Evidence Pack Generator
Side-effects: DB_READ, FS_WRITE
Exit codes: 0=OK, 2=VIOLATION, 3=HARNESS_ERROR

Executa gates de validação para capabilities (AUTH, RBAC, ATHLETES, TEAMS, TRAINING, DB_MIGRATIONS)
e gera Evidence Packs estruturados para auditoria.
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any
import os

# Paths canônicos
WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = WORKSPACE_ROOT / "Hb Track - Backend"
REPORTS_DIR = WORKSPACE_ROOT / "_reports" / "audit"

# Matriz de Capabilities
CAPABILITY_GATES = {
    "AUTH": {
        "criticality": "CRÍTICA",
        "gates": {
            "A": {  # Comportamental (E2E/Integration)
                "name": "AUTH_E2E_LOGIN",
                "cmd": ["python", "-m", "pytest", "-xv", "tests/test_login_superadmin.py", "tests/invariants/test_inv_auth_001_cookie_precedence.py"],
                "type": "behavioral"
            },
            "C": {  # Contratual (OpenAPI)
                "name": "AUTH_CONTRACT_OPENAPI",
                "cmd": ["python", "-c", "import sys; from app.main import app; schema = app.openapi(); routes = [r.path for r in app.routes if 'auth' in r.path or 'login' in r.path]; sys.exit(0 if routes else 2)"],
                "type": "structural"
            },
            "E": {  # Operacional (Smoke)
                "name": "AUTH_SMOKE_RUNTIME",
                "cmd": ["python", "-m", "pytest", "-xv", "tests/smoke_test_canonical_routes.py::test_auth_without_token", "tests/smoke_test_canonical_routes.py::test_auth_context"],
                "type": "operational"
            }
        }
    },
    "RBAC": {
        "criticality": "CRÍTICA",
        "gates": {
            "B": {  # Estrutural (Pytest)
                "name": "RBAC_PYTEST_PERMISSIONS",
                "cmd": ["python", "-m", "pytest", "-xv", "app/tests/test_permissions_map.py", "tests/memberships/"],
                "type": "structural"
            },
            "C": {  # Contratual (OpenAPI)
                "name": "RBAC_CONTRACT_OPENAPI",
                "cmd": ["python", "-c", "import sys; from app.main import app; deps = [str(d) for r in app.routes for d in getattr(r, 'dependencies', [])]; sys.exit(0 if any('role' in str(d).lower() or 'permission' in str(d).lower() for d in deps) else 2)"],
                "type": "structural"
            },
            "E": {  # Operacional (Smoke)
                "name": "RBAC_SMOKE_PROTECTED",
                "cmd": ["python", "-m", "pytest", "-xv", "-k", "auth", "tests/smoke_test_canonical_routes.py"],
                "type": "operational"
            }
        }
    },
    "ATHLETES": {
        "criticality": "MÉDIA/ALTA",
        "gates": {
            "B": {  # Estrutural (Pytest)
                "name": "ATHLETES_PYTEST",
                "cmd": ["python", "-m", "pytest", "-xv", "tests/athletes/"],
                "type": "structural"
            },
            "D": {  # Migração
                "name": "DB_MIGRATIONS_ATHLETES",
                "cmd": ["python", "-m", "alembic", "history", "--verbose"],
                "type": "migration"
            },
            "E": {  # Operacional (Smoke)
                "name": "ATHLETES_SMOKE_RUNTIME",
                "cmd": ["python", "-m", "pytest", "-xv", "-k", "athlete", "tests/smoke_test_canonical_routes.py"],
                "type": "operational"
            }
        }
    },
    "TEAMS": {
        "criticality": "MÉDIA/ALTA",
        "gates": {
            "B": {  # Estrutural (Pytest)
                "name": "TEAMS_PYTEST",
                "cmd": ["python", "-m", "pytest", "-xv", "tests/teams/"],
                "type": "structural"
            },
            "D": {  # Migração
                "name": "DB_MIGRATIONS_TEAMS",
                "cmd": ["python", "-m", "alembic", "history", "--verbose"],
                "type": "migration"
            },
            "E": {  # Operacional (Smoke)
                "name": "TEAMS_SMOKE_RUNTIME",
                "cmd": ["python", "-m", "pytest", "-xv", "-k", "team", "tests/smoke_test_canonical_routes.py"],
                "type": "operational"
            }
        }
    },
    "TRAINING": {
        "criticality": "CRÍTICA",
        "gates": {
            "A": {  # Comportamental (E2E)
                "name": "TRAINING_E2E_FLOW",
                "cmd": ["python", "-m", "pytest", "-xv", "tests/e2e/test_training_flow_e2e.py", "tests/test_training_crud_e2e.py"],
                "type": "behavioral"
            },
            "D": {  # Migração
                "name": "DB_MIGRATIONS_UPGRADE_HEAD",
                "cmd": ["python", "-m", "alembic", "current"],
                "type": "migration"
            },
            "E": {  # Operacional (Smoke)
                "name": "TRAINING_SMOKE_RUNTIME",
                "cmd": ["python", "-m", "pytest", "-xv", "-k", "training", "tests/smoke_test_canonical_routes.py"],
                "type": "operational"
            }
        }
    },
    "DB_MIGRATIONS": {
        "criticality": "ESTRUTURAL",
        "gates": {
            "D": {  # Migração
                "name": "DB_MIGRATIONS_UPGRADE_HEAD",
                "cmd": ["python", "-m", "alembic", "current"],
                "type": "migration"
            },
            "D2": {  # Verificação  de hash
                "name": "DB_MIGRATIONS_HASH_CHECK",
                "cmd": ["python", "-m", "pytest", "-xv", "tests/test_migration_hash.py"],
                "type": "migration"
            }
        }
    }
}


def get_git_commit() -> str:
    """Retorna o commit hash atual."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=WORKSPACE_ROOT,
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout.strip() if result.returncode == 0 else "UNKNOWN"
    except Exception:
        return "UNKNOWN"


def get_base_url() -> str:
    """Retorna a base URL do ambiente de teste."""
    # Tenta ler do .env, caso contrário usa default
    env_file = BACKEND_ROOT / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.startswith("FRONTEND_URL="):
                    return line.split("=", 1)[1].strip()
    return os.getenv("HB_AUDIT_BASE_URL", "http://localhost:8000")


def run_gate(gate_name: str, cmd: List[str], cwd: Path) -> Dict[str, Any]:
    """Executa um gate individual e retorna os resultados."""
    print(f"[INFO] Executando gate: {gate_name}")
    print(f"       Comando: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutos
            encoding='utf-8',
            errors='replace'  # Replace invalid chars instead of failing
        )
        
        return {
            "gate": gate_name,
            "command": " ".join(cmd),
            "exit_code": result.returncode,
            "stdout": result.stdout if result.stdout else "",  # Always save, even if empty
            "stderr": result.stderr if result.stderr else "",  # Always save, even if empty
            "status": "PASS" if result.returncode == 0 else "FAIL"
        }
    except subprocess.TimeoutExpired as e:
        # Capture partial output even on timeout
        stdout = e.stdout.decode('utf-8', errors='replace') if e.stdout else ""
        stderr = e.stderr.decode('utf-8', errors='replace') if e.stderr else ""
        return {
            "gate": gate_name,
            "command": " ".join(cmd),
            "exit_code": 3,
            "stdout": stdout,
            "stderr": stderr + "\n\nTIMEOUT: Gate excedeu 5 minutos",
            "status": "HARNESS_ERROR"
        }
    except Exception as e:
        return {
            "gate": gate_name,
            "command": " ".join(cmd),
            "exit_code": 3,
            "stdout": "",
            "stderr": f"EXCEPTION: {str(e)}",
            "status": "HARNESS_ERROR"
        }


def generate_evidence_pack(capability: str, gates_results: List[Dict], run_id: str, commit: str, base_url: str) -> Path:
    """Gera um Evidence Pack estruturado para uma capability."""
    # Criar diretório do Evidence Pack
    pack_dir = REPORTS_DIR / run_id / capability
    pack_dir.mkdir(parents=True, exist_ok=True)
    
    # Context.json
    context = {
        "run_id": run_id,
        "capability": capability,
        "commit_hash": commit,
        "base_url": base_url,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    with open(pack_dir / "context.json", "w") as f:
        json.dump(context, f, indent=2)
    
    # Summary.json
    total = len(gates_results)
    passed = sum(1 for r in gates_results if r["status"] == "PASS")
    failed = sum(1 for r in gates_results if r["status"] == "FAIL")
    errors = sum(1 for r in gates_results if r["status"] == "HARNESS_ERROR")
    
    # Determinar status geral
    if errors > 0:
        overall_status = "HARNESS_ERROR"
    elif failed > 0:
        overall_status = "FAIL"
    else:
        overall_status = "PASS"
    
    summary = {
        "run_id": run_id,
        "capability": capability,
        "criticality": CAPABILITY_GATES[capability]["criticality"],
        "overall_status": overall_status,
        "gates_summary": {
            "total": total,
            "passed": passed,
            "failed": failed,
            "errors": errors
        },
        "gates": gates_results,
        "evidence_pack_path": str(pack_dir.relative_to(WORKSPACE_ROOT))
    }
    with open(pack_dir / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    # Logs individuais por gate
    for result in gates_results:
        gate_name = result["gate"].replace("/", "_").replace(" ", "_")
        
        # Always save stdout.log (even if empty, for evidence)
        stdout_path = pack_dir / f"{gate_name}_stdout.log"
        with open(stdout_path, "w", encoding="utf-8") as f:
            f.write(result["stdout"] if result["stdout"] else "(no output)")
        
        # Always save stderr.log (even if empty, for evidence)
        stderr_path = pack_dir / f"{gate_name}_stderr.log"
        with open(stderr_path, "w", encoding="utf-8") as f:
            f.write(result["stderr"] if result["stderr"] else "(no output)")
    
    return pack_dir


def main():
    parser = argparse.ArgumentParser(description="Executor de gates de capabilities")
    parser.add_argument(
        "--capability",
        choices=list(CAPABILITY_GATES.keys()) + ["ALL"],
        default="ALL",
        help="Capability a auditar (ou ALL para todas)"
    )
    parser.add_argument(
        "--run-id",
        default=None,
        help="Run ID customizado (default: HB-AUDIT-YYYYMMDD-NNN)"
    )
    args = parser.parse_args()
    
    # Gerar Run ID
    if args.run_id:
        run_id = args.run_id
    else:
        timestamp = datetime.now().strftime("%Y%m%d")
        existing = list(REPORTS_DIR.glob(f"HB-AUDIT-{timestamp}-*"))
        next_n = len(existing) + 1
        run_id = f"HB-AUDIT-{timestamp}-{next_n:03d}"
    
    # Obter contexto
    commit = get_git_commit()
    base_url = get_base_url()
    
    print(f"=" * 80)
    print(f"HB TRACK - Capability Gates Executor")
    print(f"=" * 80)
    print(f"Run ID:      {run_id}")
    print(f"Commit Hash: {commit}")
    print(f"Base URL:    {base_url}")
    print(f"=" * 80)
    print()
    
    # Selecionar capabilities
    if args.capability == "ALL":
        capabilities = list(CAPABILITY_GATES.keys())
    else:
        capabilities = [args.capability]
    
    # Executar gates para cada capability
    all_results = {}
    overall_exit = 0
    
    for capability in capabilities:
        print(f"\n{'=' * 80}")
        print(f"CAPABILITY: {capability} ({CAPABILITY_GATES[capability]['criticality']})")
        print(f"{'=' * 80}")
        
        gates = CAPABILITY_GATES[capability]["gates"]
        gates_results = []
        
        for gate_id, gate_info in gates.items():
            result = run_gate(gate_info["name"], gate_info["cmd"], BACKEND_ROOT)
            gates_results.append(result)
            
            status_symbol = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "⚠️"
            print(f"  {status_symbol} {gate_info['name']} ({gate_info['type']}): {result['status']}")
            
            if result["status"] != "PASS":
                overall_exit = 2 if result["status"] == "FAIL" else 3
        
        # Gerar Evidence Pack
        pack_dir = generate_evidence_pack(capability, gates_results, run_id, commit, base_url)
        all_results[capability] = {
            "gates_results": gates_results,
            "evidence_pack": str(pack_dir.relative_to(WORKSPACE_ROOT))
        }
        
        print(f"\n📦 Evidence Pack gerado: {pack_dir.relative_to(WORKSPACE_ROOT)}")
    
    # Relatório final consolidado
    print(f"\n{'=' * 80}")
    print(f"RELATÓRIO FINAL")
    print(f"{'=' * 80}")
    
    for capability, data in all_results.items():
        passed = sum(1 for r in data["gates_results"] if r["status"] == "PASS")
        total = len(data["gates_results"])
        status = "✅ PASS" if passed == total else "❌ FAIL"
        print(f"{status} {capability}: {passed}/{total} gates passaram")
        print(f"   Evidence Pack: {data['evidence_pack']}")
    
    print(f"\n{'=' * 80}")
    print(f"Run ID: {run_id}")
    print(f"Evidence Packs: _reports/audit/{run_id}/")
    print(f"{'=' * 80}")
    
    return overall_exit


if __name__ == "__main__":
    sys.exit(main())
