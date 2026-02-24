#!/usr/bin/env python3
import os
import re
from pathlib import Path
import sys

# Get INDEX content
index_path = Path('docs/hbtrack/_INDEX.md')
index_content = index_path.read_text(encoding='utf-8')

# Extract INDEX status mappings
index_status = {}
for line in index_content.split('\n')[7:]:  # Skip header
    if line.strip().startswith('|') and 'AR_' in line:
        parts = [p.strip() for p in line.split('|')]
        if len(parts) >= 4:
            ar_id = parts[1].strip()
            status = parts[3].strip()
            if ar_id and status:
                index_status[ar_id] = status

# Get all AR files
ar_files = list(Path('docs/hbtrack/ars').rglob('AR_*.md'))

# Check for discrepancies
print("🔍 VERIFICANDO DESINCRONIZAÇÕES...\n")
desync_list = []

for ar_file in sorted(ar_files):
    content = ar_file.read_text(encoding='utf-8')
    
    # Extract AR_ID
    match = re.search(r'# AR_(\d+(?:\.\d+)?[A-Z]?)\s*[—\-]', content)
    if match:
        ar_id = 'AR_' + match.group(1)
        
        # Find status in file
        status_match = re.search(r'\*\*Status\*\*:\s*([^\n]+)', content)
        if status_match:
            file_status = status_match.group(1).strip()
            
            # Compare with INDEX
            if ar_id in index_status:
                index_st = index_status[ar_id]
                if file_status != index_st:
                    desync_list.append((ar_id, file_status, index_st, ar_file.name))

# Print results
if desync_list:
    print(f"❌ ENCONTRADOS {len(desync_list)} DESINCRONIZADOS:\n")
    print(f"{'AR_ID':<10} | {'Status no Arquivo':<35} | {'Status no INDEX':<35} | {'Arquivo'}")
    print("-" * 120)
    for ar_id, file_st, index_st, filename in desync_list:
        print(f"{ar_id:<10} | {file_st:<35s} | {index_st:<35s} | {filename[:40]}")
    sys.exit(1)
else:
    print("✅ TODOS OS STATUSES SINCRONIZADOS!")
    sys.exit(0)
