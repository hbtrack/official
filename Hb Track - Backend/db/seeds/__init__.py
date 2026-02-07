"""
Seeds do banco de dados HB Tracking

Ordem de execução:
1. 001_seed_roles.py - Roles (R4)
2. 002_seed_superadmin.py - Super Admin (R3, RDB6)
3. 004_seed_organization.py - Organização inicial (R34)
4. 003_seed_categories.py - Categorias (R15, RDB11)

NOTA: roles e superadmin já são aplicados pela migração inicial.
"""
