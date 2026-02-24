#!/usr/bin/env python3
"""
Script para atualizar Evidence File paths de legacy para canônico nas ARs 032-045.

Padrão de substituição:
- Legacy: docs/hbtrack/evidence/AR_XXX_description.log
- Canônico: docs/hbtrack/evidence/AR_XXX/executor_main.log
"""

import re
from pathlib import Path

WORKSPACE = Path(__file__).parent.parent
ARS_DIR = WORKSPACE / "docs" / "hbtrack" / "ars"

TARGET_ARS = [
    "032", "034", "035", "037", "038", "039", 
    "040", "041", "042", "043", "044", "045"
]

def find_ar_file(ar_id: str) -> Path | None:
    """Encontra arquivo da AR recursivamente."""
    pattern = f"AR_{ar_id}_*.md"
    matches = list(ARS_DIR.rglob(pattern))
    return matches[0] if matches else None

def update_evidence_path(ar_file: Path, ar_id: str) -> bool:
    """
    Atualiza o Evidence File path de legacy para canônico.
    Retorna True se houve alteração.
    """
    content = ar_file.read_text(encoding='utf-8')
    original = content
    
    # Pattern: `docs/hbtrack/evidence/AR_XXX_*.log`
    legacy_pattern = rf'`docs/hbtrack/evidence/AR_{ar_id}_[^`]+\.log`'
    canonical_path = f'`docs/hbtrack/evidence/AR_{ar_id}/executor_main.log`'
    
    # Substituir
    content = re.sub(legacy_pattern, canonical_path, content)
    
    if content != original:
        ar_file.write_text(content, encoding='utf-8')
        return True
    return False

def main():
    print("="*70)
    print("FIX EVIDENCE PATHS: Legacy → Canonical")
    print("="*70)
    
    updated = []
    not_found = []
    no_change = []
    
    for ar_id in TARGET_ARS:
        ar_file = find_ar_file(ar_id)
        
        if not ar_file:
            print(f"❌ AR_{ar_id}: File not found")
            not_found.append(ar_id)
            continue
        
        if update_evidence_path(ar_file, ar_id):
            print(f"✅ AR_{ar_id}: Updated → docs/hbtrack/evidence/AR_{ar_id}/executor_main.log")
            updated.append(ar_id)
        else:
            print(f"⚠️  AR_{ar_id}: No changes needed (already canonical?)")
            no_change.append(ar_id)
    
    print("\n" + "="*70)
    print(f"Summary: {len(updated)} updated, {len(no_change)} no change, {len(not_found)} not found")
    print("="*70)
    
    if updated:
        print("\nUpdated ARs:", ", ".join(f"AR_{id}" for id in updated))

if __name__ == "__main__":
    main()
