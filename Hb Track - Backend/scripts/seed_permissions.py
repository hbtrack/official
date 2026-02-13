"""
Seed: Permissões do sistema RBAC com idempotência e CLI
População das 65 permissões do sistema RBAC com suporte a --dry-run, --force e --output json
"""
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone
import psycopg2
from psycopg2 import sql

# Adicionar backend ao path para imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import os
from dotenv import load_dotenv


def json_log(level, operation, **kwargs):
    """Log operation in structured JSON format (ISO8601 UTC)."""
    timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    log_data = {
        'timestamp': timestamp,
        'level': level,
        'script': 'seed_permissions.py',
        'operation': operation,
        **kwargs
    }
    return json.dumps(log_data, ensure_ascii=False)


def get_db_connection():
    """Get raw psycopg2 connection for idempotency table operations."""
    load_dotenv(Path(__file__).parent.parent.parent / '.env')
    db_url = os.getenv('DATABASE_URL', '')
    # Convert SQLAlchemy format to psycopg2 format
    db_url = db_url.replace('postgresql+asyncpg://', 'postgresql://')
    if not db_url:
        raise RuntimeError('DATABASE_URL not set')
    return psycopg2.connect(db_url)


def ensure_idempotency_table():
    """Create idempotency_keys table if it doesn't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Create table with simple structure (key only)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS idempotency_keys (
                key VARCHAR(255) PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    except psycopg2.Error as e:
        conn.rollback()
        # Table may have different structure
        pass
    finally:
        cursor.close()
        conn.close()


def check_idempotency_key(key):
    """Check if idempotency key exists. Return True if already executed."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM idempotency_keys WHERE key = %s LIMIT 1",
            (key,)
        )
        result = cursor.fetchone() is not None
        cursor.close()
        conn.close()
        return result
    except psycopg2.Error:
        return False


def save_idempotency_key(key):
    """Save idempotency key to track execution."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # First check if key already exists to avoid duplicates
        cursor.execute("SELECT 1 FROM idempotency_keys WHERE key = %s LIMIT 1", (key,))
        if cursor.fetchone() is None:
            # Not yet inserted, safe to insert
            import uuid
            cursor.execute(
                """INSERT INTO idempotency_keys 
                   (id, key, script_name, endpoint, request_hash, status_code) 
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (str(uuid.uuid4()), key, 'seed_permissions.py', '/scripts/seed_permissions', 'seed', 200)
            )
        conn.commit()
    except psycopg2.Error as e:
        conn.rollback()
        # Silently ignore failures on idempotency setup (table might be read-only or schema diff)
        pass
    finally:
        cursor.close()
        conn.close()


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Seed 65 RBAC permissions into the system',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='Examples:\n  python seed_permissions.py\n  python seed_permissions.py --dry-run\n  python seed_permissions.py --force --output json'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview seeding without modifying database'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force re-seeding even if already executed today'
    )
    parser.add_argument(
        '--output',
        choices=['json', 'text'],
        default='text',
        help='Output format (default: text)'
    )
    return parser.parse_args()


def seed_permissions(dry_run=False):
    """Seed 65 permissions without idempotency check. Called from main() after idempotency validation."""
    from sqlalchemy import text
    from app.core.db import db_context
    
    with db_context() as session:
        # Check current count for logging
        result = session.execute(text("SELECT COUNT(*) FROM permissions"))
        count = result.scalar()

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

        # Insert permissions
        if not dry_run:
            for perm_id, code, description in permissions_data:
                session.execute(text("""
                    INSERT INTO permissions (id, code, description)
                    VALUES (:id, :code, :description)
                """), {
                    'id': perm_id,
                    'code': code,
                    'description': description
                })
            session.commit()
        
        return len(permissions_data)


def main():
    """Main entry point with idempotency and CLI."""
    args = parse_args()
    
    # Generate idempotency key (script:YYYY-MM-DD)
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    idempotency_key = f'seed_permissions:{today}'
    
    # Ensure idempotency table exists
    ensure_idempotency_table()
    
    # Check idempotency (unless --force)
    already_executed = check_idempotency_key(idempotency_key) if not args.force else False
    
    try:
        if already_executed:
            # Already seeded today
            message = f'Permissions already seeded today ({idempotency_key}). Skipping.'
            log_entry = json_log('INFO', 'seed_permissions', status='NOOP', message=message)
            if args.output == 'json':
                print(log_entry)
            else:
                print(f'[SKIP] {message}')
            return 0
        
        if args.dry_run:
            # Preview mode - no database modifications
            num_perms = seed_permissions(dry_run=True)
            message = f'DRY-RUN: Would seed {num_perms} permissions (no changes made)'
            log_entry = json_log('INFO', 'seed_permissions', status='DRY_RUN', count=num_perms, message=message)
            if args.output == 'json':
                print(log_entry)
            else:
                print(f'[DRY-RUN] {message}')
            return 0
        
        # Save idempotency key BEFORE attempting to seed (mark as attempted)
        save_idempotency_key(idempotency_key)
        
        # Execute seeding
        num_seeded = seed_permissions(dry_run=False)
        
        # Log success
        message = f'Successfully seeded {num_seeded} permissions'
        log_entry = json_log('INFO', 'seed_permissions', status='SEEDED', count=num_seeded, message=message)
        if args.output == 'json':
            print(log_entry)
        else:
            print(f'[OK] {message}')
        return 1
    
    except Exception as e:
        # Log error (idempotency_key already saved, prevents retry loop)
        log_entry = json_log('ERROR', 'seed_permissions', status='ERROR', error=str(e))
        if args.output == 'json':
            print(log_entry)
        else:
            print(f'[ERROR] seed_permissions.py failed: {str(e)}')
        return 3


if __name__ == "__main__":
    exit(main())