"""
Aplicação principal FastAPI - HB Tracking

FASE 7 - Preparação para Produção

Referências RAG:
- R31: Ações críticas auditáveis
- R32: Log obrigatório (quem, quando, o quê)
- R34: Clube único na V1
- R42: Modo somente leitura sem vínculo ativo
"""
import logging
import sys
from typing import Any, Dict, List

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from sqlalchemy.exc import IntegrityError

from app.api.v1 import api_router
from app.core.config import settings
from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError, ValidationError
from app.core.logging import setup_logging
from app.core.middleware import RequestIDMiddleware, SecurityHeadersMiddleware
from app.core.rate_limit import limiter, rate_limit_exceeded_handler
from app.middleware.csrf import CSRFMiddleware
from app.schemas.error import ErrorCode

# Configurar logging estruturado (FASE 7)
setup_logging(settings.ENV, settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


def _get_request_id(request: Request) -> str:
    """
    Obtém o request_id de forma resiliente.

    Dá preferência ao header X-Request-ID (tráfego externo)
    e cai para request.state.request_id (gerado pelo middleware)
    antes de retornar 'unknown'.
    """
    header_id = request.headers.get("X-Request-ID")
    state_id = getattr(request.state, "request_id", None)
    return header_id or state_id or "unknown"


def _serialize_validation_errors(exc: RequestValidationError) -> List[Dict[str, Any]]:
    """
    Normaliza a estrutura de errors() do Pydantic para um formato JSON-safe.

    Converte objetos em ctx para string para evitar problemas de serialização.
    """
    serialized: List[Dict[str, Any]] = []

    for error in exc.errors():
        error_dict: Dict[str, Any] = {
            "loc": error.get("loc", []),
            "msg": str(error.get("msg", "")),
            "type": error.get("type", "value_error"),
        }

        ctx = error.get("ctx")
        if isinstance(ctx, dict):
            error_dict["ctx"] = {k: str(v) for k, v in ctx.items()}

        serialized.append(error_dict)

    return serialized


# Criar app FastAPI
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION_NUMBER,
    docs_url=f"/api/{settings.API_VERSION}/docs",
    redoc_url=f"/api/{settings.API_VERSION}/redoc",
    openapi_url=f"/api/{settings.API_VERSION}/openapi.json",
)

# ============================================================================
# Middlewares - Ordem Importa!
# FastAPI processa middlewares em ordem REVERSA (LIFO - Last In First Out)
# ============================================================================

# CORS — Política determinística lida de settings (AR_234)
# Starlette processa middlewares em ordem LIFO: o adicionado PRIMEIRO é o INNERMOST
# (processa resposta primeiro; recebe request por último).
# Preflight OPTIONS é seguro: CSRFMiddleware só intercepta UNSAFE_METHODS
# (POST/PUT/PATCH/DELETE) — OPTIONS passa diretamente para o CORSMiddleware.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.cors_allow_methods_list,
    allow_headers=settings.cors_allow_headers_list,
    expose_headers=settings.cors_expose_headers_list,
    max_age=settings.CORS_MAX_AGE,
    **({"allow_origin_regex": settings.CORS_ALLOW_ORIGIN_REGEX}
       if settings.CORS_ALLOW_ORIGIN_REGEX else {}),
)

# Security Headers (depois do CORS)
app.add_middleware(
    SecurityHeadersMiddleware,
    is_production=settings.is_production,
    hsts_max_age=settings.HSTS_MAX_AGE,
    hsts_include_subdomains=settings.HSTS_INCLUDE_SUBDOMAINS,
    hsts_preload=settings.HSTS_PRELOAD,
)

# Request ID (depois de Security Headers)
app.add_middleware(RequestIDMiddleware)

# CSRF Protection (depois de Request ID, antes de rate limiting)
# Valida X-CSRF-Token para métodos unsafe (POST/PUT/PATCH/DELETE) com Cookie auth
app.add_middleware(CSRFMiddleware)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# ============================================================================
# Exception Handlers Globais (FASE 6)
# ============================================================================


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handler para erros de validação Pydantic.

    Retorna erro 422 com detalhes dos campos inválidos.
    Serializa ValueError objects para JSON-safe dict.
    """
    errors = _serialize_validation_errors(exc)
    logger.warning("Validation error: %s", errors)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error_code": ErrorCode.VALIDATION_ERROR.value,
            "message": "Erro de validação",
            "details": {"errors": errors},
            "request_id": _get_request_id(request),
        },
    )


@app.exception_handler(NotFoundError)
async def not_found_error_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    """
    Handler para NotFoundError - recursos não encontrados.

    Mapeia exceção de serviço para HTTP 404.
    """
    logger.info("NotFoundError: %s", exc.message)

    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error_code": "NOT_FOUND",
            "message": exc.message,
            "request_id": _get_request_id(request),
        },
    )


@app.exception_handler(ForbiddenError)
async def forbidden_error_handler(request: Request, exc: ForbiddenError) -> JSONResponse:
    """
    Handler para ForbiddenError - acesso negado.

    Mapeia exceção de serviço para HTTP 403.
    """
    logger.warning("ForbiddenError: %s", exc.message)

    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={
            "error_code": "FORBIDDEN",
            "message": exc.message,
            "request_id": _get_request_id(request),
        },
    )


@app.exception_handler(ValidationError)
async def custom_validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """
    Handler para ValidationError customizado.

    Mapeia exceção de serviço para HTTP 422.
    """
    logger.warning("ValidationError: %s", exc.message)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error_code": "VALIDATION_ERROR",
            "message": exc.message,
            "field": exc.field,
            "request_id": _get_request_id(request),
        },
    )


@app.exception_handler(ConflictError)
async def conflict_error_handler(request: Request, exc: ConflictError) -> JSONResponse:
    """
    Handler para ConflictError - conflitos de dados.

    Mapeia exceção de serviço para HTTP 409.
    """
    logger.warning("ConflictError: %s", exc.message)

    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "error_code": "CONFLICT",
            "message": exc.message,
            "request_id": _get_request_id(request),
        },
    )


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    """
    Handler para erros de integridade do banco.

    Mapeia constraints do PostgreSQL para error codes específicos.
    """
    # Detectar constraint específica
    error_msg = str(exc.orig) if getattr(exc, "orig", None) is not None else str(exc)
    error_msg_lower = error_msg.lower()

    logger.error("IntegrityError: %s", error_msg)

    error_code = "DATABASE_CONSTRAINT_VIOLATION"
    message = "Violação de constraint do banco de dados"

    # RDB10: Team registration overlap
    if "uq_team_reg_active_athlete_team_season" in error_msg:
        error_code = ErrorCode.TEAM_REG_OVERLAP.value
        message = "Atleta já possui inscrição ativa nesta equipe/temporada (RDB10)"

    # RDB9: Membership overlap
    elif "membership" in error_msg_lower and "overlap" in error_msg_lower:
        error_code = ErrorCode.MEMBERSHIP_OVERLAP.value
        message = "Vínculo sobrepõe período existente (RDB9)"

    # RDB8: Season overlap
    elif "season" in error_msg_lower and "overlap" in error_msg_lower:
        error_code = ErrorCode.SEASON_OVERLAP.value
        message = "Temporada sobrepõe período existente (RDB8)"

    # Unique constraint (email, cpf, etc)
    elif "unique" in error_msg_lower or "duplicate" in error_msg_lower:
        if "email" in error_msg_lower:
            error_code = ErrorCode.DUPLICATE_USER.value
            message = "Email já cadastrado"
        elif "cpf" in error_msg_lower:
            error_code = ErrorCode.DUPLICATE_PERSON.value
            message = "CPF já cadastrado"
        else:
            message = "Registro duplicado"

    # Foreign key constraint
    elif "foreign key" in error_msg_lower or "violates foreign key" in error_msg_lower:
        message = "Referência inválida: registro referenciado não existe"

    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "error_code": error_code,
            "message": message,
            "request_id": _get_request_id(request),
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handler genérico para erros não tratados.

    Retorna erro 500 e registra stack trace no log.
    """
    # logger.exception já inclui stack trace no log
    logger.exception("Unhandled exception during request")

    # Em produção, não expor detalhes do erro
    if settings.is_production:
        message = "Erro interno do servidor"
    else:
        # Em desenvolvimento, incluir mensagem para facilitar o debug
        message = f"Erro interno: {exc}"

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error_code": ErrorCode.INTERNAL_SERVER_ERROR.value,
            "message": message,
            "request_id": _get_request_id(request),
        },
    )

from fastapi.routing import APIRoute

for route in app.routes:
    if isinstance(route, APIRoute):
        route.operation_id = route.name  # Usa o nome da função como ID

# ============================================================================
# Routers
# ============================================================================

# Incluir routers
app.include_router(api_router, prefix=f"/api/{settings.API_VERSION}")

# ============================================================================
# Root Endpoint
# ============================================================================


@app.get("/", include_in_schema=False)
async def root() -> JSONResponse:
    """Root endpoint - redirect para docs."""
    return JSONResponse(
        content={
            "message": "HB Tracking API",
            "version": settings.API_VERSION_NUMBER,
            "docs": f"/api/{settings.API_VERSION}/docs",
        }
    )

# ============================================================================
# Startup/Shutdown Events
# ============================================================================


@app.on_event("startup")
async def startup_event() -> None:
    """
    Evento de startup da aplicação.

    Executa:
    1. Log de runtime Python (evidência permanente no journald)
    2. Warmup do banco de dados (acordar Neon)
    3. Healthcheck inicial
    4. Log de inicialização
    5. Step 17: Iniciar background tasks (WebSocket cleanup, notification cleanup)
    """
    # EVIDÊNCIA DE RUNTIME: Log permanente no journald (verificação objetiva de Python)
    logger.warning("═══════════════════════════════════════════════════════════")
    logger.warning("RUNTIME sys.executable = %s", sys.executable)
    logger.warning("RUNTIME sys.version = %s", sys.version.replace(chr(10), " "))
    logger.warning(
        "RUNTIME Python %s.%s.%s",
        sys.version_info.major,
        sys.version_info.minor,
        sys.version_info.micro,
    )
    logger.warning("═══════════════════════════════════════════════════════════")

    logger.info(
        "🚀 HB Track API %s iniciando...",
        settings.API_VERSION_NUMBER,
        extra={
            "environment": settings.ENV,
            "log_level": settings.LOG_LEVEL,
        },
    )

    # OBRIGATÓRIO: Warmup do banco no boot (proteção contra cold start do Neon)
    from app.core.db import healthcheck_db, warmup_database

    if warmup_database():
        # Healthcheck completo após warmup
        health = healthcheck_db()
        status_value = health.get("status")
        if status_value == "healthy":
            logger.info("✅ Database: PostgreSQL %s", health.get("pg_version", "unknown"))
            logger.info("📊 Ambiente: %s", settings.ENV)
            logger.info(
                "🚀 HB Tracking API %s pronta para receber requests",
                settings.API_VERSION_NUMBER,
            )
        else:
            logger.warning("⚠️ Database health check retornou: %s", health)
    else:
        logger.error(
            "❌ Falha no warmup do banco de dados. "
            "A aplicação pode ter problemas no primeiro request."
        )
        logger.info("📊 Ambiente: %s", settings.ENV)

    # Step 17: Iniciar background tasks
    from app.core.background_tasks import start_background_tasks

    start_background_tasks()
    logger.info("✅ Background tasks iniciadas (WebSocket cleanup, notification cleanup)")

    logger.info(
        "CORS config: origins=%s credentials=%s methods=%s headers=%s",
        settings.cors_origins_list,
        settings.CORS_ALLOW_CREDENTIALS,
        settings.cors_allow_methods_list,
        settings.cors_allow_headers_list,
    )

    logger.info("🚀 HB Track API %s iniciada", settings.API_VERSION_NUMBER)


@app.on_event("shutdown")
async def shutdown_event() -> None:
    logger.info("🛑 HB Track API encerrada")
