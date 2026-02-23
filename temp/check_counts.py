#!/usr/bin/env python3
from pathlib import Path

base = Path('docs/hbtrack/ars')
print(f"governance: {len(list((base/'governance').glob('AR_*.md')))} (expected 25)")
print(f"competitions: {len(list((base/'competitions').glob('AR_*.md')))} (expected 11)")
print(f"features: {len(list((base/'features').glob('AR_*.md')))} (expected 7)")
print(f"top-level: {len(list(base.glob('AR_*.md')))} (expected 0)")
print(f"drafts: {len(list((base/'drafts').glob('AR_*.md')))} if exists")

if list(base.glob('AR_*.md')):
    print("\nTop-level AR files:")
    for f in sorted(base.glob('AR_*.md')):
        print(f"  {f.name}")
