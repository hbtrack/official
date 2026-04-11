#!/usr/bin/env python3
"""
Session 4C.2 — V6 v2 Expanded Remediation
Re-run v6 with 104 validated fields (5 original + 99 expansion, 0 CONTEXT_DEPENDENT)
Expected impact: 249 violations down to ~13 (CONTEXT_DEPENDENT excluded)
"""

import json
import yaml
import os
import sys
from pathlib import Path
from collections import defaultdict

# Load v6 v2 field list (104 fields, no CONTEXT_DEPENDENT)
with open('_reports/BACKLOG_2C_SESSION_4C2_V6_V2_FIELD_LIST.json', 'r') as f:
    v6_v2_data = json.load(f)

v6_v2_fields = set(v6_v2_data['fields'])
context_dependent_excluded = set(v6_v2_data['context_dependent_fields'])

print(f"[INFO] V6 v2 Expanded Configuration")
print(f"[INFO] Fields to apply patterns: {len(v6_v2_fields)}")
print(f"[INFO] Fields explicitly excluded (CONTEXT_DEPENDENT): {len(context_dependent_excluded)}")

# Padrões canonicais (EXATOS do gate)
PATTERNS = {
    # UUIDs
    'uuid_v4': '^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$',
    # Timestamps (com milliseconds/microseconds opcionais)
    'timestamp_utc': r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3,6})?Z$',
    # Dates
    'date_only': r'^\d{4}-\d{2}-\d{2}$'
}

# Classificar fields por tipo
field_types = {}
with open('_reports/BACKLOG_2C_SESSION_4D_DECISION_TREE.json', 'r') as f:
    decision_tree = json.load(f)
    
for family in decision_tree.get('families', []):
    decision = family['decision']
    for field_info in family.get('fields', []):
        field_name = field_info['name']
        if field_name in v6_v2_fields:
            if 'UUID' in decision or 'uuid' in decision.lower():
                field_types[field_name] = 'uuid_v4'
            elif 'TIMESTAMP' in decision or 'timestamp' in decision.lower():
                field_types[field_name] = 'timestamp_utc'
            elif 'DATE' in decision or 'date' in decision.lower():
                field_types[field_name] = 'date_only'

print(f"\n[INFO] Pattern Assignment:")
print(f"[INFO]   UUID fields: {len([f for f,t in field_types.items() if t=='uuid_v4'])}")
print(f"[INFO]   Timestamp fields: {len([f for f,t in field_types.items() if t=='timestamp_utc'])}")
print(f"[INFO]   Date fields: {len([f for f,t in field_types.items() if t=='date_only'])}")

# Find contracts
contracts_dir = Path('contracts/asyncapi/components/schemas')
yaml_files = list(contracts_dir.glob('*.yaml'))

print(f"\n[INFO] Processing {len(yaml_files)} schema files...")

stats = {
    'files_processed': 0,
    'files_modified': 0,
    'patterns_added': defaultdict(int),
    'errors': []
}

for yaml_file in yaml_files:
    stats['files_processed'] += 1
    
    try:
        with open(yaml_file, 'r') as f:
            content = yaml.safe_load(f)
        
        if not content or 'properties' not in content:
            continue
        
        properties = content['properties']
        file_modified = False
        
        for field_name, field_config in properties.items():
            # Skip if not in v6_v2 list
            if field_name not in v6_v2_fields:
                continue
            
            # Skip if field is not a string type
            if field_config.get('type') != 'string':
                continue
            
            # Skip if pattern already exists
            if 'pattern' in field_config:
                continue
            
            # Determine pattern to apply
            pattern_type = field_types.get(field_name)
            if not pattern_type:
                continue
            
            # Add pattern
            pattern_value = PATTERNS.get(pattern_type)
            if pattern_value:
                field_config['pattern'] = pattern_value
                stats['patterns_added'][pattern_type] += 1
                file_modified = True
        
        # Write back if modified
        if file_modified:
            with open(yaml_file, 'w') as f:
                yaml.dump(content, f, sort_keys=False, allow_unicode=True)
            stats['files_modified'] += 1
    
    except Exception as e:
        stats['errors'].append(f"{yaml_file.name}: {str(e)}")

# Report
print(f"\n[INFO] === RESULTADO V6 v2 EXPANDED ===")
print(f"[INFO] Arquivos processados: {stats['files_processed']}")
print(f"[INFO] Arquivos modificados: {stats['files_modified']}")
print(f"[INFO] Padrões adicionados por tipo:")
print(f"[INFO]   - UUID: {stats['patterns_added']['uuid_v4']}")
print(f"[INFO]   - Timestamp: {stats['patterns_added']['timestamp_utc']}")
print(f"[INFO]   - Date: {stats['patterns_added']['date_only']}")

if stats['errors']:
    print(f"[ERROR] Erros durante processamento: {len(stats['errors'])}")
    for err in stats['errors'][:5]:
        print(f"[ERROR]   - {err}")

# Save execution report
report = {
    'session': '4C.2',
    'version': 'v6_v2',
    'execution_date': '2026-03-20',
    'fields_configuration': {
        'total_v6_v2_fields': len(v6_v2_fields),
        'context_dependent_excluded': len(context_dependent_excluded),
        'uuid_fields': len([f for f,t in field_types.items() if t=='uuid_v4']),
        'timestamp_fields': len([f for f,t in field_types.items() if t=='timestamp_utc']),
        'date_fields': len([f for f,t in field_types.items() if t=='date_only'])
    },
    'execution': stats
}

with open('_reports/SESSION_4C2_V6_V2_EXPANDED_EXECUTION_REPORT.json', 'w') as f:
    json.dump(report, f, indent=2)

print(f"\n[INFO] Relatório salvo em: _reports/SESSION_4C2_V6_V2_EXPANDED_EXECUTION_REPORT.json")

sys.exit(0 if not stats['errors'] else 1)
