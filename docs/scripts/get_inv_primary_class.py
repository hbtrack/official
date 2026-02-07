#!/usr/bin/env python3
"""
Helper script para extrair primary class de um invariante.

Usage:
    python get_inv_primary_class.py --inv INV-TRAIN-002

Output:
    C2 (ou UNKNOWN se não encontrado)

Exit Code:
    0 (sempre, para não quebrar gate runner)
"""

import argparse
import sys
from pathlib import Path

# Import InvariantsParser from verify_invariants_tests.py
sys.path.insert(0, str(Path(__file__).parent))
from verify_invariants_tests import InvariantsParser


def main():
    parser = argparse.ArgumentParser(description='Extract primary class from invariant')
    parser.add_argument('--inv', required=True, help='Invariant ID (ex: INV-TRAIN-002)')
    args = parser.parse_args()
    
    inv_id = args.inv
    
    try:
        # Path para INVARIANTS_TRAINING.md
        md_path = Path(__file__).parent.parent / '02-modulos' / 'training' / 'INVARIANTS_TRAINING.md'
        
        if not md_path.exists():
            print("UNKNOWN", flush=True)
            sys.exit(0)
        
        # Parsear invariantes
        inv_parser = InvariantsParser()
        invariants, violations = inv_parser.parse(md_path, strict_spec=False)
        
        # Encontrar invariante
        inv = None
        for i in invariants:
            if i.id == inv_id:
                inv = i
                break
        
        if not inv:
            print("UNKNOWN", flush=True)
            sys.exit(0)
        
        # Extrair primary classes (units required:true)
        primary_classes = inv.primary_classes
        
        if primary_classes:
            # Retornar primeira primary class
            print(sorted(primary_classes)[0], flush=True)
        elif inv.units:
            # Fallback: primeira unit class
            print(inv.units[0].class_type, flush=True)
        else:
            print("UNKNOWN", flush=True)
        
        sys.exit(0)
    
    except Exception as e:
        # Em caso de erro, retornar UNKNOWN (não quebrar gate)
        print("UNKNOWN", flush=True)
        sys.exit(0)


if __name__ == '__main__':
    main()
