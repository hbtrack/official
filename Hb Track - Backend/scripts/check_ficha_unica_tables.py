"""
Script de Verificação de Tabelas para Ficha Única
FASE 1.1 - Verificar Tabelas Existentes

Referência: FICHA.MD - Seção 1.1
"""
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import inspect, text
from app.core.db import engine

# Tabelas necessárias para Ficha Única
REQUIRED_TABLES = [
    # Pessoas e dados normalizados
    'persons',
    'person_contacts',
    'person_documents',
    'person_addresses',
    'person_media',
    
    # Usuários e autenticação
    'users',
    'roles',
    'password_resets',
    
    # Organizações e vínculos
    'organizations',
    'org_memberships',
    
    # Equipes e atletas
    'teams',
    'athletes',
    'team_registrations',
    
    # Idempotência (será criada nesta fase)
    'idempotency_keys',
]

# Tabelas de lookup necessárias
LOOKUP_TABLES = [
    'categories',
    'defensive_positions',
    'offensive_positions',
    'schooling_levels',  # Nome correto da tabela no banco
]

def check_table_exists(inspector, table_name: str) -> bool:
    """Verifica se uma tabela existe no banco"""
    return table_name in inspector.get_table_names()

def check_column_exists(inspector, table_name: str, column_name: str) -> bool:
    """Verifica se uma coluna existe em uma tabela"""
    if not check_table_exists(inspector, table_name):
        return False
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def check_trigger_exists(table_name: str) -> bool:
    """Verifica se trigger de updated_at existe"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text(f"""
                SELECT EXISTS (
                    SELECT 1 FROM pg_trigger 
                    WHERE tgname = 'trg_{table_name}_updated_at'
                )
            """))
            return result.scalar()
    except Exception:
        return False

def main():
    print("=" * 60)
    print("VERIFICAÇÃO DE TABELAS - FICHA ÚNICA")
    print("=" * 60)
    print()
    
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    # ========== TABELAS PRINCIPAIS ==========
    print("📋 TABELAS PRINCIPAIS")
    print("-" * 40)
    
    missing_main = []
    for table in REQUIRED_TABLES:
        exists = table in existing_tables
        status = "✅" if exists else "❌"
        print(f"{status} {table}")
        if not exists:
            missing_main.append(table)
    
    print()
    
    # ========== TABELAS DE LOOKUP ==========
    print("📋 TABELAS DE LOOKUP")
    print("-" * 40)
    
    missing_lookup = []
    for table in LOOKUP_TABLES:
        exists = table in existing_tables
        status = "✅" if exists else "❌"
        print(f"{status} {table}")
        if not exists:
            missing_lookup.append(table)
    
    print()
    
    # ========== CAMPOS DE AUDITORIA ==========
    print("📋 CAMPOS DE AUDITORIA (created_by_user_id)")
    print("-" * 40)
    
    audit_tables = [
        'person_contacts', 'person_documents', 
        'person_addresses', 'person_media',
        'org_memberships', 'team_registrations'
    ]
    
    missing_audit = []
    for table in audit_tables:
        if table in existing_tables:
            has_audit = check_column_exists(inspector, table, 'created_by_user_id')
            status = "✅" if has_audit else "⚠️ "
            print(f"{status} {table}.created_by_user_id")
            if not has_audit:
                missing_audit.append(table)
        else:
            print(f"⏭️  {table} (tabela não existe)")
    
    print()
    
    # ========== TRIGGERS DE UPDATED_AT ==========
    print("📋 TRIGGERS DE UPDATED_AT")
    print("-" * 40)
    
    trigger_tables = [
        'persons', 'users', 'organizations', 
        'teams', 'athletes', 'org_memberships', 
        'team_registrations'
    ]
    
    missing_triggers = []
    for table in trigger_tables:
        has_trigger = check_trigger_exists(table)
        status = "✅" if has_trigger else "⚠️ "
        print(f"{status} trg_{table}_updated_at")
        if not has_trigger:
            missing_triggers.append(table)
    
    print()
    
    # ========== RESUMO ==========
    print("=" * 60)
    print("RESUMO")
    print("=" * 60)
    
    total_issues = len(missing_main) + len(missing_lookup)
    
    if missing_main:
        print(f"\n❌ Tabelas principais faltando ({len(missing_main)}):")
        for t in missing_main:
            print(f"   - {t}")
    
    if missing_lookup:
        print(f"\n⚠️  Tabelas de lookup faltando ({len(missing_lookup)}):")
        for t in missing_lookup:
            print(f"   - {t}")
    
    if missing_audit:
        print(f"\n⚠️  Campos de auditoria faltando ({len(missing_audit)}):")
        for t in missing_audit:
            print(f"   - {t}.created_by_user_id")
    
    if missing_triggers:
        print(f"\n⚠️  Triggers faltando ({len(missing_triggers)}):")
        for t in missing_triggers:
            print(f"   - trg_{t}_updated_at")
    
    if total_issues == 0 and not missing_audit and not missing_triggers:
        print("\n🎉 Todas as tabelas e estruturas estão OK!")
        return 0
    else:
        print(f"\n⚠️  Execute as migrations para corrigir os problemas acima.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
