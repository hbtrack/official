#!/usr/bin/env python3
"""
Session 4B v3: Remediação Bucket 1 com padrões literais canônicos

Estratégia correta:
1. Carregar padrões canônicos de DOMAIN_AXIOMS.json
2. Para cada campo Bucket 1, adicionar `pattern: <regex>` literal (não referência)
3. Se pattern estiver errado, substituir; se não existir, adicionar
4. Preservar formato YAML ao máximo
"""

import json
import re
from pathlib import Path
from typing import Dict, Tuple, List

# ============================================================================
# CARREGAR AXIOMAS
# ============================================================================

with open('.contract_driven/DOMAIN_AXIOMS.json', 'r') as f:
    axioms = json.load(f)

PATTERNS_FROM_AXIOMS = {
    'uuid_v4': axioms['domain_axioms']['global_formats']['uuid_v4']['pattern'],
    'timestamp_utc': axioms['domain_axioms']['global_formats']['timestamp_utc']['pattern'],
    'date_only': axioms['domain_axioms']['global_formats']['date_only']['pattern'],
    'trace_id': axioms['domain_axioms']['global_formats']['trace_id']['pattern'],
    'request_id': axioms['domain_axioms']['global_formats']['request_id']['pattern'],
}

print("Padrões canônicos carregados:")
for name, pattern in PATTERNS_FROM_AXIOMS.items():
    print(f"  {name}: {pattern}")

# ============================================================================
# BUCKET 1 MAPPING
# ============================================================================

BUCKET_1_FIELDS = {
    'adjustedAt': 'timestamp_utc',
    'captureStartedAt': 'timestamp_utc',
    'completedAt': 'timestamp_utc',
    'computedAt': 'timestamp_utc',
    'correctionAt': 'timestamp_utc',
    'createdAt': 'timestamp_utc',
    'decidedAt': 'timestamp_utc',
    'declaredAt': 'timestamp_utc',
    'endedAt': 'timestamp_utc',
    'failedAt': 'timestamp_utc',
    'nextRetryAt': 'timestamp_utc',
    'occurredAt': 'timestamp_utc',
    'publishedAt': 'timestamp_utc',
    'startedAt': 'timestamp_utc',
    'updatedAt': 'timestamp_utc',
    'athleteId': 'uuid_v4',
    'coachId': 'uuid_v4',
    'conversationId': 'uuid_v4',
    'createdByUserId': 'uuid_v4',
    'decidedByCoachId': 'uuid_v4',
    'generatedSessionId': 'uuid_v4',
    'generatedTrainingSessionId': 'uuid_v4',
    'matchId': 'uuid_v4',
    'organizationId': 'uuid_v4',
    'sessionId': 'uuid_v4',
    'teamId': 'uuid_v4',
    'trainingId': 'uuid_v4',
    'endDate': 'date_only',
    'startDate': 'date_only',
    'traceId': 'trace_id',
    'requestId': 'request_id',
}

# ============================================================================
# PROCESSAMENTO
# ============================================================================

def process_yaml_file(path: Path) -> Tuple[bool, int, List[str]]:
    """
    Estratégia:
    - Para cada campo Bucket 1, procurar em properties
    - Se existe, garantir que tem pattern canônico
    - Se não tem pattern, adicionar após type: string
    - Usar string replacement: preserva melhor o formato
    """
    
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    original_content = ''.join(lines)
    modified = False
    count = 0
    messages = []
    
    # Processar campos Bucket 1
    for field_name, pattern_type in BUCKET_1_FIELDS.items():
        canonical_pattern = PATTERNS_FROM_AXIOMS[pattern_type]
        
        # Procurar por campo em properties
        field_indent = None
        field_line_idx = None
        
        for i, line in enumerate(lines):
            # Procurar por "  fieldName:" ou "  - fieldName:"
            if re.match(rf'^(\s+){re.escape(field_name)}:\s*$', line):
                field_indent = len(line) - len(line.lstrip())
                field_line_idx = i
                break
        
        if field_line_idx is None:
            continue
        
        # Procurar linhas seguintes para type e pattern
        type_indent = ' ' * (field_indent + 2)
        type_line_idx = None
        pattern_line_idx = None
        
        for i in range(field_line_idx + 1, min(field_line_idx + 10, len(lines))):
            line = lines[i]
            
            # Parou de processamento se voltou a indentação menor
            if line.strip() and not line.startswith(' ' * (field_indent + 2)):
                break
            
            # Procurar type
            if re.match(rf'^{type_indent}type:\s*string\s*$', line):
                type_line_idx = i
            
            # Procurar pattern
            if re.match(rf'^{type_indent}pattern:\s*', line):
                pattern_line_idx = i
        
        # Se não tem type, pular (não é um field normal)
        if type_line_idx is None:
            continue
        
        # Se tem pattern, verificar se precisa substituir
        if pattern_line_idx is not None:
            current_line = lines[pattern_line_idx]
            expected_line = f"{type_indent}pattern: {canonical_pattern}\n"
            
            if current_line != expected_line:
                lines[pattern_line_idx] = expected_line
                modified = True
                count += 1
                messages.append(f"  [{field_name}] pattern atualizado para {pattern_type}")
        else:
            # Não tem pattern, adicionar depois de type
            new_line = f"{type_indent}pattern: {canonical_pattern}\n"
            lines.insert(type_line_idx + 1, new_line)
            modified = True
            count += 1
            messages.append(f"  [{field_name}] pattern adicionado ({pattern_type})")
    
    if modified:
        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
    
    return modified, count, messages

# ============================================================================
# MAIN
# ============================================================================

def main():
    print("="*70)
    print("SESSION 4B v3 — BUCKET 1 REMEDIAÇÃO (padrões literais)")
    print("="*70)
    
    schema_dirs = [
        Path('contracts/openapi/components/schemas'),
        Path('contracts/asyncapi/components/schemas'),
        Path('contracts/schemas'),
    ]
    
    results = {
        'files_processed': 0,
        'files_modified': 0,
        'total_patterns_added': 0,
        'total_patterns_updated': 0,
    }
    
    print("\n" + "="*70)
    print("PROCESSANDO...")
    print("="*70 + "\n")
    
    for schema_dir in schema_dirs:
        if not schema_dir.exists():
            continue
        
        for yaml_file in sorted(schema_dir.rglob('*.yaml')):
            results['files_processed'] += 1
            
            try:
                modified, count, messages = process_yaml_file(yaml_file)
                
                if modified:
                    results['files_modified'] += 1
                    results['total_patterns_added'] += count
                    
                    print(f"✅ {yaml_file.name}")
                    for msg in messages:
                        print(f"   {msg}")
            
            except Exception as e:
                print(f"❌ {yaml_file}: {e}")
    
    print("\n" + "="*70)
    print("RESULTADO")
    print("="*70)
    print(f"\nArquivos processados: {results['files_processed']}")
    print(f"Arquivos modificados: {results['files_modified']}")
    print(f"Padrões adicionados/atualizados: {results['total_patterns_added']}")
    print("\n✅ Remediação completa! Próximo: rerodar validador")

if __name__ == '__main__':
    main()
