#!/usr/bin/env python3
"""
Remediação v2: substituir padrões literais por x-domain-pattern-ref

Estratégia:
1. Procurar campos do Bucket 1 por nome
2. Se tem pattern literal canônico, adicionar x-domain-pattern-ref + remover pattern
3. Se não tem pattern, apenas adicionar x-domain-pattern-ref
"""

import yaml
from pathlib import Path
from typing import Dict

BUCKET_1_FIELDS = {
    # Timestamp (15)
    'adjustedAt', 'captureStartedAt', 'completedAt', 'computedAt', 'correctionAt',
    'createdAt', 'decidedAt', 'declaredAt', 'endedAt', 'failedAt', 'nextRetryAt',
    'occurredAt', 'publishedAt', 'startedAt', 'updatedAt',
    # UUID (12)
    'athleteId', 'coachId', 'conversationId', 'createdByUserId', 'decidedByCoachId',
    'generatedSessionId', 'generatedTrainingSessionId', 'matchId', 'organizationId',
    'sessionId', 'teamId', 'trainingId',
    # Date (1)
    'endDate',
}

# Mapping campo → pattern ref
FIELD_TO_PATTERN = {
    # Timestamp
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
    # UUID
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
    # Date
    'endDate': 'date_only',
}

def process_file(yaml_path: Path) -> bool:
    """Process a single YAML file to add x-domain-pattern-ref."""
    
    with open(yaml_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    data = yaml.safe_load(content)
    if not isinstance(data, dict):
        return False
    
    modified = False
    
    # Procurar nos properties
    if 'properties' in data and isinstance(data['properties'], dict):
        for field_name in BUCKET_1_FIELDS:
            if field_name in data['properties']:
                field_def = data['properties'][field_name]
                if isinstance(field_def, dict):
                    pattern_ref = FIELD_TO_PATTERN.get(field_name)
                    if pattern_ref and 'x-domain-pattern-ref' not in field_def:
                        # Adicionar x-domain-pattern-ref
                        field_def['x-domain-pattern-ref'] = pattern_ref
                        # Remover pattern literal se existir
                        if 'pattern' in field_def:
                            del field_def['pattern']
                        modified = True
    
    if modified:
        # Re-salvar com yaml.dump
        with open(yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        return True
    
    return False

def main():
    print("="*70)
    print("REMEDIAÇÃO v2 — Add x-domain-pattern-ref (28 Bucket 1 campos)")
    print("="*70)
    
    results = {'processed': 0, 'modified': 0}
    
    schema_dirs = [
        Path('contracts/openapi/components/schemas'),
        Path('contracts/asyncapi/components/schemas'),
        Path('contracts/schemas'),
    ]
    
    for schema_dir in schema_dirs:
        if not schema_dir.exists():
            continue
        
        for yaml_file in schema_dir.rglob('*.yaml'):
            results['processed'] += 1
            
            try:
                if process_file(yaml_file):
                    results['modified'] += 1
                    print(f"✅ {yaml_file}")
            except Exception as e:
                print(f"❌ {yaml_file}: {e}")
    
    print("\n" + "="*70)
    print(f"Processados: {results['processed']} | Modificados: {results['modified']}")
    print("="*70)

if __name__ == '__main__':
    main()
