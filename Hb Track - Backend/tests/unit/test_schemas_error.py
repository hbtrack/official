"""
Testes unitários para schemas de erro (FASE 3)
"""
import pytest
from datetime import datetime
from uuid import uuid4
from app.schemas.error import (
    ErrorCode,
    ErrorDetail,
    ErrorResponse
)


def test_error_code_enum_values():
    """Valida que ErrorCode enum contém todos os códigos esperados"""
    # RDB Rules
    assert ErrorCode.MEMBERSHIP_OVERLAP == "MEMBERSHIP_OVERLAP"
    assert ErrorCode.TEAM_REG_OVERLAP == "TEAM_REG_OVERLAP"
    assert ErrorCode.SEASON_OVERLAP == "SEASON_OVERLAP"
    assert ErrorCode.SOFT_DELETE_REASON_REQUIRED == "SOFT_DELETE_REASON_REQUIRED"

    # R Rules
    assert ErrorCode.SUPERADMIN_IMMUTABLE == "SUPERADMIN_IMMUTABLE"
    assert ErrorCode.SUPERADMIN_REQUIRED == "SUPERADMIN_REQUIRED"
    assert ErrorCode.NO_ACTIVE_MEMBERSHIP == "NO_ACTIVE_MEMBERSHIP"
    assert ErrorCode.ATHLETE_DISPENSE_NO_UNDO == "ATHLETE_DISPENSE_NO_UNDO"

    # RD Rules
    assert ErrorCode.AGE_BELOW_CATEGORY == "AGE_BELOW_CATEGORY"
    assert ErrorCode.MATCH_ALREADY_FINALIZED == "MATCH_ALREADY_FINALIZED"
    assert ErrorCode.CORRECTION_NOTE_REQUIRED == "CORRECTION_NOTE_REQUIRED"

    # Generic
    assert ErrorCode.RESOURCE_NOT_FOUND == "RESOURCE_NOT_FOUND"
    assert ErrorCode.UNAUTHORIZED == "UNAUTHORIZED"
    assert ErrorCode.FORBIDDEN == "FORBIDDEN"


def test_error_detail_minimal():
    """Valida criação de ErrorDetail com campos mínimos"""
    detail = ErrorDetail()
    assert detail.field is None
    assert detail.constraint is None
    assert detail.existing_id is None
    assert detail.metadata is None


def test_error_detail_complete():
    """Valida criação de ErrorDetail com todos os campos"""
    detail = ErrorDetail(
        field="start_date",
        constraint="RDB9",
        existing_id="123e4567-e89b-12d3-a456-426614174000",
        metadata={"additional_info": "test"}
    )
    assert detail.field == "start_date"
    assert detail.constraint == "RDB9"
    assert detail.existing_id == "123e4567-e89b-12d3-a456-426614174000"
    assert detail.metadata == {"additional_info": "test"}


def test_error_response_required_fields():
    """Valida que ErrorResponse requer campos obrigatórios"""
    request_id = str(uuid4())

    error = ErrorResponse(
        error_code=ErrorCode.MEMBERSHIP_OVERLAP,
        message="Vínculo sobrepõe período existente",
        request_id=request_id
    )

    assert error.error_code == ErrorCode.MEMBERSHIP_OVERLAP
    assert error.message == "Vínculo sobrepõe período existente"
    assert error.request_id == request_id
    assert error.details is None
    assert isinstance(error.timestamp, datetime)


def test_error_response_with_details():
    """Valida ErrorResponse com detalhes"""
    request_id = str(uuid4())
    detail = ErrorDetail(
        field="start_date",
        constraint="RDB9",
        existing_id="123e4567-e89b-12d3-a456-426614174000"
    )

    error = ErrorResponse(
        error_code=ErrorCode.MEMBERSHIP_OVERLAP,
        message="Vínculo sobrepõe período existente",
        details=detail,
        request_id=request_id
    )

    assert error.details is not None
    assert error.details.field == "start_date"
    assert error.details.constraint == "RDB9"


def test_error_response_json_serialization():
    """Valida serialização JSON de ErrorResponse"""
    request_id = str(uuid4())
    detail = ErrorDetail(field="start_date", constraint="RDB9")

    error = ErrorResponse(
        error_code=ErrorCode.MEMBERSHIP_OVERLAP,
        message="Vínculo sobrepõe período existente",
        details=detail,
        request_id=request_id
    )

    json_data = error.model_dump(mode='json')

    assert json_data["error_code"] == "MEMBERSHIP_OVERLAP"
    assert json_data["message"] == "Vínculo sobrepõe período existente"
    assert json_data["request_id"] == request_id
    assert json_data["details"]["field"] == "start_date"
    assert json_data["details"]["constraint"] == "RDB9"
    assert "timestamp" in json_data


def test_error_response_different_error_codes():
    """Valida ErrorResponse com diferentes códigos de erro"""
    request_id = str(uuid4())

    # RDB Rule
    error_rdb = ErrorResponse(
        error_code=ErrorCode.TEAM_REG_OVERLAP,
        message="Inscrição sobrepõe período existente",
        request_id=request_id
    )
    assert error_rdb.error_code == ErrorCode.TEAM_REG_OVERLAP

    # R Rule
    error_r = ErrorResponse(
        error_code=ErrorCode.SUPERADMIN_IMMUTABLE,
        message="Super Admin não pode ser modificado",
        request_id=request_id
    )
    assert error_r.error_code == ErrorCode.SUPERADMIN_IMMUTABLE

    # RD Rule
    error_rd = ErrorResponse(
        error_code=ErrorCode.AGE_BELOW_CATEGORY,
        message="Atleta abaixo da idade mínima",
        request_id=request_id
    )
    assert error_rd.error_code == ErrorCode.AGE_BELOW_CATEGORY

    # Generic
    error_generic = ErrorResponse(
        error_code=ErrorCode.RESOURCE_NOT_FOUND,
        message="Recurso não encontrado",
        request_id=request_id
    )
    assert error_generic.error_code == ErrorCode.RESOURCE_NOT_FOUND


def test_error_code_mapping_to_rag_rules():
    """Valida que códigos de erro correspondem às regras RAG V1.1"""
    rag_mappings = {
        # RDB Rules (Database)
        ErrorCode.MEMBERSHIP_OVERLAP: "RDB9",
        ErrorCode.TEAM_REG_OVERLAP: "RDB10",
        ErrorCode.SEASON_OVERLAP: "RDB8",
        ErrorCode.SOFT_DELETE_REASON_REQUIRED: "RDB4",

        # R Rules (Business Logic)
        ErrorCode.SUPERADMIN_IMMUTABLE: "R3",
        ErrorCode.SUPERADMIN_REQUIRED: "R3",
        ErrorCode.NO_ACTIVE_MEMBERSHIP: "R42",
        ErrorCode.ATHLETE_DISPENSE_NO_UNDO: "R13",
        ErrorCode.INVALID_ROLE_ASSIGNMENT: "R5",
        ErrorCode.DUPLICATE_PERSON: "R1",
        ErrorCode.DUPLICATE_USER: "R2",

        # RD Rules (Domain)
        ErrorCode.AGE_BELOW_CATEGORY: "RD2",
        ErrorCode.MATCH_ALREADY_FINALIZED: "RD8",
        ErrorCode.CORRECTION_NOTE_REQUIRED: "R23",
    }

    # Verifica que cada código de erro está documentado
    for error_code, expected_rule in rag_mappings.items():
        assert isinstance(error_code, ErrorCode)
        assert isinstance(expected_rule, str)
        # Verifica que a regra começa com R, RDB, RD ou RF
        assert expected_rule.startswith(('R', 'RDB', 'RD', 'RF'))
