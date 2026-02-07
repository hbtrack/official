"""
Health check endpoint

Referências RAG:
- RDB1: PostgreSQL + pgcrypto
- RDB5: audit_logs imutável
- R3, RDB6: Super Admin único
- R4: Papéis do sistema
- R15: Categorias de idade
"""
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from app.core.db import healthcheck_db, engine
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Health"])


@router.get("/health", status_code=status.HTTP_200_OK)
async def health():
    """
    Health check completo

    Verifica:
    - Database connection
    - PostgreSQL version
    - pgcrypto extension (RDB1)
    - Alembic migration version

    Returns:
        dict: Status de saúde do sistema
    """
    db_health = healthcheck_db()

    return {
        "status": "healthy" if db_health["status"] == "healthy" else "unhealthy",
        "version": settings.API_VERSION_NUMBER,
        "environment": settings.ENV,
        "database": db_health
    }


@router.get("/health/liveness", status_code=status.HTTP_200_OK)
async def liveness():
    """
    Liveness probe (Kubernetes)

    Retorna 200 se a aplicação está rodando
    """
    return {"status": "alive"}


@router.get("/health/readiness", status_code=status.HTTP_200_OK)
async def readiness():
    """
    Readiness probe (Kubernetes)

    Retorna 200 se a aplicação está pronta para receber tráfego
    """
    db_health = healthcheck_db()

    if db_health["status"] != "healthy":
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not_ready", "reason": "database_unavailable"}
        )

    return {"status": "ready"}


@router.get("/health/full", status_code=status.HTTP_200_OK)
async def health_full():
    """
    Healthcheck completo (validações profundas)

    Verifica:
    - Database connection
    - Critical tables exist
    - Alembic migration version
    - Super admin exists (R3, RDB6)
    - Roles seeded (R4)
    - Categories seeded (R15)
    - VIEW v_seasons_with_status exists
    
    Returns:
        dict: Status detalhado de saúde com todas as validações
    """
    db_health = healthcheck_db()

    if db_health["status"] != "healthy":
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "database": db_health}
        )

    # Validações adicionais
    checks = {}

    try:
        with engine.connect() as conn:
            # Verificar super admin (R3, RDB6)
            result = conn.execute(text(
                "SELECT COUNT(*) FROM users WHERE is_superadmin = true"
            ))
            superadmin_count = result.scalar()
            checks["superadmin_exists"] = superadmin_count == 1
            checks["superadmin_count"] = superadmin_count

            # Verificar roles (R4)
            result = conn.execute(text("SELECT COUNT(*) FROM roles"))
            roles_count = result.scalar()
            checks["roles_seeded"] = roles_count >= 4
            checks["roles_count"] = roles_count

            # Verificar categorias (R15)
            result = conn.execute(text("SELECT COUNT(*) FROM categories"))
            categories_count = result.scalar()
            checks["categories_seeded"] = categories_count >= 6
            checks["categories_count"] = categories_count

            # Verificar VIEW v_seasons_with_status
            result = conn.execute(text(
                "SELECT COUNT(*) FROM pg_views WHERE viewname = 'v_seasons_with_status'"
            ))
            checks["view_seasons_exists"] = result.scalar() > 0

            # Verificar organizations (R34 - clube único)
            result = conn.execute(text("SELECT COUNT(*) FROM organizations"))
            org_count = result.scalar()
            checks["organization_exists"] = org_count >= 1
            checks["organization_count"] = org_count

            # Verificar triggers críticos
            result = conn.execute(text("""
                SELECT COUNT(*) FROM pg_trigger t
                JOIN pg_class c ON t.tgrelid = c.oid
                WHERE c.relname = 'audit_logs'
                  AND t.tgname LIKE 'trg_%'
            """))
            checks["audit_triggers_exist"] = result.scalar() > 0

    except Exception as e:
        logger.error(f"Healthcheck failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "error": str(e)}
        )

    # Determinar status geral
    critical_checks = [
        checks.get("superadmin_exists", False),
        checks.get("roles_seeded", False),
        checks.get("organization_exists", False),
    ]
    
    if all(critical_checks):
        overall_status = "healthy"
    elif any(critical_checks):
        overall_status = "degraded"
    else:
        overall_status = "unhealthy"

    return {
        "status": overall_status,
        "version": settings.API_VERSION_NUMBER,
        "environment": settings.ENV,
        "database": db_health,
        "checks": checks
    }
