#!/usr/bin/env python3
"""
Remediate Bucket 1 patterns with more robust field detection.
v5: Handle various indentations and malformed patterns
"""
import os
import json
import re
from pathlib import Path

# Load canonical patterns
with open(".contract_driven/DOMAIN_AXIOMS.json") as f:
    axioms = json.load(f)["domain_axioms"]["global_formats"]

# Bucket 1 field mapping (pattern type per field)
bucket1_mappings = {
    # Timestamps (15 fields)
    "adjustedAt": "timestamp_utc",
    "captureStartedAt": "timestamp_utc",
    "completedAt": "timestamp_utc",
    "computedAt": "timestamp_utc",
    "correctionAt": "timestamp_utc",
    "createdAt": "timestamp_utc",
    "decidedAt": "timestamp_utc",
    "declaredAt": "timestamp_utc",
    "endedAt": "timestamp_utc",
    "failedAt": "timestamp_utc",
    "nextRetryAt": "timestamp_utc",
    "occurredAt": "timestamp_utc",
    "publishedAt": "timestamp_utc",
    "startedAt": "timestamp_utc",
    "updatedAt": "timestamp_utc",
    
    # UUIDs (12 fields)
    "athleteId": "uuid_v4",
    "coachId": "uuid_v4",
    "conversationId": "uuid_v4",
    "createdByUserId": "uuid_v4",
    "decidedByCoachId": "uuid_v4",
    "generatedSessionId": "uuid_v4",
    "generatedTrainingSessionId": "uuid_v4",
    "matchId": "uuid_v4",
    "organizationId": "uuid_v4",
    "sessionId": "uuid_v4",
    "teamId": "uuid_v4",
    "trainingId": "uuid_v4",
    
    # Dates
    "endDate": "date_only",
    "startDate": "date_only",
    
    # Special
    "traceId": "trace_id",
    "requestId": "request_id",
}

def find_pattern_field(content, field_name, pattern_type):
    """Find field + pattern combination with flexible indentation."""
    # Pattern to match: fieldName: at any indentation, followed by type: string and pattern:
    # This is more flexible with whitespace
    pattern = rf'^(\s*){re.escape(field_name)}:\s*$\n(\s*)type:\s*string\s*$\n\1(\s*)pattern:\s*(.*)$'
    
    matches = list(re.finditer(pattern, content, re.MULTILINE))
    return matches

def replace_in_file(filepath, field_name, pattern_type):
    """Replace pattern for a specific field."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    original = content
    canonical = axioms[pattern_type]["pattern"]
    
    # Strategy: Find line number of field, then replace next pattern: line
    lines = content.split('\n')
    modified = False
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Look for exact field definition (at any indentation)
        if re.match(rf'^\s*{re.escape(field_name)}:\s*$', line):
            # Check next few lines for type: string and pattern:
            j = i + 1
            found_type = False
            while j < min(i + 10, len(lines)):
                if 'type:' in lines[j] and 'string' in lines[j]:
                    found_type = True
                    break
                j += 1
            
            if found_type:
                # Look for pattern: in subsequent lines
                k = j + 1
                while k < min(j + 5, len(lines)):
                    if 'pattern:' in lines[k]:
                        # Get indentation of field and type
                        field_indent = len(line) - len(line.lstrip())
                        pattern_indent = len(lines[k]) - len(lines[k].lstrip())
                        
                        # Replace the pattern line
                        lines[k] = ' ' * pattern_indent + f'pattern: {canonical}'
                        modified = True
                        break
                    k += 1
        i += 1
    
    if modified:
        content = '\n'.join(lines)
        with open(filepath, 'w') as f:
            f.write(content)
        return True
    return False

# Main execution
yaml_files = list(Path("contracts").rglob("*.yaml"))
print(f"📦 Encontrados {len(yaml_files)} arquivos YAML")

total_files = 0
total_patterns = 0
file_changes = []

for field_name, pattern_type in bucket1_mappings.items():
    fixes = 0
    for yaml_file in yaml_files:
        if replace_in_file(str(yaml_file), field_name, pattern_type):
            fixes += 1
            total_files += 1
            file_changes.append((str(yaml_file), field_name))
    
    if fixes > 0:
        total_patterns += fixes
        print(f"  ✅ {field_name}: {fixes} arquivo(s)")

print(f"\n{'='*70}")
print(f"✅ Processados: {len(yaml_files)} | Modificados: {total_files} | Padrões: {total_patterns}")
print(f"{'='*70}")
