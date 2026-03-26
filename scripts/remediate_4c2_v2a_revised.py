#!/usr/bin/env python3
"""
4C.2.v2a REMEDIATION (REVISED) — Phases 1-3

Corrigido: YAML dump now preserves structure properly
"""

import json
import yaml
from pathlib import Path
from collections import defaultdict

PATTERNS = {
    'uuid_v4': r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$',
    'timestamp_utc': r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3,6})?Z$',
    'date_only': r'^\d{4}-\d{2}-\d{2}$'
}

PHASE_1 = ['correlationId', 'lastAttemptAt', 'organizationId', 'revokedByUserId', 'targetResourceId', 'trainingSessionId']

PHASE_2 = {
    'uuid_v4': ['actorUserId', 'athleteUserId', 'awayTeamId', 'clipId', 'competitionId', 'deliveryId', 'entryId', 'eventId', 'homeTeamId', 'jobId', 'recipientUserId', 'scoutEventId', 'seasonId', 'segmentId', 'userId'],
    'timestamp_utc': ['expiresAt', 'scheduledAt', 'syncCompletedAt'],
    'date_only': ['questionnaireDate']
}

PHASE_3 = {
    'attentionQueueItemId': 'uuid_v4', 'completionEvidenceId': 'uuid_v4', 'deliveredAt': 'timestamp_utc', 'executionRecordId': 'uuid_v4',
    'feedbackThreadId': 'uuid_v4', 'interventionCycleId': 'uuid_v4', 'needId': 'uuid_v4', 'objectiveId': 'uuid_v4',
    'readinessId': 'uuid_v4', 'recommendationId': 'uuid_v4', 'requestedAt': 'timestamp_utc', 'snapshotId': 'uuid_v4'
}

def process_all_schemas():
    """Process all schema files and apply fixes inline"""
    
    schema_files = list(Path('contracts/asyncapi/components/schemas').glob('*.yaml'))
    phase_stats = {'phase1': 0, 'phase2': 0, 'phase3': 0}
    files_modified = set()
    modifications = defaultdict(list)
    
    # Build field catalog
    field_to_files = defaultdict(list)
    for f in schema_files:
        try:
            with open(f, 'r') as fp:
                content = yaml.safe_load(fp)
            if content and 'properties' in content:
                for field_name in content['properties'].keys():
                    field_to_files[field_name].append(f)
        except:
            pass
    
    print("=" * 70)
    print("4C.2.v2a REMEDIATION (REVISED)")
    print("=" * 70)
    
    # Process each schema file
    for schema_file in schema_files:
        try:
            with open(schema_file, 'r') as f:
                lines = f.readlines()
            
            # Parse YAML
            with open(schema_file, 'r') as f:
                content = yaml.safe_load(f)
            
            if not content or 'properties' not in content:
                continue
            
            modified = False
            
            # FASE 1: Type Array → String
            for field_name in PHASE_1:
                if field_name in content['properties']:
                    field = content['properties'][field_name]
                    if isinstance(field.get('type'), list):
                        field['type'] = 'string'
                        modifications[schema_file.name].append({'phase': 1, 'field': field_name})
                        phase_stats['phase1'] += 1
                        modified = True
                        print(f"  [P1] {schema_file.name}: {field_name} → type='string'")
            
            # FASE 2: Add Pattern
            for ptype, fields in PHASE_2.items():
                pattern = PATTERNS[ptype]
                for field_name in fields:
                    if field_name in content['properties']:
                        field = content['properties'][field_name]
                        if field.get('type') == 'string' and 'pattern' not in field:
                            field['pattern'] = pattern
                            modifications[schema_file.name].append({'phase': 2, 'field': field_name, 'ptype': ptype})
                            phase_stats['phase2'] += 1
                            modified = True
                            print(f"  [P2] {schema_file.name}: {field_name} → pattern added")
            
            # FASE 3: Fix Pattern
            for field_name, ptype in PHASE_3.items():
                if field_name in content['properties']:
                    field = content['properties'][field_name]
                    new_pattern = PATTERNS[ptype]
                    if 'pattern' in field and field['pattern'] != new_pattern:
                        field['pattern'] = new_pattern
                        modifications[schema_file.name].append({'phase': 3, 'field': field_name})
                        phase_stats['phase3'] += 1
                        modified = True
                        print(f"  [P3] {schema_file.name}: {field_name} → pattern fixed")
            
            # Write back if modified
            if modified:
                with open(schema_file, 'w') as f:
                    yaml.dump(content, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=1000)
                files_modified.add(schema_file.name)
        
        except Exception as e:
            print(f"  ❌ Error in {schema_file}: {e}")
    
    # Report
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"✅ Phase 1 (Type Array→String):  {phase_stats['phase1']} fixes")
    print(f"✅ Phase 2 (Add Pattern):        {phase_stats['phase2']} fixes")
    print(f"✅ Phase 3 (Fix Pattern):        {phase_stats['phase3']} fixes")
    print(f"\n📊 Total Fixes:   {sum(phase_stats.values())}")
    print(f"📁 Files Modified: {len(files_modified)}")
    
    # Save report
    report = {
        'session': '4C.2.v2a',
        'status': 'EXECUTION_REVISED',
        'phase_1': phase_stats['phase1'],
        'phase_2': phase_stats['phase2'],
        'phase_3': phase_stats['phase3'],
        'total_fixes': sum(phase_stats.values()),
        'files_modified': len(files_modified),
        'modifications': dict(modifications)
    }
    
    with open('_reports/SESSION_4C2V2A_EXECUTION_REVISED.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n💾 Report: _reports/SESSION_4C2V2A_EXECUTION_REVISED.json")

if __name__ == '__main__':
    process_all_schemas()

