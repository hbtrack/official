"""
Intake Services - Ficha Única de Cadastro

FASE 3 - FICHA.MD

Módulos:
- ficha_unica_service: Serviço principal de cadastro
- validators: Funções de normalização e validação
- scope_validator: Validação de escopo por papel
- idempotency: Controle de idempotência de requisições
"""

# Serviço principal
from app.services.intake.ficha_unica_service import FichaUnicaService

# Validadores
from app.services.intake.validators import (
    normalize_cpf,
    normalize_phone,
    normalize_email,
    validate_cpf_checksum,
    check_duplicate_contact,
    check_duplicate_document,
    check_email_exists,
    check_cpf_exists,
    check_phone_exists,
    is_goalkeeper_position,
    validate_goalkeeper_positions,
)

# Validação de escopo
from app.services.intake.scope_validator import (
    validate_ficha_scope,
    ROLES_CREATE_ORGANIZATION,
    ROLES_CREATE_TEAM,
    ROLES_CREATE_ATHLETE,
    ROLES_CREATE_MEMBERSHIP,
)

# Idempotência
from app.services.intake.idempotency import (
    compute_request_hash,
    serialize_response,
    check_idempotency,
    save_idempotency,
    cleanup_expired_keys,
    IdempotencyGuard,
)

__all__ = [
    # Serviço principal
    "FichaUnicaService",
    # Validadores
    "normalize_cpf",
    "normalize_phone",
    "normalize_email",
    "validate_cpf_checksum",
    "check_duplicate_contact",
    "check_duplicate_document",
    "check_email_exists",
    "check_cpf_exists",
    "check_phone_exists",
    "is_goalkeeper_position",
    "validate_goalkeeper_positions",
    # Validação de escopo
    "validate_ficha_scope",
    "ROLES_CREATE_ORGANIZATION",
    "ROLES_CREATE_TEAM",
    "ROLES_CREATE_ATHLETE",
    "ROLES_CREATE_MEMBERSHIP",
    # Idempotência
    "compute_request_hash",
    "serialize_response",
    "check_idempotency",
    "save_idempotency",
    "cleanup_expired_keys",
    "IdempotencyGuard",
]
