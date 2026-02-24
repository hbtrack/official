#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch script para regenerar evidências canônicas de ARs em SUCESSO.

ARs alvo: 032, 034, 035, 037, 038, 039, 040, 041, 042, 043, 044, 045

Para cada AR:
1. Ler o arquivo .md da AR
2. Extrair validation_command da seção "Validation Command (Contrato)"
3. Executar hb report <id> "<validation_command>"
4. Logar resultado (exit code, evidence path)
"""

import re
import subprocess
import sys
from pathlib import Path

# Force UTF-8 output on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Base paths
WORKSPACE = Path(__file__).parent.parent
ARS_DIR = WORKSPACE / "docs" / "hbtrack" / "ars"

# ARs a processar (em ordem de dependência)
TARGET_ARS = [
    "032",  # Hb cli Spec sync
    "034",  # Governança Plans
    "035",  # hb_watch.py
    "037",  # Competition.points_per_draw model
    "038",  # Migration 0057
    "039",  # CompetitionStanding UniqueConstraint
    "040",  # Migration 0058
    "041",  # Competition model CHECKs
    "042",  # CompetitionMatch CHECK
    "043",  # hb_cli.py scan recursivo
    "044",  # git mv planos
    "045",  # git mv ars
]

def find_ar_file(ar_id: str) -> Path | None:
    """Encontra arquivo da AR recursivamente."""
    pattern = f"AR_{ar_id}_*.md"
    matches = list(ARS_DIR.rglob(pattern))
    if matches:
        return matches[0]
    return None

def extract_validation_command(ar_file: Path) -> str | None:
    """Extrai validation_command da AR (seção Validation Command)."""
    content = ar_file.read_text(encoding='utf-8')
    
    # Regex para extrair comando entre ```
    # Pattern: ## Validation Command ... ``` ... ```
    pattern = r'##\s+Validation Command[^\n]*\n```[^\n]*\n(.*?)\n```'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        cmd = match.group(1).strip()
        return cmd
    
    return None

def run_hb_report(ar_id: str, validation_cmd: str) -> tuple[int, str]:
    """Executa hb report e retorna (exit_code, output)."""
    full_cmd = [
        "python",
        str(WORKSPACE / "scripts" / "run" / "hb_cli.py"),
        "report",
        ar_id,
        validation_cmd
    ]
    
    try:
        result = subprocess.run(
            full_cmd,
            cwd=WORKSPACE,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=60
        )
        return result.returncode, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return 124, f"TIMEOUT: Command exceeded 60s"
    except Exception as e:
        return 1, f"ERROR: {e}"

def main():
    print("="*70)
    print("BATCH EVIDENCE REGENERATION")
    print("="*70)
    print(f"Target ARs: {', '.join(TARGET_ARS)}")
    print(f"Workspace: {WORKSPACE}")
    print()
    
    results = []
    
    for ar_id in TARGET_ARS:
        print(f"\n[AR_{ar_id}] Processing...")
        
        # Find AR file
        ar_file = find_ar_file(ar_id)
        if not ar_file:
            print(f"  [FAIL] AR file not found")
            results.append((ar_id, "NOT_FOUND", None, None))
            continue
        
        print(f"  File: {ar_file.relative_to(WORKSPACE)}")
        
        # Extract validation command
        validation_cmd = extract_validation_command(ar_file)
        if not validation_cmd:
            print(f"  [FAIL] Validation command not found in AR")
            results.append((ar_id, "NO_VALIDATION_CMD", None, None))
            continue
        
        # Truncate command for display
        cmd_display = validation_cmd[:80] + "..." if len(validation_cmd) > 80 else validation_cmd
        print(f"  Command: {cmd_display}")
        
        # Run hb report
        exit_code, output = run_hb_report(ar_id, validation_cmd)
        
        if exit_code == 0:
            evidence_path = f"docs/hbtrack/evidence/AR_{ar_id}/executor_main.log"
            print(f"  [PASS] Exit 0 - Evidence: {evidence_path}")
            results.append((ar_id, "PASS", exit_code, evidence_path))
        else:
            print(f"  [FAIL] Exit {exit_code}")
            # Print last 5 lines of output for debugging
            lines = output.strip().split('\n')
            for line in lines[-5:]:
                print(f"    {line}")
            results.append((ar_id, "FAIL", exit_code, None))
    
    # Summary
    print("\n" + "="*70)
    print("BATCH SUMMARY")
    print("="*70)
    
    pass_count = sum(1 for r in results if r[1] == "PASS")
    fail_count = len(results) - pass_count
    
    print(f"Total: {len(results)} ARs")
    print(f"PASS: {pass_count}")
    print(f"FAIL: {fail_count}")
    print()
    
    print("Results by AR:")
    for ar_id, status, exit_code, evidence in results:
        status_icon = "✅" if status == "PASS" else "❌"
        print(f"  {status_icon} AR_{ar_id}: {status} (exit={exit_code})")
    
    # Exit with failure if any AR failed
    sys.exit(0 if fail_count == 0 else 1)

if __name__ == "__main__":
    main()
