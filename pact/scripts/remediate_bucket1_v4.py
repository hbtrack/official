#!/usr/bin/env python3
"""
Session 4B v4: Remediação ultra-simples com string replacement
"""

import json
from pathlib import Path

# Carregar axiomas
with open('.contract_driven/DOMAIN_AXIOMS.json', 'r') as f:
    axioms = json.load(f)

PATTERNS = {
    'uuid_v4': axioms['domain_axioms']['global_formats']['uuid_v4']['pattern'],
    'timestamp_utc': axioms['domain_axioms']['global_formats']['timestamp_utc']['pattern'],
    'date_only': axioms['domain_axioms']['global_formats']['date_only']['pattern'],
    'trace_id': axioms['domain_axioms']['global_formats']['trace_id']['pattern'],
    'request_id': axioms['domain_axioms']['global_formats']['request_id']['pattern'],
}

BUCKET_1 = {
    'adjustedAt': 'timestamp_utc', 'captureStartedAt': 'timestamp_utc', 'completedAt': 'timestamp_utc',
    'computedAt': 'timestamp_utc', 'correctionAt': 'timestamp_utc', 'createdAt': 'timestamp_utc',
    'decidedAt': 'timestamp_utc', 'declaredAt': 'timestamp_utc', 'endedAt': 'timestamp_utc',
    'failedAt': 'timestamp_utc', 'nextRetryAt': 'timestamp_utc', 'occurredAt': 'timestamp_utc',
    'publishedAt': 'timestamp_utc', 'startedAt': 'timestamp_utc', 'updatedAt': 'timestamp_utc',
    'athleteId': 'uuid_v4', 'coachId': 'uuid_v4', 'conversationId': 'uuid_v4',
    'createdByUserId': 'uuid_v4', 'decidedByCoachId': 'uuid_v4', 'generatedSessionId': 'uuid_v4',
    'generatedTrainingSessionId': 'uuid_v4', 'matchId': 'uuid_v4', 'organizationId': 'uuid_v4',
    'sessionId': 'uuid_v4', 'teamId': 'uuid_v4', 'trainingId': 'uuid_v4',
    'endDate': 'date_only', 'startDate': 'date_only',
    'traceId': 'trace_id', 'requestId': 'request_id',
}

def process_file(path: Path) -> tuple[bool, int]:
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    count = 0
    
    # Para cada campo, procurar e substituir o pattern
    for field_name, pattern_type in BUCKET_1.items():
        expected_pattern = PATTERNS[pattern_type]
        
        # Procurar por:
        # "  fieldName:\n    type: string\n    pattern: <ALGO>\n"
        # Substituir por:
        # "  fieldName:\n    type: string\n    pattern: <ESPERADO>\n"
        
        # Regex flexível: fieldName: seguido de qualquer pattern
        pattern_re = rf'(  {field_name}:\n    type: string\n    (?:.*\n)*?    pattern: )([^\n]*)'
        
        def replacer(match):
            nonlocal count
            prefix = match.group(1)
            old_pattern = match.group(2)
            
            if old_pattern != expected_pattern:
                count += 1
                return f"{prefix}{expected_pattern}"
            return match.group(0)
        
        import re
        content = re.sub(pattern_re, replacer, content)
    
    if content != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, count
    
    return False, 0

# Main
print("SESSION 4B v4 — Remediação ultra-simples")
print("="*70)

results = {'processed': 0, 'modified': 0, 'lines': 0}

for yaml_file in Path('contracts').rglob('*.yaml'):
    results['processed'] += 1
    mod, cnt = process_file(yaml_file)
    if mod:
        results['modified'] += 1
        results['lines'] += cnt
        print(f"✅ {yaml_file.name}: {cnt} padrões")

print("="*70)
print(f"Processados: {results['processed']} | Modificados: {results['modified']}")
print(f"Padrões 'fixed': {results['lines']}")
