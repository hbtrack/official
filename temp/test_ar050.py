import sys
import pathlib
import os

# Mudar para o diretório do backend
os.chdir('Hb Track - Backend')

sys.path.insert(0, '.')
from app.schemas.wellness import WellnessPreBase, WellnessPostBase
import inspect

src = pathlib.Path('app/schemas/wellness.py').read_text(encoding='utf-8')
scale_refs = src.count('0-10') + src.count('ge=0')

assert scale_refs >= 4, f'FAIL: expected >= 4 scale refs (0-10/ge=0), got {scale_refs}'
assert 'ge=1' in src and 'le=5' in src, 'FAIL: sleep_quality 1-5 not found'

print(f'PASS: wellness.py has {scale_refs} scale refs, sleep_quality 1-5 preserved')
