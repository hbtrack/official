#!/usr/bin/env python3
"""
Session 4B: Executar remediação Bucket 1 automático de Item 2C

Estratégia:
1. Mapear campos Bucket 1 inequívocos → padrão canônico
2. Adicionar x-domain-pattern-ref em lugar de regex literal
3. Preservar máxima formatação YAML
4. Registrar cada mudança

Campos Bucket 1 (INEQUÍVOCOS):
- timestamp_utc: createdAt, updatedAt, completedAt, occurredAt, publishedAt, etc.
- uuid_v4: athleteId, organizationId, sessionId, teamId, matchId, etc.
- date_only: endDate, startDate
- trace_id: traceId
- request_id: requestId

Critério de inclusão: Nome do campo deve deixar a semântica 100% óbvia.
Não incluir: id genérico, nomes ambíguos, enums.
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple

# ============================================================================
# BUCKET 1 MAPPING (INEQUÍVOCOS)
# ============================================================================

BUCKET_1_FIELDS = {
    # Timestamp fields — sufixo 'At' (15 campos)
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
    
    # UUID fields — sufixo 'Id' (12 campos)
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
    
    # Date fields — sufixo 'Date' (2 campos)
    'endDate': 'date_only',
    'startDate': 'date_only',
    
    # Específicos
    'traceId': 'trace_id',
    'requestId': 'request_id',
}

# ============================================================================
# UTILS
# ============================================================================

def process_yaml_file(path: Path) -> Tuple[bool, int, List[str]]:
    """
    Processo:
    1. Ler arquivo
    2. Para cada campo Bucket 1, encontrar sua definição
    3. Remover `pattern:` se existir
    4. Adicionar `x-domain-pattern-ref: <padrão>`
    5. Salvar com preservação de formato
    
    Retorna:
    - (modified, count, messages)
    """
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    modified = False
    count = 0
    messages = []
    
    for field_name, pattern_ref in BUCKET_1_FIELDS.items():
        # Procurar padrão: linha com "fieldName:" seguida de type/pattern
        # Usar regex simples: "  fieldName:" (com indentação)
        
        # Padrão 1: Remover pattern literal e adicionar x-domain-pattern-ref
        # De: "  fieldName:\n    type: string\n    pattern: ^....\n"
        # Para: "  fieldName:\n    type: string\n    x-domain-pattern-ref: pattern_type\n"
        
        # Regex para encontrar campo com pattern literal
        field_pattern = rf'^(\s+)({re.escape(field_name)}):\s*\n(?=\1\s+type:)\1\s+type:\s*string\s*\n\1\s+pattern:\s*[^\n]*\n'
        
        def replacer(match):
            nonlocal modified, count
            indent = match.group(1)
            field = match.group(2)
            # Substituir pattern por x-domain-pattern-ref
            result = f"{indent}{field}:\n{indent}  type: string\n{indent}  x-domain-pattern-ref: {pattern_ref}\n"
            modified = True
            count += 1
            messages.append(f"  [{field}] pattern → x-domain-pattern-ref:{pattern_ref}")
            return result
        
        content = re.sub(field_pattern, replacer, content, flags=re.MULTILINE)
        
        # Padrão 2: Adicionar x-domain-pattern-ref se não existe pattern
        # De: "  fieldName:\n    type: string\n"
        # Para: "  fieldName:\n    type: string\n    x-domain-pattern-ref: pattern_type\n"
        
        field_pattern_no_match = rf'^(\s+)({re.escape(field_name)}):\s*\n(?=\1\s+type:)\1\s+type:\s*string\s*\n(?!\1\s+(?:pattern|x-domain-pattern-ref))'
        
        def replacer2(match):
            nonlocal modified, count
            indent = match.group(1)
            field = match.group(2)
            # Inserir x-domain-pattern-ref depois de type: string
            result = f"{indent}{field}:\n{indent}  type: string\n{indent}  x-domain-pattern-ref: {pattern_ref}\n"
            modified = True
            count += 1
            messages.append(f"  [{field}] added x-domain-pattern-ref:{pattern_ref}")
            return result
        
        # Aplicar só se não já foi modificado pelo padrão acima
        lines = content.split('\n')
        new_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Procurar por "  fieldName:" (com indentação)
            if re.match(rf'^(\s+){re.escape(field_name)}:\s*$', line):
                indent_match = re.match(r'^(\s+)', line)
                if indent_match:
                    indent = indent_match.group(1)
                    
                    # Procurar próximas linhas
                    if i + 1 < len(lines) and re.match(rf'^{re.escape(indent)}\s+type:\s*string\s*$', lines[i + 1]):
                        # Verificar se tem pattern ou x-domain-pattern-ref já
                        has_pattern_or_ref = False
                        if i + 2 < len(lines):
                            next_line = lines[i + 2]
                            if re.match(rf'^{re.escape(indent)}\s+(?:pattern|x-domain-pattern-ref):', next_line):
                                has_pattern_or_ref = True
                        
                        new_lines.append(line)  # Adicionar fieldName:
                        new_lines.append(lines[i + 1])  # Adicionar type: string
                        
                        if not has_pattern_or_ref:
                            # Adicionar x-domain-pattern-ref
                            new_lines.append(f"{indent}  x-domain-pattern-ref: {pattern_ref}")
                            modified = True
                            count += 1
                            messages.append(f"  [{field_name}] added x-domain-pattern-ref:{pattern_ref} (no pattern/ref)")
                            i += 2
                        else:
                            i += 1
                    else:
                        new_lines.append(line)
                        i += 1
                else:
                    new_lines.append(line)
                    i += 1
            else:
                new_lines.append(line)
                i += 1
        
        content = '\n'.join(new_lines)
    
    if modified:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, count, messages
    
    return False, 0, messages

# ============================================================================
# MAIN
# ============================================================================

def main():
    print("="*70)
    print("SESSION 4B — BUCKET 1 REMEDIAÇÃO AUTOMÁTICA")
    print("="*70)
    print(f"\n📋 Campos Bucket 1 a processar: {len(BUCKET_1_FIELDS)}")
    print("\nDistribuição:")
    count_by_type = {}
    for field, ptype in BUCKET_1_FIELDS.items():
        count_by_type[ptype] = count_by_type.get(ptype, 0) + 1
    for ptype in sorted(count_by_type.keys()):
        print(f"  - {ptype}: {count_by_type[ptype]}")
    
    schema_dirs = [
        Path('contracts/openapi/components/schemas'),
        Path('contracts/asyncapi/components/schemas'),
        Path('contracts/schemas'),
    ]
    
    results = {
        'files_processed': 0,
        'files_modified': 0,
        'total_refs_added': 0,
        'modified_files': [],
    }
    
    print("\n" + "="*70)
    print("PROCESSANDO ARQUIVOS...")
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
                    results['total_refs_added'] += count
                    results['modified_files'].append(str(yaml_file))
                    
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
    print(f"Refs adicionadas: {results['total_refs_added']}")
    
    if results['modified_files']:
        print(f"\n✅ Bucket 1 remediação completa!")
        print("   Próximo passo: rerodar validador")
    else:
        print("\n⚠️ Nenhuma modificação realizada")

if __name__ == '__main__':
    main()
