"""
Master script para executar todos os seeds em ordem

Ordem de execução:
1. roles (004 roles básicos)
2. superadmin (usuário admin)
3. organization (organização padrão)
4. positions (posições defensivas e ofensivas)
5. permissions (65 permissões do sistema)
6. role_permissions (144 mapeamentos)
7. schooling_levels (6 níveis de escolaridade)

NOTA: Categories já são inseridas via migration 0009, não via seed.

Este script pode ser executado de forma idempotente - cada seed verifica
se os dados já existem antes de inserir.
"""
import os
import sys
import importlib.util
from pathlib import Path

def load_seed_function(filepath, function_name):
    """Carrega função de seed de um arquivo"""
    spec = importlib.util.spec_from_file_location("seed_module", filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, function_name)

# Carregar funções de seed
seed_dir = Path(__file__).parent
seed_roles = load_seed_function(seed_dir / "001_seed_roles.py", "seed_roles")
seed_superadmin = load_seed_function(seed_dir / "002_seed_superadmin.py", "seed_superadmin")
seed_organization = load_seed_function(seed_dir / "004_seed_organization.py", "seed_organization")
seed_positions = load_seed_function(seed_dir / "005_seed_positions.py", "seed_positions")
seed_permissions = load_seed_function(seed_dir / "006_seed_permissions.py", "seed_permissions")
seed_role_permissions = load_seed_function(seed_dir / "007_seed_role_permissions.py", "seed_role_permissions")
seed_schooling_levels = load_seed_function(seed_dir / "008_seed_schooling_levels.py", "seed_schooling_levels")


def main():
    print("=" * 70)
    print("EXECUTANDO TODOS OS SEEDS")
    print("=" * 70)

    print("\n[1/7] Roles (R4)...")
    try:
        seed_roles()
    except Exception as e:
        print(f"[ERRO] Falha ao executar seed de roles: {e}")
        return 1

    print("\n[2/7] Super Admin (R3, RDB6)...")
    try:
        seed_superadmin()
    except Exception as e:
        print(f"[ERRO] Falha ao executar seed de superadmin: {e}")
        return 1

    print("\n[3/7] Organization (R34)...")
    try:
        seed_organization()
    except Exception as e:
        print(f"[ERRO] Falha ao executar seed de organization: {e}")
        return 1

    print("\n[4/7] Positions (Defensivas e Ofensivas)...")
    try:
        seed_positions()
    except Exception as e:
        print(f"[ERRO] Falha ao executar seed de positions: {e}")
        return 1

    print("\n[5/7] Permissions (65 permissões)...")
    try:
        seed_permissions()
    except Exception as e:
        print(f"[ERRO] Falha ao executar seed de permissions: {e}")
        return 1

    print("\n[6/7] Role Permissions (mapeamentos RBAC)...")
    try:
        seed_role_permissions()
    except Exception as e:
        print(f"[ERRO] Falha ao executar seed de role_permissions: {e}")
        return 1

    print("\n[7/7] Schooling Levels (6 níveis)...")
    try:
        seed_schooling_levels()
    except Exception as e:
        print(f"[ERRO] Falha ao executar seed de schooling_levels: {e}")
        return 1

    print("\n" + "=" * 70)
    print("TODOS OS SEEDS EXECUTADOS COM SUCESSO!")
    print("NOTA: Categories são inseridas via migration 0009, não via seed.")
    print("=" * 70)
    print("[OK] TODOS OS SEEDS EXECUTADOS COM SUCESSO!")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
