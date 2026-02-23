#!/usr/bin/env python3
"""Direct validation of AR_045 requirements"""
import pathlib

base = pathlib.Path('docs/hbtrack/ars')

# Validation criteria from AR_045
subdirs = ['governance', 'competitions', 'features']

# Check 1: All subdirs exist
missing = [d for d in subdirs if not (base/d).is_dir()]
assert not missing, f'FAIL: missing subdirs {missing}'
print("✓ All required subdirs exist")

# Check 2: No orphan .md files at top-level (except _INDEX.md)
orphans = [f.name for f in base.glob('*.md') if f.name != '_INDEX.md']
if orphans:
    print(f"FAIL: MDs at top-level: {orphans}")
    print(f"Count: {len(orphans)}")
    assert not orphans
else:
    print("✓ No orphan .md files at top-level")

# Check 3: File counts match expectations
counts = {d: len(list((base/d).glob('*.md'))) for d in subdirs}
for subdir, expected in [('governance', 25), ('competitions', 11), ('features', 7)]:
    actual = counts[subdir]
    match = "✓" if actual == expected else "✗"
    print(f"{match} {subdir}: {actual} (expected {expected})")
    if actual != expected:
        # List the files
        files = sorted([f.name for f in (base/subdir).glob('AR_*.md')])
        for f in files[:5]:
            print(f"    {f}")
        if len(files) > 5:
            print(f"    ... and {len(files)-5} more")

assert counts['governance'] == 25, f"FAIL: governance count {counts['governance']} != 25"
assert counts['competitions'] == 11, f"FAIL: competitions count {counts['competitions']} != 11"
assert counts['features'] == 7, f"FAIL: features count {counts['features']} != 7"

print(f"\n✅ PASS: ars organized correctly")
print(f"   governance: {counts['governance']}")
print(f"   competitions: {counts['competitions']}")
print(f"   features: {counts['features']}")
print(f"   Total feature ARs: {sum(counts.values())}")
