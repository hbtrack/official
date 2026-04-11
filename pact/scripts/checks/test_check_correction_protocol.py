#!/usr/bin/env python3
"""
Teste unitário para validar check_correction_protocol.py

Valida:
1. Required gates baseado em by_capability + pre-gate BUILD_LOCK_INTEGRITY
2. Enforcement de lifecycle=MISSING → BLOCKED_INPUT (4)
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict

# Garantir que estamos no workspace root
WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
os.chdir(WORKSPACE_ROOT)

# Add checks dir to path
sys.path.insert(0, str(WORKSPACE_ROOT / "scripts" / "checks"))

from check_correction_protocol import validate_correction_case


def create_test_case(root: Path, corr_id: str, config: Dict[str, Any]) -> None:
    """Cria um caso de teste com estrutura mínima."""
    case_path = root / "cases" / corr_id
    case_path.mkdir(parents=True, exist_ok=True)
    
    # state.yaml
    state = {
        "corr_id": corr_id,
        "failure_type_primary": config.get("failure_type", "FT_AUTH_CONTRACT"),
        "capability": config.get("capability", "AUTH"),
        "links_ref": "links.yaml",
        "primary_run_id": config.get("primary_run_id", "TEST-RUN-001"),
        "gates_required": config.get("gates_required", [])
    }
    with open(case_path / "state.yaml", "w") as f:
        import yaml
        yaml.dump(state, f)
    
    # links.yaml
    links = {
        "corr_id": corr_id,
        "primary_run_id": config.get("primary_run_id", "TEST-RUN-001")
    }
    with open(case_path / "links.yaml", "w") as f:
        import yaml
        yaml.dump(links, f)
    
    # facts.yaml
    with open(case_path / "facts.yaml", "w") as f:
        import yaml
        yaml.dump({"facts": []}, f)
    
    # repro.yaml
    repro = {
        "command": "pytest",
        "expected": "pass",
        "observed": "fail",
        "exit_code": 1,
        "run_id": config.get("repro_run_id", "TEST-RUN-002")
    }
    with open(case_path / "repro.yaml", "w") as f:
        import yaml
        yaml.dump(repro, f)
    
    # patch_plan.yaml
    with open(case_path / "patch_plan.yaml", "w") as f:
        import yaml
        yaml.dump({"plan": []}, f)
    
    # evidence_manifest.json
    with open(case_path / "evidence_manifest.json", "w") as f:
        json.dump({"artifacts": []}, f)
    
    # Criar audit packs mockados
    for run_id in [config.get("primary_run_id", "TEST-RUN-001"), config.get("repro_run_id", "TEST-RUN-002")]:
        audit_path = root / "audit" / run_id
        audit_path.mkdir(parents=True, exist_ok=True)
        
        # Criar estrutura canônica mínima
        checks_dir = audit_path / "checks"
        checks_dir.mkdir(exist_ok=True)
        
        # Criar pelo menos um gate mockado para passar check_audit_pack
        gate_dir = checks_dir / "MOCK_GATE"
        gate_dir.mkdir(exist_ok=True)
        (gate_dir / "stdout.log").touch()
        (gate_dir / "stderr.log").touch()
        
        gate_result = {
            "id": "MOCK_GATE",
            "command": "echo test",
            "exit_code": 0,
            "status": "PASS",
            "duration_ms": 100,
            "artifacts": ["stdout.log", "stderr.log"]
        }
        with open(gate_dir / "result.json", "w") as f:
            json.dump(gate_result, f)
        
        # context.json
        context = {
            "run_id": run_id,
            "git": {"commit": "abc123", "branch": "main", "dirty": False},
            "env": {},
            "timestamp": "2026-02-18T00:00:00Z"
        }
        with open(audit_path / "context.json", "w") as f:
            json.dump(context, f)
        
        # summary.json
        summary = {
            "run_id": run_id,
            "timestamp": "2026-02-18T00:00:00Z",
            "overall_exit_code": 0,
            "checks": [
                {
                    "id": "MOCK_GATE",
                    "exit_code": 0,
                    "status": "PASS"
                }
            ]
        }
        with open(audit_path / "summary.json", "w") as f:
            json.dump(summary, f)


def test_valid_case_with_pregate():
    """Testa caso válido com BUILD_LOCK_INTEGRITY incluído."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        create_test_case(root, "CORR-001", {
            "failure_type": "FT_AUTH_CONTRACT",
            "capability": "AUTH",
            "gates_required": [
                "BUILD_LOCK_INTEGRITY",  # Pre-gate obrigatório
                "AUTH_E2E_LOGIN",
                "AUTH_CONTRACT_OPENAPI",
                "AUTH_SMOKE_RUNTIME"
            ],
            "primary_run_id": "TEST-RUN-001",
            "repro_run_id": "TEST-RUN-002"
        })
        
        result = validate_correction_case("CORR-001", str(root))
        assert result == 0, f"Expected 0, got {result}"
        print("✅ test_valid_case_with_pregate: PASS")


def test_missing_pregate():
    """Testa caso inválido sem BUILD_LOCK_INTEGRITY."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        create_test_case(root, "CORR-002", {
            "failure_type": "FT_AUTH_CONTRACT",
            "capability": "AUTH",
            "gates_required": [
                # Falta BUILD_LOCK_INTEGRITY!
                "AUTH_E2E_LOGIN",
                "AUTH_CONTRACT_OPENAPI",
                "AUTH_SMOKE_RUNTIME"
            ],
            "primary_run_id": "TEST-RUN-001",
            "repro_run_id": "TEST-RUN-002"
        })
        
        result = validate_correction_case("CORR-002", str(root))
        assert result == 4, f"Expected 4 (BLOCKED_INPUT), got {result}"
        print("✅ test_missing_pregate: PASS")


def test_lifecycle_missing_blocks():
    """Testa que gates com lifecycle=MISSING bloqueiam o caso."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # FT_DB_PARITY → DB_PARITY_SCAN que tem lifecycle=MISSING
        create_test_case(root, "CORR-003", {
            "failure_type": "FT_DB_PARITY",
            "capability": "DB_MIGRATIONS",
            "gates_required": [
                "BUILD_LOCK_INTEGRITY",
                "DB_PARITY_SCAN"  # lifecycle=MISSING no registry
            ],
            "primary_run_id": "TEST-RUN-001",
            "repro_run_id": "TEST-RUN-002"
        })
        
        result = validate_correction_case("CORR-003", str(root))
        assert result == 4, f"Expected 4 (BLOCKED due to lifecycle=MISSING), got {result}"
        print("✅ test_lifecycle_missing_blocks: PASS")


def test_missing_capability():
    """Testa que falta de capability bloqueia."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        case_path = root / "cases" / "CORR-004"
        case_path.mkdir(parents=True, exist_ok=True)
        
        # state.yaml sem capability
        state = {
            "corr_id": "CORR-004",
            "failure_type_primary": "FT_AUTH_CONTRACT",
            # "capability": "AUTH",  # FALTA!
            "links_ref": "links.yaml",
            "primary_run_id": "TEST-RUN-001",
            "gates_required": ["BUILD_LOCK_INTEGRITY", "AUTH_E2E_LOGIN"]
        }
        
        import yaml
        with open(case_path / "state.yaml", "w") as f:
            yaml.dump(state, f)
        
        # Outros arquivos mínimos
        with open(case_path / "links.yaml", "w") as f:
            yaml.dump({"corr_id": "CORR-004", "primary_run_id": "TEST-RUN-001"}, f)
        for fname in ["facts.yaml", "repro.yaml", "patch_plan.yaml"]:
            (case_path / fname).touch()
        with open(case_path / "evidence_manifest.json", "w") as f:
            json.dump({}, f)
        
        result = validate_correction_case("CORR-004", str(root))
        assert result == 4, f"Expected 4 (missing capability), got {result}"
        print("✅ test_missing_capability: PASS")


if __name__ == "__main__":
    import sys
    
    # Skip tests se não tem PyYAML
    try:
        import yaml
    except ImportError:
        print("SKIP: PyYAML not available")
        sys.exit(0)
    
    print("Running check_correction_protocol tests...\n")
    
    try:
        test_valid_case_with_pregate()
        test_missing_pregate()
        test_lifecycle_missing_blocks()
        test_missing_capability()
        
        print("\n✅ All tests PASSED")
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ Test FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
