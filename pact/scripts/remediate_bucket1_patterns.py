#!/usr/bin/env python3
"""
Remediação automática de 98 violações do Bucket 1 (padrões canônicos).

Estratégia:
1. Carregar padrões canônicos de DOMAIN_AXIOMS.json
2. Mapear campos do Bucket 1 para seus padrões esperados
3. Iterar sobre arquivos YAML/JSON de schema
4. Encontrar campos do Bucket 1 e aplicar pattern correto
5. Salvar arquivos modificados
"""

import json
import yaml
import re
from pathlib import Path
from typing import Dict, List, Tuple, Set

# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

# Bucket 1 mapping: campo → padrão esperado
BUCKET_1_FIELDS = {
    # Timestamp fields (15 campos)
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
    
    # UUID fields (12 campos)
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
    
    # Date fields (1 campo)
    'endDate': 'date_only',
}

# Padrões canônicos (com escape para YAML)
CANONICAL_PATTERNS = {
    'uuid_v4': '^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$',
    'date_only': '^\\d{4}-\\d{2}-\\d{2}$',
    'timestamp_utc': '^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(?:\\.\\d{3,6})?Z$',
}

# ============================================================================
# HELPERS
# ============================================================================

def load_yaml_preserving_format(path: Path) -> Tuple[dict, str]:
    """Load YAML while preserving original formatting."""
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    data = yaml.safe_load(content)
    return data, content

def save_yaml_preserving_format(path: Path, data: dict, original_content: str) -> bool:
    """Save YAML with smart pattern replacement instead of full dump."""
    # Carregar original de novo para ter estrutura atual
    with open(path, 'r', encoding='utf-8') as f:
        current_content = f.read()
    
    # Fazer substituições de pattern nos campos do Bucket 1
    modified = False
    for field_name, pattern_type in BUCKET_1_FIELDS.items():
        pattern_str = CANONICAL_PATTERNS[pattern_type]
        
        # Procurar por definição de campo em YAML
        # Padrão: "fieldName:\n  ..."
        # ou dentro de properties: "  fieldName:"
        
        # Regex para encontrar o campo e seu contexto
        # Tenta encontrar linhas com o campo e suas opções de pattern/format
        
        # Contexto: campo dentro de properties ou definição de schema
        field_pattern = rf'^(\s+)({field_name}):\s*$'
        
        lines = current_content.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i]
            match = re.match(field_pattern, line)
            
            if match:
                indent = match.group(1)
                # Procurar linhas seguintes por type, pattern, format
                j = i + 1
                has_pattern = False
                has_format = False
                
                while j < len(lines):
                    next_line = lines[j]
                    
                    # Se chegar a uma linha com indentação menor, saiu do campo
                    if next_line.strip() and not next_line.startswith(indent + ' '):
                        break
                    
                    # Verificar se tem pattern ou format
                    if re.match(rf'^{indent}\s+pattern:\s*', next_line):
                        has_pattern = True
                        # Substituir pattern
                        old_pattern_line = next_line
                        new_pattern_line = f"{indent}  pattern: {pattern_str}"
                        if old_pattern_line != new_pattern_line:
                            lines[j] = new_pattern_line
                            modified = True
                        break
                    
                    if re.match(rf'^{indent}\s+format:\s*', next_line):
                        has_format = True
                        break
                    
                    j += 1
                
                # Se não tem pattern, adicionar após type (ou como primeira opção)
                if not has_pattern and not has_format:
                    # Procurar line com "type:" para adicionar pattern depois
                    for k in range(i + 1, min(i + 10, len(lines))):
                        if re.match(rf'^{indent}\s+type:\s*', lines[k]):
                            # Adicionar pattern na linha seguinte
                            insert_idx = k + 1
                            new_pattern_line = f"{indent}  pattern: {pattern_str}"
                            lines.insert(insert_idx, new_pattern_line)
                            modified = True
                            break
            
            i += 1
        
        current_content = '\n'.join(lines)
    
    if modified:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(current_content)
        return True
    
    return False

def process_schema_files() -> Dict[str, int]:
    """Process all schema files looking for Bucket 1 fields."""
    results = {
        'files_processed': 0,
        'files_modified': 0,
        'patterns_added': 0,
        'patterns_fixed': 0,
    }
    
    schema_dirs = [
        Path('contracts/openapi/components/schemas'),
        Path('contracts/asyncapi/components/schemas'),
        Path('contracts/schemas'),
    ]
    
    for schema_dir in schema_dirs:
        if not schema_dir.exists():
            continue
        
        for yaml_file in schema_dir.rglob('*.yaml'):
            results['files_processed'] += 1
            
            try:
                data, original = load_yaml_preserving_format(yaml_file)
                
                # Procurar por campos do Bucket 1
                modified = save_yaml_preserving_format(yaml_file, data, original)
                
                if modified:
                    results['files_modified'] += 1
                    print(f"✅ Modified: {yaml_file}")
            
            except Exception as e:
                print(f"❌ Error in {yaml_file}: {e}")
    
    return results

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("="*70)
    print("REMEDIAÇÃO AUTOMÁTICA — BUCKET 1 (98 VIOLAÇÕES)")
    print("="*70)
    
    print(f"\n📋 Campos a corrigir: {len(BUCKET_1_FIELDS)}")
    print("\nCampos por tipo:")
    for pattern_type in ['timestamp_utc', 'uuid_v4', 'date_only']:
        fields = [f for f, p in BUCKET_1_FIELDS.items() if p == pattern_type]
        print(f"  {pattern_type}: {len(fields)} [{', '.join(fields[:3])}...]")
    
    print("\n" + "="*70)
    print("PROCESSANDO ARQUIVOS...")
    print("="*70)
    
    results = process_schema_files()
    
    print("\n" + "="*70)
    print("RESULTADO")
    print("="*70)
    print(f"Arquivos processados: {results['files_processed']}")
    print(f"Arquivos modificados: {results['files_modified']}")
    print("\n✅ Remediação completada!")
    print("\nPróxima ação: rerodar validador com `python3 scripts/contracts/validate/validate_contracts.py`")
