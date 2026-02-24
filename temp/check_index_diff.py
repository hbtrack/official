import pathlib, re

ar_dir = pathlib.Path('docs/hbtrack/ars')
idx_path = pathlib.Path('docs/hbtrack/_INDEX.md')

files = [f for f in ar_dir.rglob('AR_*.md') if '_INDEX' not in f.name]
ar_ids = set()
for f in files:
    m = re.match(r'AR_([0-9]{3})', f.name)
    if m:
        ar_ids.add(m.group(1))

idx = idx_path.read_text(encoding='utf-8')
rows = [l for l in idx.splitlines() if l.startswith('| AR_')]
row_ids = set()
for r in rows:
    m = re.match(r'\| AR_([0-9]+)', r)
    if m:
        row_ids.add(m.group(1))

print('In index but not on disk:', sorted(row_ids - ar_ids))
print('On disk but not in index:', sorted(ar_ids - row_ids))
print(f'Disk: {len(ar_ids)} | Index rows: {len(row_ids)}')
