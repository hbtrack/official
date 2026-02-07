#!/usr/bin/env python3
"""
Validação RAG rápida para produção
"""
import os
import sys
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

class RAGValidator:
    def __init__(self, conn):
        self.conn = conn
        self.cursor = conn.cursor(cursor_factory=RealDictCursor)
        self.errors = []
        self.success_count = 0
        self.total_checks = 0

    def check(self, name, query, expected=True, error_msg=''):
        self.total_checks += 1
        try:
            self.cursor.execute(query)
            result = self.cursor.fetchone()
            passed = bool(result and result.get('passed', False)) == expected

            if passed:
                self.success_count += 1
                print(f'  [OK] {name}')
                return True
            else:
                self.errors.append(f'{name}: {error_msg or "Check failed"}')
                print(f'  [FAIL] {name}')
                return False
        except Exception as e:
            self.errors.append(f'{name}: {str(e)}')
            print(f'  [ERROR] {name}: {str(e)}')
            return False

print('=' * 80)
print('VALIDACAO RAG - PRODUCAO')
print('=' * 80)

conn = psycopg2.connect(DATABASE_URL)
validator = RAGValidator(conn)

# R8/R39: NOT NULL
print('\n[1] R8/R39: season_id e team_id NOT NULL')
validator.check(
    'season_id NOT NULL',
    """
    SELECT (is_nullable = 'NO') AS passed
    FROM information_schema.columns
    WHERE table_name = 'training_sessions' AND column_name = 'season_id'
    """
)
validator.check(
    'team_id NOT NULL',
    """
    SELECT (is_nullable = 'NO') AS passed
    FROM information_schema.columns
    WHERE table_name = 'training_sessions' AND column_name = 'team_id'
    """
)

# Sem NULLs em dados
validator.check(
    'Sem NULLs em season_id',
    """
    SELECT (COUNT(*) = 0) AS passed
    FROM training_sessions
    WHERE season_id IS NULL AND deleted_at IS NULL
    """
)
validator.check(
    'Sem NULLs em team_id',
    """
    SELECT (COUNT(*) = 0) AS passed
    FROM training_sessions
    WHERE team_id IS NULL AND deleted_at IS NULL
    """
)

# RF29/RD85: Views
print('\n[2] RF29/RD85: Materialized Views')
for view in ['mv_training_performance', 'mv_athlete_training_summary',
             'mv_wellness_summary', 'mv_medical_cases_summary']:
    validator.check(
        f'View {view}',
        f"SELECT (COUNT(*) > 0) AS passed FROM pg_matviews WHERE matviewname = '{view}'"
    )

# RDB4/RDB5: Soft delete e audit
print('\n[3] RDB4/RDB5: Soft Delete e Audit')
validator.check(
    'deleted_at existe',
    """
    SELECT (COUNT(*) > 0) AS passed
    FROM information_schema.columns
    WHERE table_name = 'training_sessions' AND column_name = 'deleted_at'
    """
)
validator.check(
    'audit_logs existe',
    """
    SELECT (COUNT(*) > 0) AS passed
    FROM information_schema.tables
    WHERE table_name = 'audit_logs'
    """
)

# R33: FKs
print('\n[4] R33: Foreign Keys')
validator.check(
    'FK season',
    """
    SELECT (COUNT(*) > 0) AS passed
    FROM pg_constraint
    WHERE conrelid = 'training_sessions'::regclass
      AND contype = 'f'
      AND conname LIKE '%season%'
    """
)
validator.check(
    'FK team',
    """
    SELECT (COUNT(*) > 0) AS passed
    FROM pg_constraint
    WHERE conrelid = 'training_sessions'::regclass
      AND contype = 'f'
      AND conname LIKE '%team%'
    """
)

# Sem registros órfãos
validator.check(
    'Sem registros órfãos (season)',
    """
    SELECT (COUNT(*) = 0) AS passed
    FROM training_sessions ts
    LEFT JOIN seasons s ON s.id = ts.season_id
    WHERE ts.deleted_at IS NULL AND s.id IS NULL
    """
)
validator.check(
    'Sem registros órfãos (team)',
    """
    SELECT (COUNT(*) = 0) AS passed
    FROM training_sessions ts
    LEFT JOIN teams t ON t.id = ts.team_id
    WHERE ts.deleted_at IS NULL AND t.id IS NULL
    """
)

# Índices
print('\n[5] RD85: Índices')
for idx in ['idx_training_sessions_season', 'idx_training_sessions_team',
            'idx_training_sessions_org_season_date']:
    validator.check(
        f'Índice {idx}',
        f"""
        SELECT (COUNT(*) > 0) AS passed
        FROM pg_indexes
        WHERE tablename = 'training_sessions' AND indexname = '{idx}'
        """
    )

# Report
print('\n' + '=' * 80)
print(f'Total checks: {validator.total_checks}')
print(f'Sucessos: {validator.success_count}')
print(f'Falhas: {len(validator.errors)}')
success_rate = (validator.success_count / validator.total_checks * 100) if validator.total_checks > 0 else 0
print(f'Taxa de sucesso: {success_rate:.1f}%')

if len(validator.errors) == 0:
    print('\n[SUCCESS] CONFORMIDADE RAG: APROVADO')
    print('Sistema esta 100% conforme REGRAS_SISTEMAS.md V1.1')
else:
    print('\n[FAIL] CONFORMIDADE RAG: REPROVADO')
    for i, error in enumerate(validator.errors, 1):
        print(f'  {i}. {error}')

print('=' * 80)

conn.close()
sys.exit(0 if len(validator.errors) == 0 else 1)
