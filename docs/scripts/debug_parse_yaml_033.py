#!/usr/bin/env python3
"""Debug script para verificar parsing do YAML do INV-TRAIN-033"""

import re
from pathlib import Path

# Ler markdown
md_path = Path('docs/02-modulos/training/INVARIANTS_TRAINING.md')
content = md_path.read_text(encoding='utf-8')

# Encontrar bloco SPEC do INV-TRAIN-033
sections = re.split(r'^### (INV-TRAIN-\d{3}(?:-[A-Z]\d*)?)', content, flags=re.MULTILINE)
for i in range(1, len(sections), 2):
    if i + 1 >= len(sections):
        break
    inv_id = sections[i]
    if inv_id == 'INV-TRAIN-033':
        section_content = sections[i + 1]
        spec_match = re.search(
            r'\*\*SPEC\*\*:\s*```(?:yaml)?\s*\n(.*?)\n```',
            section_content,
            re.DOTALL
        )
        if spec_match:
            yaml_content = spec_match.group(1)
            print('YAML Content:')
            print('=' * 60)
            print(yaml_content)
            print('=' * 60)
            
            # Parsear YAML simples
            lines = yaml_content.strip().split('\n')
            in_anchors = False
            print('\nParsing anchors:')
            for line in lines:
                stripped = line.strip()
                if 'anchors:' in stripped:
                    in_anchors = True
                    print(f'  Found anchors section at: {line!r}')
                elif in_anchors:
                    if stripped and not stripped.startswith('#'):
                        if ':' in stripped:
                            if not stripped.startswith('-'):
                                print(f'  Anchor line: {line!r}')
                            else:
                                in_anchors = False
                        else:
                            in_anchors = False
        break
