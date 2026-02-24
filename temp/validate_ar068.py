"""Validate AR_068: persons.birth_date NOT NULL + triggers (file-based)."""
import pathlib

# Check migration 0053 exists
v = pathlib.Path('Hb Track - Backend/db/alembic/versions')
migs = [f for f in v.iterdir() if '0053' in f.name and f.suffix == '.py']
assert migs, f'FAIL: migration 0053 nao encontrada em {list(v.iterdir())}'

src = migs[0].read_text(encoding='utf-8')
assert 'fn_sync_birth_date_athletes_to_persons' in src, 'FAIL: sync trigger function ausente'
assert 'fn_validate_birth_date_parity_on_person' in src, 'FAIL: parity trigger function ausente'
assert 'trg_validate_birth_date_persons' in src, 'FAIL: validate trigger ausente'
assert 'nullable=False' in src, 'FAIL: NOT NULL constraint ausente na migration'

# Check model person.py
m = pathlib.Path('Hb Track - Backend/app/models/person.py').read_text(encoding='utf-8')
assert 'nullable=False' in m and 'birth_date' in m, 'FAIL: person.py nao tem birth_date nullable=False'

print('PASS AR_068: persons.birth_date NOT NULL + triggers verificados')
