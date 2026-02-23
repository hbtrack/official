#!/usr/bin/env python3
"""Organize remaining AR files into appropriate subfolders"""
import shutil
from pathlib import Path
import re

base = Path('docs/hbtrack/ars')

# Map for remaining ARs based on content
moves = {
    # AR_002.5_* - schema related (features)
    'AR_002.5_A': 'features',
    'AR_002.5_B': 'features',
    'AR_002.5_C': 'features',
    'AR_002.5_D': 'features',
    
    # AR_043-046 - governance/infrastructure
    'AR_043': 'governance',
    'AR_044': 'governance',
    'AR_045': 'governance',
    'AR_046': 'governance',
    
    # AR_047-052 - features/invariants
    'AR_047': 'features',
    'AR_048': 'features',
    'AR_049': 'features',
    'AR_050': 'features',
    'AR_051': 'governance',  # hb_cli gates - governance
    'AR_052': 'governance',  # evidence pack validation - governance
    
    # AR_056-063 - stubs (leave at top-level for now)
    # These are placeholder ARs that don't have implementation yet
}

print("=== Moving unorganized ARs ===")
for f in sorted(base.glob('AR_*.md')):
    if f.parent == base:  # Only at top-level
        # Extract AR ID (e.g., AR_002.5_A or AR_043)
        m = re.match(r'AR_([0-9.]+[A-Z]?)', f.name)
        if m:
            ar_id = m.group(1)
            # Check if it's in our moves map
            target_subdir = moves.get(f'AR_{ar_id}')
            if target_subdir:
                dest = base / target_subdir / f.name
                print(f'Moving AR_{ar_id} to {target_subdir}/')
                shutil.move(str(f), str(dest))
            else:
                # Check if it's a stub (AR_056+)
                if int(ar_id.split('.')[0]) >= 56:
                    print(f'Keeping AR_{ar_id} at top-level (stub)')
                else:
                    print(f'Unknown: AR_{ar_id}')

# Check final state
print("\n=== Final State ===")
for subdir in ['governance', 'competitions', 'features']:
    path = base / subdir
    count = len(list(path.glob('AR_*.md')))
    print(f'{subdir}: {count} files')

top_level = list(base.glob('AR_*.md'))
print(f'top-level: {len(top_level)} AR files (stubs)')
