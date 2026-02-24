import pathlib, re

ar_dir = pathlib.Path('docs/hbtrack/ars')
files = [f for f in ar_dir.glob('**/*.md') if '_INDEX' not in f.name and re.match(r'AR_[0-9]{3}', f.name)]
ar_ids = set()
for f in files:
    m = re.match(r'AR_([0-9]{3})', f.name)
    if m:
        ar_ids.add(m.group(1))

idx = (ar_dir / '_INDEX.md').read_text(encoding='utf-8')
rows = [l for l in idx.splitlines() if l.startswith('| AR_')]

missing = [i for i in sorted(ar_ids) if f'AR_{i}' not in idx]
extra = [r.split('|')[1].strip()[:6] for r in rows if r.split('|')[1].strip()[:6] not in [f'AR_{i}' for i in ar_ids]]

print(f'Files on disk: {len(ar_ids)} ARs ({sorted(ar_ids)[:5]}...)')
print(f'Rows in _INDEX.md: {len(rows)}')
print(f'Missing from index: {missing}')
print(f'Extra in index (not on disk): {extra[:10]}')
