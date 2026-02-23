#!/usr/bin/env python3
"""Check AR organization for AR_045"""
import pathlib
import re

base = pathlib.Path('docs/hbtrack/ars')

# Check all subdirs and their counts
print("=== Subdir Status ===")
for subdir in ['governance', 'competitions', 'features']:
    path = base / subdir
    if path.exists():
        files = list(path.glob('AR_*.md'))
        print(f'{subdir}: {len(files)} files')
        if len(files) <= 5:
            for f in sorted(files):
                print(f'  - {f.name}')
    else:
        print(f'{subdir}: does not exist')

# Check top-level (should be 0 except for _INDEX.md)
print("\n=== Top-level AR Files (should be empty) ===")
top_level = sorted([f.name for f in base.glob('AR_*.md') if f.is_file()])
print(f'Count: {len(top_level)} AR files\n')

if top_level:
    for f in top_level:
        # Extract AR number
        m = re.search(r'AR_([0-9.]+)', f)
        if m:
            ar_id = m.group(1)
            # Determine where it should go
            if ar_id in ('001', '002', '008', '009', '036', '037', '038', '039', '040', '041', '042'):
                dest = 'competitions'
            elif ar_id in ('003', '004', '005', '007', '014', '015', '003.5') or ar_id.startswith('002.5'):
                dest = 'features'
            elif ar_id in ('006', '010', '011', '012', '013', '016', '017', '018', '019', '020',
                          '021', '022', '023', '024', '025', '026', '027', '028', '029', '030', '031', '032', '033', '034', '035'):
                dest = 'governance'
            else:
                dest = '???'
            print(f'  {f} -> {dest}/')

# Expected final counts
print("\n=== Expected Final Counts ===")
print("governance: 25")
print("competitions: 11")
print("features: 11 (7 + 4 for AR_002.5_*)")
print("Total: 47 AR files in subdirs")
