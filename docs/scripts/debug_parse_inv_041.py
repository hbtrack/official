#!/usr/bin/env python3
"""
Debug script para verificar parsing do INV-TRAIN-041.
Mostra como anchors['api']['responses'] e anchors['api']['security'] estão sendo parseados.
"""
import sys
from pathlib import Path

# Add parent directory to path to import from verify_invariants_tests
sys.path.insert(0, str(Path(__file__).parent))

from verify_invariants_tests import InvariantsParser

def main():
    md_path = Path(__file__).parent.parent / "02-modulos" / "training" / "INVARIANTS_TRAINING.md"
    
    parser = InvariantsParser()
    invariants, _ = parser.parse(md_path)
    
    inv_041 = [i for i in invariants if i.id == 'INV-TRAIN-041']
    if not inv_041:
        print("ERROR: INV-TRAIN-041 not found")
        return 1
    
    inv = inv_041[0]
    print(f"INV-TRAIN-041 found: {inv.id}")
    print(f"Units: {len(inv.units)}")
    
    if inv.units:
        unit = inv.units[0]
        anchors = unit.anchors
        print(f"\nANCHORS (full): {anchors}")
        
        if 'api' in anchors:
            api = anchors['api']
            print(f"\napi.operation_id: {api.get('operation_id')}")
            print(f"api.method: {api.get('method')}")
            print(f"api.path: {api.get('path')}")
            print(f"api.responses: {api.get('responses')}")
            print(f"api.security: {api.get('security')}")
            
            # Check if bug is present (security merged into responses)
            responses = api.get('responses', [])
            security = api.get('security', [])
            
            if 'HTTPBearer' in responses:
                print("\n[WARNING] BUG DETECTED: 'HTTPBearer' found in responses (should be in security)")
            if not security:
                print("\n[WARNING] BUG DETECTED: api.security is empty or missing")
            if security and 'HTTPBearer' in security:
                print("\n[OK] CORRECT: 'HTTPBearer' found in api.security")
                
    return 0

if __name__ == "__main__":
    sys.exit(main())
