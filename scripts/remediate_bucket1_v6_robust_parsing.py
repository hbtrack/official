#!/usr/bin/env python3
"""
Session 4C.1 — Remediate Bucket 1 Remaining (v6 Robust via Parsing)

Objetivo: Aplicar padrões canônicos apenas aos 25 campos HIGH-confidence
usando parsing real de YAML/JSON para evitar erros de regex.

Regra conservadora:
- Apenas os 25 campos listados
- Nenhum campo "por semelhança"  
- Padrões exatos do DOMAIN_AXIOMS.json
- Parsing YAML/JSON seguro

Autor: HB Track Pipeline | Data: 2026-03-20
"""

import json
import pathlib
import sys
import yaml
from collections import defaultdict

def log(msg, level="INFO"):
    """Log with level prefix."""
    prefix = f"[{level}]"
    print(f"{prefix:15} {msg}")

def main():
    root = pathlib.Path(__file__).parent.parent
    
    # Carregar DOMAIN_AXIOMS para padrões canônicos
    axioms_path = root / ".contract_driven" / "DOMAIN_AXIOMS.json"
    axioms = json.loads(axioms_path.read_text())
    formats = axioms['domain_axioms']['global_formats']
    
    # Padrões canônicos
    uuid_pattern = formats['uuid_v4']['pattern']
    timestamp_pattern = formats['timestamp_utc']['pattern']
    date_pattern = formats['date_only']['pattern']
    
    log("=== SESSION 4C.1 — V6 ROBUST (YAML Parsing) ===")
    log(f"Carregar axiomas de: {axioms_path.name}")
    
    # 25 campos HIGH-confidence da Session 4C
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
    
    all_25_fields = uuid_fields | timestamp_fields | date_fields
    pattern_map = {}
    for f in uuid_fields:
        pattern_map[f] = uuid_pattern
    for f in timestamp_fields:
        pattern_map[f] = timestamp_pattern
    for f in date_fields:
        pattern_map[f] = date_pattern
    
    log(f"Total 25 campos auditados: UUID={len(uuid_fields)}, Timestamp={len(timestamp_fields)}, Date={len(date_fields)}")
    
    # Encontrar todos os arquivos YAML/JSON em contracts/
    contracts_dir = root / "contracts"
    yaml_files = list(contracts_dir.rglob("*.yaml"))
    json_files = list(contracts_dir.rglob("*.json"))
    all_files = yaml_files + json_files
    log(f"Total {len(all_files)} arquivos de contrato encontrados")
    
    # Estatísticas
    stats = {
        'files_processed': 0,
        'files_modified': 0,
        'replacements_total': 0,
        'replacements_by_type': defaultdict(int),
        'details': []
    }
    
    # Processar cada arquivo YAML
    for fpath in sorted(yaml_files):
        try:
            data = yaml.safe_load(fpath.read_text(encoding='utf-8'))
            if data is None:
                continue
        except Exception as e:
            log(f"SKIP {fpath.relative_to(root)}: não é YAML válido ({type(e).__name__})", "WARN")
            stats['files_processed'] += 1
            continue
        
        stats['files_processed'] += 1
        original_data = json.dumps(data, sort_keys=True)
        changes_in_file = 0
        
        # Verificar properties (OpenAPI/AsyncAPI style)
        if isinstance(data, dict) and 'properties' in data:
            for field_name, field_schema in data['properties'].items():
                if field_name in pattern_map and isinstance(field_schema, dict):
                    if 'pattern' in field_schema:
                        old_pattern = field_schema['pattern']
                        new_pattern = pattern_map[field_name]
                        
                        if old_pattern != new_pattern:
                            field_schema['pattern'] = new_pattern
                            field_type = 'uuid' if field_name in uuid_fields else ('timestamp' if field_name in timestamp_fields else 'date')
                            stats['replacements_by_type'][field_type] += 1
                            changes_in_file += 1
                            stats['details'].append({
                                'file': str(fpath.relative_to(root)),
                                'field': field_name,
                                'type': field_type,
                                'old_pattern': old_pattern[:50],
                                'new_pattern': new_pattern
                            })
        
        # Salvar se modificado
        if changes_in_file > 0:
            try:
                modified_yaml = yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True)
                fpath.write_text(modified_yaml, encoding='utf-8')
                stats['files_modified'] += 1
                stats['replacements_total'] += changes_in_file
            except Exception as e:
                log(f"Erro escrevendo {fpath.relative_to(root)}: {e}", "ERROR")
    
    # Relatório final
    log("\n=== RESULTADO V6 ROBUST ===")
    log(f"Arquivos processados: {stats['files_processed']}")
    log(f"Arquivos modificados: {stats['files_modified']}")
    log(f"Total substituições: {stats['replacements_total']}")
    log(f"  - UUID: {stats['replacements_by_type']['uuid']}")
    log(f"  - Timestamp: {stats['replacements_by_type']['timestamp']}")
    log(f"  - Date: {stats['replacements_by_type']['date']}")
    
    # Salvar relatório detalhado
    report_path = root / "_reports" / "SESSION_4C_1_V6_EXECUTION_REPORT.json"
    report = {
        "session": "4C.1",
        "phase": "V6_ROBUST_PARSING",
        "execution": {
            "axioms_source": str(axioms_path.relative_to(root)),
            "parsing_method": "YAML SafeLoad + Direct Property Modification",
            "fields_targeted": {
                "uuid": list(uuid_fields),
                "timestamp": list(timestamp_fields),
                "date": list(date_fields),
                "total": 25
            },
            "patterns": {
                "uuid_v4": uuid_pattern,
                "timestamp_utc": timestamp_pattern,
                "date_only": date_pattern
            }
        },
        "results": {
            "files_processed": stats['files_processed'],
            "files_modified": stats['files_modified'],
            "total_replacements": stats['replacements_total'],
            "replacements_by_type": dict(stats['replacements_by_type']),
            "no_field_outside_25": True,
            "conservative_mode": True,
            "parsing_safe": True
        },
        "details": stats['details']
    }
    report_path.write_text(json.dumps(report, indent=2))
    log(f"\nRelatório salvo em: {report_path.relative_to(root)}")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
