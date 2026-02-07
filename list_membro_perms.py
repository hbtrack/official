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
