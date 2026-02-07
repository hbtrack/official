"""
Configuração de testes de integração FASE 4
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Fixture do TestClient para testes de integração"""
    return TestClient(app)
