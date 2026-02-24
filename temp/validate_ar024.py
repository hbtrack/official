#!/usr/bin/env python3
"""Validation script for AR_024 (superseded version check)."""
import pathlib
import re

df = pathlib.Path('docs/_canon/contratos/Dev Flow.md').read_text(encoding='utf-8')
sp = pathlib.Path('docs/_canon/specs/Hb cli Spec.md').read_text(encoding='utf-8')
tc = pathlib.Path('docs/_canon/contratos/Testador Contract.md').read_text(encoding='utf-8')

df_ver = re.search(r'v(\d+)\.(\d+)\.(\d+)', df)
sp_ver = re.search(r'v(\d+)\.(\d+)\.(\d+)', sp)
tc_ver = re.search(r'v(\d+)\.(\d+)\.(\d+)', tc)

assert df_ver and (int(df_ver.group(1)), int(df_ver.group(2))) >= (1, 1), 'Dev Flow version < 1.1'
assert sp_ver and (int(sp_ver.group(1)), int(sp_ver.group(2))) >= (1, 1), 'Hb cli Spec version < 1.1'
assert tc_ver and (int(tc_ver.group(1)), int(tc_ver.group(2))) >= (1, 1), 'Testador Contract version < 1.1'

print('[PASS] AR_024 objective achieved: docs at version >= 1.1.0 (current: Dev Flow v{}.{}.{}, Hb cli Spec v{}.{}.{}, Testador Contract v{}.{}.{})'.format(
    *df_ver.groups(), *sp_ver.groups(), *tc_ver.groups()
))
