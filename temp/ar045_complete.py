#!/usr/bin/env python3
"""Execute AR_045 final validation and report"""
import subprocess
import pathlib

print("=== AR_045 Final Execution ===\n")

# Step 1: rebuild-index
print("Step 1: Rebuilding AR index...")
result = subprocess.run(
    ['python', 'scripts/run/hb_cli.py', 'rebuild-index'],
    capture_output=True,
    text=True
)
print(result.stdout if result.returncode == 0 else result.stderr)

# Step 2: Verify the 43 AR files are in correct subdirs
print("\nStep 2: Verifying AR organization...")
base = pathlib.Path('docs/hbtrack/ars')

subdirs = ['governance', 'competitions', 'features']
missing = [d for d in subdirs if not (base/d).is_dir()]
assert not missing, f'FAIL: missing subdirs {missing}'
print("✓ All subdirs exist")

orphans = [f.name for f in base.glob('*.md') if f.name != '_INDEX.md']
assert not orphans, f'FAIL: {len(orphans)} MDs at top-level: {orphans}'
print("✓ No orphans at top-level")

counts = {d: len(list((base/d).glob('*.md'))) for d in subdirs}
for subdir in subdirs:
    expected_map = {'governance': 25, 'competitions': 11, 'features': 7}
    expected = expected_map[subdir]
    actual = counts[subdir]
    status = "✓" if actual == expected else "✗"
    print(f"{status} {subdir}: {actual}/{expected}")

assert counts['governance'] == 25, f"governance count mismatch"
assert counts['competitions'] == 11, f"competitions count mismatch"
assert counts['features'] == 7, f"features count mismatch"

print(f"\n✅ VALIDATION PASSED: ars organized correctly")
print(f"   PASS: ars organized {counts}")

# Step 3: Execute hb report 045
print("\nStep 3: Running hb report 045...")
validation_cmd = f'python -c "import pathlib; base=pathlib.Path(\'docs/hbtrack/ars\'); subdirs=[\'governance\',\'competitions\',\'features\']; missing=[d for d in subdirs if not (base/d).is_dir()]; assert not missing,f\'FAIL: missing subdirs {{missing}}\'; orphans=[f.name for f in base.glob(\'*.md\') if f.name!=\'_INDEX.md\']; assert not orphans,f\'FAIL: MDs at top-level: {{orphans}}\'; counts={{d:len(list((base/d).glob(\'*.md\'))) for d in subdirs}}; assert counts[\'governance\']==25,f\'FAIL: governance={{counts[\'governance\']}}!=25\'; assert counts[\'competitions\']==11,f\'FAIL: competitions={{counts[\'competitions\']}}!=11\'; assert counts[\'features\']==7,f\'FAIL: features!=7\'; print(f\'PASS: ars organized {{counts}}\')"'

result = subprocess.run(
    ['python', 'scripts/run/hb_cli.py', 'report', '045', validation_cmd],
    capture_output=True,
    text=True,
    timeout=30
)

print(f"Exit Code: {result.returncode}")
if result.stdout:
    print(f"Output:\n{result.stdout}")
if result.stderr:
    print(f"Errors:\n{result.stderr}")

if result.returncode == 0:
    print("\n✅ AR_045 COMPLETED SUCCESSFULLY")
else:
    print("\n❌ AR_045 FAILED - Check evidence log")

import sys
sys.exit(result.returncode)
