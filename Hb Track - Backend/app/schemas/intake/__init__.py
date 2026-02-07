"""Intake Schemas - Ficha Única de Cadastro

FASE 2 - FICHA.MD Seção 2.2 e 2.3
"""

from app.schemas.intake.ficha_unica import (
    # Funções utilitárias
    normalize_cpf,
    normalize_email,
    normalize_phone,
    validate_cpf,
    # Person schemas
    PersonCreate,
    PersonContactCreate,
    PersonDocumentCreate,
    PersonAddressCreate,
    PersonMediaCreate,
    # User schemas
    UserCreate,
    # Season schemas
    SeasonCreateInline,
    SeasonSelection,
    # Organization schemas
    OrganizationCreateInline,
    OrganizationSelection,
    MembershipCreate,
    # Team schemas
    TeamCreateInline,
    TeamSelection,
    # Athlete schemas
    AthleteCreate,
    RegistrationCreate,
    # Main payload
    FichaUnicaRequest,
    # Response schemas
    FichaUnicaResponse,
    FichaUnicaDryRunResponse,
    ValidationResult,
)

__all__ = [
    # Funções utilitárias
    "normalize_cpf",
    "normalize_email",
    "normalize_phone",
    "validate_cpf",
    # Person schemas
    "PersonCreate",
    "PersonContactCreate",
    "PersonDocumentCreate",
    "PersonAddressCreate",
    "PersonMediaCreate",
    # User schemas
    "UserCreate",
    # Season schemas
    "SeasonCreateInline",
    "SeasonSelection",
    # Organization schemas
    "OrganizationCreateInline",
    "OrganizationSelection",
    "MembershipCreate",
    # Team schemas
    "TeamCreateInline",
    "TeamSelection",
    # Athlete schemas
    "AthleteCreate",
    "RegistrationCreate",
    # Main payload
    "FichaUnicaRequest",
    # Response schemas
    "FichaUnicaResponse",
    "FichaUnicaDryRunResponse",
    "ValidationResult",
]
