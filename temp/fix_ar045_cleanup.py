#!/usr/bin/env python3
"""Fix AR_045 folder organization"""
import subprocess
from pathlib import Path
import re

base = Path('docs/hbtrack/ars')

# Step 1: Move AR_002.5_* out of features (they don't belong in the 7-count)
# They might go to top-level temporarily or to a separate folder
print("=== Step 1: Handle AR_002.5_* files ===")
ar_002_5_files = list(base.glob('AR_002.5_*.md'))
print(f"Found {len(ar_002_5_files)} AR_002.5_* files in top-level")
for f in ar_002_5_files:
    print(f"  {f.name}")

# Step 2: Move extra ARs out of governance (AR_043, 044, 045 shouldn't be there)
print("\n=== Step 2: Remove AR_043/044/045 from governance ===")
gov_path = base / 'governance'
for ar_num in ['043', '044', '045']:
    for f in gov_path.glob(f'AR_{ar_num}_*.md'):
        # Move back to top-level
        dest = base / f.name
        result = subprocess.run(['git', 'mv', str(f), str(dest)], capture_output=True)
        if result.returncode == 0:
            print(f"[OK] Moved {f.name} back to top-level")
        else:
            print(f"[FAIL] {f.name}: {result.stderr.decode()}")

# Step 3: Verify final counts
print("\n=== Final Status ===")
for subdir in ['governance', 'competitions', 'features']:
    path = base / subdir
    if path.exists():
        count = len(list(path.glob('AR_*.md')))
        print(f'{subdir}: {count} files')

top_level = sorted([f.name for f in base.glob('AR_*.md') if f.is_file()])
print(f'top-level: {len(top_level)} AR files')
for f in top_level[:10]:
    print(f'  {f}')
if len(top_level) > 10:
    print(f'  ... and {len(top_level)-10} more')
