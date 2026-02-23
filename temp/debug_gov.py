#!/usr/bin/env python3
from pathlib import Path
import re

base = Path('docs/hbtrack/ars')

# Check all counts 
gov = len(list((base/'governance').glob('AR_*.md')))
comp = len(list((base/'competitions').glob('AR_*.md')))
feat = len(list((base/'features').glob('AR_*.md')))
top = len(list(base.glob('AR_*.md')))

print(f"governance: {gov} (expected 25, diff: {gov-25})")
print(f"competitions: {comp} (expected 11, diff: {comp-11})")
print(f"features: {feat} (expected 7, diff: {feat-7})")
print(f"top-level: {top} (expected 0)")

if gov > 25:
    print(f"\nToo many in governance ({gov}), checking extras...")
    gov_files = sorted([f.name for f in (base/'governance').glob('AR_*.md')])
    expected_ar_ids = [6, 10, 11, 12, 13, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35]
    for f in gov_files:
        m = re.search(r'AR_([0-9]+)', f)
        if m:
            ar_id = int(m.group(1))
            if ar_id not in expected_ar_ids:
                print(f"  EXTRA: AR_{ar_id}: {f}")
