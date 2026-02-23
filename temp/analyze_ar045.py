#!/usr/bin/env python3
"""Analyze AR_045 requirements vs current state"""
import shutil  
from pathlib import Path

base = Path('docs/hbtrack/ars')

# Expected by AR_045 validation
governance_expected = 1 + 4 + 20  # AR_006, AR_010-013, AR_016-035
competitions_expected = 11  # AR_001, 002, 008, 009, 036-042
features_expected = 7  # AR_003, 004, 005, 007, 014, 015, 003.5

print('=== AR_045 Validation Expectations ===')
print(f'governance: {governance_expected} files')
print(f'competitions: {competitions_expected} files')
print(f'features: {features_expected} files')
print(f'Total in subdirs: {governance_expected + competitions_expected + features_expected}')
print(f'At top-level: 0 (only _INDEX.md allowed)')

# Current state
gov_count = len(list((base / 'governance').glob('AR_*.md')))
comp_count = len(list((base / 'competitions').glob('AR_*.md')))
feat_count = len(list((base / 'features').glob('AR_*.md')))
top_level = [f.name for f in base.glob('AR_*.md')]

print(f'\n=== Current State ===')
print(f'governance: {gov_count} files (expected {governance_expected})')
print(f'competitions: {comp_count} files (expected {competitions_expected})')
print(f'features: {feat_count} files (expected {features_expected})')
print(f'top-level: {len(top_level)} AR files (need: 0)')

print(f'\n=== Problem ===')
print(f'governance has {gov_count - governance_expected} extra files (should remove 3)')
print(f'features has {feat_count - features_expected} extra files')

# Move AR_002.5_* from features to top-level
print(f'\n=== FIX: Move AR_002.5_* OUT of features to top-level ===')
for f in (base / 'features').glob('AR_002.5_*.md'):
    dest = base / f.name
    print(f'Copying {f.name} to top-level')
    shutil.copy2(f, dest)
    f.unlink()

# Recalculate
feat_count = len(list((base / 'features').glob('AR_*.md')))
print(f'\nfeatures count after removing AR_002.5_*: {feat_count} (expected {features_expected})')

# Get list of files in governance to identify the 3 extra
gov_files = sorted([f.name for f in (base / 'governance').glob('AR_*.md')])
expected_in_gov = ['006', '010', '011', '012', '013', '016', '017', '018', '019', '020',
                  '021', '022', '023', '024', '025', '026', '027', '028', '029', '030', '031', '032', '033', '034', '035']

print(f'\n=== Governance Files Analysis ===')
import re
extra = []
for f in gov_files:
    m = re.search(r'AR_([0-9.]+)', f)
    if m:
        ar_id = m.group(1)
        if ar_id not in expected_in_gov:
            extra.append((ar_id, f))
            print(f'EXTRA: {f}')

print(f'\nFound {len(extra)} extra files in governance (need to remove)')
