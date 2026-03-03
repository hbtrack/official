import re

c = open('docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md', encoding='utf-8', errors='replace').read()

# Get header / version
v = re.search(r'Vers.o:\s*(\S+)', c)
print(f"Version: {v.group(1) if v else 'N/A'}")

# Get §0 summary
sec0 = re.search(r'(## §0.*?)(?=\n## §)', c, re.DOTALL)
if sec0:
    print("\n=== §0 RESUMO EXECUTIVO ===")
    print(sec0.group(1)[:3000])

# Count PASS and PASS-related lines
pass_lines = [l for l in c.splitlines() if '| PASS |' in l or '| PASS|' in l]
print(f"\n\nLINHAS COM PASS: {len(pass_lines)}")
for l in pass_lines:
    print(l[:120])

# Summary of test_result column values
not_run_rows = [l for l in c.splitlines() if '| NOT_RUN |' in l]
print(f"\nNOT_RUN rows (sample 5): {len(not_run_rows)}")

# Check for DONE definition 
done_def = re.search(r'DONE.*?[:=].*?\n', c, re.IGNORECASE)
if done_def:
    print(f"\nDONE: {done_def.group()}")
