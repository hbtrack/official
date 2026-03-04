"""Testes unitários para configurações"""
import pytest
from app.core.config import Settings, settings


def test_settings_singleton():
    """Valida que settings é singleton"""
    from app.core.config import settings as settings2
    assert settings is settings2


def test_settings_required_fields():
    """Valida campos obrigatórios"""
    assert settings.DATABASE_URL is not None
    assert settings.JWT_SECRET is not None
    assert settings.API_TITLE == "HB Tracking API"


def test_settings_env_detection():
    """Valida detecção de ambiente"""
    assert settings.ENV in ["local", "staging", "production", "test"]

    if settings.ENV == "local":
        assert settings.is_local is True
        assert settings.is_production is False


def test_settings_cors_origins_is_list():
    """Valida que CORS_ORIGINS pode ser convertida para lista"""
    assert isinstance(settings.CORS_ORIGINS, str)
    origins_list = settings.cors_origins_list
    assert isinstance(origins_list, list)
    assert len(origins_list) > 0
