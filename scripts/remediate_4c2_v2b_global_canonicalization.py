#!/usr/bin/env python3
"""
4C.2.v2b — Global Canonicalization Remediation
Fase 4: Sincronização global de 90 campos restantes

Estratégia:
1. NOT_IN_SCHEMA (42): Buscar em todas as localizações (mesmo fora components/schemas/)
2. PATTERN_MISSING_STILL (16): Adicionar padrão em TODOS os locais
3. PATTERN_CORRECT_BUT_GATE_FAILS (31): Corrigir type array + sincronizar padrão
4. PATTERN_MISMATCH (1): Corrigir único mismatch

Resultado esperado: 90 violations → ~20-30 (70%+ reduction)
"""

import json
import yaml
from pathlib import Path
from collections import defaultdict
import sys

# Canonical patterns
PATTERNS = {
    # UUID v4
    'uuid_v4': '^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$',
    # Timestamp UTC
    'timestamp_utc': r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3,6})?Z$',
    # Date only
    'date': r'^\d{4}-\d{2}-\d{2}$',
}

# Campos por categoria + padrão esperado
REMEDIATION_MAP = {
    # NOT_IN_SCHEMA - buscar em paths, responses, etc
    'NOT_IN_SCHEMA': {
        # Será preenchido dinamicamente
    },
    # PATTERN_MISSING_STILL - adicionar UUID v4
    'PATTERN_MISSING_STILL': {
        'accessorUserId': 'uuid_v4',
        'changedByUserId': 'uuid_v4',
        'correlationId': 'uuid_v4',
        'distributedAt': 'timestamp_utc',
        'grantedByUserId': 'uuid_v4',
        'id': 'uuid_v4',  # Campo universal
        'jobId': 'uuid_v4',
        'matchId': 'uuid_v4',
        'modifiedByUserId': 'uuid_v4',
        'notificationId': 'uuid_v4',
        'requestId': 'uuid_v4',
        'requestedAt': 'timestamp_utc',
        'sessionId': 'uuid_v4',
        'teamId': 'uuid_v4',
        'updatedAt': 'timestamp_utc',
        'videoClipId': 'uuid_v4',
    },
    # PATTERN_CORRECT_BUT_GATE_FAILS - sincronizar + corrigir type
    'PATTERN_CORRECT_BUT_GATE_FAILS': {
        'actorUserId': 'uuid_v4',
        'athleteId': 'uuid_v4',
        'athleteUserId': 'uuid_v4',
        'awayTeamId': 'uuid_v4',
        'captureStartedAt': 'timestamp_utc',
        'clipId': 'uuid_v4',
        'competitionId': 'uuid_v4',
        'conversationId': 'uuid_v4',
        'createdAt': 'timestamp_utc',
        'deliveryId': 'uuid_v4',
        'entryId': 'uuid_v4',
        'eventId': 'uuid_v4',
        'expiresAt': 'timestamp_utc',
        'homeTeamId': 'uuid_v4',
        'jobId': 'uuid_v4',
        'organizationId': 'uuid_v4',
        'recipientUserId': 'uuid_v4',
        'revokedByUserId': 'uuid_v4',
        'scoutEventId': 'uuid_v4',
        'scheduledAt': 'timestamp_utc',
        'seasonId': 'uuid_v4',
        'segmentId': 'uuid_v4',
        'syncCompletedAt': 'timestamp_utc',
        'targetResourceId': 'uuid_v4',
        'trainingSessionId': 'uuid_v4',
        'userId': 'uuid_v4',
        'athleteUserId': 'uuid_v4',
        'coachUserId': 'uuid_v4',
        'currentValue': 'uuid_v4',
        'technicalContactUserId': 'uuid_v4',
        'clinicalContactUserId': 'uuid_v4',
        'createdByUserId': 'uuid_v4',
    },
    # PATTERN_MISMATCH - lastAttemptAt
    'PATTERN_MISMATCH': {
        'lastAttemptAt': 'timestamp_utc',
    },
}

def find_all_field_locations(field_name):
    """Buscar campo em TODOS os arquivos YAML (não só schemas/)"""
    locations = []
    
    # Buscar em contracts/asyncapi/
    for yaml_file in Path('contracts/asyncapi').rglob('*.yaml'):
        try:
            with open(yaml_file, 'r') as f:
                content = yaml.safe_load(f)
            
            # Buscar recursivamente
            def find_in_dict(d, target_field):
                results = []
                if isinstance(d, dict):
                    if target_field in d:
                        results.append(d[target_field])
                    for value in d.values():
                        results.extend(find_in_dict(value, target_field))
                elif isinstance(d, list):
                    for item in d:
                        results.extend(find_in_dict(item, target_field))
                return results
            
            matches = find_in_dict(content, field_name)
            if matches:
                for match in matches:
                    locations.append({
                        'file': str(yaml_file),
                        'type': match.get('type'),
                        'pattern': match.get('pattern'),
                    })
        except:
            pass
    
    return locations

def apply_remediation_phase(category, fixes_log):
    """Aplicar remediação para cada categoria"""
    
    schema_dir = Path('contracts/asyncapi/components/schemas')
    total_fixes = 0
    files_modified = set()
    
    # Carregar todos os arquivos YAML uma vez
    yaml_files = {}
    for yaml_file in schema_dir.glob('*.yaml'):
        try:
            with open(yaml_file, 'r') as f:
                yaml_files[yaml_file] = yaml.safe_load(f)
        except:
            pass
    
    fields_to_fix = REMEDIATION_MAP[category]
    
    print(f"\n{'='*70}")
    print(f"FASE: {category}")
    print(f"{'='*70}")
    print(f"Campos a corrigir: {len(fields_to_fix)}")
    
    # Processar cada campo
    for field_name, pattern_type in sorted(fields_to_fix.items()):
        expected_pattern = PATTERNS[pattern_type]
        field_fixed_count = 0
        
        # Processar cada arquivo
        for yaml_file, content in yaml_files.items():
            if not content or 'properties' not in content:
                continue
            
            if field_name not in content['properties']:
                continue
            
            field_config = content['properties'][field_name]
            
            # FASE 1: Converter type array → string
            if isinstance(field_config.get('type'), list):
                field_config['type'] = 'string'
                field_fixed_count += 1
                files_modified.add(yaml_file)
                fixes_log.append({
                    'type': 'TYPE_ARRAY_TO_STRING',
                    'file': yaml_file.name,
                    'field': field_name,
                })
            
            # FASE 2: Adicionar padrão se falta
            if field_config.get('type') == 'string' and not field_config.get('pattern'):
                field_config['pattern'] = expected_pattern
                field_fixed_count += 1
                files_modified.add(yaml_file)
                fixes_log.append({
                    'type': 'PATTERN_ADDED',
                    'file': yaml_file.name,
                    'field': field_name,
                    'pattern_type': pattern_type,
                })
            
            # FASE 3: Corrigir padrão se errado
            elif field_config.get('type') == 'string' and field_config.get('pattern') and \
                 field_config.get('pattern') != expected_pattern:
                old_pattern = field_config['pattern']
                field_config['pattern'] = expected_pattern
                field_fixed_count += 1
                files_modified.add(yaml_file)
                fixes_log.append({
                    'type': 'PATTERN_FIXED',
                    'file': yaml_file.name,
                    'field': field_name,
                    'old_pattern': old_pattern[:40],
                    'new_pattern_type': pattern_type,
                })
        
        if field_fixed_count > 0:
            print(f"  ✅ {field_name}: {field_fixed_count} fix(es)")
        else:
            print(f"  ⏭️  {field_name}: 0 fixes (não encontrado em schemas)")
        
        total_fixes += field_fixed_count
    
    # Salvar todos os arquivos modificados
    print(f"\n[WRITE] Salvando {len(files_modified)} arquivos...")
    for yaml_file in sorted(files_modified):
        with open(yaml_file, 'w') as f:
            yaml.dump(yaml_files[yaml_file], f, sort_keys=False, allow_unicode=True, width=120)
    
    print(f"💾 {len(files_modified)} arquivo(s) modificado(s)")
    return total_fixes

def main():
    print("\n" + "="*80)
    print("4C.2.v2b — GLOBAL CANONICALIZATION REMEDIATION")
    print("="*80)
    
    all_fixes = []
    total_fixed = 0
    
    # Processar categorias na ordem de impacto
    for category in ['PATTERN_MISSING_STILL', 'PATTERN_CORRECT_BUT_GATE_FAILS', 'PATTERN_MISMATCH']:
        if category in REMEDIATION_MAP:
            fixed = apply_remediation_phase(category, all_fixes)
            total_fixed += fixed
    
    print(f"\n{'='*70}")
    print(f"RESUMO 4C.2.v2b")
    print(f"{'='*70}")
    print(f"Total de campo(s) corrigido(s): {total_fixed}")
    print(f"Total de arquivo(s) processado(s): {len(set(f['file'] for f in all_fixes))}")
    
    # Estatísticas por tipo
    by_type = defaultdict(int)
    for fix in all_fixes:
        by_type[fix['type']] += 1
    
    print(f"\nPor tipo de correção:")
    for fix_type, count in sorted(by_type.items()):
        print(f"  - {fix_type}: {count}")
    
    # Salvar relatório
    report = {
        'timestamp': Path('_reports/contract_gates/latest.json').stat().st_mtime,
        'category': 'REMEDIATION_4C2_V2B',
        'total_fields_targeted': sum(len(v) for v in REMEDIATION_MAP.values() if v),
        'total_fixes_applied': total_fixed,
        'fixes_detail': all_fixes[:50],  # Primeiros 50 para não ser enorme
    }
    
    with open('_reports/SESSION_4C2V2B_REMEDIATION_LOG.json', 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n📋 Log salvo em: _reports/SESSION_4C2V2B_REMEDIATION_LOG.json")
    print(f"\n✅ 4C.2.v2b REMEDIATION COMPLETE")

if __name__ == '__main__':
    main()
