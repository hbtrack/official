#!/usr/bin/env python3
"""
Seed E2E Canônico com UUIDs Determinísticos para Testes Training Module

DIFERENÇA DO seed_e2e.py:
- seed_e2e.py: UUIDs FIXOS hardcoded (88888888-...)
- seed_e2e_canonical.py: UUIDs DETERMINÍSTICOS via uuid5(NAMESPACE_DNS, "namespace:name")

BENEFÍCIOS:
- Reprodutibilidade 100% (mesmo UUID em qualquer ambiente)
- Debugging facilitado (IDs conhecidos antecipadamente)
- Asserções hardcoded nos testes
- Documentação clara (SEED_CANONICO.md)

USO:
    python scripts/seed_e2e_canonical.py --deterministic

ESTRUTURA:
- 32 users (IDs de email hash)
- 16 teams (IDs de "categoria-genero" slug)
- 240 athletes (15/team, IDs de "nome-completo" slug)
- 320 sessions (20/team, IDs de "team-date-type")
- 50 notifications, badges, rankings determinísticos
"""
import argparse
import os
import sys
import uuid
from pathlib import Path
from datetime import datetime, date, timedelta
from typing import Dict, List, Tuple

from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_values
import bcrypt

# =============================================================================
# CONFIGURAÇÃO
# =============================================================================

env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv('DATABASE_URL', '')
DATABASE_URL = DATABASE_URL.replace('postgresql+psycopg2://', 'postgresql://')
DATABASE_URL = DATABASE_URL.replace('postgresql+asyncpg://', 'postgresql://')

# Namespace para UUIDs determinísticos
NAMESPACE_DNS = uuid.NAMESPACE_DNS

# Seed version
SEED_VERSION = "3.0.0-canonical"

# =============================================================================
# FUNÇÃO DETERMINISTIC_UUID
# =============================================================================

def deterministic_uuid(namespace: str, name: str) -> uuid.UUID:
    """
    Gera UUID determinístico usando uuid5(NAMESPACE_DNS, "namespace:name").
    
    Exemplos:
        deterministic_uuid("users", "dirigente@example.com")
        deterministic_uuid("teams", "sub20-masculino")
        deterministic_uuid("athletes", "joao-silva")
        deterministic_uuid("sessions", "sub20-masculino-2026-01-20-tatico")
    
    Returns:
        UUID sempre igual para mesmos inputs
    """
    key = f"{namespace}:{name}"
    return uuid.uuid5(NAMESPACE_DNS, key)


# =============================================================================
# MAPEAMENTO DE IDS CONHECIDOS (SEED CANONICO)
# =============================================================================

class CanonicalIds:
    """
    IDs Canônicos Determinísticos - Documentados em SEED_CANONICO.md
    """
    
    # Organization E2E
    ORG_E2E = deterministic_uuid("organizations", "e2e-hbtrack-test-org")
    
    # Users por role (email como identificador - ATENÇÃO: devem corresponder a shared-data.ts)
    USER_ADMIN = deterministic_uuid("users", "e2e.admin@teste.com")  # admin é dirigente
    USER_COORDENADOR = deterministic_uuid("users", "e2e.coordenador@teste.com")
    USER_TREINADOR = deterministic_uuid("users", "e2e.treinador@teste.com")
    USER_ATLETA = deterministic_uuid("users", "e2e.atleta@teste.com")
    USER_ATLETA_MARIA = deterministic_uuid("users", "maria.santos@e2e.teste")
    
    # Teams por categoria-genero slug
    TEAM_SUB20_M = deterministic_uuid("teams", "sub20-masculino")
    TEAM_SUB20_F = deterministic_uuid("teams", "sub20-feminino")
    TEAM_SUB17_M = deterministic_uuid("teams", "sub17-masculino")
    TEAM_SUB17_F = deterministic_uuid("teams", "sub17-feminino")
    TEAM_SUB14_M = deterministic_uuid("teams", "sub14-masculino")
    TEAM_SUB14_F = deterministic_uuid("teams", "sub14-feminino")
    TEAM_ADULTO_M = deterministic_uuid("teams", "adulto-masculino")
    TEAM_ADULTO_F = deterministic_uuid("teams", "adulto-feminino")
    
    # Athletes (nome completo como identificador)
    ATHLETE_JOAO_SILVA = deterministic_uuid("athletes", "joao-silva")
    ATHLETE_MARIA_SANTOS = deterministic_uuid("athletes", "maria-santos")
    ATHLETE_PEDRO_OLIVEIRA = deterministic_uuid("athletes", "pedro-oliveira")
    
    # Templates padrão
    TEMPLATE_TATICO = deterministic_uuid("templates", "tatico-ofensivo")
    TEMPLATE_FISICO = deterministic_uuid("templates", "fisico-intensivo")
    TEMPLATE_EQUILIBRADO = deterministic_uuid("templates", "equilibrado")
    TEMPLATE_DEFESA = deterministic_uuid("templates", "defesa-posicional")
    
    # Sessions (team-date-type como identificador)
    SESSION_SUB20_2026_01_20_TATICO = deterministic_uuid("sessions", "sub20-masculino-2026-01-20-tatico")
    SESSION_SUB20_2026_01_22_FISICO = deterministic_uuid("sessions", "sub20-masculino-2026-01-22-fisico")
    
    # Cycles
    MACRO_PREPARATORIO = deterministic_uuid("cycles", "macro-preparatorio-2026")
    MESO_FASE1 = deterministic_uuid("cycles", "meso-fase1-2026")


# =============================================================================
# DADOS BRASILEIROS
# =============================================================================

NOMES_MASCULINOS = [
    'João', 'Pedro', 'Lucas', 'Gabriel', 'Rafael', 'Miguel', 'Davi', 'Arthur',
    'Guilherme', 'Felipe', 'Bernardo', 'Enzo', 'Nicolas', 'Lorenzo', 'Matheus',
    'Henrique', 'Gustavo', 'Thiago', 'Vinicius', 'Bruno'
]

NOMES_FEMININOS = [
    'Maria', 'Ana', 'Beatriz', 'Julia', 'Larissa', 'Camila', 'Fernanda', 'Gabriela',
    'Isabella', 'Laura', 'Mariana', 'Rafaela', 'Amanda', 'Carolina', 'Leticia',
    'Patricia', 'Sofia', 'Valentina', 'Alice', 'Helena'
]

SOBRENOMES = [
    'Silva', 'Santos', 'Oliveira', 'Souza', 'Pereira', 'Costa', 'Ferreira', 'Rodrigues',
    'Almeida', 'Nascimento', 'Lima', 'Araújo', 'Fernandes', 'Carvalho', 'Gomes'
]

CATEGORIAS = [
    {'id': 2, 'name': 'Infantil', 'slug': 'sub14', 'min_age': 12, 'max_age': 14},
    {'id': 3, 'name': 'Cadete', 'slug': 'sub17', 'min_age': 15, 'max_age': 17},
    {'id': 4, 'name': 'Juvenil', 'slug': 'sub20', 'min_age': 18, 'max_age': 20},
    {'id': 6, 'name': 'Adulto', 'slug': 'adulto', 'min_age': 21, 'max_age': 40},
]

# =============================================================================
# SEED PRINCIPAL
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description='Seed E2E Canônico Determinístico')
    parser.add_argument('--deterministic', action='store_true', default=True,
                        help='Usar UUIDs determinísticos (padrão)')
    args = parser.parse_args()
    
    print("="*80)
    print("SEED E2E CANÔNICO - UUIDs Determinísticos")
    print(f"Versão: {SEED_VERSION}")
    print(f"Modo: {'DETERMINÍSTICO' if args.deterministic else 'RANDOM'}")
    print("="*80)
    print()
    
    # Conectar ao banco
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = False
    cursor = conn.cursor()
    
    try:
        print("PASSO 1: Verificar tabelas auxiliares...")
        verify_auxiliary_tables(cursor)
        print("OK - Tabelas auxiliares\n")
        
        print("PASSO 2: Criar 32 usuarios com IDs deterministicos...")
        user_ids = seed_users(cursor, args.deterministic)
        print(f"OK - Criados {len(user_ids)} usuarios\n")
        
        print("PASSO 3: Criar 16 teams...")
        team_ids = seed_teams(cursor, args.deterministic)
        print(f"OK - Criados {len(team_ids)} teams\n")
        
        print("PASSO 3.5: Vincular staff aos teams (team_memberships)...")
        team_memberships_staff = seed_team_memberships(cursor, team_ids, args.deterministic)
        print(f"OK - Criados {team_memberships_staff} team_memberships (staff apenas)\n")
        
        print("PASSO 4: Criar 240 athletes (15 por team)...")
        athlete_count = seed_athletes(cursor, team_ids, args.deterministic)
        print(f"OK - Criados {athlete_count} athletes com org_memberships\n")
        
        print("PASSO 4.5: Vincular atletas aos teams (team_memberships)...")
        team_memberships_total = seed_team_memberships(cursor, team_ids, args.deterministic)
        print(f"OK - Total team_memberships: {team_memberships_total} (staff + atletas)\n")
        
        print("PASSO 5: Criar 4 templates padrao...")
        template_ids = seed_templates(cursor, args.deterministic)
        print(f"OK - Criados {len(template_ids)} templates\n")
        
        print("PASSO 6: Criar cycles (2 macro + 4 meso)...")
        cycle_ids = seed_cycles(cursor, team_ids, args.deterministic)
        print(f"OK - Criados {len(cycle_ids)} cycles\n")
        
        print("PASSO 7: Criar 320 training sessions (20 por team)...")
        session_count = seed_training_sessions(cursor, team_ids, args.deterministic)
        print(f"OK - Criados {session_count} sessions\n")
        
        print("PASSO 8: Criar wellness data (pre + post)...")
        wellness_count = seed_wellness_data(cursor)
        print(f"OK - Criados {wellness_count} wellness records\n")
        
        print("PASSO 9: Criar 30 exercicios variados...")
        exercise_count = seed_exercises(cursor, args.deterministic)
        print(f"OK - Criados {exercise_count} exercicios\n")
        
        print("PASSO 10: Vincular exercicios as sessoes...")
        session_exercise_count = seed_session_exercises(cursor)
        print(f"OK - Criados {session_exercise_count} session_exercises\n")
        
        print("PASSO 11: Criar attendance (presencas)...")
        attendance_count = seed_attendance(cursor)
        print(f"OK - Criados {attendance_count} attendance records\n")
        
        print("PASSO 12: Criar microcycles semanais...")
        microcycle_count = seed_microcycles(cursor, team_ids, cycle_ids)
        print(f"OK - Criados {microcycle_count} microcycles\n")
        
        print("PASSO 13: Criar exercise favorites...")
        favorite_count = seed_exercise_favorites(cursor, exercise_count)
        print(f"OK - Criados {favorite_count} favoritos\n")
        
        print("PASSO 14: Criar athlete badges...")
        badge_count = seed_athlete_badges(cursor)
        print(f"OK - Criados {badge_count} badges\n")
        
        print("PASSO 15: Criar badges e rankings...")
        gamification_count = seed_gamification(cursor)
        print(f"OK - Criados {gamification_count} badges/rankings\n")
        
        print("PASSO 16: Criar notificacoes...")
        notification_count = seed_notifications(cursor)
        print(f"OK - Criados {notification_count} notifications\n")
        
        # Commit final
        conn.commit()
        
        print("\n" + "="*80)
        print("SEED CANONICO COMPLETO!")
        print("="*80)
        print("\nResumo:")
        print(f"  - {len(user_ids)} usuarios")
        print(f"  - {len(team_ids)} teams")
        print(f"  - {team_memberships_total} team_memberships (staff + atletas)")
        print(f"  - {athlete_count} athletes")
        print(f"  - {len(template_ids)} templates")
        print(f"  - {len(cycle_ids)} cycles")
        print(f"  - {microcycle_count} microcycles")
        print(f"  - {session_count} training sessions")
        print(f"  - {exercise_count} exercises")
        print(f"  - {session_exercise_count} session_exercises")
        print(f"  - {attendance_count} attendance records")
        print(f"  - {wellness_count} wellness records")
        print(f"  - {favorite_count} exercise favorites")
        print(f"  - {badge_count} athlete badges")
        print(f"  - {gamification_count} gamification items")
        print(f"  - {notification_count} notifications")
        print()
        print("Consulte SEED_CANONICO.md para mapeamento completo de IDs")
        print()
        
    except Exception as e:
        conn.rollback()
        print(f"\nERRO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()


# =============================================================================
# FUNÇÕES DE SEED
# =============================================================================

def verify_auxiliary_tables(cursor):
    """Verifica se tabelas auxiliares existem."""
    cursor.execute("SELECT COUNT(*) FROM categories")
    if cursor.fetchone()[0] == 0:
        raise RuntimeError("Tabela categories vazia! Execute seed inicial primeiro.")


def seed_users(cursor, deterministic: bool) -> List[uuid.UUID]:
    """Cria 32 usuários com IDs determinísticos."""
    user_ids = []
    
    # Criar organização E2E (se não existe)
    org_id = CanonicalIds.ORG_E2E
    cursor.execute("""
        INSERT INTO organizations (id, name, created_at)
        VALUES (%s, %s, NOW())
        ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name
    """, (str(org_id), 'E2E-HBTRACK-TEST-ORG'))
    
    # Criar 6 usuários principais (dirigente, coordenador, 2 treinadores, 2 atletas)
    main_users = [
        ('Admin', 'E2E', 'e2e.admin@teste.com', 1),  # role_id 1 = dirigente (admin é dirigente)
        ('Coordenador', 'E2E', 'e2e.coordenador@teste.com', 2),  # role_id 2
        ('Treinador', 'E2E', 'e2e.treinador@teste.com', 3),
        ('Treinador', 'Auxiliar E2E', 'treinador2@e2e.teste', 3),
        ('Atleta', 'E2E', 'e2e.atleta@teste.com', 4),  # role_id 4 = atleta
        ('Maria', 'Santos', 'maria.santos@e2e.teste', 4),
    ]
    
    password_hash = bcrypt.hashpw('Admin@123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    for first_name, last_name, email, role_id in main_users:
        user_id = deterministic_uuid("users", email)
        person_id = deterministic_uuid("persons", email)
        full_name = f"{first_name} {last_name}"
        
        # Person
        cursor.execute("""
            INSERT INTO persons (id, full_name, first_name, last_name, gender, birth_date, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
            ON CONFLICT (id) DO UPDATE SET full_name = EXCLUDED.full_name
        """, (str(person_id), full_name, first_name, last_name, 'masculino', '1990-01-01'))
        
        # User
        cursor.execute("""
            INSERT INTO users (id, person_id, email, password_hash)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET email = EXCLUDED.email
        """, (str(user_id), str(person_id), email, password_hash))
        
        # Org Membership
        cursor.execute("""
            INSERT INTO org_memberships (person_id, organization_id, role_id, start_at)
            VALUES (%s, %s, %s, NOW())
            ON CONFLICT (person_id, organization_id, role_id) 
            WHERE end_at IS NULL AND deleted_at IS NULL
            DO NOTHING
        """, (str(person_id), str(org_id), role_id))
        
        user_ids.append(user_id)
    
    # Criar 26 usuários adicionais (atletas para preencher teams)
    for i in range(26):
        email = f"atleta{i+3}@e2e.teste"
        first_name = f"Atleta"
        last_name = f"E2E {i+3}"
        full_name = f"{first_name} {last_name}"
        
        user_id = deterministic_uuid("users", email)
        person_id = deterministic_uuid("persons", email)
        
        cursor.execute("""
            INSERT INTO persons (id, full_name, first_name, last_name, gender, birth_date, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
            ON CONFLICT (id) DO UPDATE SET full_name = EXCLUDED.full_name
        """, (str(person_id), full_name, first_name, last_name, 'masculino', '2000-01-01'))
        
        cursor.execute("""
            INSERT INTO users (id, person_id, email, password_hash)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET email = EXCLUDED.email
        """, (str(user_id), str(person_id), email, password_hash))
        
        cursor.execute("""
            INSERT INTO org_memberships (person_id, organization_id, role_id, start_at)
            VALUES (%s, %s, %s, NOW())
            ON CONFLICT (person_id, organization_id, role_id) 
            WHERE end_at IS NULL AND deleted_at IS NULL
            DO NOTHING
        """, (str(person_id), str(org_id), 4))
        
        user_ids.append(user_id)
    
    return user_ids


def seed_teams(cursor, deterministic: bool) -> List[Tuple[uuid.UUID, str, int]]:
    """Cria 16 teams (2 por categoria x 2 gêneros)."""
    org_id = CanonicalIds.ORG_E2E
    teams = []
    
    for categoria in CATEGORIAS:
        for genero in ['masculino', 'feminino']:
            for num in [1, 2]:
                slug = f"{categoria['slug']}-{genero[0]}-{num:02d}"
                name = f"E2E-{categoria['name']}-{genero.capitalize()}-{num:02d}"
                
                team_id = deterministic_uuid("teams", slug)
                
                # Team (CRIAR ANTES DE SEASON)
                cursor.execute("""
                    INSERT INTO teams (id, organization_id, name, category_id, gender, created_at)
                    VALUES (%s, %s, %s, %s, %s, NOW())
                    ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name
                """, (str(team_id), str(org_id), name, categoria['id'], genero))
                
                # Season (CRIAR DEPOIS DE TEAM)
                season_id = deterministic_uuid("seasons", f"{slug}-2026")
                cursor.execute("""
                    INSERT INTO seasons (id, team_id, year, name, start_date, end_date, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, NOW())
                    ON CONFLICT (id) DO NOTHING
                """, (str(season_id), str(team_id), 2026, 'Temporada 2026', '2026-01-01', '2026-12-31'))
                
                teams.append((team_id, genero, categoria['id']))
    
    return teams


def seed_team_memberships(cursor, teams: List[Tuple[uuid.UUID, str, int]], deterministic: bool) -> int:
    """
    Vincula TODOS os usuários (staff + atletas) às equipes via team_memberships.
    
    Estratégia de vinculação:
    - Coordenador: TODOS os 16 teams (role organizacional global)
    - Treinador 1: 8 teams masculinos
    - Treinador 2: 8 teams femininos
    - Atletas: vinculados ao seu team via person_id do athlete
    
    Returns:
        Quantidade de team_memberships criados
    """
    org_id = CanonicalIds.ORG_E2E
    count = 0
    
    # 1. Buscar staff members (dirigente, coordenador, treinadores)
    cursor.execute("""
        SELECT om.person_id, om.id as org_membership_id, r.id as role_id, u.email
        FROM org_memberships om
        JOIN roles r ON r.id = om.role_id
        JOIN users u ON u.person_id = om.person_id
        WHERE om.organization_id = %s
        AND r.id IN (1, 2, 3)  -- dirigente, coordenador, treinador
        AND om.deleted_at IS NULL
        ORDER BY r.id, u.email
    """, (str(org_id),))
    
    staff_members = cursor.fetchall()
    
    # 2. Vincular coordenador a TODOS os teams
    coordenadores = [s for s in staff_members if s[2] == 2]  # role_id == 2
    for person_id, org_membership_id, role_id, email in coordenadores:
        for team_id, genero, categoria_id in teams:
            tm_id = deterministic_uuid("team_memberships", f"{person_id}-{team_id}")
            cursor.execute("""
                INSERT INTO team_memberships (
                    id, person_id, team_id, org_membership_id, 
                    status, start_at, created_at
                )
                VALUES (%s, %s, %s, %s, 'ativo', '2026-01-01', NOW())
                ON CONFLICT (id) DO UPDATE SET status = 'ativo'
            """, (str(tm_id), str(person_id), str(team_id), str(org_membership_id)))
            count += 1
    
    # 3. Vincular treinadores por gênero
    treinadores = [s for s in staff_members if s[2] == 3]  # role_id == 3
    
    if len(treinadores) >= 2:
        # Treinador 1 → teams masculinos
        treinador1 = treinadores[0]
        teams_masculinos = [t for t in teams if t[1] == 'masculino']
        for team_id, genero, categoria_id in teams_masculinos:
            tm_id = deterministic_uuid("team_memberships", f"{treinador1[0]}-{team_id}")
            cursor.execute("""
                INSERT INTO team_memberships (
                    id, person_id, team_id, org_membership_id, 
                    status, start_at, created_at
                )
                VALUES (%s, %s, %s, %s, 'ativo', '2026-01-01', NOW())
                ON CONFLICT (id) DO UPDATE SET status = 'ativo'
            """, (str(tm_id), str(treinador1[0]), str(team_id), str(treinador1[1])))
            count += 1
        
        # Treinador 2 → teams femininos
        treinador2 = treinadores[1]
        teams_femininos = [t for t in teams if t[1] == 'feminino']
        for team_id, genero, categoria_id in teams_femininos:
            tm_id = deterministic_uuid("team_memberships", f"{treinador2[0]}-{team_id}")
            cursor.execute("""
                INSERT INTO team_memberships (
                    id, person_id, team_id, org_membership_id, 
                    status, start_at, created_at
                )
                VALUES (%s, %s, %s, %s, 'ativo', '2026-01-01', NOW())
                ON CONFLICT (id) DO UPDATE SET status = 'ativo'
            """, (str(tm_id), str(treinador2[0]), str(team_id), str(treinador2[1])))
            count += 1
    
    # 4. Vincular ATLETAS aos seus teams via person_id
    cursor.execute("""
        SELECT DISTINCT a.person_id, tr.team_id, om.id as org_membership_id
        FROM athletes a
        JOIN team_registrations tr ON tr.athlete_id = a.id
        JOIN org_memberships om ON om.person_id = a.person_id
        WHERE om.organization_id = %s
        AND tr.deleted_at IS NULL
        AND a.deleted_at IS NULL
    """, (str(org_id),))
    
    athletes_teams = cursor.fetchall()
    
    for person_id, team_id, org_membership_id in athletes_teams:
        tm_id = deterministic_uuid("team_memberships", f"{person_id}-{team_id}")
        cursor.execute("""
            INSERT INTO team_memberships (
                id, person_id, team_id, org_membership_id, 
                status, start_at, created_at
            )
            VALUES (%s, %s, %s, %s, 'ativo', '2026-01-01', NOW())
            ON CONFLICT (id) DO UPDATE SET status = 'ativo'
        """, (str(tm_id), str(person_id), str(team_id), str(org_membership_id)))
        count += 1
    
    return count


def seed_athletes(cursor, teams: List[Tuple], deterministic: bool) -> int:
    """Cria 15 atletas por team (240 total) com org_memberships e todas as posições."""
    count = 0
    org_id = CanonicalIds.ORG_E2E
    
    for team_id, genero, categoria_id in teams:
        nomes = NOMES_FEMININOS if genero == 'feminino' else NOMES_MASCULINOS
        
        for i in range(15):
            first_name = nomes[i % len(nomes)]
            last_name = SOBRENOMES[i % len(SOBRENOMES)]
            full_name = f"{first_name} {last_name}"
            slug = f"{first_name.lower()}-{last_name.lower()}-{str(team_id)[:8]}-{i}"
            
            person_id = deterministic_uuid("persons", slug)
            athlete_id = deterministic_uuid("athletes", slug)
            
            # Calcular birth_year com variação para ter atletas de 13-14 anos na categoria infantil
            if categoria_id == 2:  # Infantil (12-14 anos) → 2010-2013
                birth_year = 2012 + (i % 2)  # Alterna 2012, 2013
            elif categoria_id == 3:  # Cadete (15-17 anos) → 2007-2009
                birth_year = 2007 + (i % 3)
            elif categoria_id == 4:  # Juvenil (18-20 anos) → 2004-2006
                birth_year = 2004 + (i % 3)
            else:  # Adulto (21+ anos) → 1995-2000
                birth_year = 1995 + (i % 6)
            
            birth_month = 3 + (i % 10)  # Meses 3-12
            birth_day = 5 + (i % 23)  # Dias 5-27
            
            # Person
            cursor.execute("""
                INSERT INTO persons (id, full_name, first_name, last_name, gender, birth_date, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
                ON CONFLICT (id) DO UPDATE SET full_name = EXCLUDED.full_name
            """, (str(person_id), full_name, first_name, last_name, genero, f"{birth_year}-{birth_month:02d}-{birth_day:02d}"))
            
            # Posições (goleiro tem IDs diferentes, linha tem posições normais)
            is_goleiro = (i == 0)
            position_def_main = 5 if is_goleiro else ((i % 4) + 1)  # 5=goleiro, 1-4=linha
            position_def_sec = None if is_goleiro else (((i + 1) % 4) + 1) if i % 3 == 0 else None
            position_off_main = 1 if is_goleiro else ((i % 5) + 1)  # 1=goleiro ofensivo, 2-6=posições
            position_off_sec = None if is_goleiro else (((i + 2) % 5) + 1) if i % 3 == 0 else None
            
            # Athlete com TODAS as posições + organization_id
            cursor.execute("""
                INSERT INTO athletes (
                    id, person_id, organization_id, athlete_name, birth_date, 
                    main_defensive_position_id, secondary_defensive_position_id,
                    main_offensive_position_id, secondary_offensive_position_id,
                    shirt_number, state, created_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'ativa', NOW())
                ON CONFLICT (id) DO UPDATE SET 
                    athlete_name = EXCLUDED.athlete_name,
                    organization_id = EXCLUDED.organization_id,
                    main_offensive_position_id = EXCLUDED.main_offensive_position_id,
                    secondary_offensive_position_id = EXCLUDED.secondary_offensive_position_id,
                    secondary_defensive_position_id = EXCLUDED.secondary_defensive_position_id
            """, (str(athlete_id), str(person_id), str(org_id), full_name, f"{birth_year}-{birth_month:02d}-{birth_day:02d}",
                  position_def_main, position_def_sec, position_off_main, position_off_sec, i+1))
            
            # Org Membership (CRÍTICO: atletas precisam estar na organização)
            cursor.execute("""
                INSERT INTO org_memberships (person_id, organization_id, role_id, start_at)
                VALUES (%s, %s, %s, NOW())
                ON CONFLICT (person_id, organization_id, role_id) 
                WHERE end_at IS NULL AND deleted_at IS NULL
                DO NOTHING
            """, (str(person_id), str(org_id), 4))  # role_id 4 = atleta
            
            # Team Registration
            cursor.execute("""
                INSERT INTO team_registrations (athlete_id, team_id, start_at, created_at)
                VALUES (%s, %s, %s, NOW())
                ON CONFLICT (athlete_id, team_id) 
                WHERE deleted_at IS NULL AND end_at IS NULL
                DO NOTHING
            """, (str(athlete_id), str(team_id), '2026-01-01'))
            
            count += 1
    
    return count


def seed_templates(cursor, deterministic: bool) -> List[uuid.UUID]:
    """Cria 4 templates padrão."""
    org_id = CanonicalIds.ORG_E2E
    templates = [
        (CanonicalIds.TEMPLATE_TATICO, 'Tático Ofensivo', 'Foco em ataque posicional', 'target', 45, 10, 25, 5, 10, 0, 5, True),
        (CanonicalIds.TEMPLATE_FISICO, 'Físico Intensivo', 'Alta intensidade física', 'flame', 5, 5, 5, 5, 10, 10, 60, True),
        (CanonicalIds.TEMPLATE_EQUILIBRADO, 'Equilibrado', 'Distribuição uniforme', 'activity', 15, 15, 15, 15, 10, 10, 20, False),
        (CanonicalIds.TEMPLATE_DEFESA, 'Defesa Posicional', 'Foco defensivo', 'shield', 5, 50, 5, 30, 0, 5, 5, False),
    ]
    
    template_ids = []
    for template in templates:
        cursor.execute("""
            INSERT INTO session_templates (
                id, org_id, name, description, icon,
                focus_attack_positional_pct, focus_defense_positional_pct,
                focus_transition_offense_pct, focus_transition_defense_pct,
                focus_attack_technical_pct, focus_defense_technical_pct,
                focus_physical_pct, is_favorite, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            ON CONFLICT (org_id, name) DO UPDATE SET 
                description = EXCLUDED.description,
                icon = EXCLUDED.icon
        """, (str(template[0]), str(org_id), *template[1:]))
        template_ids.append(template[0])
    
    return template_ids


def seed_cycles(cursor, teams: List[Tuple], deterministic: bool) -> List[uuid.UUID]:
    """Cria cycles (2 macro + 4 meso por team principal)."""
    # Simplificado: criar apenas para primeiro team
    team_id = teams[0][0]
    cycle_ids = []
    
    # Macrociclo Preparatório
    macro1_id = CanonicalIds.MACRO_PREPARATORIO
    cursor.execute("""
        INSERT INTO training_cycles (
            id, organization_id, team_id, type, start_date, end_date, objective, status, created_by_user_id, created_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        ON CONFLICT (id) DO UPDATE SET objective = EXCLUDED.objective
    """, (str(macro1_id), str(CanonicalIds.ORG_E2E), str(team_id), 'macro', '2026-01-01', '2026-06-30', 'Preparação física base', 'active', str(CanonicalIds.USER_COORDENADOR)))
    cycle_ids.append(macro1_id)
    
    # Mesociclo Fase 1
    meso1_id = CanonicalIds.MESO_FASE1
    cursor.execute("""
        INSERT INTO training_cycles (
            id, organization_id, team_id, parent_cycle_id, type, start_date, end_date, objective, status, created_by_user_id, created_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        ON CONFLICT (id) DO UPDATE SET objective = EXCLUDED.objective
    """, (str(meso1_id), str(CanonicalIds.ORG_E2E), str(team_id), str(macro1_id), 'meso', '2026-01-01', '2026-02-28', 'Fase 1 - Resistência', 'active', str(CanonicalIds.USER_COORDENADOR)))
    cycle_ids.append(meso1_id)
    
    return cycle_ids


def seed_training_sessions(cursor, teams: List[Tuple], deterministic: bool) -> int:
    """Cria 20 training sessions por team (10 passadas + 10 futuras)."""
    count = 0
    today = datetime.now()
    
    for team_id, genero, categoria_id in teams[:3]:  # Primeiros 3 teams para teste
        cursor.execute("SELECT id FROM seasons WHERE team_id = %s LIMIT 1", (str(team_id),))
        season_row = cursor.fetchone()
        if not season_row:
            continue
        season_id = season_row[0]
        
        # 10 sessões passadas
        for i in range(10):
            days_ago = 30 - (i * 3)
            session_date = today - timedelta(days=days_ago)
            slug = f"{str(team_id)[:8]}-{session_date.strftime('%Y-%m-%d')}-tatico"
            
            session_id = deterministic_uuid("sessions", slug)
            
            cursor.execute("""
                INSERT INTO training_sessions (
                    id, organization_id, team_id, session_at, session_type,
                    main_objective, duration_planned_minutes, location,
                    status, created_by_user_id, started_at, ended_at, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                ON CONFLICT (id) DO UPDATE SET main_objective = EXCLUDED.main_objective
            """, (
                str(session_id),
                str(CanonicalIds.ORG_E2E),
                str(team_id),
                session_date,
                'quadra',
                f'Treino tático #{i+1}',
                90,
                'Ginásio Principal',
                'readonly',
                str(CanonicalIds.USER_COORDENADOR),
                session_date,
                session_date + timedelta(minutes=90),
            ))
            count += 1
        
        # 10 sessões futuras
        for i in range(10):
            days_ahead = (i * 3) + 1
            session_date = today + timedelta(days=days_ahead)
            slug = f"{str(team_id)[:8]}-{session_date.strftime('%Y-%m-%d')}-fisico"
            
            session_id = deterministic_uuid("sessions", slug)
            
            cursor.execute("""
                INSERT INTO training_sessions (
                    id, organization_id, team_id, session_at, session_type,
                    main_objective, duration_planned_minutes, location,
                    status, created_by_user_id, started_at, ended_at, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                ON CONFLICT (id) DO UPDATE SET main_objective = EXCLUDED.main_objective
            """, (
                str(session_id),
                str(CanonicalIds.ORG_E2E),
                str(team_id),
                session_date,
                'quadra',
                f'Treino físico #{i+1}',
                90,
                'Ginásio Principal',
                'scheduled',
                str(CanonicalIds.USER_COORDENADOR),
                None,
                None,
            ))
            count += 1
    
    return count


def seed_wellness_data(cursor) -> int:
    """
    Cria wellness_pre e wellness_post para TODOS os atletas em sessões encerradas.
    Usa execute_values para batch processing (performance).
    Valores seguem distribuição mais realística.
    """
    org_id = str(CanonicalIds.ORG_E2E)
    user_id = str(CanonicalIds.USER_COORDENADOR)
    
    # Buscar TODAS as combinações session × athlete (sem LIMIT)
    cursor.execute("""
        SELECT ts.id, tr.id as reg_id, tr.athlete_id
        FROM training_sessions ts
        JOIN team_registrations tr ON tr.team_id = ts.team_id AND tr.end_at IS NULL
        WHERE ts.status IN ('pending_review', 'readonly')
        ORDER BY ts.session_at DESC
    """)
    
    rows = cursor.fetchall()
    
    if not rows:
        print("  AVISO: Nenhuma sessão fechada encontrada")
        return 0
    
    # Preparar dados em batch para wellness_pre
    wellness_pre_data = []
    wellness_post_data = []
    
    for session_id, reg_id, athlete_id in rows:
        # Verificar se já existe wellness_pre
        cursor.execute("""
            SELECT COUNT(*) FROM wellness_pre 
            WHERE training_session_id = %s AND athlete_id = %s
        """, (session_id, athlete_id))
        
        if cursor.fetchone()[0] == 0:
            # Gerar valores realísticos usando hash determinístico
            seed_hash = hash(f"{session_id}{athlete_id}")
            
            # Sleep hours: distribuição normal ~7.5h (6.0-9.0)
            sleep_hours = 7.5 + ((seed_hash % 60) - 30) / 20.0  # 6.0-9.0h
            sleep_hours = max(5.0, min(9.5, sleep_hours))
            
            # Sleep quality: 3-5 (maioria 4)
            sleep_quality = 4 if (seed_hash % 10) < 7 else (3 if (seed_hash % 10) < 9 else 5)
            
            # Fatigue: 1-5 (maioria 2-3)
            fatigue = 2 + ((seed_hash % 100) // 25)  # Distribuição: 2(25%), 3(25%), 4(25%), 5(25%)
            
            # Stress: 1-5 (maioria baixo)
            stress = 1 + ((seed_hash % 100) // 33)  # Maioria 1-2
            stress = min(5, stress)
            
            # Muscle soreness: 1-5 (correlacionado com fadiga)
            muscle_soreness = max(1, min(5, fatigue + ((seed_hash % 3) - 1)))
            
            # Readiness: calculado baseado nos outros (7-10)
            readiness = 10 - ((fatigue + stress + (5 - sleep_quality)) // 3)
            readiness = max(5, min(10, readiness))
            
            wellness_pre_data.append((
                org_id, session_id, athlete_id,
                round(sleep_hours, 1), sleep_quality, fatigue, stress, muscle_soreness,
                readiness, user_id
            ))
        
        # Verificar se já existe wellness_post
        cursor.execute("""
            SELECT COUNT(*) FROM wellness_post 
            WHERE training_session_id = %s AND athlete_id = %s
        """, (session_id, athlete_id))
        
        if cursor.fetchone()[0] == 0:
            seed_hash = hash(f"{session_id}{athlete_id}post")
            
            # RPE: 4-9 (maioria 5-7)
            rpe = 5 + ((seed_hash % 100) // 20)  # 5-9
            rpe = min(9, rpe)
            
            # Fatigue after: 3-8 (correlacionado com RPE)
            fatigue_after = min(8, max(3, rpe - 1 + ((seed_hash % 3) - 1)))
            
            # Mood after: 3-5 (maioria bom)
            mood_after = 4 if (seed_hash % 10) < 7 else (3 if (seed_hash % 10) < 9 else 5)
            
            # Muscle soreness after: 2-6
            muscle_soreness_after = 3 + ((seed_hash % 100) // 25)
            
            wellness_post_data.append((
                org_id, session_id, athlete_id,
                rpe, fatigue_after, mood_after, muscle_soreness_after, user_id
            ))
    
    # Batch insert wellness_pre
    if wellness_pre_data:
        execute_values(
            cursor,
            """
            INSERT INTO wellness_pre (
                organization_id, training_session_id, athlete_id,
                sleep_hours, sleep_quality, fatigue_pre, stress_level, muscle_soreness,
                readiness_score, filled_at, created_by_user_id, created_at
            ) VALUES %s
            """,
            wellness_pre_data,
            template="(%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW() - INTERVAL '1 day', %s, NOW())"
        )
    
    # Batch insert wellness_post
    if wellness_post_data:
        execute_values(
            cursor,
            """
            INSERT INTO wellness_post (
                organization_id, training_session_id, athlete_id,
                session_rpe, fatigue_after, mood_after,
                muscle_soreness_after, filled_at, created_by_user_id, created_at
            ) VALUES %s
            """,
            wellness_post_data,
            template="(%s, %s, %s, %s, %s, %s, %s, NOW() - INTERVAL '12 hours', %s, NOW())"
        )
    
    total_count = len(wellness_pre_data) + len(wellness_post_data)
    print(f"  - {len(wellness_pre_data)} wellness_pre criados")
    print(f"  - {len(wellness_post_data)} wellness_post criados")
    
    return total_count


def seed_gamification(cursor) -> int:
    """Cria badges e rankings (placeholder)."""
    # Implementação simplificada - apenas retorna 0 por enquanto
    return 0


def seed_notifications(cursor) -> int:
    """Cria notificações (placeholder)."""
    # Implementação simplificada - apenas retorna 0 por enquanto
    return 0


def seed_exercises(cursor, deterministic: bool) -> int:
    """Cria 30 exercícios variados vinculados à organização e tags."""
    org_id = CanonicalIds.ORG_E2E
    user_id = CanonicalIds.USER_COORDENADOR
    
    # Buscar algumas tags para vincular
    cursor.execute("SELECT id FROM exercise_tags WHERE is_active = TRUE ORDER BY display_order LIMIT 20")
    tag_rows = cursor.fetchall()
    tag_ids = [row[0] for row in tag_rows]
    
    if not tag_ids:
        print("  AVISO: Nenhuma tag encontrada, exercícios criados sem tags")
        tag_ids = [None]
    
    exercises = [
        ('Aquecimento Dinâmico', 'Movimentação com bola em duplas', ['Aquecimento'], 'Técnico'),
        ('Passe em Movimento', 'Passes progressivos com deslocamento', ['Fundamentos', 'Passe'], 'Técnico'),
        ('Arremesso de 7 metros', 'Treino de penalty com goleiro', ['Arremesso'], 'Técnico'),
        ('Defesa 6-0', 'Posicionamento defensivo base', ['Defesa', 'Sistema'], 'Tático'),
        ('Ataque Posicional', 'Circulação de bola no ataque', ['Ataque', 'Sistema'], 'Tático'),
        ('Contraataque 2x1', 'Superioridade numérica', ['Contraataque'], 'Tático'),
        ('Transição Defesa-Ataque', 'Recuperação rápida após perda', ['Transição'], 'Tático'),
        ('Finalização 1x1', 'Duelo atacante vs goleiro', ['Arremesso', '1x1'], 'Técnico'),
        ('Drible e Finta', 'Movimentos de finta com bola', ['Fundamentos', 'Drible'], 'Técnico'),
        ('Jogo Reduzido 3x3', 'Espaço reduzido com metas pequenas', ['Jogo'], 'Tático'),
        ('Circuit Training', 'Circuito de força e resistência', ['Físico'], 'Físico'),
        ('Velocidade com Bola', 'Sprint com mudanças de direção', ['Físico', 'Velocidade'], 'Físico'),
        ('Coordenação Motora', 'Escada de agilidade e cones', ['Físico', 'Coordenação'], 'Físico'),
        ('Bloqueio Defensivo', 'Técnica de bloqueio no pivô', ['Defesa', 'Pivô'], 'Técnico'),
        ('Pivô Ofensivo', 'Movimentação e finalização do pivô', ['Ataque', 'Pivô'], 'Técnico'),
        ('Defesa Individual', 'Marcação homem a homem', ['Defesa'], 'Tático'),
        ('Ataque 3-3', 'Sistema ofensivo com 3 armadores', ['Ataque', 'Sistema'], 'Tático'),
        ('Goleiro - Reflexos', 'Trabalho de reação e posicionamento', ['Goleiro'], 'Técnico'),
        ('Cruzamentos', 'Passes cruzados entre alas e pontas', ['Fundamentos', 'Passe'], 'Técnico'),
        ('Pressing Alto', 'Pressão defensiva avançada', ['Defesa', 'Pressão'], 'Tático'),
        ('Jogo de Ponta', 'Movimentação e finalizações das pontas', ['Ataque'], 'Tático'),
        ('Situação 2x2', 'Duelos em superioridade/inferioridade', ['Jogo'], 'Tático'),
        ('Resistência Anaeróbica', 'Tiros de alta intensidade', ['Físico'], 'Físico'),
        ('Recepção e Passe', 'Domínio e distribuição rápida', ['Fundamentos', 'Passe'], 'Técnico'),
        ('Defesa Mista', 'Combinação de zona e individual', ['Defesa', 'Sistema'], 'Tático'),
        ('Ataque Rápido', 'Transição veloz após recuperação', ['Contraataque'], 'Tático'),
        ('Drible em Velocidade', 'Ultrapassagens em alta velocidade', ['Drible', 'Velocidade'], 'Técnico'),
        ('Jogo Posicional 5x5', 'Meia quadra com sistemas definidos', ['Jogo'], 'Tático'),
        ('Core Stability', 'Fortalecimento do core', ['Físico', 'Força'], 'Físico'),
        ('Vídeo Analysis', 'Análise tática em sala', ['Tático'], 'Vídeo'),
    ]
    
    count = 0
    for name, description, tag_names, category in exercises:
        exercise_id = deterministic_uuid("exercises", f"{org_id}-{name.lower().replace(' ', '-')}")
        
        # Pegar até 2 tags aleatórias (usar tag_ids disponíveis como strings)
        selected_tags = [str(t) for t in tag_ids[:min(2, len(tag_ids))]]
        
        # Converter para formato PostgreSQL array de UUIDs
        tags_array = '{' + ','.join(selected_tags) + '}' if selected_tags else '{}'
        
        cursor.execute("""
            INSERT INTO exercises (
                id, organization_id, name, description, tag_ids, category,
                created_by_user_id, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s::uuid[], %s, %s, NOW(), NOW())
            ON CONFLICT (id) DO UPDATE SET 
                description = EXCLUDED.description,
                category = EXCLUDED.category
        """, (
            str(exercise_id),
            str(org_id),
            name,
            description,
            tags_array,
            category,
            str(user_id)
        ))
        count += 1
    
    return count


def seed_session_exercises(cursor) -> int:
    """Vincula 3-5 exercícios a cada sessão encerrada."""
    org_id = CanonicalIds.ORG_E2E
    
    # Buscar exercícios criados
    cursor.execute("SELECT id FROM exercises WHERE organization_id = %s ORDER BY name", (str(org_id),))
    exercise_rows = cursor.fetchall()
    exercise_ids = [row[0] for row in exercise_rows]
    
    if not exercise_ids:
        print("  AVISO: Nenhum exercício encontrado")
        return 0
    
    # Buscar sessões fechadas
    cursor.execute("""
        SELECT id FROM training_sessions 
        WHERE organization_id = %s AND status IN ('pending_review', 'readonly')
        ORDER BY session_at DESC
        LIMIT 50
    """, (str(org_id),))
    
    session_rows = cursor.fetchall()
    count = 0
    
    for session_row in session_rows:
        session_id = session_row[0]
        
        # Adicionar 3-5 exercícios por sessão
        num_exercises = min(4, len(exercise_ids))
        for i in range(num_exercises):
            exercise_id = exercise_ids[i % len(exercise_ids)]
            se_id = deterministic_uuid("session_exercises", f"{session_id}-{exercise_id}-{i}")
            
            cursor.execute("""
                INSERT INTO training_session_exercises (
                    id, session_id, exercise_id, order_index, duration_minutes,
                    created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
                ON CONFLICT (id) DO UPDATE SET order_index = EXCLUDED.order_index
            """, (
                str(se_id),
                str(session_id),
                str(exercise_id),
                i,
                20
            ))
            count += 1
    
    return count


def seed_attendance(cursor) -> int:
    """Cria registros de presença para sessões encerradas."""
    org_id = CanonicalIds.ORG_E2E
    user_id = CanonicalIds.USER_COORDENADOR
    
    # Buscar sessões fechadas com seus times
    cursor.execute("""
        SELECT ts.id, ts.team_id
        FROM training_sessions ts
        WHERE ts.organization_id = %s 
        AND ts.status IN ('pending_review', 'readonly')
        ORDER BY ts.session_at DESC
        LIMIT 30
    """, (str(org_id),))
    
    sessions = cursor.fetchall()
    count = 0
    
    for session_id, team_id in sessions:
        # Buscar team_registrations do time (atletas registrados)
        cursor.execute("""
            SELECT tr.id, tr.athlete_id
            FROM team_registrations tr
            JOIN athletes a ON a.id = tr.athlete_id
            WHERE tr.team_id = %s 
            AND tr.deleted_at IS NULL
            AND a.deleted_at IS NULL
            ORDER BY tr.created_at
            LIMIT 15
        """, (str(team_id),))
        
        registrations = cursor.fetchall()
        
        for idx, (reg_id, athlete_id) in enumerate(registrations):
            # 85% presentes, 15% ausentes
            is_present = idx % 7 != 0  # A cada 7, um ausente
            
            attendance_id = deterministic_uuid("attendance", f"{session_id}-{athlete_id}")
            
            # Verificar se já existe
            cursor.execute("""
                SELECT COUNT(*) FROM attendance 
                WHERE training_session_id = %s AND athlete_id = %s
            """, (str(session_id), str(athlete_id)))
            
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO attendance (
                        id, training_session_id, team_registration_id, athlete_id,
                        presence_status, minutes_effective, source, participation_type,
                        created_at, created_by_user_id, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s, NOW())
                """, (
                    str(attendance_id),
                    str(session_id),
                    str(reg_id),
                    str(athlete_id),
                    'present' if is_present else 'absent',
                    90 if is_present else 0,
                    'manual',
                    'full' if is_present else None,
                    str(user_id)
                ))
                count += 1
    
    return count


def seed_microcycles(cursor, teams: List[Tuple], cycle_ids: List[uuid.UUID]) -> int:
    """Cria microciclos semanais para os primeiros 3 teams."""
    org_id = CanonicalIds.ORG_E2E
    user_id = CanonicalIds.USER_COORDENADOR
    count = 0
    
    # Criar microciclos apenas para o primeiro team que tem mesocycle
    if not cycle_ids or len(cycle_ids) < 2:
        return 0
    
    meso_id = cycle_ids[1]  # Segundo cycle é o mesocycle
    team_id = teams[0][0] if teams else None
    
    if not team_id:
        return 0
    
    # Criar 8 semanas de microciclos (2 meses)
    start_date = date(2026, 1, 6)  # Primeira segunda-feira de janeiro
    
    for week_num in range(8):
        week_start = start_date + timedelta(weeks=week_num)
        week_end = week_start + timedelta(days=6)
        
        micro_id = deterministic_uuid("microcycles", f"{team_id}-2026-W{week_num+1:02d}")
        
        cursor.execute("""
            INSERT INTO training_microcycles (
                id, organization_id, team_id, cycle_id,
                week_start, week_end, microcycle_type,
                planned_focus_attack_positional_pct, planned_focus_defense_positional_pct,
                planned_focus_transition_offense_pct, planned_focus_transition_defense_pct,
                planned_focus_attack_technical_pct, planned_focus_defense_technical_pct,
                planned_focus_physical_pct, planned_weekly_load,
                created_by_user_id, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            ON CONFLICT (id) DO UPDATE SET microcycle_type = EXCLUDED.microcycle_type
        """, (
            str(micro_id),
            str(org_id),
            str(team_id),
            str(meso_id),
            week_start,
            week_end,
            'normal',
            20.0, 20.0, 15.0, 15.0, 10.0, 10.0, 10.0,
            3000,  # planned_weekly_load
            str(user_id)
        ))
        count += 1
    
    return count


def seed_exercise_favorites(cursor, exercise_count: int) -> int:
    """Cria favoritos de exercícios para treinadores."""
    org_id = CanonicalIds.ORG_E2E
    
    # Buscar exercícios
    cursor.execute("SELECT id FROM exercises WHERE organization_id = %s ORDER BY name LIMIT 10", (str(org_id),))
    exercise_rows = cursor.fetchall()
    
    if not exercise_rows:
        return 0
    
    # Buscar treinadores
    treinadores = [
        CanonicalIds.USER_COORDENADOR,
        CanonicalIds.USER_TREINADOR
    ]
    
    count = 0
    for user_id in treinadores:
        # Cada treinador favorita 5 exercícios
        for i, (exercise_id,) in enumerate(exercise_rows[:5]):
            cursor.execute("""
                INSERT INTO exercise_favorites (user_id, exercise_id, created_at)
                VALUES (%s, %s, NOW())
                ON CONFLICT (user_id, exercise_id) DO NOTHING
            """, (str(user_id), str(exercise_id)))
            count += 1
    
    return count


def seed_athlete_badges(cursor) -> int:
    """Cria badges para atletas com boa performance em wellness."""
    # Buscar atletas que têm wellness_pre preenchido
    cursor.execute("""
        SELECT DISTINCT wp.athlete_id, COUNT(*) as wellness_count
        FROM wellness_pre wp
        GROUP BY wp.athlete_id
        HAVING COUNT(*) >= 5
        ORDER BY wellness_count DESC
        LIMIT 10
    """)
    
    athletes = cursor.fetchall()
    count = 0
    
    for athlete_id, wellness_count in athletes:
        badge_id = deterministic_uuid("badges", f"{athlete_id}-wellness-champion")
        
        cursor.execute("""
            INSERT INTO athlete_badges (
                id, athlete_id, badge_type, month_reference, earned_at
            ) VALUES (%s, %s, %s, %s, NOW())
            ON CONFLICT (id) DO NOTHING
        """, (
            str(badge_id),
            str(athlete_id),
            'wellness_champion_monthly',
            '2026-01-01'
        ))
        count += 1
    
    return count


# =============================================================================
# EXECUÇÃO
# =============================================================================

if __name__ == '__main__':
    main()
