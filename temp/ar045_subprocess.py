#!/usr/bin/env python3
"""Execute AR_045 report using Python subprocess"""
import subprocess
import sys

# The exact validation command from AR_045
validation_cmd = 'python -c "import pathlib; base=pathlib.Path(\'docs/hbtrack/ars\'); subdirs=[\'governance\',\'competitions\',\'features\']; missing=[d for d in subdirs if not (base/d).is_dir()]; assert not missing,f\'FAIL: missing subdirs {missing}\'; orphans=[f.name for f in base.glob(\'*.md\') if f.name!=\'_INDEX.md\']; assert not orphans,f\'FAIL: MDs at top-level: {orphans}\'; counts={d:len(list((base/d).glob(\'*.md\'))) for d in subdirs}; assert counts[\'governance\']==25,f\'FAIL: governance={counts[chr(103)+chr(111)+chr(118)+chr(101)+chr(114)+chr(110)+chr(97)+chr(110)+chr(99)+chr(101)]}!=25\'; assert counts[\'competitions\']==11,f\'FAIL: competitions={counts[chr(99)+chr(111)+chr(109)+chr(112)+chr(101)+chr(116)+chr(105)+chr(116)+chr(105)+chr(111)+chr(110)+chr(115)]}!=11\'; assert counts[\'features\']==7,f\'FAIL: features!=7\'; print(f\'PASS: ars organized {counts}\')"'

print("Executing: hb report 045")
print(f"Validation command (length {len(validation_cmd)}): ")
print(validation_cmd[:100] + "...")
print()

result = subprocess.run(
    ['python', 'scripts/run/hb_cli.py', 'report', '045', validation_cmd],
    text=True
)

sys.exit(result.returncode)
