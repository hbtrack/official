"""
FASE 8 - Script de Validação de Conformidade RAG

Valida que o banco de dados e a aplicação estão em conformidade
com as regras definidas em REGRAS_SISTEMAS.md

Referências RAG:
- RDB1-RDB14: Regras de banco de dados
- R1-R42: Regras estruturais
- RF1-RF31: Regras funcionais

Allowlists (RDB2.1, RDB4.1):
- ALLOWLIST_INT_PK: tabelas que podem usar integer/smallint como PK
- ALLOWLIST_NO_SOFT_DELETE: tabelas que não requerem soft delete
- EXCLUDE_SOFT_DELETE: tabelas excluídas por outras regras (ex: audit_logs por RDB5)
"""
import sys
from sqlalchemy import text
from app.core.db import engine
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


# =============================================================================
# ALLOWLISTS (RDB2.1 e RDB4.1) - Lista fechada
# Qualquer tabela fora destas listas é DOMÍNIO e deve seguir RDB2/RDB4
# =============================================================================

# RDB2.1: Tabelas que podem usar integer/smallint como PK
ALLOWLIST_INT_PK = {
    'roles',              # Lookup de papéis (R4)
    'categories',         # Lookup de categorias (R15)
    'permissions',        # Lookup de permissões
    'role_permissions',   # Junction table
    'alembic_version',    # Técnica (migrations)
}

# RDB4.1: Tabelas que não requerem deleted_at/deleted_reason
ALLOWLIST_NO_SOFT_DELETE = {
    'roles',              # Lookup imutável
    'categories',         # Lookup imutável
    'permissions',        # Lookup imutável
    'role_permissions',   # Junction table imutável
    'alembic_version',    # Técnica (migrations)
}

# Tabelas excluídas do soft delete por outras regras
EXCLUDE_SOFT_DELETE = {
    'audit_logs',         # RDB5: append-only, nunca deletada
}


def print_header(title: str):
    """Imprime cabeçalho formatado."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_check(name: str, passed: bool, details: str = ""):
    """Imprime resultado de verificação."""
    status = "[PASS]" if passed else "[FAIL]"
    print(f"  {status} | {name}")
    if details:
        print(f"         -> {details}")


def print_info(message: str):
    """Imprime informacao."""
    print(f"  [INFO] {message}")


def validate_rag_conformance():
    """Executa todas as validações de conformidade RAG."""
    results = []
    
    print_header("FASE 8 - Validação de Conformidade RAG")
    print(f"  Ambiente: {settings.ENV}")
    print(f"  Database: {settings.DATABASE_URL[:50]}...")
    
    # Mostrar allowlists para transparência
    print_info(f"ALLOWLIST_INT_PK: {sorted(ALLOWLIST_INT_PK)}")
    print_info(f"ALLOWLIST_NO_SOFT_DELETE: {sorted(ALLOWLIST_NO_SOFT_DELETE | EXCLUDE_SOFT_DELETE)}")
    
    with engine.connect() as conn:
        # ============================================================
        # RDB1: PostgreSQL + pgcrypto
        # ============================================================
        print_header("RDB1: PostgreSQL 17 + pgcrypto")
        
        result = conn.execute(text("SELECT version()"))
        pg_version = result.scalar()
        passed = "PostgreSQL" in pg_version and ("17" in pg_version or "16" in pg_version or "15" in pg_version)
        print_check("PostgreSQL version", passed, pg_version[:60])
        results.append(("RDB1-version", passed))
        
        result = conn.execute(text("SELECT extname FROM pg_extension WHERE extname = 'pgcrypto'"))
        pgcrypto = result.scalar()
        passed = pgcrypto == "pgcrypto"
        print_check("pgcrypto extension", passed, f"Found: {pgcrypto}")
        results.append(("RDB1-pgcrypto", passed))
        
        # ============================================================
        # RDB2: PKs são UUID v4 server-generated
        # RDB2.1: Exceção para tabelas técnicas/lookup (integer permitido)
        # ============================================================
        print_header("RDB2: UUIDs como PKs (+ RDB2.1 exceções)")
        
        # Usar allowlist definida no topo
        allowlist_sql = "('" + "', '".join(ALLOWLIST_INT_PK) + "')"
        
        result = conn.execute(text(f"""
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE column_name = 'id'
              AND table_schema = 'public'
              AND table_name NOT IN {allowlist_sql}
            ORDER BY table_name
        """))
        domain_tables = result.fetchall()
        all_uuid = all(row[2] == 'uuid' for row in domain_tables)
        non_uuid = [row[0] for row in domain_tables if row[2] != 'uuid']
        
        if all_uuid:
            print_check("Domain tables use UUID PKs", True, f"{len(domain_tables)} domain tables checked")
        else:
            print_check("Domain tables use UUID PKs", False, f"Non-UUID: {non_uuid}")
        results.append(("RDB2-uuid", all_uuid))
        
        # ============================================================
        # RDB3: Timestamps em UTC (timestamptz)
        # ============================================================
        print_header("RDB3: Timestamps em UTC")
        
        result = conn.execute(text("SHOW timezone"))
        timezone = result.scalar()
        passed = timezone in ("UTC", "Etc/UTC")
        print_check("Database timezone", passed, f"Timezone: {timezone}")
        results.append(("RDB3-timezone", passed))
        
        result = conn.execute(text("""
            SELECT COUNT(*) FROM information_schema.columns
            WHERE column_name IN ('created_at', 'updated_at', 'deleted_at')
              AND table_schema = 'public'
              AND data_type = 'timestamp with time zone'
        """))
        timestamptz_count = result.scalar()
        passed = timestamptz_count > 0
        print_check("timestamptz columns", passed, f"{timestamptz_count} columns found")
        results.append(("RDB3-timestamptz", passed))
        
        # ============================================================
        # RDB4: Soft delete obrigatório
        # RDB4.1: Exceção para tabelas técnicas/lookup
        # ============================================================
        # Tabelas EXCLUÍDAS da verificação (conforme RAG):
        # - ALLOWLIST_NO_SOFT_DELETE: lookup tables
        # - EXCLUDE_SOFT_DELETE: audit_logs (RDB5 append-only)
        print_header("RDB4: Soft Delete (+ RDB4.1 exceções)")
        
        # Combinar allowlists
        all_excluded = ALLOWLIST_NO_SOFT_DELETE | EXCLUDE_SOFT_DELETE
        excluded_sql = "('" + "', '".join(all_excluded) + "')"
        
        result = conn.execute(text(f"""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_type = 'BASE TABLE'
              AND table_name NOT IN {excluded_sql}
        """))
        domain_tables = [row[0] for row in result.fetchall()]
        
        tables_with_deleted_at = 0
        missing_tables = []
        for table in domain_tables:
            result = conn.execute(text(f"""
                SELECT COUNT(*) FROM information_schema.columns
                WHERE table_name = '{table}'
                  AND column_name = 'deleted_at'
            """))
            if result.scalar() > 0:
                tables_with_deleted_at += 1
            else:
                missing_tables.append(table)
        
        # RDB4 exige 100% das tabelas de domínio com deleted_at
        passed = len(missing_tables) == 0
        if passed:
            print_check("Tables with deleted_at", passed, f"{tables_with_deleted_at}/{len(domain_tables)} domain tables")
        else:
            print_check("Tables with deleted_at", passed, f"Missing: {missing_tables}")
        results.append(("RDB4-soft-delete", passed))
        
        # ============================================================
        # RDB5: audit_logs imutável
        # ============================================================
        print_header("RDB5: Audit Logs Imutável")
        
        result = conn.execute(text("""
            SELECT COUNT(*) FROM pg_trigger
            WHERE tgrelid = 'audit_logs'::regclass
        """))
        audit_triggers = result.scalar()
        passed = audit_triggers >= 1
        print_check("audit_logs triggers", passed, f"{audit_triggers} trigger(s) found")
        results.append(("RDB5-audit", passed))
        
        # ============================================================
        # RDB6: Super Admin único
        # ============================================================
        print_header("RDB6: Super Admin Único")
        
        result = conn.execute(text("SELECT COUNT(*) FROM users WHERE is_superadmin = true"))
        superadmin_count = result.scalar()
        passed = superadmin_count == 1
        print_check("Exactly 1 superadmin", passed, f"Found: {superadmin_count}")
        results.append(("RDB6-superadmin", passed))
        
        # ============================================================
        # R4: Papéis do sistema
        # ============================================================
        print_header("R4: Papéis do Sistema")
        
        result = conn.execute(text("SELECT code FROM roles ORDER BY code"))
        roles = [row[0] for row in result.fetchall()]
        expected_roles = {"atleta", "coordenador", "dirigente", "treinador"}
        passed = expected_roles.issubset(set(roles))
        print_check("Required roles exist", passed, f"Found: {', '.join(roles)}")
        results.append(("R4-roles", passed))
        
        # ============================================================
        # R15: Categorias de idade
        # ============================================================
        print_header("R15: Categorias de Idade")
        
        result = conn.execute(text("SELECT code, min_age, max_age FROM categories ORDER BY min_age"))
        categories = result.fetchall()
        passed = len(categories) >= 6
        cat_list = ", ".join([f"{c[0]}({c[1]}-{c[2]})" for c in categories])
        print_check("Categories seeded", passed, f"Found: {cat_list}")
        results.append(("R15-categories", passed))
        
        # ============================================================
        # R34: Organização única (V1)
        # ============================================================
        print_header("R34: Organização Única")
        
        result = conn.execute(text("SELECT COUNT(*) FROM organizations"))
        org_count = result.scalar()
        passed = org_count >= 1
        print_check("Organization exists", passed, f"Found: {org_count}")
        results.append(("R34-organization", passed))
        
        # ============================================================
        # VIEW: v_seasons_with_status
        # ============================================================
        print_header("VIEW: v_seasons_with_status")
        
        result = conn.execute(text("""
            SELECT COUNT(*) FROM pg_views 
            WHERE viewname = 'v_seasons_with_status'
        """))
        view_exists = result.scalar() > 0
        print_check("VIEW exists", view_exists)
        results.append(("VIEW-seasons", view_exists))
        
        if view_exists:
            result = conn.execute(text("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'v_seasons_with_status'
            """))
            columns = [row[0] for row in result.fetchall()]
            has_status = "status_derivado" in columns or "status" in columns
            print_check("Has status column", has_status, f"Columns: {', '.join(columns[:5])}...")
            results.append(("VIEW-status-column", has_status))
        
        # ============================================================
        # Triggers documentados
        # ============================================================
        print_header("Triggers Documentados")
        
        result = conn.execute(text("""
            SELECT COUNT(DISTINCT tgname) FROM pg_trigger t
            JOIN pg_class c ON t.tgrelid = c.oid
            WHERE c.relnamespace = 'public'::regnamespace
              AND NOT tgisinternal
        """))
        trigger_count = result.scalar()
        passed = trigger_count >= 5
        print_check("Triggers defined", passed, f"Found: {trigger_count} triggers")
        results.append(("Triggers", passed))
        
        # ============================================================
        # Índices importantes
        # ============================================================
        print_header("Índices de Performance")
        
        result = conn.execute(text("""
            SELECT COUNT(*) FROM pg_indexes
            WHERE schemaname = 'public'
        """))
        index_count = result.scalar()
        passed = index_count >= 10
        print_check("Indexes created", passed, f"Found: {index_count} indexes")
        results.append(("Indexes", passed))
    
    # ============================================================
    # Resumo Final
    # ============================================================
    print_header("RESUMO DA VALIDACAO")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    success_rate = (passed_count / total_count) * 100
    
    print(f"\n  Total: {passed_count}/{total_count} verificacoes passaram ({success_rate:.1f}%)")
    
    if success_rate >= 90:
        print(f"\n  [OK] SISTEMA ESTA EM CONFORMIDADE COM RAG (>= 90%)")
        return True
    elif success_rate >= 70:
        print(f"\n  [WARN] SISTEMA PARCIALMENTE CONFORME (70-90%)")
        return False
    else:
        print(f"\n  [FAIL] SISTEMA NAO CONFORME (< 70%)")
        return False


def validate_security_checklist():
    """Valida checklist de segurança."""
    print_header("8.3 - Checklist de Segurança")
    
    results = []
    
    # JWT_SECRET forte
    jwt_secret = settings.JWT_SECRET
    passed = len(jwt_secret) >= 32 and jwt_secret != "changeme"
    print_check("JWT_SECRET forte (>=32 chars)", passed)
    results.append(passed)
    
    # ENV não é production sem configuração
    if settings.is_production:
        passed = "localhost" not in settings.DATABASE_URL
        print_check("DATABASE_URL não é localhost em prod", passed)
        results.append(passed)
    
    # CORS configurado
    cors_origins = settings.cors_origins_list
    passed = len(cors_origins) > 0
    print_check("CORS_ORIGINS configurado", passed, f"Origins: {cors_origins[:3]}...")
    results.append(passed)
    
    return all(results)


def validate_observability():
    """Valida checklist de observabilidade."""
    print_header("8.5 - Checklist de Observabilidade")
    
    results = []
    
    # Verificar se logging está configurado
    import app.core.logging as app_logging
    passed = hasattr(app_logging, 'JSONFormatter')
    print_check("JSONFormatter disponível", passed)
    results.append(passed)
    
    # Verificar middleware
    import app.core.middleware as app_middleware
    passed = hasattr(app_middleware, 'RequestIDMiddleware')
    print_check("RequestIDMiddleware disponível", passed)
    results.append(passed)
    
    return all(results)


if __name__ == "__main__":
    print("\n" + "="*60)
    print("  HB TRACKING - FASE 8: VALIDACAO PRODUCTION-READY")
    print("="*60)
    
    try:
        rag_ok = validate_rag_conformance()
        security_ok = validate_security_checklist()
        obs_ok = validate_observability()
        
        print_header("RESULTADO FINAL")
        
        if rag_ok and security_ok and obs_ok:
            print("\n  [OK] SISTEMA PRONTO PARA PRODUCAO")
            sys.exit(0)
        else:
            print("\n  [WARN] VERIFICAR ITENS PENDENTES")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n  [ERROR] ERRO NA VALIDACAO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
