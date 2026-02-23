#!/usr/bin/env python3
"""Move procedure and extra ARs out of governance/features for AR_045 validation"""
import shutil
from pathlib import Path
import re

base = Path('docs/hbtrack/ars')

# ARs that should NOT be in governance during AR_045 validation
# These are newer procedure ARs or extras that don't fit in the original scope
ars_to_move_out = {
    'governance': ['043', '044', '045', '046', '051', '052', '054', '055', '064'],
}

print("=== Moving ARs out of subdirs ===")
for subdir, ar_ids in ars_to_move_out.items():
    subdir_path = base / subdir
    for ar_id in ar_ids:
        for f in subdir_path.glob(f'AR_{ar_id}_*.md'):
            dest = base / f.name
            print(f'Moving {f.name} out of {subdir}/')
            shutil.move(str(f), str(dest))

# Also check features for AR_002 and other non-original-7 files
features_path = base / 'features'
for f in features_path.glob('AR_*.md'):
    # Original features ARs are: 003, 004, 005, 007, 014, 015, 003.5, 002.5_A/B/C/D
    m = re.search(r'AR_([0-9.]+)', f.name)
    if m:
        ar_id = m.group(1)
        # Expected features: 003, 004, 005, 007, 014, 015, 003.5, 002.5_*
        expected = ['003', '004', '005', '007', '014', '015', '003.5',
                   '002.5', '002.5_A', '002.5_B', '002.5_C', '002.5_D']
        if not any(ar_id.startswith(e) for e in expected):
            # Move out
            dest = base / f.name
            print(f'Moving {f.name} out of features/')
            shutil.move(str(f), str(dest))

# Verify
print("\n=== Final Counts ===")
for subdir in ['governance', 'competitions', 'features']:
    count = len(list((base/subdir).glob('AR_*.md')))
    print(f'{subdir}: {count}')

orphans = sorted([f.name for f in base.glob('AR_*.md')])
print(f'top-level: {len(orphans)} AR files')
