#!/usr/bin/env python3
import pathlib

base = pathlib.Path('docs/hbtrack/ars')
subdirs = ['governance', 'competitions', 'features']

# Check subdirs exist
missing = [d for d in subdirs if not (base/d).is_dir()]
assert not missing, f'FAIL: missing subdirs {missing}'

# Check no *.md at top-level except _INDEX.md
orphans = [f.name for f in base.glob('*.md') if f.name != '_INDEX.md']
assert not orphans, f'FAIL: MDs at top-level: {orphans}'

# Count files per subdir
counts = {d: len(list((base/d).glob('*.md'))) for d in subdirs}
assert counts['governance'] == 25, f'FAIL: governance={counts["governance"]}!=25'
assert counts['competitions'] == 11, f'FAIL: competitions={counts["competitions"]}!=11'
assert counts['features'] == 7, f'FAIL: features!=7'

print(f'PASS: ars organized {counts}')
