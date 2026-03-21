#!/usr/bin/env python3
"""
4C.2.v2a REMEDIATION SCRIPT — Phases 1-3

Objetivo: Fix 37 campos fixáveis em 3 fases
  Fase 1: Type Array → Change ['string', 'null'] to 'string' (6 campos)
  Fase 2: Pattern Missing → Add missing patterns (19 campos)
  Fase 3: Pattern Wrong → Fix incorrect patterns (12 campos)

Expected Impact: 249 violations → ~80-120 (~50% reduction)
"""

import json
import yaml
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple

# ============================================================================
# CONFIGURATION
# ============================================================================

PATTERNS = {
    'uuid_v4': r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$',
    'timestamp_utc': r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3,6})?Z$',
    'date_only': r'^\d{4}-\d{2}-\d{2}$'
}

PHASE_1_TYPE_ARRAY = [
    'correlationId', 'lastAttemptAt', 'organizationId', 
    'revokedByUserId', 'targetResourceId', 'trainingSessionId'
]

# Fase 2: Pattern Missing (19 campos)
PHASE_2_BY_TYPE = {
    'uuid_v4': [
        'actorUserId', 'athleteUserId', 'awayTeamId', 'clipId', 'competitionId',
        'deliveryId', 'entryId', 'eventId', 'homeTeamId', 'jobId', 
        'recipientUserId', 'scoutEventId', 'seasonId', 'segmentId', 'userId'
    ],
    'timestamp_utc': ['expiresAt', 'scheduledAt', 'syncCompletedAt'],
    'date_only': ['questionnaireDate']
}

# Fase 3: Pattern Wrong (12 campos)
PHASE_3_FIELDS = {
    'attentionQueueItemId': 'uuid_v4',
    'completionEvidenceId': 'uuid_v4',
    'deliveredAt': 'timestamp_utc',
    'executionRecordId': 'uuid_v4',
    'feedbackThreadId': 'uuid_v4',
    'interventionCycleId': 'uuid_v4',
    'needId': 'uuid_v4',
    'objectiveId': 'uuid_v4',
    'readinessId': 'uuid_v4',
    'recommendationId': 'uuid_v4',
    'requestedAt': 'timestamp_utc',
    'snapshotId': 'uuid_v4'
}

# ============================================================================
# EXECUTION
# ============================================================================

def load_diagnosis() -> Dict:
    """Load structural diagnosis from JSON"""
    with open('_reports/SESSION_4C2_STRUCTURAL_DIAGNOSIS.json', 'r') as f:
        return json.load(f)

def get_schema_files() -> List[Path]:
    """Get all schema YAML files"""
    return list(Path('contracts/asyncapi/components/schemas').glob('*.yaml'))

def process_schemas() -> Tuple[Dict, int, int, int]:
    """
    Process all schemas and apply fixes
    Returns: (modifications, files_modified, total_fixes_applied, violations_fixed)
    """
    diagnosis = load_diagnosis()
    schema_files = get_schema_files()
    
    modifications = defaultdict(list)
    files_modified = set()
    phase_stats = {'phase1': 0, 'phase2': 0, 'phase3': 0}
    
    # Build lookup table: field_name -> file_name -> field_config
    field_locations = defaultdict(dict)
    for yaml_file in schema_files:
        try:
            with open(yaml_file, 'r') as f:
                content = yaml.safe_load(f)
            
            if content and 'properties' in content:
                for field_name, field_config in content['properties'].items():
                    field_locations[field_name][yaml_file.name] = {
                        'config': field_config,
                        'file': yaml_file,
                        'type': field_config.get('type'),
                        'pattern': field_config.get('pattern')
                    }
        except Exception as e:
            print(f"[WARN] Error reading {yaml_file}: {e}")
    
    # ========================================================================
    # PHASE 1: Fix Type Arrays
    # ========================================================================
    print("\n[PHASE 1] Type Array → String Only")
    print("-" * 70)
    
    for field_name in PHASE_1_TYPE_ARRAY:
        if field_name not in field_locations:
            print(f"  ⚠️  {field_name} not found in any schema")
            continue
        
        for yaml_name, loc_info in field_locations[field_name].items():
            field_config = loc_info['config']
            yaml_file = loc_info['file']
            
            if isinstance(field_config.get('type'), list):
                # Change ['string', 'null'] to 'string'
                old_type = field_config['type']
                field_config['type'] = 'string'
                
                modifications[yaml_file.name].append({
                    'field': field_name,
                    'phase': 1,
                    'action': f"Change type from {old_type} to 'string'",
                    'old_value': old_type,
                    'new_value': 'string'
                })
                
                files_modified.add(yaml_file)
                phase_stats['phase1'] += 1
                print(f"  ✅ {field_name:30} in {yaml_name:40} → type='string'")
    
    # ========================================================================
    # PHASE 2: Add Missing Patterns
    # ========================================================================
    print("\n[PHASE 2] Add Missing Patterns")
    print("-" * 70)
    
    for pattern_type, fields in PHASE_2_BY_TYPE.items():
        pattern = PATTERNS[pattern_type]
        
        for field_name in fields:
            if field_name not in field_locations:
                print(f"  ⚠️  {field_name} not found in any schema")
                continue
            
            for yaml_name, loc_info in field_locations[field_name].items():
                field_config = loc_info['config']
                yaml_file = loc_info['file']
                
                if field_config.get('type') == 'string' and 'pattern' not in field_config:
                    field_config['pattern'] = pattern
                    
                    modifications[yaml_file.name].append({
                        'field': field_name,
                        'phase': 2,
                        'action': f"Add {pattern_type} pattern",
                        'pattern_type': pattern_type,
                        'new_pattern': pattern[:60]
                    })
                    
                    files_modified.add(yaml_file)
                    phase_stats['phase2'] += 1
                    print(f"  ✅ {field_name:30} in {yaml_name:40} → pattern added")
    
    # ========================================================================
    # PHASE 3: Fix Wrong Patterns
    # ========================================================================
    print("\n[PHASE 3] Fix Wrong Patterns")
    print("-" * 70)
    
    for field_name, pattern_type in PHASE_3_FIELDS.items():
        pattern = PATTERNS[pattern_type]
        
        if field_name not in field_locations:
            print(f"  ⚠️  {field_name} not found in any schema")
            continue
        
        for yaml_name, loc_info in field_locations[field_name].items():
            field_config = loc_info['config']
            yaml_file = loc_info['file']
            
            if 'pattern' in field_config:
                old_pattern = field_config['pattern']
                if old_pattern != pattern:
                    field_config['pattern'] = pattern
                    
                    modifications[yaml_file.name].append({
                        'field': field_name,
                        'phase': 3,
                        'action': f"Fix pattern: {pattern_type}",
                        'pattern_type': pattern_type,
                        'old_pattern': old_pattern[:60],
                        'new_pattern': pattern[:60]
                    })
                    
                    files_modified.add(yaml_file)
                    phase_stats['phase3'] += 1
                    print(f"  ✅ {field_name:30} in {yaml_name:40} → pattern fixed")
    
    # ========================================================================
    # WRITE BACK
    # ========================================================================
    print("\n[WRITE] Saving modified schemas...")
    print("-" * 70)
    
    for yaml_file in files_modified:
        try:
            with open(yaml_file, 'r') as f:
                content = yaml.safe_load(f)
            
            with open(yaml_file, 'w') as f:
                yaml.dump(content, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            
            print(f"  💾 {yaml_file.name}")
        except Exception as e:
            print(f"  ❌ Error writing {yaml_file}: {e}")
    
    return modifications, len(files_modified), sum(phase_stats.values()), phase_stats

def generate_report(modifications, files_modified, total_fixes, phase_stats):
    """Generate execution report"""
    report = {
        'execution_date': '2026-03-20',
        'session': '4C.2.v2a',
        'phase': 'REMEDIATION_PHASES_1_3',
        'overview': {
            'files_modified': files_modified,
            'total_fixes': total_fixes,
            'phase_1_type_array': phase_stats['phase1'],
            'phase_2_add_pattern': phase_stats['phase2'],
            'phase_3_fix_pattern': phase_stats['phase3']
        },
        'modifications_by_file': dict(modifications),
        'expected_impact': {
            'baseline_violations': 249,
            'expected_after': '80-120',
            'reduction_pct': '50%',
            'rationale': 'Fixes 37 fixable fields in phases 1-3'
        }
    }
    
    with open('_reports/SESSION_4C2V2A_EXECUTION.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    return report

def main():
    print("=" * 70)
    print("4C.2.v2a REMEDIATION — Phases 1-3")
    print("=" * 70)
    
    modifications, files_modified, total_fixes, phase_stats = process_schemas()
    report = generate_report(modifications, files_modified, total_fixes, phase_stats)
    
    print("\n" + "=" * 70)
    print("RESUMO")
    print("=" * 70)
    print(f"\n✅ Fase 1 (Type Array):     {phase_stats['phase1']} campos")
    print(f"✅ Fase 2 (Add Pattern):   {phase_stats['phase2']} campos")
    print(f"✅ Fase 3 (Fix Pattern):   {phase_stats['phase3']} campos")
    print(f"\n📊 Total Fixes: {total_fixes}")
    print(f"📁 Files Modified: {files_modified}")
    print(f"\n💾 Report: _reports/SESSION_4C2V2A_EXECUTION.json")
    print(f"\n🎯 Expected Impact: 249 violations → ~80-120 (50% reduction)")

if __name__ == '__main__':
    main()
