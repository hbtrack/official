"""
Script para garantir que o superadmin tenha is_superadmin=true e senha correta

IDEMPOTENT: Execução múltipla resulta em noop se estado já está correto.

Exit Codes:
  0: noop (superadmin já estava correto)
  2: updated (superadmin foi atualizado)
  3: error (falha de execução)
  4: not_found (usuário admin@hbtracking.com não existe)

Usage:
  python fix_superadmin.py                    # Executa fix (aplica mudanças)
  python fix_superadmin.py --dry-run          # Preview sem aplicar
  python fix_superadmin.py --output json      # Saída JSON estruturada
  python fix_superadmin.py --help             # Mostra ajuda

Refactored: 2026-02-14 (AR-2026-02-14-SCRIPTS-REFACTOR-FIX-SUPERADMIN)
"""
import os
import sys
import json
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import psycopg2
import bcrypt
from dotenv import load_dotenv


def json_log(
    operation: str,
    status: str,
    user_id: Optional[int] = None,
    changes: Optional[Dict[str, bool]] = None,
    dry_run: bool = False,
    error: Optional[str] = None
) -> Dict[str, Any]:
    """Estrutura de log JSON conforme SCRIPTS_GUIDE.md sec 3"""
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "script": "fix_superadmin.py",
        "operation": operation,
        "status": status,
        "dry_run": dry_run
    }
    if user_id is not None:
        log_entry["user_id"] = user_id
    if changes is not None:
        log_entry["changes"] = changes
    if error is not None:
        log_entry["error"] = error
    return log_entry


def check_superadmin_state(
    cur: psycopg2.extensions.cursor,
    expected_password: str
) -> Tuple[bool, Optional[int], Dict[str, bool]]:
    """
    Verifica estado atual do superadmin.
    
    Returns:
        (needs_update, user_id, changes_needed)
        
        needs_update: True se precisa atualizar, False se já está correto
        user_id: ID do usuário (None se não encontrado)
        changes_needed: Dicionário de campos que precisam mudança
    """
    cur.execute("""
        SELECT id, password_hash, is_superadmin, status, is_locked
        FROM users
        WHERE email = 'admin@hbtracking.com'
    """)
    
    row = cur.fetchone()
    if not row:
        return True, None, {"user": "not_found"}
    
    user_id, password_hash, is_superadmin, status, is_locked = row
    
    changes = {}
    
    # Check password (usar bcrypt.checkpw para comparar)
    password_matches = False
    if password_hash:
        try:
            password_matches = bcrypt.checkpw(
                expected_password.encode('utf-8'),
                password_hash.encode('utf-8')
            )
        except Exception:
            password_matches = False
    
    if not password_matches:
        changes["password"] = True
    
    if not is_superadmin:
        changes["is_superadmin"] = True
        
    if status != 'ativo':
        changes["status"] = True
        
    if is_locked:
        changes["is_locked"] = True
    
    needs_update = len(changes) > 0
    return needs_update, user_id, changes


def update_superadmin(
    cur: psycopg2.extensions.cursor,
    password: str,
    dry_run: bool = False
) -> Tuple[int, int]:
    """
    Atualiza superadmin com senha e flags corretas.
    
    Returns:
        (affected_rows, user_id)
    """
    # Gerar hash da senha
    password_hash = bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')
    
    if dry_run:
        # Dry-run: apenas SELECT para simular
        cur.execute("""
            SELECT id FROM users WHERE email = 'admin@hbtracking.com'
        """)
        row = cur.fetchone()
        return (1 if row else 0), (row[0] if row else None)
    
    # Executar UPDATE
    cur.execute("""
        UPDATE users 
        SET is_superadmin = true, 
            password_hash = %s,
            status = 'ativo',
            is_locked = false
        WHERE email = 'admin@hbtracking.com'
        RETURNING id
    """, (password_hash,))
    
    row = cur.fetchone()
    affected = cur.rowcount
    user_id = row[0] if row else None
    
    return affected, user_id


def main():
    parser = argparse.ArgumentParser(
        description='Fix superadmin user (idempotent)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Apply fixes
  %(prog)s --dry-run          # Preview without applying
  %(prog)s --output json      # JSON structured output
        """
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without applying'
    )
    parser.add_argument(
        '--output',
        choices=['text', 'json'],
        default='text',
        help='Output format (default: text)'
    )
    
    args = parser.parse_args()
    
    # Carrega .env
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(dotenv_path=env_path)
    
    DATABASE_URL = os.getenv('DATABASE_URL_SYNC') or os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        log = json_log(
            operation="init",
            status="error",
            dry_run=args.dry_run,
            error="DATABASE_URL não definido"
        )
        if args.output == 'json':
            print(json.dumps(log))
        else:
            print("❌ ERROR: DATABASE_URL não definido")
        sys.exit(3)
    
    # Converte URL para psycopg2
    DATABASE_URL = DATABASE_URL.replace('postgresql+asyncpg://', 'postgresql://')
    DATABASE_URL = DATABASE_URL.replace('postgresql+psycopg2://', 'postgresql://')
    
    # Senha padrão
    password = 'Admin@123'
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # STEP 1: Check state
        needs_update, user_id, changes_needed = check_superadmin_state(cur, password)
        
        if "user" in changes_needed and changes_needed["user"] == "not_found":
            # User não existe
            log = json_log(
                operation="check",
                status="not_found",
                dry_run=args.dry_run,
                error="Usuário admin@hbtracking.com não encontrado"
            )
            if args.output == 'json':
                print(json.dumps(log))
            else:
                print('❌ Usuário admin@hbtracking.com não encontrado!')
                print('   Execute o seed inicial: python scripts/seed_v1_2_initial.py')
            cur.close()
            conn.close()
            sys.exit(4)
        
        # STEP 2: Decide action
        if not needs_update:
            # Já está correto (IDEMPOTENT NOOP)
            log = json_log(
                operation="check",
                status="noop",
                user_id=user_id,
                changes=changes_needed,
                dry_run=args.dry_run
            )
            if args.output == 'json':
                print(json.dumps(log))
            else:
                print('✅ Superadmin já está correto (noop)')
                print(f'   Email: admin@hbtracking.com')
                print(f'   User ID: {user_id}')
                if args.dry_run:
                    print('   [DRY-RUN] Nenhuma mudança necessária')
            cur.close()
            conn.close()
            sys.exit(0)
        
        # STEP 3: Apply update
        affected, updated_user_id = update_superadmin(cur, password, dry_run=args.dry_run)
        
        if not args.dry_run:
            conn.commit()
        
        if affected > 0:
            log = json_log(
                operation="update",
                status="success",
                user_id=updated_user_id or user_id,
                changes=changes_needed,
                dry_run=args.dry_run
            )
            if args.output == 'json':
                print(json.dumps(log))
            else:
                if args.dry_run:
                    print('✅ [DRY-RUN] Superadmin SERIA atualizado:')
                else:
                    print('✅ Superadmin atualizado com sucesso!')
                print(f'   Email: admin@hbtracking.com')
                print(f'   User ID: {updated_user_id or user_id}')
                print(f'   Senha: Admin@123')
                print(f'   Mudanças aplicadas: {", ".join(changes_needed.keys())}')
            cur.close()
            conn.close()
            sys.exit(2)
        else:
            # Não deveria chegar aqui (logic error)
            log = json_log(
                operation="update",
                status="error",
                dry_run=args.dry_run,
                error="UPDATE não afetou linhas (logic error)"
            )
            if args.output == 'json':
                print(json.dumps(log))
            else:
                print('❌ ERROR: UPDATE não afetou linhas')
            cur.close()
            conn.close()
            sys.exit(3)
            
    except Exception as e:
        log = json_log(
            operation="execute",
            status="error",
            dry_run=args.dry_run,
            error=str(e)
        )
        if args.output == 'json':
            print(json.dumps(log))
        else:
            print(f'❌ ERROR: {e}')
        sys.exit(3)


if __name__ == '__main__':
    main()
