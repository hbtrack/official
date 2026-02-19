#!/usr/bin/env python3
"""
Script de Migração: Audit Pack Capability-Based → Canonical SSOT

Converte auditorias existentes (estrutura por capability) para o formato
canônico esperado pelo check_audit_pack.py (estrutura checks/).

Exit codes:
  0: Migração bem-sucedida
  2: Validação falhou após migração
  3: Erro de infra (I/O, JSON parsing)
  4: Input inválido (audit pack não existe ou já está no formato canônico)

Usage:
  python scripts/migrate/migrate_audit_pack_to_canonical.py HB-AUDIT-20260218-005 [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Paths
WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
REPORTS_ROOT = WORKSPACE_ROOT / "docs" / "_generated" / "_reports" / "audit"

# Exit code mapping
STATUS_MAP = {0: "PASS", 2: "FAIL_ACTIONABLE", 3: "ERROR_INFRA", 4: "BLOCKED_INPUT"}


def load_json(path: Path) -> Optional[Dict[str, Any]]:
    """Carrega JSON com error handling."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"ERROR: Failed to load {path}: {e}")
        return None


def save_json(path: Path, data: Dict[str, Any]) -> bool:
    """Salva JSON com error handling."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"ERROR: Failed to save {path}: {e}")
        return False


def is_canonical_structure(audit_dir: Path) -> bool:
    """Verifica se o audit pack já está no formato canônico."""
    checks_dir = audit_dir / "checks"
    return checks_dir.exists() and checks_dir.is_dir()


def detect_capability_folders(audit_dir: Path) -> List[str]:
    """Detecta pastas de capability (AUTH, ATHLETES, etc.)."""
    capability_folders = []
    for item in audit_dir.iterdir():
        if item.is_dir() and item.name.isupper() and len(item.name) >= 3:
            # Verifica se tem summary.json (indicador de capability)
            if (item / "summary.json").exists():
                capability_folders.append(item.name)
    return capability_folders


def consolidate_context(audit_dir: Path, capabilities: List[str]) -> Optional[Dict[str, Any]]:
    """Consolida context.json de todas as capabilities em um único global."""
    # Pega o primeiro context que encontrar (todos devem ter o mesmo run_id)
    for cap in capabilities:
        cap_context_path = audit_dir / cap / "context.json"
        if cap_context_path.exists():
            context = load_json(cap_context_path)
            if context:
                # Adaptar para formato canônico
                return {
                    "run_id": context.get("run_id"),
                    "git": {
                        "commit": context.get("commit_hash", "UNKNOWN"),
                        "branch": "main",  # Não temos essa info na estrutura antiga
                        "dirty": False
                    },
                    "env": {
                        "HB_AUDIT_BASE_URL": context.get("base_url", "http://localhost:8000")
                    },
                    "timestamp": context.get("timestamp", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
                }
    return None


def extract_gates_from_capability(audit_dir: Path, capability: str) -> List[Dict[str, Any]]:
    """Extrai informações de gates de um capability summary.json."""
    summary_path = audit_dir / capability / "summary.json"
    if not summary_path.exists():
        return []
    
    summary = load_json(summary_path)
    if not summary or "gates" not in summary:
        return []
    
    gates = []
    for gate_info in summary["gates"]:
        gates.append({
            "id": gate_info.get("gate"),
            "command": gate_info.get("command"),
            "exit_code": gate_info.get("exit_code", 3),
            "status": gate_info.get("status", "ERROR_INFRA"),
            "capability": capability,
            "stdout_log": audit_dir / capability / f"{gate_info.get('gate')}_stdout.log",
            "stderr_log": audit_dir / capability / f"{gate_info.get('gate')}_stderr.log"
        })
    return gates


def create_gate_result_json(gate_info: Dict[str, Any], duration_ms: int = 0) -> Dict[str, Any]:
    """Cria result.json no formato canônico para um gate."""
    # Mapear exit_code para status correto
    exit_code = gate_info["exit_code"]
    if exit_code == 1:  # Pytest fail
        exit_code = 2  # Normalizar para FAIL_ACTIONABLE
    
    status = STATUS_MAP.get(exit_code, "ERROR_INFRA")
    
    return {
        "id": gate_info["id"],
        "command": gate_info["command"],
        "exit_code": exit_code,
        "status": status,
        "duration_ms": duration_ms,
        "artifacts": ["stdout.log", "stderr.log"],
        "metadata": {
            "capability": gate_info["capability"],
            "migrated_from_legacy": True
        }
    }


def migrate_audit_pack(run_id: str, dry_run: bool = False, reports_root: Path = REPORTS_ROOT) -> int:
    """Migra um audit pack do formato capability-based para canônico."""
    audit_dir = reports_root / run_id
    
    # Validações iniciais
    if not audit_dir.exists():
        print(f"ERROR: Audit pack not found: {audit_dir}")
        return 4
    
    if is_canonical_structure(audit_dir):
        print(f"INFO: Audit pack {run_id} already in canonical format (checks/ exists)")
        return 4
    
    capabilities = detect_capability_folders(audit_dir)
    if not capabilities:
        print(f"ERROR: No capability folders found in {run_id}")
        return 4
    
    print(f"INFO: Found capabilities: {', '.join(capabilities)}")
    
    # --- PASSO 1: Consolidar context.json ---
    print("\n[STEP 1] Consolidating context.json...")
    global_context = consolidate_context(audit_dir, capabilities)
    if not global_context:
        print("ERROR: Failed to consolidate context.json")
        return 3
    
    # --- PASSO 2: Extrair todos os gates ---
    print("\n[STEP 2] Extracting gates from capabilities...")
    all_gates = []
    for cap in capabilities:
        gates = extract_gates_from_capability(audit_dir, cap)
        all_gates.extend(gates)
        print(f"  {cap}: {len(gates)} gates")
    
    if not all_gates:
        print("ERROR: No gates found in capability summaries")
        return 3
    
    # --- PASSO 3: Criar estrutura checks/ ---
    print("\n[STEP 3] Creating checks/ structure...")
    checks_dir = audit_dir / "checks"
    
    if dry_run:
        print(f"[DRY-RUN] Would create: {checks_dir}")
    else:
        checks_dir.mkdir(exist_ok=True)
    
    summary_checks = []
    overall_exit_code = 0
    
    for gate in all_gates:
        gate_id = gate["id"]
        gate_dir = checks_dir / gate_id
        
        print(f"  Processing gate: {gate_id}")
        
        if not dry_run:
            gate_dir.mkdir(exist_ok=True)
            
            # Copiar logs
            for log_type in ["stdout_log", "stderr_log"]:
                src = gate[log_type]
                dst = gate_dir / log_type.replace("_log", ".log")
                if src.exists():
                    shutil.copy2(src, dst)
                else:
                    # Criar log vazio se não existir
                    dst.touch()
            
            # Criar result.json
            result_json = create_gate_result_json(gate, duration_ms=0)
            if not save_json(gate_dir / "result.json", result_json):
                return 3
        
        # Adicionar ao summary
        exit_code = gate["exit_code"]
        if exit_code == 1:  # Normalizar pytest fail
            exit_code = 2
        
        summary_checks.append({
            "id": gate_id,
            "exit_code": exit_code,
            "status": STATUS_MAP.get(exit_code, "ERROR_INFRA")
        })
        
        # Calcular overall (severidade: 0 < 2 < 3 < 4)
        severity_map = {0: 0, 2: 1, 3: 2, 4: 3}
        if severity_map.get(exit_code, 1) > severity_map.get(overall_exit_code, 0):
            overall_exit_code = exit_code
    
    # --- PASSO 4: Criar summary.json global ---
    print("\n[STEP 4] Creating global summary.json...")
    global_summary = {
        "run_id": run_id,
        "timestamp": global_context["timestamp"],
        "overall_exit_code": overall_exit_code,
        "checks": summary_checks,
        "migration": {
            "from_format": "capability-based",
            "migrated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "original_capabilities": capabilities
        }
    }
    
    if dry_run:
        print(f"[DRY-RUN] Would create: {audit_dir / 'summary.json'}")
        print(f"[DRY-RUN] Overall exit code: {overall_exit_code}")
    else:
        # Salvar context e summary globais
        if not save_json(audit_dir / "context.json", global_context):
            return 3
        if not save_json(audit_dir / "summary.json", global_summary):
            return 3
    
    # --- PASSO 5: Backup das pastas antigas ---
    print("\n[STEP 5] Backing up original capability folders...")
    backup_dir = audit_dir / "_backup_capability_structure"
    
    if not dry_run:
        backup_dir.mkdir(exist_ok=True)
        for cap in capabilities:
            src = audit_dir / cap
            dst = backup_dir / cap
            if src.exists():
                shutil.move(str(src), str(dst))
                print(f"  Moved {cap}/ → _backup_capability_structure/{cap}/")
    else:
        print(f"[DRY-RUN] Would backup to: {backup_dir}")
    
    print(f"\n✅ SUCCESS: Migration completed for {run_id}")
    print(f"   Structure: checks/ with {len(all_gates)} gates")
    print(f"   Overall exit code: {overall_exit_code} ({STATUS_MAP[overall_exit_code]})")
    
    if not dry_run:
        print(f"\n⚠️  NEXT STEP: Run validation:")
        print(f"   python scripts/checks/check_audit_pack.py {run_id}")
    
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Migrate audit pack from capability-based to canonical SSOT format"
    )
    parser.add_argument("run_id", help="RUN_ID under _reports/audit/<RUN_ID>")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    parser.add_argument("--root", default=str(REPORTS_ROOT), help="Reports root directory")
    
    args = parser.parse_args()
    
    reports_root = Path(args.root)
    
    return migrate_audit_pack(args.run_id, dry_run=args.dry_run, reports_root=reports_root)


if __name__ == "__main__":
    sys.exit(main())
