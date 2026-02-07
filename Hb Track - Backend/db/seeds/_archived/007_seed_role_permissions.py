"""
Seed: Mapeamento de permissões por papel (role_permissions)
População completa dos mapeamentos RBAC baseado nos dados de backup
"""
import sys
from pathlib import Path

# Adicionar backend ao path para imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import text
from app.core.db import db_context


def seed_role_permissions():
    with db_context() as session:
        # Verificar se já existem mapeamentos
        result = session.execute(text("SELECT COUNT(*) FROM role_permissions"))
        count = result.scalar()

        if count > 0:
            print(f"[SKIP] Mapeamentos role_permissions já existem ({count} mapeamentos). Pulando seed.")
            return

        # Verificar se roles e permissions existem
        result = session.execute(text("SELECT COUNT(*) FROM roles"))
        roles_count = result.scalar()
        
        result = session.execute(text("SELECT COUNT(*) FROM permissions"))
        permissions_count = result.scalar()

        if roles_count == 0:
            print("[ERROR] Tabela roles está vazia. Execute 001_seed_roles.py primeiro.")
            return

        if permissions_count == 0:
            print("[ERROR] Tabela permissions está vazia. Execute 006_seed_permissions.py primeiro.")
            return

        # Obter IDs dos roles
        result = session.execute(text("SELECT id, code FROM roles"))
        roles = {code: role_id for role_id, code in result.fetchall()}

        print(f"Roles encontrados: {list(roles.keys())}")

        # Mapeamentos baseados na matriz RBAC do backup
        role_permissions_data = [
            # DIRIGENTE (ID=1) - Acesso completo administrativo
            (1, 1), (1, 2), (1, 3), (1, 4), (1, 5),   # persons.*
            (1, 6), (1, 7), (1, 8), (1, 9), (1, 10), (1, 11),  # athletes.*
            (1, 12), (1, 13), (1, 14), (1, 15), (1, 16),  # teams.*
            (1, 17), (1, 18), (1, 19), (1, 20), (1, 21),  # organizations.*
            (1, 22), (1, 23), (1, 24), (1, 25), (1, 26),  # seasons.*
            (1, 27), (1, 28), (1, 29), (1, 30), (1, 31),  # training.*
            (1, 32), (1, 33), (1, 34), (1, 35), (1, 36),  # attendance.*
            (1, 37), (1, 38), (1, 39), (1, 40),           # wellness.*
            (1, 41), (1, 42), (1, 43), (1, 44), (1, 45),  # matches.*
            (1, 46), (1, 47), (1, 48), (1, 49), (1, 50),  # users.*
            (1, 51), (1, 52), (1, 53), (1, 54),           # org_memberships.*
            (1, 55), (1, 56), (1, 57), (1, 58),           # team_registrations.*
            (1, 59), (1, 60),                             # reports.*
            (1, 61),                                      # audit_logs.read

            # COORDENADOR (ID=2) - Gestão técnica e equipes
            (2, 1), (2, 2), (2, 3), (2, 5),              # persons (sem delete)
            (2, 6), (2, 7), (2, 8), (2, 10), (2, 11),     # athletes (sem delete)
            (2, 12), (2, 13), (2, 14), (2, 16),           # teams (sem delete)
            (2, 18), (2, 21),                             # organizations (read only)
            (2, 22), (2, 23), (2, 24), (2, 26),           # seasons (sem delete)
            (2, 27), (2, 28), (2, 29), (2, 31),           # training (sem delete)
            (2, 32), (2, 33), (2, 34), (2, 36),           # attendance (sem delete)
            (2, 37), (2, 38), (2, 39),                    # wellness (sem delete)
            (2, 41), (2, 42), (2, 43), (2, 45),           # matches (sem delete)
            (2, 47), (2, 48),                             # users (read, update only)
            (2, 51), (2, 52), (2, 53),                    # org_memberships (sem delete)
            (2, 55), (2, 56), (2, 57),                    # team_registrations (sem delete)
            (2, 59), (2, 60),                             # reports.*

            # TREINADOR (ID=3) - Gestão de treinos e atletas
            (3, 1), (3, 2), (3, 5),                       # persons (read, create, list)
            (3, 6), (3, 7), (3, 8), (3, 10), (3, 11),     # athletes (sem delete)
            (3, 13), (3, 16),                             # teams (read, list only)
            (3, 18),                                      # organizations (read only)
            (3, 23), (3, 26),                             # seasons (read, list only)
            (3, 27), (3, 28), (3, 29), (3, 31),           # training (CRUD sem delete)
            (3, 32), (3, 33), (3, 34), (3, 36),           # attendance (CRUD sem delete)
            (3, 37), (3, 38), (3, 39),                    # wellness (CRUD sem delete)
            (3, 42), (3, 45),                             # matches (read, list only)
            (3, 47),                                      # users (read only)
            (3, 52),                                      # org_memberships (read only)
            (3, 56),                                      # team_registrations (read only)
            (3, 59),                                      # reports (view only)

            # ATLETA (ID=4) - Acesso aos próprios dados
            (4, 2),                                       # persons (read only)
            (4, 7), (4, 10),                              # athletes (read, list próprios dados)
            (4, 13), (4, 16),                             # teams (read, list próprias equipes)
            (4, 18),                                      # organizations (read only)
            (4, 23), (4, 26),                             # seasons (read, list)
            (4, 28), (4, 31),                             # training (read, list próprios treinos)
            (4, 33), (4, 36),                             # attendance (read próprias presenças)
            (4, 37), (4, 38),                             # wellness (create, read próprios dados)
            (4, 42), (4, 45),                             # matches (read, list próprios jogos)
            (4, 47),                                      # users (read próprios dados)
            (4, 52),                                      # org_memberships (read próprio vínculo)
            (4, 56),                                      # team_registrations (read próprias inscrições)
        ]

        # Inserir mapeamentos usando IDs dos roles
        inserted_count = 0
        for role_code_or_id, permission_id in role_permissions_data:
            # Se role_code_or_id for numérico, assumir que é ID direto
            # Senão, buscar ID pelo código
            if isinstance(role_code_or_id, int):
                role_id = role_code_or_id
            else:
                role_id = roles.get(role_code_or_id)
                if role_id is None:
                    print(f"[WARNING] Role '{role_code_or_id}' não encontrado. Pulando.")
                    continue

            try:
                session.execute(text("""
                    INSERT INTO role_permissions (role_id, permission_id)
                    VALUES (:role_id, :permission_id)
                """), {
                    'role_id': role_id,
                    'permission_id': permission_id
                })
                inserted_count += 1
            except Exception as e:
                print(f"[ERROR] Erro ao inserir role_id={role_id}, permission_id={permission_id}: {e}")

        print(f"[OK] {inserted_count} mapeamentos role_permissions criados!")


if __name__ == "__main__":
    seed_role_permissions()