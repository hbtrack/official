#!/usr/bin/env python3
"""
Script de Seed E2E - Ambiente de Testes Determinísticos

Execução: python scripts/seed_e2e.py

IMPORTANTE: Este script é IDEMPOTENTE
- Pode rodar 10x sem duplicar dados
- Usa UUIDs fixos para consistência
- Pertence ao namespace E2E isolado

SEED MÍNIMO:
- Organização E2E (UUID fixo)
- Temporada E2E ativa
- 6 usuários: admin, dirigente, coordenador, treinador, atleta, membro
- Roles e categories (se não existem)

REGRAS:
- Todos os dados E2E usam prefixo "E2E-" ou email "@e2e.teste"
- Nunca afeta dados de produção/desenvolvimento
- Cleanup via globalTeardown do Playwright
"""
import os
import sys
from pathlib import Path
from datetime import datetime, date
from uuid import UUID

from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_values
import bcrypt

# =============================================================================
# CONFIGURAÇÃO
# =============================================================================

# Carrega .env do backend
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL não definido. Configure .env.")

# Converte URL SQLAlchemy para formato libpq (psycopg2 direto)
# postgresql+psycopg2://... → postgresql://...
# postgresql+asyncpg://... → postgresql://...
DATABASE_URL = DATABASE_URL.replace('postgresql+psycopg2://', 'postgresql://')
DATABASE_URL = DATABASE_URL.replace('postgresql+asyncpg://', 'postgresql://')

# =============================================================================
# UUIDs FIXOS PARA E2E (determinismo)
# =============================================================================

# Organização E2E
E2E_ORG_ID = UUID('88888888-8888-8888-8888-000000000001')
E2E_ORG_NAME = 'E2E-HBTRACK-TEST-ORG'

# Temporada E2E
E2E_SEASON_ID = UUID('88888888-8888-8888-8888-000000000010')
E2E_SEASON_NAME = 'E2E-Temporada-2026'

# Pessoas E2E (para cada usuário)
E2E_PERSON_ADMIN_ID = UUID('88888888-8888-8888-8881-000000000001')  # admin é dirigente
E2E_PERSON_COORDENADOR_ID = UUID('88888888-8888-8888-8881-000000000003')
E2E_PERSON_TREINADOR_ID = UUID('88888888-8888-8888-8881-000000000004')
E2E_PERSON_ATLETA_ID = UUID('88888888-8888-8888-8881-000000000005')
E2E_PERSON_MEMBRO_ID = UUID('88888888-8888-8888-8881-000000000006')
E2E_PERSON_ATLETA_VETERANO_ID = UUID('88888888-8888-8888-8881-000000000007')  # Para teste negativo (39 anos)

# Usuários E2E
E2E_USER_ADMIN_ID = UUID('88888888-8888-8888-8882-000000000001')  # admin é dirigente
E2E_USER_COORDENADOR_ID = UUID('88888888-8888-8888-8882-000000000003')
E2E_USER_TREINADOR_ID = UUID('88888888-8888-8888-8882-000000000004')
E2E_USER_ATLETA_ID = UUID('88888888-8888-8888-8882-000000000005')
E2E_USER_MEMBRO_ID = UUID('88888888-8888-8888-8882-000000000006')

# Org Memberships E2E
E2E_MEMBERSHIP_ADMIN_ID = UUID('88888888-8888-8888-8883-000000000000')  # admin é dirigente
E2E_MEMBERSHIP_COORDENADOR_ID = UUID('88888888-8888-8888-8883-000000000002')
E2E_MEMBERSHIP_TREINADOR_ID = UUID('88888888-8888-8888-8883-000000000003')
E2E_MEMBERSHIP_ATLETA_ID = UUID('88888888-8888-8888-8883-000000000004')
E2E_MEMBERSHIP_MEMBRO_ID = UUID('88888888-8888-8888-8883-000000000005')

# Equipes E2E (uma para cada usuário para testes de RBAC)
E2E_TEAM_DIRIGENTE_ID = UUID('88888888-8888-8888-8884-000000000001')
E2E_TEAM_COORDENADOR_ID = UUID('88888888-8888-8888-8884-000000000002')
E2E_TEAM_TREINADOR_ID = UUID('88888888-8888-8888-8884-000000000003')
E2E_TEAM_ATLETA_ID = UUID('88888888-8888-8888-8884-000000000004')

E2E_TEAM_NAMES = {
    'dirigente': 'E2E-Equipe-Dirigente',
    'coordenador': 'E2E-Equipe-Coordenador',
    'treinador': 'E2E-Equipe-Treinador',
    'atleta': 'E2E-Equipe-Atleta',
}

# Jogos E2E (para agenda e estatísticas)
E2E_MATCH_1_ID = UUID('88888888-8888-8888-8885-000000000001')  # Passado com resultado
E2E_MATCH_2_ID = UUID('88888888-8888-8888-8885-000000000002')  # Futuro próximo
E2E_MATCH_3_ID = UUID('88888888-8888-8888-8885-000000000003')  # Futuro distante

# Treinos E2E (para agenda)
E2E_TRAINING_1_ID = UUID('88888888-8888-8888-8886-000000000001')  # Passado com presença
E2E_TRAINING_2_ID = UUID('88888888-8888-8888-8886-000000000002')  # Hoje/amanhã
E2E_TRAINING_3_ID = UUID('88888888-8888-8888-8886-000000000003')  # Futuro

# Equipe do Coordenador - UUIDs fixos
# 10 Atletas (persons)
E2E_COORD_ATHLETE_PERSON_IDS = [
    UUID('88888888-8888-8888-8887-000000000001'),
    UUID('88888888-8888-8888-8887-000000000002'),
    UUID('88888888-8888-8888-8887-000000000003'),
    UUID('88888888-8888-8888-8887-000000000004'),
    UUID('88888888-8888-8888-8887-000000000005'),
    UUID('88888888-8888-8888-8887-000000000006'),
    UUID('88888888-8888-8888-8887-000000000007'),
    UUID('88888888-8888-8888-8887-000000000008'),
    UUID('88888888-8888-8888-8887-000000000009'),
    UUID('88888888-8888-8888-8887-000000000010'),
]

# 2 Treinadores adicionais (persons)
E2E_COORD_COACH_PERSON_IDS = [
    UUID('88888888-8888-8888-8887-000000000011'),  # Treinador auxiliar 1
    UUID('88888888-8888-8888-8887-000000000012'),  # Treinador auxiliar 2
]

# Org memberships para os 2 treinadores
E2E_COORD_COACH_MEMBERSHIP_IDS = [
    UUID('88888888-8888-8888-8887-000000000021'),
    UUID('88888888-8888-8888-8887-000000000022'),
]

# Temporada da equipe do coordenador
E2E_COORD_SEASON_ID = UUID('88888888-8888-8888-8887-000000000030')

# Treinos da equipe do coordenador (3 passados + 3 futuros)
E2E_COORD_TRAINING_IDS = [
    UUID('88888888-8888-8888-8887-000000000041'),  # Passado -10 dias
    UUID('88888888-8888-8888-8887-000000000042'),  # Passado -7 dias
    UUID('88888888-8888-8888-8887-000000000043'),  # Passado -3 dias
    UUID('88888888-8888-8888-8887-000000000044'),  # Futuro +3 dias
    UUID('88888888-8888-8888-8887-000000000045'),  # Futuro +7 dias
    UUID('88888888-8888-8888-8887-000000000046'),  # Futuro +10 dias
]

# Jogos da equipe do coordenador (3 passados + 3 futuros)
E2E_COORD_MATCH_IDS = [
    UUID('88888888-8888-8888-8887-000000000051'),  # Passado -15 dias
    UUID('88888888-8888-8888-8887-000000000052'),  # Passado -10 dias
    UUID('88888888-8888-8888-8887-000000000053'),  # Passado -5 dias
    UUID('88888888-8888-8888-8887-000000000054'),  # Futuro +5 dias
    UUID('88888888-8888-8888-8887-000000000055'),  # Futuro +12 dias
    UUID('88888888-8888-8888-8887-000000000056'),  # Futuro +20 dias
]

# Equipes adversárias para jogos do coordenador
E2E_COORD_ADVERSARY_IDS = [
    UUID('88888888-8888-8888-8887-000000000061'),  # E2E-Adversário-Coord-A
    UUID('88888888-8888-8888-8887-000000000062'),  # E2E-Adversário-Coord-B
    UUID('88888888-8888-8888-8887-000000000063'),  # E2E-Adversário-Coord-C
]

# Templates de Treino E2E (4 padrão + espaço para 46 customizados)
E2E_TEMPLATE_TATICO_ID = UUID('88888888-8888-8888-8889-000000000001')
E2E_TEMPLATE_FISICO_ID = UUID('88888888-8888-8888-8889-000000000002')
E2E_TEMPLATE_EQUILIBRADO_ID = UUID('88888888-8888-8888-8889-000000000003')
E2E_TEMPLATE_DEFESA_ID = UUID('88888888-8888-8888-8889-000000000004')

# Macrociclos E2E (planejamento)
E2E_MACROCICLO_1_ID = UUID('88888888-8888-8888-888A-000000000001')  # Preparatório (ativo)
E2E_MACROCICLO_2_ID = UUID('88888888-8888-8888-888A-000000000002')  # Competitivo (futuro)

# Mesociclos E2E (dentro do macrociclo preparatório)
E2E_MESOCICLO_1_ID = UUID('88888888-8888-8888-888A-000000000011')  # Fase 1 (ativo)
E2E_MESOCICLO_2_ID = UUID('88888888-8888-8888-888A-000000000012')  # Fase 2 (ativo)

# Sessões de Treino E2E da equipe dirigente (6 total: 3 passadas + 3 futuras)
E2E_SESSION_IDS = [
    UUID('88888888-8888-8888-888B-000000000001'),  # Passado -10 dias (readonly)
    UUID('88888888-8888-8888-888B-000000000002'),  # Passado -7 dias (readonly)
    UUID('88888888-8888-8888-888B-000000000003'),  # Passado -3 dias (readonly)
    UUID('88888888-8888-8888-888B-000000000004'),  # Hoje (scheduled)
    UUID('88888888-8888-8888-888B-000000000005'),  # Futuro +3 dias (scheduled)
    UUID('88888888-8888-8888-888B-000000000006'),  # Futuro +7 dias (scheduled)
]

# Senha padrão para todos os usuários E2E
E2E_PASSWORD = 'Admin@123'

# =============================================================================
# DADOS BRASILEIROS
# =============================================================================

NOMES_MASCULINOS = [
    'João', 'Pedro', 'Lucas', 'Gabriel', 'Rafael', 'Miguel', 'Davi', 'Arthur',
    'Guilherme', 'Felipe', 'Bernardo', 'Enzo', 'Nicolas', 'Lorenzo', 'Matheus'
]

NOMES_FEMININOS = [
    'Maria', 'Ana', 'Julia', 'Leticia', 'Mariana', 'Gabriela', 'Isabela', 'Beatriz',
    'Laura', 'Luiza', 'Sofia', 'Valentina', 'Giovanna', 'Helena', 'Alice'
]

SOBRENOMES = [
    'Silva', 'Santos', 'Oliveira', 'Souza', 'Costa', 'Ferreira', 'Rodrigues', 'Almeida',
    'Nascimento', 'Lima', 'Araujo', 'Fernandes', 'Carvalho', 'Gomes', 'Martins'
]

# =============================================================================
# HELPERS
# =============================================================================

def gerar_cpf_valido(base: int) -> str:
    """Gera CPF válido usando algoritmo de validação com base numérica"""
    # Converte base em 9 dígitos
    cpf_base = str(base).zfill(9)
    
    # Calcula primeiro dígito verificador
    soma = sum(int(cpf_base[i]) * (10 - i) for i in range(9))
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto
    
    # Calcula segundo dígito verificador
    cpf_com_d1 = cpf_base + str(digito1)
    soma = sum(int(cpf_com_d1[i]) * (11 - i) for i in range(10))
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto
    
    return cpf_base + str(digito1) + str(digito2)

def hash_password(password: str) -> str:
    """Gera hash bcrypt da senha"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def execute_sql(conn, sql, params=None):
    """Executa SQL e retorna cursor"""
    cur = conn.cursor()
    if params is not None and len(params) > 0:
        cur.execute(sql, params)
    else:
        cur.execute(sql)
    return cur

# =============================================================================
# SEED FUNCTIONS
# =============================================================================

def seed_roles(conn):
    """Garante que roles existem (idempotente)"""
    print("=> Verificando roles...")
    
    roles_data = [
        (1, 'dirigente', 'Dirigente'),
        (2, 'coordenador', 'Coordenador'),
        (3, 'treinador', 'Treinador'),
        (4, 'atleta', 'Atleta'),
        (5, 'membro', 'Membro'),  # Role para membros convidados
    ]
    
    cur = conn.cursor()
    execute_values(
        cur,
        """
        INSERT INTO roles (id, code, name)
        VALUES %s
        ON CONFLICT (id) DO UPDATE SET code = EXCLUDED.code, name = EXCLUDED.name
        """,
        roles_data
    )
    conn.commit()
    print(f"   OK roles verificados/criados")


def seed_categories(conn):
    """Garante que categories existem (idempotente)"""
    print("=> Verificando categories...")
    
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
        ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name, max_age = EXCLUDED.max_age
        """,
        categories_data
    )
    conn.commit()
    print(f"   OK categories verificadas/criadas")


def seed_e2e_organization(conn):
    """Cria organização E2E com UUID fixo (idempotente)"""
    print("=> Criando organização E2E...")
    
    cur = execute_sql(
        conn,
        """
        INSERT INTO organizations (id, name)
        VALUES (%s, %s)
        ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name
        RETURNING id
        """,
        (str(E2E_ORG_ID), E2E_ORG_NAME)
    )
    conn.commit()
    result = cur.fetchone()
    print(f"   OK Organização E2E: {E2E_ORG_ID}")
    return result[0] if result else E2E_ORG_ID


def seed_e2e_persons(conn):
    """Cria pessoas E2E com UUIDs fixos (idempotente)"""
    print("=> Criando pessoas E2E...")
    
    # (person_id, first_name, last_name, full_name, birth_date, gender)
    persons_data = [
        (str(E2E_PERSON_ADMIN_ID), 'E2E Admin', 'User', 'E2E Admin User', '1990-01-01', 'masculino'),  # dirigente
        (str(E2E_PERSON_COORDENADOR_ID), 'E2E Coordenador', 'User', 'E2E Coordenador User', '1988-03-20', 'feminino'),
        (str(E2E_PERSON_TREINADOR_ID), 'E2E Treinador', 'User', 'E2E Treinador User', '1992-04-25', 'masculino'),
        (str(E2E_PERSON_ATLETA_ID), 'E2E Atleta', 'User', 'E2E Atleta User', '2012-06-01', 'feminino'),  # CORRIGIDO: 14 anos (era 21)
        (str(E2E_PERSON_MEMBRO_ID), 'E2E Membro', 'User', 'E2E Membro User', '1995-06-15', 'masculino'),
        (str(E2E_PERSON_ATLETA_VETERANO_ID), 'E2E Atleta Veterano', 'Invalid', 'E2E Atleta Veterano Invalid', '1987-05-15', 'feminino'),  # Para teste negativo (39 anos)
    ]
    
    cur = conn.cursor()
    for person_id, first_name, last_name, full_name, birth_date, gender in persons_data:
        execute_sql(
            conn,
            """
            INSERT INTO persons (id, first_name, last_name, full_name, birth_date, gender)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET 
                first_name = EXCLUDED.first_name,
                last_name = EXCLUDED.last_name,
                full_name = EXCLUDED.full_name,
                birth_date = EXCLUDED.birth_date,
                gender = EXCLUDED.gender
            """,
            (person_id, first_name, last_name, full_name, birth_date, gender)
        )
    conn.commit()
    print(f"   OK 6 pessoas E2E criadas/atualizadas (incluindo atleta veterano para testes)")


def seed_e2e_users(conn):
    """Cria usuários E2E com UUIDs fixos (idempotente)"""
    print("=> Criando usuários E2E...")
    
    password_hash = hash_password(E2E_PASSWORD)
    
    # Usuários: (user_id, person_id, email, is_superadmin)
    # Nota: role é definido via org_memberships, não na tabela users
    # Nota: Superadmin é criado via migration (adm@handballtrack.app), não aqui
    users_data = [
        (str(E2E_USER_ADMIN_ID), str(E2E_PERSON_ADMIN_ID), 'e2e.admin@teste.com', False),  # dirigente
        (str(E2E_USER_COORDENADOR_ID), str(E2E_PERSON_COORDENADOR_ID), 'e2e.coordenador@teste.com', False),
        (str(E2E_USER_TREINADOR_ID), str(E2E_PERSON_TREINADOR_ID), 'e2e.treinador@teste.com', False),
        (str(E2E_USER_ATLETA_ID), str(E2E_PERSON_ATLETA_ID), 'e2e.atleta@teste.com', False),
        (str(E2E_USER_MEMBRO_ID), str(E2E_PERSON_MEMBRO_ID), 'e2e.membro@teste.com', False),
    ]

    for user_id, person_id, email, is_superadmin in users_data:
        execute_sql(
            conn,
            """
            INSERT INTO users (id, person_id, email, password_hash, is_superadmin, is_locked, status, deleted_at)
            VALUES (%s, %s, %s, %s, %s, false, 'ativo', NULL)
            ON CONFLICT (id) DO UPDATE SET
                person_id = EXCLUDED.person_id,
                email = EXCLUDED.email,
                password_hash = EXCLUDED.password_hash,
                is_superadmin = EXCLUDED.is_superadmin,
                status = 'ativo',
                deleted_at = NULL
            """,
            (user_id, person_id, email, password_hash, is_superadmin)
        )
    conn.commit()
    print(f"   OK 5 usuários E2E criados/atualizados")
    print(f"      - e2e.admin@teste.com (dirigente)")
    print(f"      - e2e.coordenador@teste.com")
    print(f"      - e2e.treinador@teste.com")
    print(f"      - e2e.atleta@teste.com")
    print(f"      - e2e.membro@teste.com")


def seed_e2e_org_memberships(conn):
    """Cria vínculos organizacionais E2E (idempotente)"""
    print("=> Criando org_memberships E2E...")
    
    # Vincular todos os 5 usuários à org E2E
    # role_id: 1=dirigente, 2=coordenador, 3=treinador, 4=atleta, 5=membro
    memberships_data = [
        (str(E2E_MEMBERSHIP_ADMIN_ID), str(E2E_PERSON_ADMIN_ID), str(E2E_ORG_ID), 1),  # admin é dirigente
        (str(E2E_MEMBERSHIP_COORDENADOR_ID), str(E2E_PERSON_COORDENADOR_ID), str(E2E_ORG_ID), 2),  # coordenador
        (str(E2E_MEMBERSHIP_TREINADOR_ID), str(E2E_PERSON_TREINADOR_ID), str(E2E_ORG_ID), 3),  # treinador
        (str(E2E_MEMBERSHIP_ATLETA_ID), str(E2E_PERSON_ATLETA_ID), str(E2E_ORG_ID), 4),  # atleta
        (str(E2E_MEMBERSHIP_MEMBRO_ID), str(E2E_PERSON_MEMBRO_ID), str(E2E_ORG_ID), 5),  # membro
    ]
    
    for membership_id, person_id, org_id, role_id in memberships_data:
        execute_sql(
            conn,
            """
            INSERT INTO org_memberships (id, person_id, organization_id, role_id, start_at)
            VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (id) DO UPDATE SET 
                role_id = EXCLUDED.role_id
            """,
            (membership_id, person_id, org_id, role_id)
        )
    conn.commit()
    print(f"   OK 5 org_memberships E2E criados")


def seed_e2e_teams(conn):
    """Cria 4 equipes E2E separadas (uma para cada usuário)"""
    print("=> Criando equipes E2E...")
    
    teams_data = [
        (str(E2E_TEAM_DIRIGENTE_ID), E2E_TEAM_NAMES['dirigente'], 2, 'feminino'),
        (str(E2E_TEAM_COORDENADOR_ID), E2E_TEAM_NAMES['coordenador'], 3, 'masculino'),
        (str(E2E_TEAM_TREINADOR_ID), E2E_TEAM_NAMES['treinador'], 4, 'feminino'),
        (str(E2E_TEAM_ATLETA_ID), E2E_TEAM_NAMES['atleta'], 2, 'masculino'),
    ]
    
    for team_id, name, category_id, gender in teams_data:
        execute_sql(
            conn,
            """
            INSERT INTO teams (id, name, organization_id, category_id, gender, is_our_team)
            VALUES (%s, %s, %s, %s, %s, true)
            ON CONFLICT (id) DO UPDATE SET 
                name = EXCLUDED.name,
                category_id = EXCLUDED.category_id,
                gender = EXCLUDED.gender
            """,
            (team_id, name, str(E2E_ORG_ID), category_id, gender)
        )
    
    conn.commit()
    print(f"   OK 4 equipes E2E criadas")


def seed_e2e_season(conn):
    """Cria temporada E2E para equipe do dirigente (deve ser criada DEPOIS da equipe)"""
    print("=> Criando temporada E2E...")
    
    execute_sql(
        conn,
        """
        INSERT INTO seasons (
            id, team_id, name, year, 
            start_date, end_date, 
            created_at, updated_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
        ON CONFLICT (id) DO UPDATE SET 
            name = EXCLUDED.name,
            year = EXCLUDED.year,
            start_date = EXCLUDED.start_date,
            end_date = EXCLUDED.end_date
        """,
        (str(E2E_SEASON_ID), str(E2E_TEAM_DIRIGENTE_ID), E2E_SEASON_NAME, 2026, 
         '2026-01-01', '2026-12-31')
    )
    conn.commit()
    print(f"   OK Temporada E2E: {E2E_SEASON_ID} ({E2E_SEASON_NAME})")


def seed_e2e_coordenador_season(conn):
    """Cria temporada E2E para equipe do coordenador"""
    print("=> Criando temporada E2E para equipe do coordenador...")
    
    execute_sql(
        conn,
        """
        INSERT INTO seasons (
            id, team_id, name, year, 
            start_date, end_date, 
            created_at, updated_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
        ON CONFLICT (id) DO UPDATE SET 
            name = EXCLUDED.name,
            year = EXCLUDED.year,
            start_date = EXCLUDED.start_date,
            end_date = EXCLUDED.end_date
        """,
        (str(E2E_COORD_SEASON_ID), str(E2E_TEAM_COORDENADOR_ID), 'E2E-Temporada-Coordenador-2026', 2026,
         '2026-01-01', '2026-12-31')
    )
    conn.commit()
    print(f"   OK Temporada coordenador: {E2E_COORD_SEASON_ID}")


def seed_e2e_coordenador_staff(conn):
    """Cria 10 atletas e 2 treinadores para a equipe do coordenador"""
    print("=> Criando staff da equipe do coordenador (10 atletas + 2 treinadores)...")
    
    from datetime import datetime, timedelta
    import random
    
    # 1. Criar 10 atletas (persons + athletes + team_registrations)
    print("   => Criando 10 atletas...")
    for i, person_id in enumerate(E2E_COORD_ATHLETE_PERSON_IDS, 1):
        # Nome aleatório
        first_name = random.choice(NOMES_MASCULINOS)  # Equipe masculina
        last_name = random.choice(SOBRENOMES)
        full_name = f"{first_name} {last_name}"
        
        # Idade para Infantil (até 14 anos): 12-14 anos
        birth_year = datetime.now().year - random.randint(12, 14)
        birth_date = f"{birth_year}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
        
        # Criar person
        execute_sql(
            conn,
            """
            INSERT INTO persons (id, first_name, last_name, full_name, birth_date, gender)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                first_name = EXCLUDED.first_name,
                last_name = EXCLUDED.last_name,
                full_name = EXCLUDED.full_name,
                birth_date = EXCLUDED.birth_date
            """,
            (str(person_id), first_name, last_name, full_name, birth_date, 'masculino')
        )
        
        # Criar athlete (soft delete antes se existir para garantir idempotência)
        athlete_name = f"E2E-Atleta-Coord-{i:02d}"
        shirt_number = i
        
        # Posições: atleta 1 é goleiro, demais são jogadores de linha
        if i == 1:
            def_pos_id = 5  # Goleiro
            off_pos_id = None
        else:
            def_pos_id = random.randint(1, 4)  # Armador, Ponta, Pivo, Extremo
            off_pos_id = random.randint(1, 6)
        
        # Soft delete athlete existente
        execute_sql(
            conn,
            "UPDATE athletes SET deleted_at = NOW(), deleted_reason = 'Re-seed E2E' WHERE person_id = %s AND deleted_at IS NULL",
            (str(person_id),)
        )
        
        execute_sql(
            conn,
            """
            INSERT INTO athletes (
                person_id, athlete_name, shirt_number, birth_date,
                main_defensive_position_id, main_offensive_position_id,
                state, injured, created_at, updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, 'ativa', false, NOW(), NOW())
            """,
            (str(person_id), athlete_name, shirt_number, birth_date, def_pos_id, off_pos_id)
        )
        
        # Criar team_registration vinculando atleta à equipe
        # Obter athlete.id
        cur = execute_sql(conn, "SELECT id FROM athletes WHERE person_id = %s AND deleted_at IS NULL", (str(person_id),))
        athlete_id = cur.fetchone()[0]
        
        # Soft delete registration existente
        execute_sql(
            conn,
            "UPDATE team_registrations SET deleted_at = NOW(), deleted_reason = 'Re-seed E2E' WHERE athlete_id = %s AND team_id = %s AND deleted_at IS NULL",
            (athlete_id, str(E2E_TEAM_COORDENADOR_ID))
        )
        
        execute_sql(
            conn,
            """
            INSERT INTO team_registrations (
                athlete_id, team_id, start_at, created_at, updated_at
            )
            VALUES (%s, %s, %s, NOW(), NOW())
            """,
            (athlete_id, str(E2E_TEAM_COORDENADOR_ID), '2026-01-01')
        )
    
    print(f"   OK 10 atletas criados para equipe do coordenador")
    
    # 2. Criar 2 treinadores auxiliares (persons + org_memberships + team_memberships)
    print("   => Criando 2 treinadores auxiliares...")
    for i, (person_id, membership_id) in enumerate(zip(E2E_COORD_COACH_PERSON_IDS, E2E_COORD_COACH_MEMBERSHIP_IDS), 1):
        first_name = random.choice(NOMES_MASCULINOS + NOMES_FEMININOS)
        last_name = random.choice(SOBRENOMES)
        full_name = f"{first_name} {last_name}"
        birth_date = f"{datetime.now().year - random.randint(30, 45)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
        gender = 'masculino' if i == 1 else 'feminino'
        
        # Criar person
        execute_sql(
            conn,
            """
            INSERT INTO persons (id, first_name, last_name, full_name, birth_date, gender)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                first_name = EXCLUDED.first_name,
                last_name = EXCLUDED.last_name,
                full_name = EXCLUDED.full_name
            """,
            (str(person_id), first_name, last_name, full_name, birth_date, gender)
        )
        
        # Criar org_membership (role_id=3 para treinador)
        execute_sql(
            conn,
            """
            INSERT INTO org_memberships (id, person_id, organization_id, role_id, start_at)
            VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (id) DO UPDATE SET
                role_id = EXCLUDED.role_id
            """,
            (str(membership_id), str(person_id), str(E2E_ORG_ID), 3)
        )
        
        # Criar team_membership
        execute_sql(
            conn,
            """
            INSERT INTO team_memberships (team_id, person_id, org_membership_id, status)
            VALUES (%s, %s, %s, 'ativo')
            ON CONFLICT DO NOTHING
            """,
            (str(E2E_TEAM_COORDENADOR_ID), str(person_id), str(membership_id))
        )
    
    print(f"   OK 2 treinadores auxiliares criados")
    
    conn.commit()


def seed_e2e_team_memberships(conn):
    """Cria vínculos separados: cada usuário em SUA equipe"""
    print("=> Criando team memberships E2E...")

    # Cada usuário vinculado à SUA própria equipe (1:1)
    team_members = [
        (str(E2E_TEAM_DIRIGENTE_ID), str(E2E_PERSON_ADMIN_ID), str(E2E_MEMBERSHIP_ADMIN_ID), 'ativo'),
        (str(E2E_TEAM_COORDENADOR_ID), str(E2E_PERSON_COORDENADOR_ID), str(E2E_MEMBERSHIP_COORDENADOR_ID), 'ativo'),
        (str(E2E_TEAM_TREINADOR_ID), str(E2E_PERSON_TREINADOR_ID), str(E2E_MEMBERSHIP_TREINADOR_ID), 'ativo'),
        (str(E2E_TEAM_ATLETA_ID), str(E2E_PERSON_ATLETA_ID), str(E2E_MEMBERSHIP_ATLETA_ID), 'ativo'),
    ]

    # Deletar memberships antigos (idempotência)
    for team_id, _, _, _ in team_members:
        execute_sql(
            conn,
            """DELETE FROM team_memberships WHERE team_id = %s""",
            (team_id,)
        )

    # Inserir novos vínculos
    for team_id, person_id, org_membership_id, status in team_members:
        execute_sql(
            conn,
            """
            INSERT INTO team_memberships (team_id, person_id, org_membership_id, status)
            VALUES (%s, %s, %s, %s)
            """,
            (team_id, person_id, org_membership_id, status)
        )

    conn.commit()
    print(f"   OK {len(team_members)} team memberships criados (1 usuário por equipe)")


def seed_e2e_populate_coach_membership_id(conn):
    """
    Step 23: Popular coach_membership_id e active_from para equipes sem coach definido.
    DEVE ser executado APÓS seed_e2e_team_memberships() pois depende dessa tabela.
    """
    print("=> Populando coach_membership_id nas equipes...")
    
    # Busca o primeiro org_membership ativo de treinador (role_id=3) vinculado à equipe
    execute_sql(
        conn,
        """
        UPDATE teams 
        SET 
            coach_membership_id = (
                SELECT tm.org_membership_id 
                FROM team_memberships tm
                JOIN org_memberships om ON tm.org_membership_id = om.id
                WHERE tm.team_id = teams.id 
                    AND tm.status = 'ativo'
                    AND om.role_id = 3
                    AND om.deleted_at IS NULL
                    AND om.end_at IS NULL
                LIMIT 1
            ),
            active_from = COALESCE(active_from, created_at::date)
        WHERE coach_membership_id IS NULL
            AND EXISTS (
                SELECT 1 
                FROM team_memberships tm
                JOIN org_memberships om ON tm.org_membership_id = om.id
                WHERE tm.team_id = teams.id 
                    AND tm.status = 'ativo'
                    AND om.role_id = 3
                    AND om.deleted_at IS NULL
                    AND om.end_at IS NULL
            )
        """,
        ()
    )
    
    # Verificar quantas equipes foram atualizadas
    cursor = execute_sql(
        conn,
        """
        SELECT COUNT(*) 
        FROM teams 
        WHERE coach_membership_id IS NOT NULL 
            AND organization_id = %s
        """,
        (str(E2E_ORG_ID),)
    )
    
    row = cursor.fetchone()
    updated_count = row[0] if row else 0
    
    conn.commit()
    print(f"   OK {updated_count} equipes com coach_membership_id populado")


def seed_e2e_matches(conn):
    """Cria jogos E2E para testes de agenda e estatísticas"""
    print("=> Criando matches E2E...")
    
    # Soft delete apenas matches scheduled (finished não podem ser alterados por trigger)
    execute_sql(
        conn,
        """
        UPDATE matches 
        SET deleted_at = NOW(), deleted_reason = 'Re-seed E2E'
        WHERE our_team_id = %s AND deleted_at IS NULL AND status != 'finished'
        """,
        (str(E2E_TEAM_DIRIGENTE_ID),)
    )
    
    # Precisamos de equipes adversárias - vamos criar equipes temporárias
    # para os adversários (sem membros, apenas para jogos)
    adversary_teams = [
        (UUID('88888888-8888-8888-8885-000000000011'), 'E2E-Adversário-A'),
        (UUID('88888888-8888-8888-8885-000000000012'), 'E2E-Adversário-B'),
        (UUID('88888888-8888-8888-8885-000000000013'), 'E2E-Adversário-C'),
    ]
    
    # Criar equipes adversárias (idempotente)
    for adv_id, adv_name in adversary_teams:
        execute_sql(
            conn,
            """
            INSERT INTO teams (
                id, organization_id, season_id, name, 
                category_id, gender, created_at, updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
            ON CONFLICT (id) DO UPDATE SET
                name = EXCLUDED.name,
                updated_at = NOW()
            """,
            (str(adv_id), str(E2E_ORG_ID), str(E2E_SEASON_ID), adv_name, 2, 'feminino')
        )
    
    # Gerar datas futuras dinamicamente
    from datetime import datetime, timedelta, time
    now = datetime.now()
    
    # (match_id, home_team_id, away_team_id, our_team_id, match_date, match_time, opponent_name, status, phase, final_score_home, final_score_away, location)
    matches_data = [
        # Match 1: Passado/Finalizado - SKIP (já existe e não pode ser alterado por trigger)
        # (
        #     str(E2E_MATCH_1_ID),
        #     str(E2E_TEAM_DIRIGENTE_ID),  # home (equipe do dirigente)
        #     str(adversary_teams[0][0]),  # away (adversário A)
        #     str(E2E_TEAM_DIRIGENTE_ID),  # our team
        #     (now - timedelta(days=4)).strftime('%Y-%m-%d'),  # Passado (-4 dias)
        #     '14:00:00',  # match_time
        #     'E2E-Adversário-A',  # opponent_name
        #     'finished',
        #     'friendly',
        #     3,  # final_score_home (vitória 3-1)
        #     1,  # final_score_away
        #     'Campo E2E'
        # ),
        (
            str(E2E_MATCH_2_ID),
            str(adversary_teams[1][0]),  # home (adversário B)
            str(E2E_TEAM_DIRIGENTE_ID),  # away (equipe do dirigente)
            str(E2E_TEAM_DIRIGENTE_ID),  # our team
            (now + timedelta(days=6)).strftime('%Y-%m-%d'),  # Futuro próximo (+6 dias)
            '16:30:00',  # match_time
            'E2E-Adversário-B',  # opponent_name
            'scheduled',
            'group',
            None,  # sem placar ainda
            None,
            'Arena Adversário B'
        ),
        (
            str(E2E_MATCH_3_ID),
            str(E2E_TEAM_DIRIGENTE_ID),  # home (equipe do dirigente)
            str(adversary_teams[2][0]),  # away (adversário C)
            str(E2E_TEAM_DIRIGENTE_ID),  # our team
            (now + timedelta(days=30)).strftime('%Y-%m-%d'),  # Futuro distante (+30 dias)
            '18:00:00',  # match_time
            'E2E-Adversário-C',  # opponent_name
            'scheduled',
            'friendly',
            None,  # sem placar ainda
            None,
            'Campo E2E'
        ),
    ]
    
    for match_data in matches_data:
        match_id, home_id, away_id, our_id, match_date, match_time, opponent_name, status, phase, score_home, score_away, location = match_data
        execute_sql(
            conn,
            """
            INSERT INTO matches (
                id, season_id, match_date, start_time, home_team_id, away_team_id,
                our_team_id, notes, phase, status, venue,
                final_score_home, final_score_away,
                created_by_user_id, created_at, updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            ON CONFLICT (id) DO NOTHING
            """,
            (match_id, str(E2E_SEASON_ID), match_date, match_time, home_id, away_id, 
             our_id, opponent_name, phase, status, location, score_home, score_away,
             str(E2E_USER_ADMIN_ID))
        )
    
    # Não é mais necessário UPDATE do placar (já inserido no CREATE)
    
    conn.commit()
    print(f"   OK {len(matches_data)} matches E2E criados (1 com resultado 3-1)")


def seed_e2e_trainings(conn):
    """Cria treinos E2E para testes de agenda"""
    print("=> Criando training sessions E2E...")
    
    # Não fazemos cleanup de trainings antigos porque há triggers bloqueando DELETE.
    # Usamos ON CONFLICT para idempotência.
    
    # Gerar datas futuras dinamicamente
    from datetime import datetime, timedelta
    now = datetime.now()
    
    # (training_id, main_objective, session_at, duration_minutes, location, session_type)
    trainings_data = [
        (
            str(E2E_TRAINING_1_ID),
            'E2E-Treino-Tático',
            (now + timedelta(days=2)).strftime('%Y-%m-%d 10:00:00'),  # +2 dias
            90,
            'Campo Principal',
            'quadra'
        ),
        (
            str(E2E_TRAINING_2_ID),
            'E2E-Treino-Físico',
            (now + timedelta(days=5)).strftime('%Y-%m-%d 14:00:00'),  # +5 dias
            120,
            'Ginásio',
            'fisico'
        ),
        (
            str(E2E_TRAINING_3_ID),
            'E2E-Treino-Técnico',
            (now + timedelta(days=10)).strftime('%Y-%m-%d 09:00:00'),  # +10 dias
            90,
            'Campo Auxiliar',
            'quadra'
        ),
    ]
    
    for training_data in trainings_data:
        training_id, objective, session_at, duration, location, session_type = training_data
        execute_sql(
            conn,
            """
            INSERT INTO training_sessions (
                id, organization_id, team_id, season_id,
                session_at, duration_planned_minutes, location,
                session_type, main_objective, status,
                created_by_user_id, created_at, updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            ON CONFLICT (id) DO UPDATE SET
                session_at = EXCLUDED.session_at,
                main_objective = EXCLUDED.main_objective,
                location = EXCLUDED.location,
                status = EXCLUDED.status,
                updated_at = NOW()
            """,
            (training_id, str(E2E_ORG_ID), str(E2E_TEAM_DIRIGENTE_ID), str(E2E_SEASON_ID),
             session_at, duration, location, session_type, objective, 'scheduled',
             str(E2E_USER_ADMIN_ID))
        )
    
    # Nota: Presença (attendance) não é criada no seed básico pois requer
    # team_registration_id. Testes E2E podem criar attendance conforme necessário.
    
    conn.commit()
    print(f"   OK {len(trainings_data)} training sessions E2E criados")


def seed_e2e_coordenador_trainings(conn):
    """Cria 6 treinos (3 passados + 3 futuros) para equipe do coordenador"""
    print("=> Criando treinos da equipe do coordenador (3 passados + 3 futuros)...")
    
    from datetime import datetime, timedelta
    now = datetime.now()
    
    # 3 treinos passados + 3 futuros
    trainings_config = [
        (-10, 'E2E-Treino-Coord-Passado-1', 'readonly', '10:00:00', 90, 'quadra'),
        (-7, 'E2E-Treino-Coord-Passado-2', 'readonly', '14:00:00', 120, 'fisico'),
        (-3, 'E2E-Treino-Coord-Passado-3', 'readonly', '09:00:00', 90, 'quadra'),
        (+3, 'E2E-Treino-Coord-Futuro-1', 'scheduled', '10:00:00', 90, 'quadra'),
        (+7, 'E2E-Treino-Coord-Futuro-2', 'scheduled', '14:00:00', 120, 'fisico'),
        (+10, 'E2E-Treino-Coord-Futuro-3', 'scheduled', '16:00:00', 90, 'quadra'),
    ]
    
    for i, (days_offset, objective, status, time_str, duration, session_type) in enumerate(trainings_config):
        training_id = E2E_COORD_TRAINING_IDS[i]
        session_at = (now + timedelta(days=days_offset)).strftime(f'%Y-%m-%d {time_str}')
        location = 'Ginásio E2E' if session_type == 'fisico' else 'Campo E2E'
        
        execute_sql(
            conn,
            """
            INSERT INTO training_sessions (
                id, organization_id, team_id, season_id,
                session_at, duration_planned_minutes, location,
                session_type, main_objective, status,
                created_by_user_id, created_at, updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            ON CONFLICT (id) DO NOTHING
            """,
            (str(training_id), str(E2E_ORG_ID), str(E2E_TEAM_COORDENADOR_ID), str(E2E_COORD_SEASON_ID),
             session_at, duration, location, session_type, objective, status,
             str(E2E_USER_COORDENADOR_ID))
        )
    
    conn.commit()
    print(f"   OK 6 treinos criados para equipe do coordenador")


def seed_e2e_coordenador_matches(conn):
    """Cria 6 jogos (3 passados + 3 futuros) para equipe do coordenador"""
    print("=> Criando jogos da equipe do coordenador (3 passados + 3 futuros)...")
    
    from datetime import datetime, timedelta
    import random
    now = datetime.now()
    
    # Criar equipes adversárias
    adversaries = [
        ('E2E-Adversário-Coord-A', E2E_COORD_ADVERSARY_IDS[0]),
        ('E2E-Adversário-Coord-B', E2E_COORD_ADVERSARY_IDS[1]),
        ('E2E-Adversário-Coord-C', E2E_COORD_ADVERSARY_IDS[2]),
    ]
    
    for adv_name, adv_id in adversaries:
        execute_sql(
            conn,
            """
            INSERT INTO teams (
                id, organization_id, season_id, name,
                category_id, gender, created_at, updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
            ON CONFLICT (id) DO UPDATE SET
                name = EXCLUDED.name,
                updated_at = NOW()
            """,
            (str(adv_id), str(E2E_ORG_ID), str(E2E_COORD_SEASON_ID), adv_name, 2, 'masculino')
        )
    
    # Configuração dos jogos: (days_offset, adversary_idx, status, home_score, away_score)
    matches_config = [
        (-15, 0, 'finished', 28, 25, '15:00:00'),  # Vitória
        (-10, 1, 'finished', 22, 24, '16:00:00'),  # Derrota
        (-5, 2, 'finished', 30, 30, '18:00:00'),   # Empate
        (+5, 0, 'scheduled', None, None, '14:00:00'),
        (+12, 1, 'scheduled', None, None, '16:30:00'),
        (+20, 2, 'scheduled', None, None, '18:00:00'),
    ]
    
    for i, (days_offset, adv_idx, status, score_home, score_away, time_str) in enumerate(matches_config):
        match_id = E2E_COORD_MATCH_IDS[i]
        adv_name, adv_id = adversaries[adv_idx]
        match_date = (now + timedelta(days=days_offset)).strftime('%Y-%m-%d')
        
        # Alternar home/away
        if i % 2 == 0:
            home_id = str(E2E_TEAM_COORDENADOR_ID)
            away_id = str(adv_id)
            venue = 'Ginásio E2E'
        else:
            home_id = str(adv_id)
            away_id = str(E2E_TEAM_COORDENADOR_ID)
            venue = f'Arena {adv_name}'
        
        execute_sql(
            conn,
            """
            INSERT INTO matches (
                id, season_id, match_date, start_time, home_team_id, away_team_id,
                our_team_id, notes, phase, status, venue,
                final_score_home, final_score_away,
                created_by_user_id, created_at, updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            ON CONFLICT (id) DO NOTHING
            """,
            (str(match_id), str(E2E_COORD_SEASON_ID), match_date, time_str, home_id, away_id,
             str(E2E_TEAM_COORDENADOR_ID), adv_name, 'friendly', status, venue,
             score_home, score_away, str(E2E_USER_COORDENADOR_ID))
        )
    
    conn.commit()
    print(f"   OK 6 jogos criados para equipe do coordenador")


# =============================================================================
# SEED OPÇÃO B: DADOS COMPLETOS PARA TESTES E2E TRAINING
# =============================================================================

def seed_e2e_templates(conn):
    """Cria 4 templates padrão E2E (idempotente)"""
    print("=> Criando session_templates E2E...")
    
    templates_data = [
        (
            str(E2E_TEMPLATE_TATICO_ID),
            str(E2E_ORG_ID),
            'Treino Tático Ofensivo',
            'Foco em ataque posicional e transição ofensiva',
            'target',
            45, 10, 25, 5, 10, 0, 5,  # focos
            False,  # is_favorite
            True,   # is_active
            str(E2E_MEMBERSHIP_TREINADOR_ID),  # created_by
        ),
        (
            str(E2E_TEMPLATE_FISICO_ID),
            str(E2E_ORG_ID),
            'Treino Físico',
            'Alta intensidade física com técnica',
            'activity',
            5, 5, 5, 5, 10, 10, 60,
            False,
            True,
            str(E2E_MEMBERSHIP_TREINADOR_ID),
        ),
        (
            str(E2E_TEMPLATE_EQUILIBRADO_ID),
            str(E2E_ORG_ID),
            'Treino Equilibrado',
            'Distribuição uniforme entre todos os focos',
            'bar-chart',
            15, 15, 15, 15, 10, 10, 20,
            False,
            True,
            str(E2E_MEMBERSHIP_TREINADOR_ID),
        ),
        (
            str(E2E_TEMPLATE_DEFESA_ID),
            str(E2E_ORG_ID),
            'Treino de Defesa',
            'Foco em defesa posicional e transição defensiva',
            'shield',
            5, 50, 5, 30, 0, 5, 5,
            False,
            True,
            str(E2E_MEMBERSHIP_TREINADOR_ID),
        ),
    ]
    
    cur = conn.cursor()
    execute_values(
        cur,
        """
        INSERT INTO session_templates (
            id, org_id, name, description, icon,
            focus_attack_positional_pct, focus_defense_positional_pct,
            focus_transition_offense_pct, focus_transition_defense_pct,
            focus_attack_technical_pct, focus_defense_technical_pct,
            focus_physical_pct,
            is_favorite, is_active, created_by_membership_id,
            created_at, updated_at
        )
        VALUES %s
        ON CONFLICT (id) DO UPDATE SET
            name = EXCLUDED.name,
            description = EXCLUDED.description,
            updated_at = NOW()
        """,
        [(t[0], t[1], t[2], t[3], t[4], t[5], t[6], t[7], t[8], t[9], t[10], t[11], 
          t[12], t[13], t[14], 'NOW()', 'NOW()') for t in templates_data]
    )
    conn.commit()
    print(f"   OK {len(templates_data)} templates E2E criados")


def seed_e2e_training_cycles(conn):
    """Cria macrociclos e mesociclos E2E para planejamento (idempotente)"""
    print("=> Criando training_cycles E2E...")
    
    from datetime import datetime, timedelta
    now = datetime.now()
    
    # Macrociclo 1: Preparatório (ativo, 120 dias)
    macro1_start = now - timedelta(days=30)
    macro1_end = now + timedelta(days=90)
    
    # Macrociclo 2: Competitivo (futuro, 90 dias)
    macro2_start = macro1_end + timedelta(days=1)
    macro2_end = macro2_start + timedelta(days=90)
    
    # Mesociclo 1: Fase 1 (dentro do macro1, 4 semanas)
    meso1_start = macro1_start
    meso1_end = macro1_start + timedelta(weeks=4)
    
    # Mesociclo 2: Fase 2 (dentro do macro1, 4 semanas após meso1)
    meso2_start = meso1_end + timedelta(days=1)
    meso2_end = meso2_start + timedelta(weeks=4)
    
    cycles_data = [
        # Macrociclos
        (
            str(E2E_MACROCICLO_1_ID),
            str(E2E_ORG_ID),
            str(E2E_TEAM_DIRIGENTE_ID),
            'macro',
            macro1_start.strftime('%Y-%m-%d'),
            macro1_end.strftime('%Y-%m-%d'),
            'E2E-Macrociclo-Preparatorio: Fase de preparação física e técnica',
            'Macrociclo preparatório para testes E2E',
            'active',
            None,  # parent_id
            str(E2E_USER_TREINADOR_ID),
        ),
        (
            str(E2E_MACROCICLO_2_ID),
            str(E2E_ORG_ID),
            str(E2E_TEAM_DIRIGENTE_ID),
            'macro',
            macro2_start.strftime('%Y-%m-%d'),
            macro2_end.strftime('%Y-%m-%d'),
            'E2E-Macrociclo-Competitivo: Fase de competições principais',
            'Macrociclo competitivo para testes E2E',
            'active',  # mudado de 'planned' para 'active'
            None,
            str(E2E_USER_TREINADOR_ID),
        ),
        # Mesociclos
        (
            str(E2E_MESOCICLO_1_ID),
            str(E2E_ORG_ID),
            str(E2E_TEAM_DIRIGENTE_ID),
            'meso',
            meso1_start.strftime('%Y-%m-%d'),
            meso1_end.strftime('%Y-%m-%d'),
            'E2E-Meso-Fase-1: Adaptação e fundamentos',
            'Mesociclo 1 dentro do preparatório',
            'active',
            str(E2E_MACROCICLO_1_ID),  # parent
            str(E2E_USER_TREINADOR_ID),
        ),
        (
            str(E2E_MESOCICLO_2_ID),
            str(E2E_ORG_ID),
            str(E2E_TEAM_DIRIGENTE_ID),
            'meso',
            meso2_start.strftime('%Y-%m-%d'),
            meso2_end.strftime('%Y-%m-%d'),
            'E2E-Meso-Fase-2: Desenvolvimento e intensificação',
            'Mesociclo 2 dentro do preparatório',
            'active',
            str(E2E_MACROCICLO_1_ID),
            str(E2E_USER_TREINADOR_ID),
        ),
    ]
    
    cur = conn.cursor()
    for cycle in cycles_data:
        execute_sql(
            conn,
            """
            INSERT INTO training_cycles (
                id, organization_id, team_id, type,
                start_date, end_date, objective, notes, status, parent_cycle_id, created_by_user_id,
                created_at, updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            ON CONFLICT (id) DO UPDATE SET
                objective = EXCLUDED.objective,
                status = EXCLUDED.status,
                updated_at = NOW()
            """,
            cycle
        )
    
    conn.commit()
    print(f"   OK {len(cycles_data)} cycles E2E criados (2 macros + 2 mesos)")


def seed_e2e_training_sessions_dirigente(conn):
    """Cria 6 sessões de treino E2E para equipe do dirigente (3 passadas + 3 futuras)"""
    print("=> Criando training_sessions E2E (equipe dirigente)...")
    
    from datetime import datetime, timedelta
    now = datetime.now()
    
    sessions_data = [
        # Sessões passadas (readonly)
        (
            str(E2E_SESSION_IDS[0]),
            str(E2E_ORG_ID),
            str(E2E_TEAM_DIRIGENTE_ID),
            (now - timedelta(days=10)).strftime('%Y-%m-%d 10:00:00'),
            'Treino Tático Passado 1',
            'quadra',
            'Ginásio Dirigente',
            90,  # duration
            'readonly',
            45, 10, 25, 5, 10, 0, 5,  # focos (soma 100%)
            None,  # deviation_justification
            str(E2E_USER_TREINADOR_ID),
        ),
        (
            str(E2E_SESSION_IDS[1]),
            str(E2E_ORG_ID),
            str(E2E_TEAM_DIRIGENTE_ID),
            (now - timedelta(days=7)).strftime('%Y-%m-%d 14:00:00'),
            'Treino Físico Passado',
            'fisico',
            'Ginásio Dirigente',
            120,
            'readonly',
            5, 5, 5, 5, 10, 10, 60,
            None,
            str(E2E_USER_TREINADOR_ID),
        ),
        (
            str(E2E_SESSION_IDS[2]),
            str(E2E_ORG_ID),
            str(E2E_TEAM_DIRIGENTE_ID),
            (now - timedelta(days=3)).strftime('%Y-%m-%d 09:00:00'),
            'Treino Equilibrado Passado',
            'quadra',
            'Ginásio Dirigente',
            90,
            'readonly',
            15, 15, 15, 15, 10, 10, 20,
            None,
            str(E2E_USER_TREINADOR_ID),
        ),
        # Sessões futuras (scheduled - não iniciadas)
        (
            str(E2E_SESSION_IDS[3]),
            str(E2E_ORG_ID),
            str(E2E_TEAM_DIRIGENTE_ID),
            now.strftime('%Y-%m-%d 16:00:00'),  # Hoje
            'Treino Hoje',
            'quadra',
            'Ginásio Dirigente',
            90,
            'scheduled',
            45, 10, 25, 5, 10, 0, 5,
            None,
            str(E2E_USER_TREINADOR_ID),
        ),
        (
            str(E2E_SESSION_IDS[4]),
            str(E2E_ORG_ID),
            str(E2E_TEAM_DIRIGENTE_ID),
            (now + timedelta(days=3)).strftime('%Y-%m-%d 10:00:00'),
            'Treino Futuro +3',
            'quadra',
            'Ginásio Dirigente',
            90,
            'scheduled',
            5, 50, 5, 30, 0, 5, 5,
            None,
            str(E2E_USER_TREINADOR_ID),
        ),
        (
            str(E2E_SESSION_IDS[5]),
            str(E2E_ORG_ID),
            str(E2E_TEAM_DIRIGENTE_ID),
            (now + timedelta(days=7)).strftime('%Y-%m-%d 14:00:00'),
            'Treino Futuro +7',
            'fisico',
            'Ginásio Dirigente',
            120,
            'scheduled',
            5, 5, 5, 5, 10, 10, 60,
            None,
            str(E2E_USER_TREINADOR_ID),
        ),
    ]
    
    cur = conn.cursor()
    for session in sessions_data:
        execute_sql(
            conn,
            """
            INSERT INTO training_sessions (
                id, organization_id, team_id, session_at, main_objective, session_type,
                location, duration_planned_minutes, status,
                focus_attack_positional_pct, focus_defense_positional_pct,
                focus_transition_offense_pct, focus_transition_defense_pct,
                focus_attack_technical_pct, focus_defense_technical_pct,
                focus_physical_pct,
                deviation_justification, created_by_user_id,
                created_at, updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            ON CONFLICT (id) DO UPDATE SET
                status = EXCLUDED.status,
                updated_at = NOW()
            """,
            session
        )
    
    conn.commit()
    print(f"   OK {len(sessions_data)} sessions E2E criadas (3 passadas readonly + 3 futuras scheduled)")


def seed_e2e_wellness_data(conn):
    """Cria dados de wellness pré/pós para atletas E2E (últimas 3 sessões)"""
    print("=> Criando wellness_pre/post E2E...")
    
    import random
    
    # Buscar atletas da equipe do dirigente através de team_registrations
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT a.id, u.id as user_id
        FROM athletes a
        JOIN team_registrations tr ON tr.athlete_id = a.id
        JOIN persons p ON p.id = a.person_id
        LEFT JOIN users u ON u.person_id = p.id
        WHERE tr.team_id = %s
        AND a.deleted_at IS NULL
        AND tr.deleted_at IS NULL
        LIMIT 1
    """, (str(E2E_TEAM_DIRIGENTE_ID),))
    
    athlete_result = cur.fetchone()
    
    if not athlete_result:
        # Se não houver atleta na equipe do dirigente, usar o primeiro atleta do coordenador
        cur.execute("""
            SELECT DISTINCT a.id, u.id as user_id
            FROM athletes a
            JOIN team_registrations tr ON tr.athlete_id = a.id
            JOIN persons p ON p.id = a.person_id
            LEFT JOIN users u ON u.person_id = p.id
            WHERE tr.team_id = %s
            AND a.deleted_at IS NULL
            AND tr.deleted_at IS NULL
            LIMIT 1
        """, (str(E2E_TEAM_COORDENADOR_ID),))
        athlete_result = cur.fetchone()
    
    if not athlete_result:
        print("   AVISO: Nenhum atleta encontrado para criar wellness data")
        return
    
    athlete_id = athlete_result[0]  # athletes.id, NÃO person_id
    athlete_user_id = athlete_result[1] if athlete_result[1] else str(E2E_USER_TREINADOR_ID)
    
    athletes = [(athlete_id, athlete_user_id)]
    
    # Sessões passadas (últimas 3)
    closed_sessions = E2E_SESSION_IDS[:3]
    
    wellness_pre_data = []
    wellness_post_data = []
    
    for athlete_aid, athlete_uid in athletes:
        for session_id in closed_sessions:
            # Wellness PRÉ (preenchido antes do treino)
            wellness_pre_data.append((
                str(E2E_ORG_ID),
                str(session_id),
                str(athlete_aid),  # athletes.id
                random.randint(6, 9),  # sleep_hours
                random.randint(3, 5),  # sleep_quality (1-5 numérico)
                random.randint(1, 3),  # fatigue_pre (1-5)
                random.randint(1, 3),  # stress_level
                random.randint(1, 3),  # muscle_soreness (1-5)
                'Wellness PRÉ E2E automático',  # notes
                None,  # menstrual_cycle_phase
                random.randint(6, 10),  # readiness_score (1-10)
                str(athlete_uid),
            ))
            
            # Wellness PÓS (preenchido após o treino)
            wellness_post_data.append((
                str(E2E_ORG_ID),
                str(session_id),
                str(athlete_aid),  # athletes.id
                random.randint(6, 10),  # session_rpe (1-10)
                random.randint(1, 5),  # fatigue_after (1-5)
                random.randint(5, 10),  # mood_after (1-10)
                random.randint(1, 5),  # muscle_soreness_after (1-5)
                'Wellness PÓS E2E automático',  # notes
                random.randint(3, 5),  # perceived_intensity (1-5 numérico)
                False,  # flag_medical_followup
                random.randint(60, 120),  # minutes_effective
                str(athlete_uid),
            ))
    
    cur = conn.cursor()
    
    # Inserir wellness_pre
    if wellness_pre_data:
        execute_values(
            cur,
            """
            INSERT INTO wellness_pre (
                organization_id, training_session_id, athlete_id, sleep_hours, sleep_quality,
                fatigue_pre, stress_level, muscle_soreness, notes,
                menstrual_cycle_phase, readiness_score, created_by_user_id,
                filled_at, created_at
            )
            VALUES %s
            """,
            [(w[0], w[1], w[2], w[3], w[4], w[5], w[6], w[7], w[8], w[9], w[10], w[11], 
              'NOW()', 'NOW()') for w in wellness_pre_data]
        )
    
    # Inserir wellness_post
    if wellness_post_data:
        execute_values(
            cur,
            """
            INSERT INTO wellness_post (
                organization_id, training_session_id, athlete_id, session_rpe, fatigue_after,
                mood_after, muscle_soreness_after, notes, perceived_intensity,
                flag_medical_followup, minutes_effective, created_by_user_id,
                filled_at, created_at
            )
            VALUES %s
            """,
            [(w[0], w[1], w[2], w[3], w[4], w[5], w[6], w[7], w[8], w[9], w[10], w[11], 
              'NOW()', 'NOW()') for w in wellness_post_data]
        )
    
    conn.commit()
    print(f"   OK Wellness data criada ({len(wellness_pre_data)} pré + {len(wellness_post_data)} pós)")


def cleanup_e2e_stale_data(conn):
    """Remove dados E2E órfãos (teams criados em testes anteriores)"""
    print("=> Limpando dados E2E antigos...")
    
    # Soft delete trigger impede DELETE físico, então vamos fazer soft delete
    # Manter apenas as 4 equipes E2E oficiais
    protected_teams = [
        str(E2E_TEAM_DIRIGENTE_ID),
        str(E2E_TEAM_COORDENADOR_ID),
        str(E2E_TEAM_TREINADOR_ID),
        str(E2E_TEAM_ATLETA_ID),
    ]
    
    cur = conn.cursor()
    cur.execute(
        """UPDATE teams 
           SET deleted_at = NOW(), deleted_reason = 'E2E cleanup'
           WHERE name LIKE 'E2E-%%' 
           AND id NOT IN (%s, %s, %s, %s)
           AND deleted_at IS NULL""",
        tuple(protected_teams)
    )
    deleted_teams = cur.rowcount
    
    # Deletar team_memberships órfãos (não tem trigger de block)
    cur.execute(
        """DELETE FROM team_memberships 
           WHERE team_id NOT IN (SELECT id FROM teams WHERE deleted_at IS NULL)"""
    )
    
    # Deletar convites pendentes E2E
    cur.execute(
        """DELETE FROM team_memberships 
           WHERE status = 'pendente'
           AND team_id IN (SELECT id FROM teams WHERE organization_id = %s)""",
        (str(E2E_ORG_ID),)
    )
    
    conn.commit()
    print(f"   OK Removidos {deleted_teams} teams E2E antigos")


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 60)
    print("SEED E2E - HB TRACKING")
    print("Ambiente de Testes Determinísticos")
    print("=" * 60)
    print()
    print(f"DATABASE: {DATABASE_URL[:50]}...")
    print(f"ORG E2E ID: {E2E_ORG_ID}")
    print(f"SENHA PADRAO: {E2E_PASSWORD}")
    print()
    
    conn = psycopg2.connect(DATABASE_URL)
    
    try:
        # 1. Garantir estrutura básica
        seed_roles(conn)
        seed_categories(conn)
        
        # 2. Criar org E2E isolada
        seed_e2e_organization(conn)
        
        # 3. Criar pessoas e usuários E2E
        seed_e2e_persons(conn)
        seed_e2e_users(conn)
        
        # 4. Criar vínculos organizacionais
        seed_e2e_org_memberships(conn)
        
        # 5. Criar equipes E2E (4 equipes separadas)
        seed_e2e_teams(conn)
        
        # 5.1. Criar temporada E2E (depois da equipe, pois season tem FK para team)
        seed_e2e_season(conn)
        
        # 5.1.1. Criar temporada para equipe do coordenador
        seed_e2e_coordenador_season(conn)

        # 5.2. Criar team memberships E2E
        seed_e2e_team_memberships(conn)
        
        # 5.2.1. Criar staff completo da equipe do coordenador (10 atletas + 2 treinadores)
        seed_e2e_coordenador_staff(conn)
        
        # 5.3. Popular coach_membership_id nas equipes (Step 23)
        seed_e2e_populate_coach_membership_id(conn)
        
        # 5.4. Criar jogos E2E (para agenda e stats)
        seed_e2e_matches(conn)
        
        # 5.4.1. Criar jogos da equipe do coordenador (3 passados + 3 futuros)
        seed_e2e_coordenador_matches(conn)
        
        # 5.5. Criar treinos E2E (para agenda)
        seed_e2e_trainings(conn)
        
        # 5.5.1. Criar treinos da equipe do coordenador (3 passados + 3 futuros)
        seed_e2e_coordenador_trainings(conn)
        
        # =====================================================================
        # OPÇÃO B: SEED COMPLETO PARA TESTES E2E TRAINING MODULE (20 CASES)
        # =====================================================================
        
        # 5.6. Criar templates E2E (4 padrão: Tático, Físico, Equilibrado, Defesa)
        seed_e2e_templates(conn)
        
        # 5.7. Criar ciclos E2E (2 macrociclos + 2 mesociclos)
        seed_e2e_training_cycles(conn)
        
        # 5.8. Criar sessões de treino E2E (6 total: 3 passadas readonly + 3 futuras scheduled)
        seed_e2e_training_sessions_dirigente(conn)
        
        # 5.9. Criar dados wellness E2E (pré/pós para sessões passadas)
        seed_e2e_wellness_data(conn)

        # 6. Limpar dados antigos
        cleanup_e2e_stale_data(conn)
        
        print()
        print("=" * 60)
        print("[OK] SEED E2E CONCLUIDO COM SUCESSO!")
        print("=" * 60)
        print()
        print("USUÁRIOS DISPONÍVEIS:")
        print("  Email                        | Senha      | Role")
        print("  -----------------------------|------------|-------------")
        print(f"  e2e.admin@teste.com          | {E2E_PASSWORD} | dirigente")
        print(f"  e2e.coordenador@teste.com    | {E2E_PASSWORD} | coordenador")
        print(f"  e2e.treinador@teste.com      | {E2E_PASSWORD} | treinador")
        print(f"  e2e.atleta@teste.com         | {E2E_PASSWORD} | atleta")
        print(f"  e2e.membro@teste.com         | {E2E_PASSWORD} | membro")
        print()
        print("NOTA: Superadmin (adm@handballtrack.app / Admin@123!) criado via migrations")
        print()
        print(f"ORGANIZAÇÃO E2E: {E2E_ORG_NAME}")
        print()
        print("EQUIPES E2E (1:1 usuário-equipe):")
        print(f"  - {E2E_TEAM_NAMES['dirigente']} (e2e.admin)")
        print(f"  - {E2E_TEAM_NAMES['coordenador']} (e2e.coordenador)")
        print(f"  - {E2E_TEAM_NAMES['treinador']} (e2e.treinador)")
        print(f"  - {E2E_TEAM_NAMES['atleta']} (e2e.atleta)")
        print()
        print("DADOS PARA TESTES (equipe do dirigente):")
        print("  - 3 jogos (1 passado com vitória 3-1, 2 futuros)")
        print("  - 3 treinos (1 passado com presença, 2 futuros)")
        print("  - 1 atleta 14 anos (compatível com Infantil)")
        print("  - 1 pessoa veterano 39 anos (para teste negativo)")
        print()
        print("DADOS PARA TESTES (equipe do coordenador):")
        print("  - 10 atletas Infantil Masculino (12-14 anos)")
        print("  - 2 treinadores auxiliares")
        print("  - 6 jogos (3 passados com resultados, 3 futuros)")
        print("  - 6 treinos (3 passados readonly, 3 futuros scheduled)")
        print()
        print("DADOS PARA TESTES E2E TRAINING MODULE (OPÇÃO B - COMPLETO):")
        print("  [OK] 4 templates padrão (Tático Ofensivo, Físico, Equilibrado, Defesa)")
        print("  [OK] 2 macrociclos (Preparatório ativo, Competitivo futuro)")
        print("  [OK] 2 mesociclos (Fase 1/2 dentro do Preparatório)")
        print("  [OK] 6 sessões de treino (3 passadas readonly + 3 futuras scheduled)")
        print("  [OK] 6 registros wellness (3 pré + 3 pós para sessões passadas)")
        print()
        print("TESTES DISPONÍVEIS:")
        print("  Playwright: npx playwright test tests/e2e/training/training-module.spec.ts")
        print("  Casos: 20 (A-Navigation 1, B-CRUD 5, C-Limit+Preview 2, D-Mobile 1, E-Features 5, F-Draft 1, G-Validations 5)")
        print()
        
    except Exception as e:
        conn.rollback()
        print(f"\nERRO durante seed: {e}")
        raise
    finally:
        conn.close()


if __name__ == '__main__':
    main()
