#!/usr/bin/env python3
"""
Session 4C.1 — V6 Add Missing Patterns (Critical Fix)

Objetivo: ADICIONAR padrões canônicos aos 25 campos que estão FALTANDO pattern,
não substituir patterns existentes.

Raiz do problema diagnosticado:
- 408/409 violations têm actual_pattern=None
- Campos já existem, mas SEM pattern definido
- v5 não alcançou esses campos porque regex procurava por pattern: <value>

Estratégia v6:
1. Carregar cada YAML
2. Encontrar field no properties
3. Se não há 'pattern', ADICIONAR com valor canônico
4. Preservar x-semantic-id e outros fields

Autor: HB Track Pipeline | Data: 2026-03-20
"""

import json
import pathlib
import sys
import yaml
from collections import defaultdict

def log(msg, level="INFO"):
    prefix = f"[{level}]"
    print(f"{prefix:15} {msg}")

def main():
    root = pathlib.Path(__file__).parent.parent
    
    # Carregar DOMAIN_AXIOMS
    axioms_path = root / ".contract_driven" / "DOMAIN_AXIOMS.json"
    axioms = json.loads(axioms_path.read_text())
    formats = axioms['domain_axioms']['global_formats']
    
    uuid_pattern = formats['uuid_v4']['pattern']
    timestamp_pattern = formats['timestamp_utc']['pattern']
    date_pattern = formats['date_only']['pattern']
    
    log("=== SESSION 4C.1 — V6 ADD MISSING PATTERNS ===")
    
    # 25 campos HIGH-confidence
    uuid_fields = {
        'athleteId', 'coachId', 'conversationId', 'createdByUserId',
        'decidedByCoachId', 'generatedSessionId', 'generatedTrainingSessionId',
        'matchId', 'organizationId', 'sessionId', 'teamId', 'trainingId'
    }
    
    timestamp_fields = {
        'captureStartedAt', 'completedAt', 'computedAt', 'createdAt',
        'decidedAt', 'endedAt', 'nextRetryAt', 'occurredAt', 'publishedAt',
        'startedAt', 'updatedAt'
    }
    
    date_fields = {'endDate', 'startDate'}
    
    pattern_map = {}
    for f in uuid_fields:
        pattern_map[f] = ('uuid', uuid_pattern)
    for f in timestamp_fields:
        pattern_map[f] = ('timestamp', timestamp_pattern)
    for f in date_fields:
        pattern_map[f] = ('date', date_pattern)
    
    log(f"Targets: UUID={len(uuid_fields)}, Timestamp={len(timestamp_fields)}, Date={len(date_fields)}")
    
    # Encontrar arquivos YAML em contracts/
    contracts_dir = root / "contracts"
    yaml_files = list(contracts_dir.rglob("*.yaml"))
    log(f"YAML files: {len(yaml_files)}")
    
    stats = {
        'files_processed': 0,
        'files_modified': 0,
        'patterns_added': 0,
        'by_type': defaultdict(int),
        'details': []
    }
    
    for fpath in sorted(yaml_files):
        try:
            data = yaml.safe_load(fpath.read_text(encoding='utf-8'))
            if data is None or not isinstance(data, dict):
                stats['files_processed'] += 1
                continue
        except Exception as e:
            log(f"SKIP {fpath.name}: {type(e).__name__}", "WARN")
            stats['files_processed'] += 1
            continue
        
        stats['files_processed'] += 1
        changes = 0
        
        # Verificar properties
        if 'properties' in data and isinstance(data['properties'], dict):
            for field_name, field_schema in data['properties'].items():
                if field_name in pattern_map and isinstance(field_schema, dict):
                    field_type, canonical_pattern = pattern_map[field_name]
                    
                    # Se NÃO tem pattern e tem type='string', ADICIONAR
                    if 'pattern' not in field_schema and field_schema.get('type') == 'string':
                        field_schema['pattern'] = canonical_pattern
                        stats['by_type'][field_type] += 1
                        changes += 1
                        stats['details'].append({
                            'file': str(fpath.relative_to(root)),
                            'field': field_name,
                            'action': 'added_pattern',
                            'type': field_type,
                            'had_format': 'format' in field_schema
                        })
        
        # Salvar se modificado
        if changes > 0:
            try:
                yaml_str = yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True)
                fpath.write_text(yaml_str, encoding='utf-8')
                stats['files_modified'] += 1
                stats['patterns_added'] += changes
            except Exception as e:
                log(f"Erro escrevendo {fpath.name}: {e}", "ERROR")
    
    log("\n=== RESULTADO V6 ADD MISSING ===")
    log(f"Arquivos processados: {stats['files_processed']}")
    log(f"Arquivos modificados: {stats['files_modified']}")
    log(f"Patterns adicionados: {stats['patterns_added']}")
    log(f"  - UUID: {stats['by_type']['uuid']}")
    log(f"  - Timestamp: {stats['by_type']['timestamp']}")
    log(f"  - Date: {stats['by_type']['date']}")
    
    # Salvar relatório
    report_path = root / "_reports" / "SESSION_4C_1_V6_ADD_MISSING_REPORT.json"
    report = {
        "session": "4C.1",
        "phase": "V6_ADD_MISSING_PATTERNS",
        "root_cause": "actual_pattern=None for 408/409 violations",
        "execution": {
            "axioms_source": str(axioms_path.relative_to(root)),
            "fields_targeted": {
                "uuid": list(uuid_fields),
                "timestamp": list(timestamp_fields),
                "date": list(date_fields),
                "total": 25
            }
        },
        "results": {
            "files_processed": stats['files_processed'],
            "files_modified": stats['files_modified'],
            "patterns_added": stats['patterns_added'],
            "by_type": dict(stats['by_type']),
            "conservative": True,
            "adds_not_replaces": True
        },
        "details": stats['details'][:100]  # First 100
    }
    report_path.write_text(json.dumps(report, indent=2))
    log(f"\nRelatório: {report_path.relative_to(root)}")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
