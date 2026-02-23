#!/usr/bin/env python3
"""Move ALL AR files to subdirectories"""
import subprocess
from pathlib import Path

base = Path('docs/hbtrack/ars')

# All AR files to move based on AR_NNN numbers
moves_map = {
    ('001', '002', '008', '009', '036', '037', '038', '039', '040', '041', '042'): 'competitions',
    ('003', '004', '005', '007', '014', '015', '003.5'): 'features',
    ('006', '010', '011', '012', '013', '016', '017', '018', '019', '020', 
     '021', '022', '023', '024', '025', '026', '027', '028', '029', '030', '031', '032', '033', '034', '035'): 'governance',
}

# Build reverse map: AR_ID -> subdir
ar_to_subdir = {}
for ids, subdir in moves_map.items():
    for ar_id in ids:
        ar_to_subdir[ar_id] = subdir

ok = 0
skip = 0

# Get ALL AR_*.md files
for ar_file in base.glob('AR_*.md'):
    if ar_file.name == '' or ar_file.name == '_INDEX.md':
        continue
        
    # Extract AR number (AR_001_...  or AR_003.5_...)
    import re
    m = re.search(r'AR_([0-9.]+)', ar_file.name)
    if not m:
        skip += 1
        continue
        
    ar_id = m.group(1)
    target_subdir = ar_to_subdir.get(ar_id)
    
    if not target_subdir:
        skip += 1
        continue
        
    if ar_file.parent.name == target_subdir:
        skip += 1
        continue
        
    result = subprocess.run(
        ['git', 'mv', str(ar_file), str(base / target_subdir / ar_file.name)],
        capture_output=True
    )
    
    if result.returncode == 0:
        ok += 1
        print(f'[OK] AR_{ar_id} -> {target_subdir}/')
    else:
        print(f'[FAIL] AR_{ar_id}: {result.stderr.decode()}')
        skip += 1

print(f'Total: Moved={ok}, Skipped={skip}')
