#!/usr/bin/env python3
"""
Script auxiliar para gerar blocos SPEC em batch

Lê INVARIANTS_TRAINING.md, identifica INVs sem bloco SPEC,
e gera blocos SPEC básicos baseados nas informações legacy.
"""

import re
from pathlib import Path


def generate_spec_block(inv_id, status, class_type, scope, evidence, test_path=None):
    """Gera bloco SPEC básico a partir de informações legacy"""
    
    # Determinar test path padrão
    if not test_path:
        inv_num = inv_id.replace("INV-TRAIN-", "")
        test_path = f"tests/training/invariants/test_inv_train_{inv_num.lower()}_*.py"
    
    # Determinar anchors baseado em evidências
    anchors = {}
    
    # Parsear evidências
    constraints = [e for e in evidence if e.startswith(('ck_', 'uq_', 'fk_', 'tr_', 'fn_', 'ux_'))]
    files = [e for e in evidence if '.py:' in e]
    operation_ids = [e for e in evidence if '_api_v' in e]
    
    # Construir anchors
    if class_type == 'A':
        # DB constraint
        if constraints:
            anchors['db.constraint'] = constraints[0]
            anchors['db.sqlstate'] = '"23514"'  # Default CHECK
            if scope:
                anchors['db.table'] = f'"{scope.split(",")[0].strip()}"'
    elif class_type in ['C1', 'C2']:
        # Service validation
        if files:
            file_match = re.match(r'([^:]+):(\d+)', files[0])
            if file_match:
                anchors['code.file'] = f'"{file_match.group(1)}"'
                anchors['code.line'] = file_match.group(2)
    elif class_type == 'D':
        # Router/API
        if operation_ids:
            anchors['api.operationId'] = f'"{operation_ids[0]}"'
    
    # Construir bloco SPEC
    spec = f'''**SPEC**:
```yaml
spec_version: "1.0"
id: "{inv_id}"
status: "{status}"
test_required: true

units:
  - unit_key: "main"
    class: "{class_type}"
    required: true
    description: "TODO: Add description"
    anchors:'''
    
    if anchors:
        for key, value in anchors.items():
            spec += f'\n      {key}: {value}'
    else:
        spec += '\n      # TODO: Add anchors'
    
    spec += f'''

tests:
  primary: "{test_path}"
  node: "TestInvTrain{inv_id.replace("INV-TRAIN-", "").replace("-", "")}"
```

'''
    
    return spec


def main():
    # Read INVARIANTS_TRAINING.md
    md_path = Path(__file__).parent.parent.parent / 'docs' / '02-modulos' / 'training' / 'INVARIANTS_TRAINING.md'
    content = md_path.read_text(encoding='utf-8')
    
    # Find all INV sections
    sections = re.split(r'^### (INV-TRAIN-\d{3}(?:-[A-Z]\d*)?)', content, flags=re.MULTILINE)
    
    generated = []
    
    for i in range(1, len(sections), 2):
        if i + 1 >= len(sections):
            break
        
        inv_id = sections[i]
        section_content = sections[i + 1]
        
        # Skip if already has SPEC block
        if '**SPEC**:' in section_content:
            continue
        
        # Extract legacy info
        status_match = re.search(r'\*\*Status\*\*:\s*(\w+)', section_content)
        status = status_match.group(1) if status_match else 'CONFIRMADA'
        
        if status == 'INATIVA':
            continue
        
        class_match = re.search(r'\*\*Classe\*\*:\s*([A-F]\d?)', section_content)
        if not class_match:
            class_match = re.search(r'Classe:\s*([A-F]\d?)', section_content)
        class_type = class_match.group(1) if class_match else 'UNKNOWN'
        
        scope_match = re.search(r'\*\*Escopo\*\*:\s*`?([^`\n]+)`?', section_content)
        scope = scope_match.group(1).strip() if scope_match else ''
        
        # Extract evidence
        evidence = []
        evidence.extend(re.findall(r'`((?:ck|uq|fk|tr|fn|ux)_[\w]+)`', section_content))
        evidence.extend(re.findall(r'`([^`]+\.py:\d+)`', section_content))
        evidence.extend(re.findall(r'`([a-z_]+_api_v\d_[^`]+)`', section_content))
        
        # Extract test path if available
        test_match = re.search(r'\*\*Teste\*\*:\s*`([^`]+)`', section_content)
        test_path = test_match.group(1).split('::')[0] if test_match else None
        
        # Generate SPEC block
        spec_block = generate_spec_block(inv_id, status, class_type, scope, evidence, test_path)
        
        generated.append({
            'inv_id': inv_id,
            'spec': spec_block
        })
    
    # Print generated blocks
    print(f"Generated {len(generated)} SPEC blocks:\n")
    print("=" * 80)
    
    for item in generated:
        print(f"\n### {item['inv_id']}\n")
        print(item['spec'])
        print("-" * 80)
    
    print(f"\n\nTotal: {len(generated)} INVs need SPEC blocks")


if __name__ == '__main__':
    main()
