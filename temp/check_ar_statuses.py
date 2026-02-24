import pathlib, re

ids = ['007','016','020','023','031']
base = pathlib.Path('docs/hbtrack/ars')
for i in ids:
    files = list(base.rglob(f'AR_{i}_*.md'))
    if files:
        content = files[0].read_text(encoding='utf-8')
        m = re.search(r'\*\*Status\*\*: .+', content)
        print(f'AR_{i}: {m.group(0) if m else "NOT FOUND"}')
        print(f'  File: {files[0]}')
