"""
Script de Seed Inicial V1.2

Execução:
    python scripts/seed_v1_2_initial.py                # Apply mode (idempotent)
    python scripts/seed_v1_2_initial.py --dry-run      # Preview mode
    python scripts/seed_v1_2_initial.py --force        # Force re-seed (bypass idempotency)
    python scripts/seed_v1_2_initial.py --help         # Usage information

Popula dados essenciais:
- Roles (Dirigente, Coordenador, Treinador, Atleta)
- Super Admin
- Categories (Infantil, Cadete, Juvenil, Adulto)
- Defensive Positions (5=Goleira)
- Offensive Positions
- Schooling Levels
- Phases of Play (4 fases do jogo)
- Advantage States (igualdade, superioridade, inferioridade)
- Event Types e Event Subtypes básicos

Idempotência:
- Usa tabela idempotency_keys (chave: 'seed_v1_2_initial:YYYY-MM-DD')
- 1ª execução do dia: popula dados, salva chave → exit 1
- 2ª execução do dia: skip (noop) → exit 0
- --force: bypassa idempotency, re-seed → exit 1

Exit Codes:
- 0: NOOP (já foi seeded hoje, nada a fazer)
- 1: SEEDED (dados populados com sucesso)
- 3: ERROR (falha de execução)
"""
import argparse
import json
import os
import sys
from datetime import date
from pathlib import Path

# Adiciona backend ao path
backend_path = Path(__file__).parent.parent / 'backend'
sys.path.insert(0, str(backend_path))

from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_values

# Carrega .env do backend (scripts/ → Hb Track - Backend/ → .env)
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


# ============================================================================
# HELPERS
# ============================================================================

def json_log(operation, status, details=None, dry_run=False, error=None):
    """
    JSON structured logging helper (SCRIPTS_GUIDE.md sec 3 compliance).
    
    Args:
        operation: Operation name (e.g., 'check_idempotency', 'seed_roles')
        status: Status string ('skip', 'seeded', 'error')
        details: Additional details (dict or string)
        dry_run: Whether this is a dry-run
        error: Error message if status='error'
    
    Returns:
        dict: JSON log entry
    """
    from datetime import datetime, timezone
    
    log_entry = {
        'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'script': 'seed_v1_2_initial.py',
        'operation': operation,
        'status': status,
        'dry_run': dry_run,
    }
    
    if details:
        log_entry['details'] = details
    if error:
        log_entry['error'] = str(error)
    
    return log_entry


def ensure_idempotency_table(conn):
    """
    Cria tabela idempotency_keys se não existir.
    
    Schema mínimo:
        key VARCHAR(255) PRIMARY KEY
    
    Note: Usa schema mínimo para compatibilidade. Colunas adicionais
    (script_name, executed_at, metadata) são opcionais.
    """
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS idempotency_keys (
            key VARCHAR(255) PRIMARY KEY
        )
    """)
    conn.commit()


def check_idempotency_key(conn, key):
    """
    Verifica se chave de idempotência existe.
    
    Args:
        conn: psycopg2 connection
        key: Chave de idempotência (e.g., 'seed_v1_2_initial:2026-02-16')
    
    Returns:
        bool: True se chave existe (já foi executado), False caso contrário
    """
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM idempotency_keys WHERE key = %s", (key,))
    return cur.fetchone() is not None


def save_idempotency_key(conn, key, script_name, metadata=None):
    """
    Salva chave de idempotência no banco.
    
    Args:
        conn: psycopg2 connection
        key: Chave de idempotência
        script_name: Nome do script (para tracking) - OPCIONAL
        metadata: Metadados opcionais (dict) - OPCIONAL
    
    Note: Adapta-se ao schema existente de idempotency_keys (endpoint, request_hash obrigatórios)
    """
    import hashlib
    
    cur = conn.cursor()
    
    # Delete existing key (if any) then insert new
    cur.execute("DELETE FROM idempotency_keys WHERE key = %s", (key,))
    
    # Tentar INSERT simples primeiro
    try:
        cur.execute("INSERT INTO idempotency_keys (key) VALUES (%s)", (key,))
    except Exception as e:
        # Se falhar, usar schema completo com valores obrigatórios
        conn.rollback()
        cur = conn.cursor()
        cur.execute("DELETE FROM idempotency_keys WHERE key = %s", (key,))
        
        # Gerar request_hash (hash do key)
        request_hash = hashlib.sha256(key.encode()).hexdigest()
        
        cur.execute(
            """
            INSERT INTO idempotency_keys (key, endpoint, request_hash)
            VALUES (%s, %s, %s)
            """,
            (key, 'seed_script', request_hash)
        )
    
    conn.commit()


def execute_sql(conn, sql, params=None):
    """Executa SQL e retorna cursor"""
    cur = conn.cursor()
    if params:
        cur.execute(sql, params)
    else:
        cur.execute(sql)
    return cur


def seed_roles(conn):
    """Seed: Roles (Dirigente, Coordenador, Treinador, Atleta)"""
    print("=> Seeding roles...")

    roles_data = [
        (1, 'dirigente', 'Dirigente'),
        (2, 'coordenador', 'Coordenador'),
        (3, 'treinador', 'Treinador'),
        (4, 'atleta', 'Atleta'),
    ]

    cur = conn.cursor()
    execute_values(
        cur,
        """
        INSERT INTO roles (id, code, name)
        VALUES %s
        ON CONFLICT (id) DO NOTHING
        """,
        roles_data
    )
    conn.commit()
    print(f"   OK {cur.rowcount} roles inseridos")


def seed_super_admin(conn):
    """Seed: Super Admin (pessoa + usuário)"""
    print("=> Seeding super admin...")

    # Verifica se já existe
    cur = execute_sql(conn, "SELECT id FROM users WHERE is_superadmin = true")
    if cur.fetchone():
        print("   SKIP Super admin já existe")
        return

    # Cria pessoa
    cur = execute_sql(
        conn,
        """
        INSERT INTO persons (full_name, birth_date)
        VALUES ('Super Administrador', '1990-01-01')
        RETURNING id
        """
    )
    person_id = cur.fetchone()[0]

    # Cria usuário super admin
    execute_sql(
        conn,
        """
        INSERT INTO users (person_id, email, password_hash, is_superadmin, is_locked, status)
        VALUES (%s, 'admin@hbtracking.com', 'CHANGE_ME_HASH', true, false, 'ativo')
        """,
        (person_id,)
    )
    conn.commit()
    print(f"   OK Super admin criado (person_id={person_id}, email=admin@hbtracking.com)")
    print("   IMPORTANTE: Alterar senha no banco ou via script de hash!")


def seed_categories(conn):
    """Seed: Categories (Mirim, Infantil, Cadete, Juvenil, Junior, Adulto, Master)"""
    print("=> Seeding categories...")

    categories_data = [
        (1, 'Mirim', 12),
        (2, 'Infantil', 14),
        (3, 'Cadete', 16),
        (4, 'Juvenil', 18),
        (5, 'Júnior', 21),
        (6, 'Adulto', 36),
        (7, 'Master', 60),
    ]

    cur = conn.cursor()
    execute_values(
        cur,
        """
        INSERT INTO categories (id, name, max_age)
        VALUES %s
        ON CONFLICT (id) DO NOTHING
        """,
        categories_data
    )
    conn.commit()
    print(f"   OK {cur.rowcount} categories inseridas")


def seed_defensive_positions(conn):
    """Seed: Defensive Positions (5=Goleira)"""
    print("=> Seeding defensive positions...")

    positions_data = [
        (1, 'central_defender', 'Armadora Central Defensiva', 'ACD'),
        (2, 'left_back_defender', 'Lateral Esquerda Defensiva', 'LED'),
        (3, 'right_back_defender', 'Lateral Direita Defensiva', 'LDD'),
        (4, 'pivot_defender', 'Pivô Defensiva', 'PD'),
        (5, 'goalkeeper', 'Goleira', 'GOL'),
    ]

    cur = conn.cursor()
    execute_values(
        cur,
        """
        INSERT INTO defensive_positions (id, code, name, abbreviation)
        VALUES %s
        ON CONFLICT (id) DO NOTHING
        """,
        positions_data
    )
    conn.commit()
    print(f"   OK {cur.rowcount} defensive positions inseridas (5=Goleira)")


def seed_offensive_positions(conn):
    """Seed: Offensive Positions"""
    print("=> Seeding offensive positions...")

    positions_data = [
        (1, 'central_back', 'Armadora Central', 'AC'),
        (2, 'left_back', 'Lateral Esquerda', 'LE'),
        (3, 'right_back', 'Lateral Direita', 'LD'),
        (4, 'left_wing', 'Ponta Esquerda', 'PE'),
        (5, 'right_wing', 'Ponta Direita', 'PD'),
        (6, 'pivot', 'Pivô', 'PI'),
    ]

    cur = conn.cursor()
    execute_values(
        cur,
        """
        INSERT INTO offensive_positions (id, code, name, abbreviation)
        VALUES %s
        ON CONFLICT (id) DO NOTHING
        """,
        positions_data
    )
    conn.commit()
    print(f"   OK {cur.rowcount} offensive positions inseridas")


def seed_schooling_levels(conn):
    """Seed: Schooling Levels"""
    print("=> Seeding schooling levels...")

    levels_data = [
        (1, 'elementary_incomplete', 'Ensino Fundamental Incompleto'),
        (2, 'elementary_complete', 'Ensino Fundamental Completo'),
        (3, 'high_school_incomplete', 'Ensino Médio Incompleto'),
        (4, 'high_school_complete', 'Ensino Médio Completo'),
        (5, 'higher_education_incomplete', 'Ensino Superior Incompleto'),
        (6, 'higher_education_complete', 'Ensino Superior Completo'),
    ]

    cur = conn.cursor()
    execute_values(
        cur,
        """
        INSERT INTO schooling_levels (id, code, name)
        VALUES %s
        ON CONFLICT (id) DO NOTHING
        """,
        levels_data
    )
    conn.commit()
    print(f"   OK {cur.rowcount} schooling levels inseridos")


def seed_phases_of_play(conn):
    """Seed: Phases of Play (4 fases do jogo)"""
    print("=> Seeding phases of play...")

    phases_data = [
        ('defense', 'Defesa'),
        ('transition_offense', 'Transição Ofensiva'),
        ('attack_positional', 'Ataque Posicional'),
        ('transition_defense', 'Transição Defensiva'),
    ]

    cur = conn.cursor()
    execute_values(
        cur,
        """
        INSERT INTO phases_of_play (code, description)
        VALUES %s
        ON CONFLICT (code) DO NOTHING
        """,
        phases_data
    )
    conn.commit()
    print(f"   OK {cur.rowcount} phases of play inseridas")


def seed_advantage_states(conn):
    """Seed: Advantage States (igualdade, superioridade, inferioridade)"""
    print("=> Seeding advantage states...")

    states_data = [
        ('even', 0, 'Igualdade numérica (6x6)'),
        ('numerical_superiority', 1, 'Superioridade numérica (+1 jogadora)'),
        ('numerical_inferiority', -1, 'Inferioridade numérica (-1 jogadora)'),
    ]

    cur = conn.cursor()
    execute_values(
        cur,
        """
        INSERT INTO advantage_states (code, delta_players, description)
        VALUES %s
        ON CONFLICT (code) DO NOTHING
        """,
        states_data
    )
    conn.commit()
    print(f"   OK {cur.rowcount} advantage states inseridos")


def seed_event_types(conn):
    """Seed: Event Types básicos"""
    print("=> Seeding event types...")

    event_types_data = [
        ('shot', 'Arremesso', True, False),
        ('goal', 'Gol', True, True),
        ('goalkeeper_save', 'Defesa de Goleira', False, False),
        ('turnover', 'Perda de Bola', False, True),
        ('foul', 'Falta', False, False),
        ('seven_meter', 'Tiro de 7 Metros', True, True),
        ('substitution', 'Substituição', False, False),
        ('timeout', 'Pedido de Tempo', False, False),
        ('exclusion_2min', 'Exclusão 2 Minutos', False, False),
        ('yellow_card', 'Cartão Amarelo', False, False),
        ('red_card', 'Cartão Vermelho', False, False),
    ]

    cur = conn.cursor()
    execute_values(
        cur,
        """
        INSERT INTO event_types (code, description, is_shot, is_possession_ending)
        VALUES %s
        ON CONFLICT (code) DO NOTHING
        """,
        event_types_data
    )
    conn.commit()
    print(f"   OK {cur.rowcount} event types inseridos")


def seed_event_subtypes(conn):
    """Seed: Event Subtypes básicos"""
    print("=> Seeding event subtypes...")

    subtypes_data = [
        # Arremessos
        ('shot_6m', 'shot', 'Arremesso 6m'),
        ('shot_9m', 'shot', 'Arremesso 9m'),
        ('shot_wing', 'shot', 'Arremesso de Ponta'),
        ('shot_counterattack', 'shot', 'Arremesso em Contra-Ataque'),
        ('shot_pivot', 'shot', 'Arremesso de Pivô'),

        # Perdas de bola
        ('turnover_pass', 'turnover', 'Perda de Bola - Passe Errado'),
        ('turnover_dribble', 'turnover', 'Perda de Bola - Drible'),
        ('turnover_steps', 'turnover', 'Perda de Bola - Passos'),
        ('turnover_offensive_foul', 'turnover', 'Perda de Bola - Falta Ofensiva'),

        # Faltas
        ('offensive_foul', 'foul', 'Falta Ofensiva'),
        ('defensive_foul', 'foul', 'Falta Defensiva'),
    ]

    cur = conn.cursor()
    execute_values(
        cur,
        """
        INSERT INTO event_subtypes (code, event_type_code, description)
        VALUES %s
        ON CONFLICT (code) DO NOTHING
        """,
        subtypes_data
    )
    conn.commit()
    print(f"   OK {cur.rowcount} event subtypes inseridos")


def parse_args():
    """Parse CLI arguments"""
    parser = argparse.ArgumentParser(
        description='Seed foundation data for HB Tracking (v1.2)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Apply mode (idempotent, exits 0 if already seeded today)
  python seed_v1_2_initial.py
  
  # Preview mode (shows what would be seeded, no DB writes)
  python seed_v1_2_initial.py --dry-run
  
  # Force re-seed (bypass idempotency check)
  python seed_v1_2_initial.py --force
  
  # Text output format
  python seed_v1_2_initial.py --output text

Exit Codes:
  0 = NOOP (already seeded today, nothing to do)
  1 = SEEDED (data populated successfully)
  3 = ERROR (execution failure)
        """
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview mode: show what would be seeded without DB writes'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force re-seed (bypass idempotency check)'
    )
    
    parser.add_argument(
        '--output',
        choices=['json', 'text'],
        default='json',
        help='Output format (default: json)'
    )
    
    return parser.parse_args()


def main():
    args = parse_args()
    
    # Log collection
    logs = []
    
    # Generate idempotency key (format: script_name:YYYY-MM-DD)
    today = date.today().isoformat()
    idempotency_key = f"seed_v1_2_initial:{today}"
    
    # DRY-RUN mode: preview only (no DB required)
    if args.dry_run:
        logs.append(json_log('mode', 'dry_run', details='Preview mode, no DB writes'))
        
        if args.output == 'json':
            print(json.dumps({
                'status': 'dry_run',
                'message': 'Preview: would seed the following entities',
                'entities': [
                    'roles (4 roles)',
                    'super_admin (1 user)',
                    'categories (7 categories)',
                    'defensive_positions (5 positions)',
                    'offensive_positions (6 positions)',
                    'schooling_levels (6 levels)',
                    'phases_of_play (4 phases)',
                    'advantage_states (3 states)',
                    'event_types (11 types)',
                    'event_subtypes (11 subtypes)',
                ],
                'idempotency_key': idempotency_key,
                'logs': logs
            }, indent=2))
        else:
            print("=" * 60)
            print("SEED V1.2 - DRY-RUN MODE (PREVIEW)")
            print("=" * 60)
            print("\nWould seed the following entities:")
            print("  - roles (4 roles)")
            print("  - super_admin (1 user)")
            print("  - categories (7 categories)")
            print("  - defensive_positions (5 positions)")
            print("  - offensive_positions (6 positions)")
            print("  - schooling_levels (6 levels)")
            print("  - phases_of_play (4 phases)")
            print("  - advantage_states (3 states)")
            print("  - event_types (11 types)")
            print("  - event_subtypes (11 subtypes)")
            print(f"\nIdempotency key: {idempotency_key}")
            print("\nNo DB writes performed (dry-run mode)")
        
        return 0  # EXIT 0: DRY-RUN
    
    # Check DATABASE_URL (required for apply/force modes)
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        if args.output == 'json':
            print(json.dumps({'status': 'error', 'message': 'DATABASE_URL not configured. Set .env'}, indent=2))
        else:
            print("ERROR: DATABASE_URL não definido. Configure .env.")
        return 3  # EXIT 3: ERROR
    
    # Convert SQLAlchemy URL to psycopg2 format (postgresql+asyncpg:// → postgresql://)
    if 'postgresql+asyncpg://' in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace('postgresql+asyncpg://', 'postgresql://')
    elif 'postgresql+psycopg2://' in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace('postgresql+psycopg2://', 'postgresql://')
    
    conn = None
    exit_code = 0
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        
        # Ensure idempotency_keys table exists
        ensure_idempotency_table(conn)
        logs.append(json_log('ensure_idempotency_table', 'success', 
                             details='idempotency_keys table ready', dry_run=args.dry_run))
        
        # Check idempotency (unless --force)
        if not args.force:
            already_seeded = check_idempotency_key(conn, idempotency_key)
            
            if already_seeded:
                logs.append(json_log('check_idempotency', 'skip',
                                     details=f'Already seeded today (key={idempotency_key})',
                                     dry_run=args.dry_run))
                
                # Output based on format
                if args.output == 'json':
                    print(json.dumps({'status': 'noop', 'message': 'Already seeded today', 'logs': logs}, indent=2))
                else:
                    print("=" * 60)
                    print("SEED V1.2 - NOOP (ALREADY SEEDED TODAY)")
                    print("=" * 60)
                    print(f"Idempotency key detected: {idempotency_key}")
                    print("Use --force to re-seed")
                
                return 0  # EXIT 0: NOOP
        
        else:
            logs.append(json_log('check_idempotency', 'bypass',
                                 details='--force flag used, bypassing idempotency',
                                 dry_run=args.dry_run))
        
        # DRY-RUN mode: preview only
        if args.dry_run:
            logs.append(json_log('mode', 'dry_run', details='Preview mode, no DB writes'))
            
            if args.output == 'json':
                print(json.dumps({
                    'status': 'dry_run',
                    'message': 'Preview: would seed the following entities',
                    'entities': [
                        'roles (4 roles)',
                        'super_admin (1 user)',
                        'categories (7 categories)',
                        'defensive_positions (5 positions)',
                        'offensive_positions (6 positions)',
                        'schooling_levels (6 levels)',
                        'phases_of_play (4 phases)',
                        'advantage_states (3 states)',
                        'event_types (11 types)',
                        'event_subtypes (11 subtypes)',
                    ],
                    'idempotency_key': idempotency_key,
                    'logs': logs
                }, indent=2))
            else:
                print("=" * 60)
                print("SEED V1.2 - DRY-RUN MODE (PREVIEW)")
                print("=" * 60)
                print("\nWould seed the following entities:")
                print("  - roles (4 roles)")
                print("  - super_admin (1 user)")
                print("  - categories (7 categories)")
                print("  - defensive_positions (5 positions)")
                print("  - offensive_positions (6 positions)")
                print("  - schooling_levels (6 levels)")
                print("  - phases_of_play (4 phases)")
                print("  - advantage_states (3 states)")
                print("  - event_types (11 types)")
                print("  - event_subtypes (11 subtypes)")
                print(f"\nIdempotency key: {idempotency_key}")
                print("\nNo DB writes performed (dry-run mode)")
            
            return 0  # EXIT 0: DRY-RUN
        
        # APPLY MODE: execute seeding
        logs.append(json_log('mode', 'apply', details='Executing seeding functions'))
        
        if args.output == 'text':
            print("=" * 60)
            print("SEED INICIAL V1.2 - HB TRACKING")
            print("=" * 60)
            print()
        
        # Execute all seeding functions
        seed_roles(conn)
        logs.append(json_log('seed_roles', 'seeded', details='4 roles'))
        
        seed_super_admin(conn)
        logs.append(json_log('seed_super_admin', 'seeded', details='Super admin user'))
        
        seed_categories(conn)
        logs.append(json_log('seed_categories', 'seeded', details='7 categories'))
        
        seed_defensive_positions(conn)
        logs.append(json_log('seed_defensive_positions', 'seeded', details='5 defensive positions'))
        
        seed_offensive_positions(conn)
        logs.append(json_log('seed_offensive_positions', 'seeded', details='6 offensive positions'))
        
        seed_schooling_levels(conn)
        logs.append(json_log('seed_schooling_levels', 'seeded', details='6 schooling levels'))
        
        seed_phases_of_play(conn)
        logs.append(json_log('seed_phases_of_play', 'seeded', details='4 phases of play'))
        
        seed_advantage_states(conn)
        logs.append(json_log('seed_advantage_states', 'seeded', details='3 advantage states'))
        
        seed_event_types(conn)
        logs.append(json_log('seed_event_types', 'seeded', details='11 event types'))
        
        seed_event_subtypes(conn)
        logs.append(json_log('seed_event_subtypes', 'seeded', details='11 event subtypes'))
        
        # Save idempotency key
        metadata = {
            'force_used': args.force,
            'entities_seeded': 10,
        }
        save_idempotency_key(conn, idempotency_key, 'seed_v1_2_initial.py', metadata)
        logs.append(json_log('save_idempotency_key', 'saved',
                             details=f'Key saved: {idempotency_key}'))
        
        # Output final status
        if args.output == 'json':
            print(json.dumps({
                'status': 'seeded',
                'message': 'Foundation data seeded successfully',
                'idempotency_key': idempotency_key,
                'logs': logs
            }, indent=2))
        else:
            print()
            print("=" * 60)
            print("OK SEED CONCLUIDO COM SUCESSO!")
            print("=" * 60)
            print()
            print("PROXIMOS PASSOS:")
            print("1. Alterar senha do super admin no banco")
            print("2. Criar organizações via API")
            print("3. Criar usuários Dirigentes e vincular organizações")
            print()
        
        exit_code = 1  # EXIT 1: SEEDED
        
    except Exception as e:
        if conn:
            conn.rollback()
        
        logs.append(json_log('seed_execution', 'error', error=str(e)))
        
        if args.output == 'json':
            print(json.dumps({
                'status': 'error',
                'message': 'Seeding failed',
                'error': str(e),
                'logs': logs
            }, indent=2))
        else:
            print(f"\nERRO durante seed: {e}")
        
        exit_code = 3  # EXIT 3: ERROR
        
    finally:
        if conn:
            conn.close()
    
    return exit_code


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
