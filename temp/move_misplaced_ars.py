#!/usr/bin/env python3
"""Move misplaced AR files back to top-level for AR_045 validation"""
import shutil
from pathlib import Path

base = Path('docs/hbtrack/ars')

# Move AR_043, 044, 045 out of governance
print("=== Moving AR_043/044/045 out of governance ===")
for ar_num in ['043', '044', '045']:
    for f in (base / 'governance').glob(f'AR_{ar_num}_*.md'):
        dest = base / f.name
        print(f'Moving {f.name}...')
        shutil.move(str(f), str(dest))
        print(f'  -> {dest}')

# Move AR_047-052 out of features
print("\n=== Moving AR_047-052 out of features ===")
for ar_num in ['047', '048', '049', '050', '051', '052']:
    for f in (base / 'features').glob(f'AR_{ar_num}_*.md'):
        dest = base / f.name
        print(f'Moving {f.name}...')
        shutil.move(str(f), str(dest))
        print(f'  -> {dest}')

# Verify final state
print("\n=== Verification ===")
for subdir in ['governance', 'competitions', 'features']:
    path = base / subdir
    count = len(list(path.glob('AR_*.md')))
    print(f'{subdir}: {count} files')

top_level = list(base.glob('AR_*.md'))
print(f'top-level: {len(top_level)} AR files')
print("\nTop-level files:")
for f in sorted([f.name for f in top_level]):
    print(f'  {f}')

print("\n=== Expected by AR_045 ===")
print("governance: 25")
print("competitions: 11")
print("features: 7")
