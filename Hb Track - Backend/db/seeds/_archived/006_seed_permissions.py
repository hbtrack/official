"""
Seed: Permissões do sistema RBAC
População completa das 65 permissões do sistema baseado nos dados de backup
"""
import sys
from pathlib import Path

# Adicionar backend ao path para imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import text
from app.core.db import db_context


def seed_permissions():
    with db_context() as session:
        # Verificar se já existem permissões
        result = session.execute(text("SELECT COUNT(*) FROM permissions"))
        count = result.scalar()

        if count > 0:
            print(f"[SKIP] Permissões já existem ({count} permissões). Pulando seed.")
            return

        # Inserir as 65 permissões do sistema
        permissions_data = [
            # Persons module
            (1, 'persons.create', 'Permite criar registros de pessoa'),
            (2, 'persons.read', 'Permite visualizar dados de pessoa'),
            (3, 'persons.update', 'Permite editar dados de pessoa'),
            (4, 'persons.delete', 'Permite excluir registros de pessoa'),
            (5, 'persons.list', 'Permite listar pessoas da organização'),

            # Athletes module
            (6, 'athletes.create', 'Permite criar registros de atleta'),
            (7, 'athletes.read', 'Permite visualizar dados de atleta'),
            (8, 'athletes.update', 'Permite editar dados de atleta'),
            (9, 'athletes.delete', 'Permite excluir registros de atleta'),
            (10, 'athletes.list', 'Permite listar atletas da organização'),
            (11, 'athletes.medical', 'Permite gerenciar situação médica de atletas'),

            # Teams module
            (12, 'teams.create', 'Permite criar equipes'),
            (13, 'teams.read', 'Permite visualizar dados de equipe'),
            (14, 'teams.update', 'Permite editar dados de equipe'),
            (15, 'teams.delete', 'Permite excluir equipes'),
            (16, 'teams.list', 'Permite listar equipes da organização'),

            # Organizations module
            (17, 'organizations.create', 'Permite criar organizações'),
            (18, 'organizations.read', 'Permite visualizar dados da organização'),
            (19, 'organizations.update', 'Permite editar dados da organização'),
            (20, 'organizations.delete', 'Permite excluir organizações'),
            (21, 'organizations.list', 'Permite listar organizações'),

            # Seasons module
            (22, 'seasons.create', 'Permite criar temporadas'),
            (23, 'seasons.read', 'Permite visualizar dados de temporada'),
            (24, 'seasons.update', 'Permite editar dados de temporada'),
            (25, 'seasons.delete', 'Permite excluir temporadas'),
            (26, 'seasons.list', 'Permite listar temporadas da organização'),

            # Training module
            (27, 'training.create', 'Permite criar sessões de treino'),
            (28, 'training.read', 'Permite visualizar dados de treino'),
            (29, 'training.update', 'Permite editar dados de treino'),
            (30, 'training.delete', 'Permite excluir sessões de treino'),
            (31, 'training.list', 'Permite listar treinos da equipe'),

            # Attendance module
            (32, 'attendance.create', 'Permite registrar presença em treinos'),
            (33, 'attendance.read', 'Permite visualizar registros de presença'),
            (34, 'attendance.update', 'Permite editar registros de presença'),
            (35, 'attendance.delete', 'Permite excluir registros de presença'),
            (36, 'attendance.list', 'Permite listar presenças de treinos/jogos'),

            # Wellness module
            (37, 'wellness.create', 'Permite registrar dados de bem-estar'),
            (38, 'wellness.read', 'Permite visualizar dados de bem-estar'),
            (39, 'wellness.update', 'Permite editar dados de bem-estar'),
            (40, 'wellness.delete', 'Permite excluir registros de bem-estar'),

            # Matches module
            (41, 'matches.create', 'Permite criar jogos/partidas'),
            (42, 'matches.read', 'Permite visualizar dados de jogo'),
            (43, 'matches.update', 'Permite editar dados de jogo'),
            (44, 'matches.delete', 'Permite excluir jogos/partidas'),
            (45, 'matches.list', 'Permite listar jogos da equipe'),

            # Users module
            (46, 'users.create', 'Permite criar usuários'),
            (47, 'users.read', 'Permite visualizar dados de usuário'),
            (48, 'users.update', 'Permite editar dados de usuário'),
            (49, 'users.delete', 'Permite excluir usuários'),
            (50, 'users.list', 'Permite listar usuários'),

            # Org memberships module
            (51, 'org_memberships.create', 'Permite criar vínculos organizacionais'),
            (52, 'org_memberships.read', 'Permite visualizar vínculos organizacionais'),
            (53, 'org_memberships.update', 'Permite editar vínculos organizacionais'),
            (54, 'org_memberships.delete', 'Permite excluir vínculos organizacionais'),

            # Team registrations module
            (55, 'team_registrations.create', 'Permite inscrever atletas em equipes'),
            (56, 'team_registrations.read', 'Permite visualizar inscrições de atletas'),
            (57, 'team_registrations.update', 'Permite editar inscrições de atletas'),
            (58, 'team_registrations.delete', 'Permite cancelar inscrições de atletas'),

            # Reports module
            (59, 'reports.view', 'Permite visualizar relatórios do sistema'),
            (60, 'reports.export', 'Permite exportar relatórios'),

            # Audit logs module
            (61, 'audit_logs.read', 'Permite visualizar logs de auditoria'),

            # Admin module
            (62, 'admin.system_config', 'Permite configurar parâmetros do sistema'),
            (63, 'admin.user_management', 'Permite gerenciar usuários globalmente'),
            (64, 'admin.data_maintenance', 'Permite operações de manutenção de dados'),
            (65, 'admin.backup_restore', 'Permite operações de backup e restore'),
        ]

        # Inserir permissões
        for perm_id, code, description in permissions_data:
            session.execute(text("""
                INSERT INTO permissions (id, code, description)
                VALUES (:id, :code, :description)
            """), {
                'id': perm_id,
                'code': code,
                'description': description
            })

        print(f"[OK] {len(permissions_data)} permissões criadas!")


if __name__ == "__main__":
    seed_permissions()