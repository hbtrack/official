# HB_SCRIPT_KIND=OPS
# HB_SCRIPT_SCOPE=infra
# HB_SCRIPT_SIDE_EFFECTS=FS_READ,FS_WRITE
# HB_SCRIPT_IDEMPOTENT=NO
# HB_SCRIPT_ENTRYPOINT=python scripts/ops/infra/list_membro_perms.py
# HB_SCRIPT_OUTPUTS=stdout
"""Listar permissões específicas do role membro."""
import sys
sys.path.insert(0, 'Hb Track - Backend')
from app.core.permissions_map import ROLE_PERMISSIONS

membro_perms = ROLE_PERMISSIONS['membro']
true_perms = [k for k, v in membro_perms.items() if v is True]

print('=' * 70)
print(f'PERMISSÕES DO ROLE "MEMBRO" ({len(true_perms)} habilitadas):')
print('=' * 70)
for i, perm in enumerate(true_perms, 1):
    print(f'{i:2}. {perm}')

