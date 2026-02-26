"""
Exception handlers e contratos de erro do sistema.

Mapeia códigos PostgreSQL para HTTP conforme "Contrato de erros por regra":
- 23P01 (ExclusionViolation) → 409 (RDB10: sobreposição de período)
- 23505 (UniqueViolation) → 409 (conflito de unicidade)
- 23514 (CheckViolation) → 422 (validação de dados)
- 23503 (ForeignKeyViolation) → 422/409 (conforme contexto)
- 23502 (NotNullViolation) → 422 (campo obrigatório)

Referências:
- fluxo-backend-oficial.md: "Contrato de erros por regra"
- regras-sistema-v1.1: RDB10, RDB13, R16, RF5.2
"""

from typing import Any, Optional, Dict
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
import logging

# Importações condicionais para mapear erros do PostgreSQL
try:
    from psycopg2 import errors as pg_errors
    from psycopg2 import IntegrityError, DataError
    PG_AVAILABLE = True
except ImportError:
    # Fallback para asyncpg
    try:
        from asyncpg import exceptions as asyncpg_errors
        PG_AVAILABLE = "asyncpg"
    except ImportError:
        PG_AVAILABLE = False

from sqlalchemy.exc import IntegrityError as SQLAlchemyIntegrityError, DataError as SQLAlchemyDataError

logger = logging.getLogger(__name__)


# ═════════════════════════════════════════════════════════════════════
# Custom Exceptions
# ═════════════════════════════════════════════════════════════════════

class NotFoundError(Exception):
    """Exceção para recursos não encontrados (HTTP 404)."""
    
    def __init__(self, message: str = "Recurso não encontrado"):
        self.message = message
        super().__init__(self.message)


class BusinessError(Exception):
    """Exceção para erros de regra de negócio (HTTP 409/422)."""
    
    def __init__(self, error_key: str, message: Optional[str] = None):
        self.error_key = error_key
        self.message = message or error_key
        super().__init__(self.message)


class ForbiddenError(Exception):
    """Exceção para acesso não autorizado (HTTP 403)."""
    
    def __init__(self, message: str = "Acesso não autorizado"):
        self.message = message
        super().__init__(self.message)


# Alias para compatibilidade
PermissionDeniedError = ForbiddenError


class ValidationError(Exception):
    """Exceção para erros de validação de dados (HTTP 422)."""
    
    def __init__(self, message: str = "Dados inválidos", field: Optional[str] = None):
        self.message = message
        self.field = field
        super().__init__(self.message)


class ConflictError(Exception):
    """Exceção para conflitos de unicidade/concorrência (HTTP 409)."""
    
    def __init__(self, message: str = "Conflito de dados"):
        self.message = message
        super().__init__(self.message)


class SessionOutsideMicrocycleWeekError(BusinessError):
    """Exceção quando sessão de treino está fora da semana do microciclo (INV-057)."""
    
    def __init__(self, message: str = "Sessão fora da semana do microciclo"):
        super().__init__(error_key="SESSION_OUTSIDE_MICROCYCLE_WEEK", message=message)


class SessionClosedError(BusinessError):
    """Exceção quando operação é proibida em sessão readonly (INV-067)."""

    def __init__(self, message: str = "Sessão encerrada — operação não permitida em status readonly"):
        super().__init__(error_key="SESSION_CLOSED", message=message)


class ExerciseImmutableError(BusinessError):
    """Exceção quando tentativa de modificar exercise SYSTEM (INV-048)."""
    
    def __init__(self, message: str = "Exercícios SYSTEM são imutáveis"):
        super().__init__(error_key="EXERCISE_IMMUTABLE", message=message)


class ExerciseReferencedError(BusinessError):
    """Exceção quando tentativa de deletar exercise referenciado em sessões históricas (INV-053)."""
    
    def __init__(self, message: str = "Exercício referenciado em sessões históricas (soft delete aplicado)"):
        super().__init__(error_key="EXERCISE_REFERENCED", message=message)


# ACL Exceptions (INV-EXB-ACL-*)

class AclNotApplicableError(BusinessError):
    """Exceção quando ACL não aplicável (exercise não é restricted) (INV-EXB-ACL-002)."""
    
    def __init__(self, message: str = "ACL não aplicável a exercícios com visibility_mode != restricted"):
        super().__init__(error_key="ACL_NOT_APPLICABLE", message=message)


class AclCrossOrgError(BusinessError):
    """Exceção quando tentativa de grant ACL cross-org (INV-EXB-ACL-003)."""
    
    def __init__(self, message: str = "Usuário não pertence à mesma organização do exercício"):
        super().__init__(error_key="ACL_CROSS_ORG", message=message)


class AclUnauthorizedError(BusinessError):
    """Exceção quando não-criador tenta gerenciar ACL (INV-EXB-ACL-004)."""
    
    def __init__(self, message: str = "Apenas o criador do exercício pode gerenciar ACL"):
        super().__init__(error_key="ACL_UNAUTHORIZED", message=message)


class AclDuplicateError(BusinessError):
    """Exceção quando tentativa de grant ACL duplicado (INV-EXB-ACL-006)."""
    
    def __init__(self, message: str = "Usuário já possui acesso a este exercício"):
        super().__init__(error_key="ACL_DUPLICATE", message=message)


class ExerciseNotVisibleError(BusinessError):
    """Exceção quando exercício não está visível para o usuário (INV-062)."""
    
    def __init__(self, message: str = "Exercício não está acessível para este usuário"):
        super().__init__(error_key="EXERCISE_NOT_VISIBLE", message=message)


# ═════════════════════════════════════════════════════════════════════
# Schemas de erro (contrato padronizado)
# ═════════════════════════════════════════════════════════════════════

class ErrorDetail(BaseModel):
    """Detalhes adicionais do erro."""
    regra: Optional[str] = None
    field: Optional[str] = None
    constraint: Optional[str] = None
    additional_info: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """
    Formato padrão de resposta de erro.
    
    Conforme "Contrato de erros por regra" (fluxo-backend-oficial.md).
    """
    code: str
    message: str
    details: Optional[ErrorDetail] = None


# ═════════════════════════════════════════════════════════════════════
# Mapeamentos de códigos PostgreSQL → HTTP
# ═════════════════════════════════════════════════════════════════════

POSTGRES_ERROR_MAP = {
    # RDB10: Sobreposição de período (EXCLUDE constraint)
    "23P01": {
        "status": status.HTTP_409_CONFLICT,
        "code": "conflict_period_overlap",
        "message": "Período de inscrição sobrepõe registro existente",
        "regra": "RDB10",
    },
    # Unique violation (índices UNIQUE)
    "23505": {
        "status": status.HTTP_409_CONFLICT,
        "code": "conflict_unique_violation",
        "message": "Registro duplicado viola restrição de unicidade",
        "regra": "DB_UNIQUE",
    },
    # Check constraint violation
    "23514": {
        "status": status.HTTP_422_UNPROCESSABLE_ENTITY,
        "code": "validation_check_constraint",
        "message": "Dados violam restrição de validação",
        "regra": "DB_CHECK",
    },
    # Foreign key violation
    "23503": {
        "status": status.HTTP_422_UNPROCESSABLE_ENTITY,
        "code": "validation_foreign_key",
        "message": "Referência inválida a registro relacionado",
        "regra": "DB_FK",
    },
    # Not null violation
    "23502": {
        "status": status.HTTP_422_UNPROCESSABLE_ENTITY,
        "code": "validation_required_field",
        "message": "Campo obrigatório não fornecido",
        "regra": "DB_NOT_NULL",
    },
}


# Mapeamentos específicos por constraint name (mais específico que código)
CONSTRAINT_NAME_MAP = {
    "ex_team_registrations_no_overlap": {
        "status": status.HTTP_409_CONFLICT,
        "code": "conflict_team_registration_overlap",
        "message": "Período de inscrição sobrepõe com registro existente para esta atleta/equipe/temporada (RDB10)",
        "regra": "RDB10",
    },
    "ck_team_registrations_date_range_valid": {
        "status": status.HTTP_422_UNPROCESSABLE_ENTITY,
        "code": "validation_invalid_date_range",
        "message": "Data de término deve ser maior ou igual à data de início",
        "regra": "RDB10",
    },
    "trg_games_block_update_finalized": {
        "status": status.HTTP_409_CONFLICT,
        "code": "conflict_edit_finalized_game",
        "message": "Jogo finalizado é somente leitura (use reabertura para editar)",
        "regra": "RDB13",
    },
}


# ═════════════════════════════════════════════════════════════════════
# Helper functions
# ═════════════════════════════════════════════════════════════════════

def extract_pg_error_code(exc: Exception) -> Optional[str]:
    """Extrai código SQLSTATE do PostgreSQL da exceção."""
    # Tentar extrair via psycopg2
    if PG_AVAILABLE == True and hasattr(exc, "orig"):
        orig = exc.orig
        if hasattr(orig, "pgcode"):
            return orig.pgcode
    
    # Tentar extrair via asyncpg
    if PG_AVAILABLE == "asyncpg" and hasattr(exc, "__cause__"):
        cause = exc.__cause__
        if hasattr(cause, "sqlstate"):
            return cause.sqlstate
    
    # Fallback: tentar extrair do diag
    if hasattr(exc, "orig") and hasattr(exc.orig, "diag"):
        return getattr(exc.orig.diag, "sqlstate", None)
    
    return None


def extract_constraint_name(exc: Exception) -> Optional[str]:
    """Extrai nome da constraint violada."""
    # psycopg2
    if hasattr(exc, "orig") and hasattr(exc.orig, "diag"):
        diag = exc.orig.diag
        return getattr(diag, "constraint_name", None)
    
    # asyncpg
    if hasattr(exc, "__cause__"):
        cause = exc.__cause__
        if hasattr(cause, "constraint_name"):
            return cause.constraint_name
    
    # Fallback: parse message
    msg = str(exc)
    if "constraint" in msg.lower():
        # Tenta extrair nome entre aspas
        import re
        match = re.search(r'"([^"]+)"', msg)
        if match:
            return match.group(1)
    
    return None


def build_error_response(
    code: str,
    message: str,
    regra: Optional[str] = None,
    field: Optional[str] = None,
    constraint: Optional[str] = None,
    additional_info: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Constrói resposta de erro no formato padronizado."""
    details = None
    if regra or field or constraint or additional_info:
        details = ErrorDetail(
            regra=regra,
            field=field,
            constraint=constraint,
            additional_info=additional_info,
        ).model_dump(exclude_none=True)
    
    response = ErrorResponse(
        code=code,
        message=message,
        details=details,
    )
    return response.model_dump(exclude_none=True)


# ═════════════════════════════════════════════════════════════════════
# Exception handlers
# ═════════════════════════════════════════════════════════════════════

async def integrity_error_handler(request: Request, exc: SQLAlchemyIntegrityError) -> JSONResponse:
    """
    Handler para IntegrityError do SQLAlchemy.
    
    Mapeia códigos PostgreSQL (23xxx) para HTTP 409/422 conforme contrato.
    """
    pg_code = extract_pg_error_code(exc)
    constraint_name = extract_constraint_name(exc)
    
    logger.warning(
        f"IntegrityError: pg_code={pg_code}, constraint={constraint_name}, msg={str(exc)}"
    )
    
    # Mapeamento específico por constraint name (prioridade)
    if constraint_name and constraint_name in CONSTRAINT_NAME_MAP:
        mapping = CONSTRAINT_NAME_MAP[constraint_name]
        return JSONResponse(
            status_code=mapping["status"],
            content=build_error_response(
                code=mapping["code"],
                message=mapping["message"],
                regra=mapping.get("regra"),
                constraint=constraint_name,
            ),
        )
    
    # Mapeamento por código SQLSTATE
    if pg_code and pg_code in POSTGRES_ERROR_MAP:
        mapping = POSTGRES_ERROR_MAP[pg_code]
        return JSONResponse(
            status_code=mapping["status"],
            content=build_error_response(
                code=mapping["code"],
                message=mapping["message"],
                regra=mapping.get("regra"),
                constraint=constraint_name,
            ),
        )
    
    # Fallback: erro genérico 409
    logger.error(f"Unmapped IntegrityError: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=build_error_response(
            code="conflict_integrity_error",
            message="Operação violou restrição de integridade do banco de dados",
            constraint=constraint_name,
            additional_info={"pg_code": pg_code} if pg_code else None,
        ),
    )


async def data_error_handler(request: Request, exc: SQLAlchemyDataError) -> JSONResponse:
    """Handler para DataError do SQLAlchemy (dados inválidos)."""
    logger.warning(f"DataError: {exc}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=build_error_response(
            code="validation_data_error",
            message="Dados fornecidos são inválidos ou incompatíveis com o tipo esperado",
        ),
    )


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handler para erros de validação do Pydantic."""
    errors = exc.errors()
    
    # Extrair primeiro erro para mensagem principal
    first_error = errors[0] if errors else {}
    field = ".".join(str(loc) for loc in first_error.get("loc", []))
    msg = first_error.get("msg", "Dados de entrada inválidos")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=build_error_response(
            code="validation_error",
            message=f"Validação falhou: {msg}",
            field=field,
            additional_info={"errors": errors},
        ),
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handler genérico para exceções não tratadas."""
    logger.error(f"Unhandled exception: {type(exc).__name__}: {exc}", exc_info=True)
    # NotImplementedError => 501 Not Implemented (endpoints / features pendentes)
    if isinstance(exc, NotImplementedError):
        return JSONResponse(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            content=build_error_response(
                code="not_implemented",
                message=str(exc) or "Recurso não implementado",
            ),
        )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=build_error_response(
            code="internal_server_error",
            message="Erro interno do servidor",
        ),
    )


# ═════════════════════════════════════════════════════════════════════
# Business logic exceptions (ValueError → HTTP)
# ═════════════════════════════════════════════════════════════════════

BUSINESS_ERROR_MAP = {
    # RDB10: Sobreposição de período (validação no service)
    "period_overlap": {
        "status": status.HTTP_409_CONFLICT,
        "code": "conflict_period_overlap",
        "message": "Período de inscrição sobrepõe com registro existente",
        "regra": "RDB10",
    },
    "invalid_date_range": {
        "status": status.HTTP_422_UNPROCESSABLE_ENTITY,
        "code": "validation_invalid_date_range",
        "message": "Data de término deve ser maior ou igual à data de início",
        "regra": "RDB10",
    },
    "cannot_reopen_ended": {
        "status": status.HTTP_409_CONFLICT,
        "code": "conflict_cannot_reopen_period",
        "message": "Não é permitido reabrir período já encerrado (RDB10)",
        "regra": "RDB10",
    },
    # R16: Categoria vs idade
    "age_category_violation": {
        "status": status.HTTP_422_UNPROCESSABLE_ENTITY,
        "code": "validation_age_category",
        "message": "Atleta não pode atuar em categoria abaixo da sua faixa etária",
        "regra": "R16",
    },
    # RF5.2: Temporada bloqueada
    "season_interrupted_locked": {
        "status": status.HTTP_409_CONFLICT,
        "code": "conflict_season_locked",
        "message": "Temporada interrompida: criação/edição bloqueada",
        "regra": "RF5.2",
    },
    # RDB13/RF15: Jogo finalizado
    "edit_finalized_game": {
        "status": status.HTTP_409_CONFLICT,
        "code": "conflict_edit_finalized_game",
        "message": "Jogo finalizado é somente leitura (use reabertura para editar)",
        "regra": "RDB13",
    },
    # RD13: Goleira
    "invalid_goalkeeper_stat": {
        "status": status.HTTP_422_UNPROCESSABLE_ENTITY,
        "code": "validation_goalkeeper_stat",
        "message": "Goleira não pode registrar estatística de atleta de linha",
        "regra": "RD13",
    },
}


def map_business_error(error_key: str) -> tuple[int, Dict[str, Any]]:
    """
    Mapeia ValueError do service para HTTP response.
    
    Usage no router:
        try:
            await service.create(...)
        except ValueError as e:
            status_code, error_body = map_business_error(str(e))
            raise HTTPException(status_code=status_code, detail=error_body)
    
    Returns:
        (status_code, error_body)
    """
    if error_key in BUSINESS_ERROR_MAP:
        mapping = BUSINESS_ERROR_MAP[error_key]
        return (
            mapping["status"],
            build_error_response(
                code=mapping["code"],
                message=mapping["message"],
                regra=mapping.get("regra"),
            ),
        )
    
    # Fallback: 422 genérico
    return (
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        build_error_response(
            code="validation_error",
            message=f"Erro de validação: {error_key}",
        ),
    )
