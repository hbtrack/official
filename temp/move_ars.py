#!/usr/bin/env python3
"""Move AR files to subdirectories as required by AR_045"""
import subprocess
from pathlib import Path

base = Path('docs/hbtrack/ars')

# AR_045 mappings
moves = {
    'competitions': ['001', '002', '008', '009', '036', '037', '038', '039', '040', '041', '042'],
    'features': ['003', '004', '005', '007', '014', '015', '003.5'],
    'governance': ['006', '010', '011', '012', '013', '016', '017', '018', '019', '020', 
                   '021', '022', '023', '024', '025', '026', '027', '028', '029', '030', '031', '032', '033', '034', '035'],
}

ok = 0
skip = 0

for subdir, ids in moves.items():
    for ar_id in ids:
        pattern = f'AR_{ar_id}_*.md' if ar_id != '003.5' else 'AR_003.5_*.md'
        files = list(base.glob(pattern))
        
        for f in files:
            # Check if file exists
            if not f.exists():
                skip += 1
                continue
                
            # Check if already in subdir
            if f.parent.name == subdir:
                skip += 1
                continue
                
            # Move it
            result = subprocess.run(
                ['git', 'mv', str(f), str(base / subdir / f.name)],
                capture_output=True
            )
            
            if result.returncode == 0:
                ok += 1
                print(f'[OK] {f.name} -> {subdir}/')
            else:
                print(f'[SKIP] {f.name}')
                skip += 1

print(f'Result: Moved={ok}, Skipped={skip}')
