#!/usr/bin/env python3
"""
Session 4C.1 — Remediate Bucket 1 Remaining (v6 Conservative)

Objetivo: Aplicar padrões canônicos apenas aos 25 campos HIGH-confidence
auditados e aprovados na Sessão 4C.

Regra conservadora:
- Apenas os 25 campos listados
- Nenhum campo "por semelhança"
- Padrões exatos do DOMAIN_AXIOMS.json
- Relatório detalhado de mudanças

Autor: HB Track Pipeline | Data: 2026-03-20
"""

import json
import pathlib
import re
import sys
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
    
    log("=== SESSION 4C.1 — V6 CONSERVATIVE ===")
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
    log(f"Total 25 campos auditados: UUID={len(uuid_fields)}, Timestamp={len(timestamp_fields)}, Date={len(date_fields)}")
    
    # Encontrar todos os arquivos YAML/JSON em contracts/
    contracts_dir = root / "contracts"
    contract_files = list(contracts_dir.rglob("*.yaml")) + list(contracts_dir.rglob("*.json"))
    log(f"Total {len(contract_files)} arquivos de contrato encontrados")
    
    # Estatísticas
    stats = {
        'files_processed': 0,
        'files_modified': 0,
        'replacements_by_type': defaultdict(int),
        'replacements_total': 0,
        'details': []
    }
    
    # Processar cada arquivo
    for fpath in sorted(contract_files):
        try:
            content = fpath.read_text(encoding='utf-8')
        except Exception as e:
            log(f"Erro lendo {fpath.relative_to(root)}: {e}", "WARN")
            continue
        
        stats['files_processed'] += 1
        original_content = content
        file_replacements = 0
        
        # UUID fields
        for field in uuid_fields:
            # Pattern: field_name: + pattern regex (relaxado para captar várias formatos)
            # Encontrar: field_name:\n    type: string\n    pattern: <anything>
            pattern_re = rf"({re.escape(field)}:\s*)\n(\s+type: string\s*)\n(\s+pattern:)\s*['\"]?[^'\"]*['\"]?"
            
            # Substituição com padrão canônico UUID (escapado para regex)
            escaped_uuid = re.escape(uuid_pattern)
            replacement = rf"\1\n\2\n\3 {escaped_uuid}"
            
            # Contar matches
            matches = re.finditer(pattern_re, content, re.MULTILINE)
            match_count = len(list(matches))
            
            if match_count > 0:
                content = re.sub(pattern_re, replacement, content, flags=re.MULTILINE)
                stats['replacements_by_type']['uuid'] += match_count
                file_replacements += match_count
                stats['details'].append({
                    'file': str(fpath.relative_to(root)),
                    'field': field,
                    'type': 'uuid',
                    'count': match_count
                })
        
        # Timestamp fields
        for field in timestamp_fields:
            pattern_re = rf"({re.escape(field)}:\s*)\n(\s+type: string\s*)\n(\s+pattern:)\s*['\"]?[^'\"]*['\"]?"
            escaped_ts = re.escape(timestamp_pattern)
            replacement = rf"\1\n\2\n\3 {escaped_ts}"
            
            matches = list(re.finditer(pattern_re, content, re.MULTILINE))
            match_count = len(matches)
            
            if match_count > 0:
                content = re.sub(pattern_re, replacement, content, flags=re.MULTILINE)
                stats['replacements_by_type']['timestamp'] += match_count
                file_replacements += match_count
                stats['details'].append({
                    'file': str(fpath.relative_to(root)),
                    'field': field,
                    'type': 'timestamp',
                    'count': match_count
                })
        
        # Date fields
        for field in date_fields:
            pattern_re = rf"({re.escape(field)}:\s*)\n(\s+type: string\s*)\n(\s+pattern:)\s*['\"]?[^'\"]*['\"]?"
            escaped_date = re.escape(date_pattern)
            replacement = rf"\1\n\2\n\3 {escaped_date}"
            
            matches = list(re.finditer(pattern_re, content, re.MULTILINE))
            match_count = len(matches)
            
            if match_count > 0:
                content = re.sub(pattern_re, replacement, content, flags=re.MULTILINE)
                stats['replacements_by_type']['date'] += match_count
                file_replacements += match_count
                stats['details'].append({
                    'file': str(fpath.relative_to(root)),
                    'field': field,
                    'type': 'date',
                    'count': match_count
                })
        
        # Escrever se modificado
        if content != original_content:
            stats['files_modified'] += 1
            stats['replacements_total'] += file_replacements
            try:
                fpath.write_text(content, encoding='utf-8')
            except Exception as e:
                log(f"Erro escrevendo {fpath.relative_to(root)}: {e}", "ERROR")
    
    # Relatório final
    log("\n=== RESULTADO V6 CONSERVATIVE ===")
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
        "phase": "V6_CONSERVATIVE",
        "timestamp": pathlib.Path('/tmp').stat().st_mtime,
        "execution": {
            "axioms_source": str(axioms_path.relative_to(root)),
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
            "conservative_mode": True
        },
        "details": stats['details']
    }
    report_path.write_text(json.dumps(report, indent=2))
    log(f"\nRelatório salvo em: {report_path.relative_to(root)}")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
