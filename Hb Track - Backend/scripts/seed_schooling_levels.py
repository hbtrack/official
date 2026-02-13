"""
Seed: Níveis de escolaridade (schooling_levels) com idempotência e CLI
População dos 6 níveis de escolaridade com suporte a --dry-run, --force e --output json
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
        'script': 'seed_schooling_levels.py',
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
                (str(uuid.uuid4()), key, 'seed_schooling_levels.py', '/scripts/seed_schooling_levels', 'seed', 200)
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
        description='Seed 6 Brazilian education levels into the schooling_levels table',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='Examples:\n  python seed_schooling_levels.py\n  python seed_schooling_levels.py --dry-run\n  python seed_schooling_levels.py --force --output json'
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


def seed_schooling_levels(dry_run=False):
    """Seed schooling levels without idempotency check. Called from main() after idempotency validation."""
    from sqlalchemy import text
    from app.core.db import db_context
    
    with db_context() as session:
        # Verificar se já existem níveis
        result = session.execute(text("SELECT COUNT(*) FROM schooling_levels"))
        count = result.scalar()

        if count > 0 and not dry_run:
            # Already seeded, return 0 (noop)
            return 0

        # Inserir os 6 níveis de escolaridade (Brazilian education system)
        schooling_data = [
            (1, '7EF', '7º ano do Ensino Fundamental'),
            (2, '8EF', '8º ano do Ensino Fundamental'), 
            (3, '9EF', '9º ano do Ensino Fundamental'),
            (4, '1EM', '1º ano do Ensino Médio'),
            (5, '2EM', '2º ano do Ensino Médio'),
            (6, '3EM', '3º ano do Ensino Médio'),
        ]

        # Inserir níveis
        inserted_count = 0
        for level_id, code, name in schooling_data:
            if not dry_run:
                session.execute(text("""
                    INSERT INTO schooling_levels (id, code, name, is_active)
                    VALUES (:id, :code, :name, true)
                """), {
                    'id': level_id,
                    'code': code,
                    'name': name
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
    idempotency_key = f'seed_schooling_levels:{today}'
    
    # Ensure idempotency table exists
    ensure_idempotency_table()
    
    # Check idempotency (unless --force)
    already_executed = check_idempotency_key(idempotency_key) if not args.force else False
    
    try:
        if already_executed:
            # Already seeded today
            message = f'Schooling levels already seeded today ({idempotency_key}). Skipping.'
            log_entry = json_log('INFO', 'seed_schooling_levels', status='NOOP', message=message)
            if args.output == 'json':
                print(log_entry)
            else:
                print(f'[SKIP] {message}')
            return 0
        
        if args.dry_run:
            # Preview mode - no database modifications
            num_levels = seed_schooling_levels(dry_run=True)
            message = f'DRY-RUN: Would seed {num_levels} schooling levels (no changes made)'
            log_entry = json_log('INFO', 'seed_schooling_levels', status='DRY_RUN', count=num_levels, message=message)
            if args.output == 'json':
                print(log_entry)
            else:
                print(f'[DRY-RUN] {message}')
            return 0
        
        # Save idempotency key BEFORE attempting to seed (mark as attempted)
        save_idempotency_key(idempotency_key)
        
        # Execute seeding
        num_seeded = seed_schooling_levels(dry_run=False)
        
        # Log success
        message = f'Successfully seeded {num_seeded} schooling levels'
        log_entry = json_log('INFO', 'seed_schooling_levels', status='SEEDED', count=num_seeded, message=message)
        if args.output == 'json':
            print(log_entry)
        else:
            print(f'[OK] {message}')
        return 1
    
    except Exception as e:
        # Log error (idempotency_key already saved, prevents retry loop)
        log_entry = json_log('ERROR', 'seed_schooling_levels', status='ERROR', error=str(e))
        if args.output == 'json':
            print(log_entry)
        else:
            print(f'[ERROR] seed_schooling_levels.py failed: {str(e)}')
        return 3


if __name__ == "__main__":
    exit(main())
