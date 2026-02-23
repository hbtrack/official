#!/usr/bin/env python3
"""
AR_045 validation script
Validates docs/hbtrack/ars/ reorganization
"""
import sys
import pathlib

def main():
    base = pathlib.Path('docs/hbtrack/ars')
    subdirs = ['governance', 'competitions', 'features']
    
    # Check subdirs exist
    missing = [d for d in subdirs if not (base/d).is_dir()]
    if missing:
        print(f'FAIL: missing subdirs {missing}')
        return 1
    
    # Check no *.md at top-level except _INDEX.md
    orphans = [f.name for f in base.glob('*.md') if f.name != '_INDEX.md']
    if orphans:
        print(f'FAIL: MDs at top-level: {orphans}')
        return 1
    
    # Count files per subdir
    counts = {d: len(list((base/d).glob('*.md'))) for d in subdirs}
    
    if counts['governance'] != 25:
        print(f'FAIL: governance={counts["governance"]}!=25')
        return 1
    
    if counts['competitions'] != 11:
        print(f'FAIL: competitions={counts["competitions"]}!=11')
        return 1
    
    if counts['features'] != 7:
        print(f'FAIL: features!=7')
        return 1
    
    print(f'PASS: ars organized {counts}')
    return 0

if __name__ == '__main__':
    sys.exit(main())
