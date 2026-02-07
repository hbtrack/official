"""
Valida que todos os error codes do API_CONTRACT.md estão mapeados (FASE 3)
"""
import pytest
from app.schemas.error import ErrorCode


def test_all_api_contract_error_codes_are_mapped():
    """
    Valida que todos os error codes documentados em API_CONTRACT.md
    estão implementados no ErrorCode enum
    """
    # Error codes documentados em docs/API_CONTRACT.md seção "Erros de Negócio"

    # === RDB Rules ===
    required_rdb_codes = {
        "MEMBERSHIP_OVERLAP",  # RDB9
        "TEAM_REG_OVERLAP",  # RDB10
        "SEASON_OVERLAP",  # RDB8
        "SOFT_DELETE_REASON_REQUIRED",  # RDB4
    }

    # === R Rules ===
    required_r_codes = {
        "SUPERADMIN_IMMUTABLE",  # R3
        "SUPERADMIN_REQUIRED",  # R3, RDB6
        "NO_ACTIVE_MEMBERSHIP",  # R42, RF3
        "ATHLETE_DISPENSE_NO_UNDO",  # R13
    }

    # === RD Rules ===
    required_rd_codes = {
        "AGE_BELOW_CATEGORY",  # RD2, RD3
        "MATCH_ALREADY_FINALIZED",  # RD8
        "CORRECTION_NOTE_REQUIRED",  # R23, R24
    }

    # Combina todos os códigos obrigatórios
    all_required_codes = required_rdb_codes | required_r_codes | required_rd_codes

    # Obtém todos os códigos implementados no ErrorCode enum
    implemented_codes = {code.value for code in ErrorCode}

    # Valida que todos os códigos obrigatórios estão implementados
    missing_codes = all_required_codes - implemented_codes

    assert len(missing_codes) == 0, (
        f"Error codes faltando no ErrorCode enum: {missing_codes}\n"
        f"Adicione estes códigos em backend/app/schemas/error.py"
    )


def test_error_code_enum_has_expected_categories():
    """Valida que ErrorCode enum tem códigos de todas as categorias"""
    error_codes = {code.value for code in ErrorCode}

    # RDB codes
    assert "MEMBERSHIP_OVERLAP" in error_codes
    assert "TEAM_REG_OVERLAP" in error_codes
    assert "SEASON_OVERLAP" in error_codes
    assert "SOFT_DELETE_REASON_REQUIRED" in error_codes

    # R codes
    assert "SUPERADMIN_IMMUTABLE" in error_codes
    assert "SUPERADMIN_REQUIRED" in error_codes
    assert "NO_ACTIVE_MEMBERSHIP" in error_codes
    assert "ATHLETE_DISPENSE_NO_UNDO" in error_codes

    # RD codes
    assert "AGE_BELOW_CATEGORY" in error_codes
    assert "MATCH_ALREADY_FINALIZED" in error_codes
    assert "CORRECTION_NOTE_REQUIRED" in error_codes

    # Generic codes
    assert "RESOURCE_NOT_FOUND" in error_codes
    assert "UNAUTHORIZED" in error_codes
    assert "FORBIDDEN" in error_codes
    assert "VALIDATION_ERROR" in error_codes


def test_error_code_count():
    """Valida número total de error codes implementados"""
    error_codes = list(ErrorCode)

    # Deve ter pelo menos os códigos documentados no API_CONTRACT.md
    # (11 específicos + alguns genéricos)
    assert len(error_codes) >= 11, (
        f"Esperado pelo menos 11 error codes, encontrado {len(error_codes)}"
    )


def test_error_code_enum_values_are_uppercase():
    """Valida que todos os error codes são UPPERCASE"""
    for code in ErrorCode:
        assert code.value.isupper(), (
            f"Error code '{code.value}' deve ser UPPERCASE"
        )
        assert code.value == code.value.replace(" ", "_"), (
            f"Error code '{code.value}' não deve conter espaços"
        )


def test_backward_compatibility_constants_exist():
    """Valida que constantes de backward compatibility existem"""
    from app.schemas.error import (
        ERROR_UNAUTHORIZED,
        ERROR_PERMISSION_DENIED,
        ERROR_NOT_FOUND,
        ERROR_CONFLICT_MEMBERSHIP_ACTIVE,
        ERROR_PERIOD_OVERLAP,
        ERROR_SEASON_LOCKED,
        ERROR_EDIT_FINALIZED_GAME,
        ERROR_VALIDATION,
        ERROR_AGE_CATEGORY_VIOLATION,
        ERROR_INVALID_STATE_TRANSITION,
        ERROR_INVALID_GOALKEEPER_STAT,
    )

    # Valida que as constantes são strings
    assert isinstance(ERROR_UNAUTHORIZED, str)
    assert isinstance(ERROR_PERMISSION_DENIED, str)
    assert isinstance(ERROR_NOT_FOUND, str)
    assert isinstance(ERROR_CONFLICT_MEMBERSHIP_ACTIVE, str)
    assert isinstance(ERROR_PERIOD_OVERLAP, str)
    assert isinstance(ERROR_SEASON_LOCKED, str)
    assert isinstance(ERROR_EDIT_FINALIZED_GAME, str)
    assert isinstance(ERROR_VALIDATION, str)
    assert isinstance(ERROR_AGE_CATEGORY_VIOLATION, str)
    assert isinstance(ERROR_INVALID_STATE_TRANSITION, str)
    assert isinstance(ERROR_INVALID_GOALKEEPER_STAT, str)
