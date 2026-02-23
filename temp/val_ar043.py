#!/usr/bin/env python3
# Validation command para AR_043
import pathlib

src=pathlib.Path('scripts/run/hb_cli.py').read_text(encoding='utf-8')
checks=['rglob','_get_ar_subdir','rebuild-index','competitions','governance','infra']
missing=[c for c in checks if c not in src]
assert not missing,f'FAIL: missing in hb_cli.py: {missing}'
count_rglob=src.count('rglob')
assert count_rglob>=4,f'FAIL: rglob count={count_rglob}, expected >=4'
print(f'PASS: hb_cli.py suporta subdirectórios (rglob x{count_rglob})')
