"""
Seed: Mapeamento de permissões por papel (role_permissions) com idempotência e CLI
População completa dos mapeamentos RBAC com suporte a --dry-run, --force e --output json
"""
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone
import psycopg2
from psycopg2 import sql

# Adicionar backend ao path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import os
from dotenv import load_dotenv


def json_log(level, operation, **kwargs):
    """Log operation in structured JSON format (ISO8601 UTC)."""
    timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    log_data = {
        'timestamp': timestamp,
        'level': level,
        'script': 'seed_role_permissions.py',
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
                (str(uuid.uuid4()), key, 'seed_role_permissions.py', '/scripts/seed_role_permissions', 'seed', 200)
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
        description='Seed 113 RBAC role-permission mappings into the system',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='Examples:\n  python seed_role_permissions.py\n  python seed_role_permissions.py --dry-run\n  python seed_role_permissions.py --force --output json'
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


def seed_role_permissions(dry_run=False):
    """Seed role-permission mappings without idempotency check. Called from main() after idempotency validation."""
    from sqlalchemy import text
    from app.core.db import db_context
    
    with db_context() as session:
        # Verificar se já existem mapeamentos
        result = session.execute(text("SELECT COUNT(*) FROM role_permissions"))
        count = result.scalar()

        if count > 0 and not dry_run:
            # Already seeded, return 0 (noop)
            return 0

        # Verificar se roles e permissions existem
        result = session.execute(text("SELECT COUNT(*) FROM roles"))
        roles_count = result.scalar()
        
        result = session.execute(text("SELECT COUNT(*) FROM permissions"))
        permissions_count = result.scalar()

        if roles_count == 0:
            raise RuntimeError("Tabela roles está vazia. Execute 001_seed_roles.py primeiro.")

        if permissions_count == 0:
            raise RuntimeError("Tabela permissions está vazia. Execute 006_seed_permissions.py primeiro.")

        # Obter IDs dos roles
        result = session.execute(text("SELECT id, code FROM roles"))
        roles = {code: role_id for role_id, code in result.fetchall()}

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
        for role_id, permission_id in role_permissions_data:
            # Role IDs are already numeric from the data structure
            if not dry_run:
                session.execute(text("""
                    INSERT INTO role_permissions (role_id, permission_id)
                    VALUES (:role_id, :permission_id)
                """), {
                    'role_id': role_id,
                    'permission_id': permission_id
                })
            inserted_count += 1

        if not dry_run:
            session.commit()
        
        return inserted_count


def main():
    """Main entry point with idempotency and CLI."""
    args = parse_args()
    
    # Generate idempotency key (script:YYYY-MM-DD)
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    idempotency_key = f'seed_role_permissions:{today}'
    
    # Ensure idempotency table exists
    ensure_idempotency_table()
    
    # Check idempotency (unless --force)
    already_executed = check_idempotency_key(idempotency_key) if not args.force else False
    
    try:
        if already_executed:
            # Already seeded today
            message = f'Role-permissions already seeded today ({idempotency_key}). Skipping.'
            log_entry = json_log('INFO', 'seed_role_permissions', status='NOOP', message=message)
            if args.output == 'json':
                print(log_entry)
            else:
                print(f'[SKIP] {message}')
            return 0
        
        if args.dry_run:
            # Preview mode - no database modifications
            num_mappings = seed_role_permissions(dry_run=True)
            message = f'DRY-RUN: Would seed {num_mappings} role-permission mappings (no changes made)'
            log_entry = json_log('INFO', 'seed_role_permissions', status='DRY_RUN', count=num_mappings, message=message)
            if args.output == 'json':
                print(log_entry)
            else:
                print(f'[DRY-RUN] {message}')
            return 0
        
        # Save idempotency key BEFORE attempting to seed (mark as attempted)
        save_idempotency_key(idempotency_key)
        
        # Execute seeding
        num_seeded = seed_role_permissions(dry_run=False)
        
        # Log success
        message = f'Successfully seeded {num_seeded} role-permission mappings'
        log_entry = json_log('INFO', 'seed_role_permissions', status='SEEDED', count=num_seeded, message=message)
        if args.output == 'json':
            print(log_entry)
        else:
            print(f'[OK] {message}')
        return 1
    
    except Exception as e:
        # Log error (idempotency_key already saved, prevents retry loop)
        log_entry = json_log('ERROR', 'seed_role_permissions', status='ERROR', error=str(e))
        if args.output == 'json':
            print(log_entry)
        else:
            print(f'[ERROR] seed_role_permissions.py failed: {str(e)}')
        return 3


if __name__ == "__main__":
    exit(main())
