"""
Schemas de erro padronizados (FASE 3)
"""
from typing import Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class ErrorCode(str, Enum):
    """
    Códigos de erro mapeados para regras RAG V1.1
    """
    # === RDB Rules (Database Constraints) ===
    MEMBERSHIP_OVERLAP = "MEMBERSHIP_OVERLAP"  # RDB9
    TEAM_REG_OVERLAP = "TEAM_REG_OVERLAP"  # RDB10
    SEASON_OVERLAP = "SEASON_OVERLAP"  # RDB8
    SOFT_DELETE_REASON_REQUIRED = "SOFT_DELETE_REASON_REQUIRED"  # RDB4

    # === R Rules (Business Logic) ===
    SUPERADMIN_IMMUTABLE = "SUPERADMIN_IMMUTABLE"  # R3
    SUPERADMIN_REQUIRED = "SUPERADMIN_REQUIRED"  # R3, RDB6
    NO_ACTIVE_MEMBERSHIP = "NO_ACTIVE_MEMBERSHIP"  # R42, RF3
    ATHLETE_DISPENSE_NO_UNDO = "ATHLETE_DISPENSE_NO_UNDO"  # R13
    INVALID_ROLE_ASSIGNMENT = "INVALID_ROLE_ASSIGNMENT"  # R5
    DUPLICATE_PERSON = "DUPLICATE_PERSON"  # R1
    DUPLICATE_USER = "DUPLICATE_USER"  # R2

    # === RD Rules (Domain Validations) ===
    AGE_BELOW_CATEGORY = "AGE_BELOW_CATEGORY"  # RD2, RD3
    MATCH_ALREADY_FINALIZED = "MATCH_ALREADY_FINALIZED"  # RD8
    CORRECTION_NOTE_REQUIRED = "CORRECTION_NOTE_REQUIRED"  # R23, R24
    INVALID_MATCH_EVENT_TYPE = "INVALID_MATCH_EVENT_TYPE"  # RD
    PLAYER_NOT_IN_ROSTER = "PLAYER_NOT_IN_ROSTER"  # RD
    INVALID_CARD_SEQUENCE = "INVALID_CARD_SEQUENCE"  # RD

    # === RF Rules (Frontend/API) ===
    INVALID_DATE_RANGE = "INVALID_DATE_RANGE"  # RF
    REQUIRED_FIELD_MISSING = "REQUIRED_FIELD_MISSING"  # RF
    INVALID_UUID_FORMAT = "INVALID_UUID_FORMAT"  # RF

    # === Generic Errors ===
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"


class ErrorDetail(BaseModel):
    """
    Detalhes adicionais do erro
    """
    field: Optional[str] = Field(None, description="Campo que causou o erro")
    constraint: Optional[str] = Field(None, description="Regra RAG violada (ex: RDB9, R3)")
    existing_id: Optional[str] = Field(None, description="ID do recurso conflitante")
    metadata: Optional[dict[str, Any]] = Field(None, description="Informações adicionais")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "field": "start_date",
                "constraint": "RDB9",
                "existing_membership_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }
    )


class ErrorResponse(BaseModel):
    """
    Resposta de erro padronizada (FASE 3)

    Usado em todos os endpoints da API para retornar erros estruturados.
    Mapeia error_code para regras RAG V1.1 (seção 8).
    """
    error_code: ErrorCode = Field(..., description="Código do erro (enum)")
    message: str = Field(..., description="Mensagem legível do erro")
    details: Optional[ErrorDetail] = Field(None, description="Detalhes adicionais do erro")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp UTC do erro")
    request_id: str = Field(..., description="ID da requisição para rastreamento")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error_code": "MEMBERSHIP_OVERLAP",
                "message": "Vínculo sobrepõe período existente",
                "details": {
                    "field": "start_date",
                    "constraint": "RDB9",
                    "existing_membership_id": "123e4567-e89b-12d3-a456-426614174000"
                },
                "timestamp": "2025-12-24T10:30:00Z",
                "request_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }
    )


# === Backward compatibility: Constants and factory functions ===
# (for existing codebase that imports these)

# Error code constants (string values for backward compatibility)
ERROR_UNAUTHORIZED = "UNAUTHORIZED"
ERROR_PERMISSION_DENIED = "FORBIDDEN"
ERROR_NOT_FOUND = "RESOURCE_NOT_FOUND"
ERROR_CONFLICT_MEMBERSHIP_ACTIVE = "MEMBERSHIP_OVERLAP"
ERROR_PERIOD_OVERLAP = "TEAM_REG_OVERLAP"
ERROR_SEASON_LOCKED = "SEASON_OVERLAP"
ERROR_EDIT_FINALIZED_GAME = "MATCH_ALREADY_FINALIZED"
ERROR_VALIDATION = "VALIDATION_ERROR"
ERROR_AGE_CATEGORY_VIOLATION = "AGE_BELOW_CATEGORY"
ERROR_INVALID_STATE_TRANSITION = "ATHLETE_DISPENSE_NO_UNDO"
ERROR_INVALID_GOALKEEPER_STAT = "INVALID_MATCH_EVENT_TYPE"


# Factory functions for creating error responses
def error_unauthorized(message: str = "Token inválido ou ausente", request_id: str = "") -> ErrorResponse:
    """Cria erro 401 unauthorized"""
    return ErrorResponse(
        error_code=ErrorCode.UNAUTHORIZED,
        message=message,
        request_id=request_id or "default-request-id"
    )


def error_permission_denied(
    message: str = "Permissão insuficiente",
    regra: str = "R25",
    request_id: str = ""
) -> ErrorResponse:
    """Cria erro 403 permission_denied (R25/R26)"""
    return ErrorResponse(
        error_code=ErrorCode.FORBIDDEN,
        message=message,
        details=ErrorDetail(constraint=regra),
        request_id=request_id or "default-request-id"
    )


def error_not_found(
    message: str = "Recurso não encontrado",
    resource: Optional[str] = None,
    request_id: str = ""
) -> ErrorResponse:
    """Cria erro 404 not_found"""
    details = ErrorDetail(field=resource) if resource else None
    return ErrorResponse(
        error_code=ErrorCode.RESOURCE_NOT_FOUND,
        message=message,
        details=details,
        request_id=request_id or "default-request-id"
    )


def error_conflict_membership_active(
    message: str = "Já existe vínculo ativo",
    request_id: str = ""
) -> ErrorResponse:
    """Cria erro 409 conflict_membership_active (RDB9)"""
    return ErrorResponse(
        error_code=ErrorCode.MEMBERSHIP_OVERLAP,
        message=message,
        details=ErrorDetail(constraint="RDB9"),
        request_id=request_id or "default-request-id"
    )


def error_period_overlap(
    message: str = "Período sobreposto para pessoa+equipe+temporada",
    request_id: str = ""
) -> ErrorResponse:
    """Cria erro 409 period_overlap (RDB10)"""
    return ErrorResponse(
        error_code=ErrorCode.TEAM_REG_OVERLAP,
        message=message,
        details=ErrorDetail(constraint="RDB10"),
        request_id=request_id or "default-request-id"
    )


def error_season_locked(
    message: str = "Temporada interrompida: criação/edição bloqueada",
    request_id: str = ""
) -> ErrorResponse:
    """Cria erro 409 season_locked (RF5.2/R37)"""
    return ErrorResponse(
        error_code=ErrorCode.SEASON_OVERLAP,
        message=message,
        details=ErrorDetail(constraint="RF5.2"),
        request_id=request_id or "default-request-id"
    )


def error_edit_finalized_game(
    message: str = "Jogo finalizado é somente leitura",
    request_id: str = ""
) -> ErrorResponse:
    """Cria erro 409 edit_finalized_game (RDB13/RF15)"""
    return ErrorResponse(
        error_code=ErrorCode.MATCH_ALREADY_FINALIZED,
        message=message,
        details=ErrorDetail(constraint="RDB13"),
        request_id=request_id or "default-request-id"
    )


def error_age_category_violation(
    message: str = "Atuação abaixo da categoria não permitida",
    request_id: str = ""
) -> ErrorResponse:
    """Cria erro 422 age_category_violation (R16/RD1-RD2)"""
    return ErrorResponse(
        error_code=ErrorCode.AGE_BELOW_CATEGORY,
        message=message,
        details=ErrorDetail(constraint="R16"),
        request_id=request_id or "default-request-id"
    )


def error_invalid_state_transition(
    message: str = "Transição de estado inválida para atleta",
    request_id: str = ""
) -> ErrorResponse:
    """Cria erro 422 invalid_state_transition (R13)"""
    return ErrorResponse(
        error_code=ErrorCode.ATHLETE_DISPENSE_NO_UNDO,
        message=message,
        details=ErrorDetail(constraint="R13"),
        request_id=request_id or "default-request-id"
    )


def error_invalid_goalkeeper_stat(
    message: str = "Goleira não pode registrar estatística de linha",
    request_id: str = ""
) -> ErrorResponse:
    """Cria erro 422 invalid_goalkeeper_stat (RD13)"""
    return ErrorResponse(
        error_code=ErrorCode.INVALID_MATCH_EVENT_TYPE,
        message=message,
        details=ErrorDetail(constraint="RD13"),
        request_id=request_id or "default-request-id"
    )


def error_validation(
    message: str = "Erro de validação no payload",
    field: Optional[str] = None,
    error: Optional[str] = None,
    request_id: str = ""
) -> ErrorResponse:
    """Cria erro 422 validation_error genérico"""
    details = None
    if field or error:
        details = ErrorDetail(field=field, metadata={"error": error} if error else None)
    return ErrorResponse(
        error_code=ErrorCode.VALIDATION_ERROR,
        message=message,
        details=details,
        request_id=request_id or "default-request-id"
    )
