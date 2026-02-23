#!/usr/bin/env python3
import yaml
from pathlib import Path

index_path = Path('docs/_INDEX.yaml')
if not index_path.exists():
    print('_INDEX.yaml not found')
    exit(1)

with open(index_path, encoding='utf-8') as f:
    data = yaml.safe_load(f)

# Find PENDENTE ARs
pendente = []
for ar in data.get('ars', []):
    status = ar.get('status', '').upper()
    if 'PENDENTE' in status or status == 'DRAFT':
        pendente.append((ar.get('id'), ar.get('title'), status))

print(f'Found {len(pendente)} PENDENTE ARs:\n')
for ar_id, title, status in sorted(pendente)[:30]:
    print(f'AR_{ar_id}: {status}')
    if title:
        print(f'  {title[:70]}')
    print()
