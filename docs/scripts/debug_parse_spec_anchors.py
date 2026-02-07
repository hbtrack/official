#!/usr/bin/env python3
"""
Script temporário para debug do parsing de anchors do SPEC INV-TRAIN-033
"""

import re
import sys
import yaml
from pathlib import Path

# Importar funções do verificador
sys.path.insert(0, str(Path(__file__).parent))
from verify_invariants_tests import normalize_anchors, InvariantSpec

def extract_inv033_block():
    """Extrai o bloco YAML do INV-TRAIN-033"""
    spec_file = Path("C:/HB TRACK/docs/02-modulos/training/INVARIANTS_TRAINING.md")
    text = spec_file.read_text(encoding='utf-8')
    
    # Encontrar todos os blocos SPEC YAML
    pattern = r'```yaml\n(spec_version:.*?)```'
    blocks = list(re.finditer(pattern, text, re.DOTALL))
    
    print(f"Total SPEC blocks found: {len(blocks)}\n")
    
    # Procurar INV-TRAIN-033
    for block in blocks:
        yaml_content = block.group(1)
        if 'INV-TRAIN-033' in yaml_content:
            print("=" * 80)
            print("RAW_BLOCK (INV-TRAIN-033):")
            print("=" * 80)
            print(yaml_content)
            print("=" * 80)
            print()
            
            # Parsear YAML
            try:
                spec_data = yaml.safe_load(yaml_content)
                print("PARSED YAML (via yaml.safe_load):")
                print("=" * 80)
                
                print(f"id: {spec_data.get('id')}")
                print(f"status: {spec_data.get('status')}")
                print(f"test_required: {spec_data.get('test_required')}")
                print()
                
                units = spec_data.get('units', [])
                print(f"units count: {len(units)}")
                print()
                
                for i, unit_data in enumerate(units):
                    print(f"--- Unit {i} ---")
                    print(f"  unit_key: {unit_data.get('unit_key')}")
                    print(f"  class: {unit_data.get('class')}")
                    print(f"  required: {unit_data.get('required')}")
                    print(f"  description: {unit_data.get('description')}")
                    
                    raw_anchors = unit_data.get('anchors', {})
                    print(f"  RAW anchors (before normalize): {raw_anchors}")
                    print(f"  RAW anchors type: {type(raw_anchors)}")
                    print(f"  RAW anchors keys: {list(raw_anchors.keys()) if raw_anchors else []}")
                    print()
                    
                    # Testar normalize_anchors
                    normalized = normalize_anchors(raw_anchors, inv_id='INV-TRAIN-033')
                    print(f"  NORMALIZED anchors (after normalize_anchors): {normalized}")
                    print(f"  NORMALIZED type: {type(normalized)}")
                    if normalized:
                        print(f"  NORMALIZED keys: {list(normalized.keys())}")
                        if 'db' in normalized:
                            print(f"    db sub-keys: {list(normalized['db'].keys())}")
                            print(f"    db.constraint: {normalized['db'].get('constraint')}")
                            print(f"    db.sqlstate: {normalized['db'].get('sqlstate')}")
                    print()
                
                tests = spec_data.get('tests', {})
                print(f"tests:")
                print(f"  primary: {tests.get('primary')}")
                print(f"  node: {tests.get('node')}")
                print()
                
            except Exception as e:
                print(f"ERROR parsing YAML: {e}")
                import traceback
                traceback.print_exc()
            
            return yaml_content
    
    print("ERROR: INV-TRAIN-033 block not found!")
    return None

if __name__ == "__main__":
    extract_inv033_block()
