"""add RBAC complete system - role membro, 61 permissions, 220 role_permissions, super admin

Revision ID: 0041
Revises: 0040
Create Date: 2026-01-17

SCHEMA CANÔNICO - Baseado em app/core/permissions_map.py (fonte canônica)
Ref: SCHEMA_CANONICO_DATABASE.md - Sistema RBAC completo

IMPORTANTE: Esta migration lê diretamente de permissions_map.py para garantir
que o banco de dados fique sincronizado com o código da aplicação.

Distribuição real (permissions_map.py):
- Total permissions: 61
- Dirigente: 61 permissões TRUE
- Coordenador: 58 permissões TRUE
- Treinador: 46 permissões TRUE
- Atleta: 32 permissões TRUE
- Membro: 23 permissões TRUE
- TOTAL role_permissions: 220
"""
from alembic import op
import sys
from pathlib import Path

# Adicionar path do backend para importar permissions_map
backend_path = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(backend_path))

from app.core.permissions_map import ROLE_PERMISSIONS, get_all_permission_keys


# revision identifiers
revision = '0041'
down_revision = '0040'
branch_labels = None
depends_on = None

# Mapa role_code -> role_id
ROLE_ID_MAP = {
    'dirigente': 1,
    'coordenador': 2,
    'treinador': 3,
    'atleta': 4,
    'membro': 5
}


def upgrade() -> None:
    """Implementar sistema RBAC completo: role membro + 61 permissions + 220 role_permissions + super admin."""
    
    # =========================================================================
    # 1. ROLE MEMBRO (ID 5)
    # =========================================================================
    op.execute("""
        INSERT INTO roles (id, code, name, description, created_at, updated_at) VALUES
        (5, 'membro', 'Membro', 'R5: Membro da organização com acesso limitado', NOW(), NOW())
        ON CONFLICT (id) DO NOTHING;
    """)
    
    # =========================================================================
    # 2. PERMISSIONS (61 registros) - Lido de permissions_map.py
    # =========================================================================
    # Coletar TODAS as permissões únicas de TODAS as roles
    all_permissions_set = set()
    for role_perms in ROLE_PERMISSIONS.values():
        all_permissions_set.update(role_perms.keys())
    
    # Converter para lista ordenada para garantir IDs consistentes
    all_permissions = sorted(list(all_permissions_set))
    
    # Gerar SQL para inserir permissions
    permissions_values = []
    for perm_id, perm_code in enumerate(all_permissions, 1):
        description = perm_code.replace('_', ' ').title()
        permissions_values.append(f"({perm_id}, '{perm_code}', '{description}', NOW(), NOW())")
    
    permissions_sql = f"""
        INSERT INTO permissions (id, code, description, created_at, updated_at)
        VALUES
        {','.join(permissions_values)}
        ON CONFLICT (id) DO NOTHING;
    """
    op.execute(permissions_sql)
    
    # =========================================================================
    # 3. ROLE_PERMISSIONS (220 registros) - Lido de permissions_map.py
    # =========================================================================
    
    # Para cada role, inserir role_permissions baseado em permissions_map.py
    for role_code, role_id in ROLE_ID_MAP.items():
        role_perms = ROLE_PERMISSIONS[role_code]
        
        # Pegar apenas permissões com valor TRUE
        true_perms = [perm_code for perm_code, enabled in role_perms.items() if enabled]
        
        if not true_perms:
            continue
        
        # Construir VALUES para INSERT
        values_list = []
        for perm_code in true_perms:
            # Encontrar permission_id baseado na posição na lista
            perm_id = all_permissions.index(perm_code) + 1
            values_list.append(f"({role_id}, {perm_id})")
        
        role_permissions_sql = f"""
            INSERT INTO role_permissions (role_id, permission_id)
            VALUES
            {','.join(values_list)}
            ON CONFLICT (role_id, permission_id) DO NOTHING;
        """
        op.execute(role_permissions_sql)
    
    # =========================================================================
    # 4. SUPER ADMIN (adm@handballtrack.app / Admin@123!)
    # =========================================================================
    # Password hash para 'Admin@123!' usando bcrypt (gerado e validado 2026-01-17 05:15)
    # Hash gerado e testado com: bcrypt.hashpw(b'Admin@123!', bcrypt.gensalt(rounds=12))
    password_hash = '$2b$12$Cz/JX1ni5W8Bn4owOX8YteF8SXy5rij9SwV5jOUy/vIRcNdfClRua'
    admin_email = 'adm@handballtrack.app'
    
    # Criar pessoa para o super admin
    op.execute(f"""
        INSERT INTO persons (id, full_name, first_name, last_name, created_at, updated_at)
        SELECT 
            '00000000-0000-0000-0000-000000000001'::uuid,
            'Administrador Sistema',
            'Administrador',
            'Sistema',
            NOW(),
            NOW()
        WHERE NOT EXISTS (
            SELECT 1 FROM persons WHERE id = '00000000-0000-0000-0000-000000000001'::uuid
        );
    """)
    
    # Criar usuário super admin vinculado à pessoa
    op.execute(f"""
        INSERT INTO users (id, person_id, email, password_hash, is_superadmin, created_at, updated_at)
        SELECT 
            gen_random_uuid(),
            '00000000-0000-0000-0000-000000000001'::uuid,
            '{admin_email}',
            '{password_hash}',
            TRUE,
            NOW(),
            NOW()
        WHERE NOT EXISTS (
            SELECT 1 FROM users WHERE LOWER(email) = LOWER('{admin_email}')
        );
    """)


def downgrade() -> None:
    """Remover sistema RBAC completo."""
    
    # Remover role_permissions
    op.execute("DELETE FROM role_permissions WHERE role_id IN (1, 2, 3, 4, 5);")
    
    # Remover permissions
    op.execute("DELETE FROM permissions;")
    
    # Remover role membro
    op.execute("DELETE FROM roles WHERE id = 5;")
    
    # Remover super admin user
    op.execute(f"DELETE FROM users WHERE person_id = '00000000-0000-0000-0000-000000000001'::uuid;")
    
    # Remover super admin person
    op.execute(f"DELETE FROM persons WHERE id = '00000000-0000-0000-0000-000000000001'::uuid;")
