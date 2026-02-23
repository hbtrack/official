#!/usr/bin/env python3
"""Check final AR organization status"""
from pathlib import Path

base = Path('docs/hbtrack/ars')

print("=== Current AR Organization ===")
for subdir in ['governance', 'competitions', 'features']:
    count = len(list((base/subdir).glob('AR_*.md')))
    print(f'{subdir}: {count} files')

orphans = [f.name for f in base.glob('*.md') if f.name != '_INDEX.md']
print(f'\ntop-level orphans: {len(orphans)} files')
if orphans:
    for f in sorted(orphans):
        print(f'  {f}')

print("\n=== Expected by AR_045 ===")
print("governance: 25")
print("competitions: 11")
print("features: 7")
print("top-level: 0 (only _INDEX.md)")

gov = len(list((base/'governance').glob('AR_*.md')))
comp = len(list((base/'competitions').glob('AR_*.md')))
feat = len(list((base/'features').glob('AR_*.md')))

if gov == 25 and comp == 11 and feat == 7 and not orphans:
    print("\n✅ PASS: Organization meets AR_045 requirements!")
else:
    print("\n❌ FAIL: Organization does not meet requirements")
    if gov != 25:
        print(f"  - governance: {gov} vs 25 expected")
    if comp != 11:
        print(f"  - competitions: {comp} vs 11 expected")
    if feat != 7:
        print(f"  - features: {feat} vs 7 expected")
    if orphans:
        print(f"  - {len(orphans)} orphan files at top-level")
