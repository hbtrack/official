"""
Script de Seed Inicial V1.2
Execução: python scripts/seed_v1_2_initial.py

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
"""
import os
import sys
from pathlib import Path

# Adiciona backend ao path
backend_path = Path(__file__).parent.parent / 'backend'
sys.path.insert(0, str(backend_path))

from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_values

# Carrega .env do backend
env_path = Path(__file__).parent.parent / 'backend' / '.env'
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL não definido. Configure .env.")


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


def main():
    print("=" * 60)
    print("SEED INICIAL V1.2 - HB TRACKING")
    print("=" * 60)
    print()

    conn = psycopg2.connect(DATABASE_URL)

    try:
        seed_roles(conn)
        seed_super_admin(conn)
        seed_categories(conn)
        seed_defensive_positions(conn)
        seed_offensive_positions(conn)
        seed_schooling_levels(conn)
        seed_phases_of_play(conn)
        seed_advantage_states(conn)
        seed_event_types(conn)
        seed_event_subtypes(conn)

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

    except Exception as e:
        conn.rollback()
        print(f"\nERRO durante seed: {e}")
        raise
    finally:
        conn.close()


if __name__ == '__main__':
    main()
