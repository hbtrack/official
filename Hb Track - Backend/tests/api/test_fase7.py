"""
Testes de FASE 7 - Preparação para Produção

Testa:
- Logging estruturado
- Middlewares (RequestID, Security Headers)
- Healthcheck avançado
"""

import pytest
from app.core.logging import JSONFormatter, setup_logging
from app.core.middleware import RequestIDMiddleware
import logging
import json


class TestJSONFormatter:
    """Testes do JSONFormatter para logging estruturado."""

    def test_basic_format(self):
        """Verifica formato JSON básico."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        output = formatter.format(record)
        data = json.loads(output)
        
        assert data["level"] == "INFO"
        assert data["logger"] == "test"
        assert data["message"] == "Test message"
        assert data["line"] == 10
        assert "timestamp" in data

    def test_extra_fields(self):
        """Verifica que campos extras são incluídos."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )
        record.request_id = "test-request-id"
        record.user_id = "test-user-id"
        
        output = formatter.format(record)
        data = json.loads(output)
        
        assert data["request_id"] == "test-request-id"
        assert data["user_id"] == "test-user-id"


class TestSetupLogging:
    """Testes da função setup_logging."""

    def test_setup_logging_production(self):
        """Verifica setup de logging em produção (JSON)."""
        setup_logging("production", "INFO")
        
        logger = logging.getLogger()
        assert len(logger.handlers) > 0
        
        # Em produção, deve usar JSONFormatter
        handler = logger.handlers[0]
        assert isinstance(handler.formatter, JSONFormatter)

    def test_setup_logging_development(self):
        """Verifica setup de logging em desenvolvimento."""
        setup_logging("local", "DEBUG")
        
        logger = logging.getLogger()
        assert len(logger.handlers) > 0
        
        # Em dev, usa formatter padrão
        handler = logger.handlers[0]
        assert not isinstance(handler.formatter, JSONFormatter)


class TestHealthFullEndpoint:
    """Testes do endpoint /health/full."""

    def test_health_full_returns_checks(self, client):
        """Verifica que /health/full retorna validações."""
        response = client.get("/api/v1/health/full")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "checks" in data
        assert "database" in data
        
        # Verificar checks específicos
        checks = data["checks"]
        assert "superadmin_exists" in checks
        assert "roles_seeded" in checks
        assert "categories_seeded" in checks
        assert "organization_exists" in checks

    def test_health_full_superadmin_check(self, client):
        """Verifica check do superadmin (R3, RDB6)."""
        response = client.get("/api/v1/health/full")
        
        assert response.status_code == 200
        data = response.json()
        
        # Deve existir exatamente 1 superadmin
        assert data["checks"]["superadmin_exists"] is True
        assert data["checks"]["superadmin_count"] == 1

    def test_health_full_roles_check(self, client):
        """Verifica check dos roles (R4)."""
        response = client.get("/api/v1/health/full")
        
        assert response.status_code == 200
        data = response.json()
        
        # Deve ter pelo menos 4 roles
        assert data["checks"]["roles_seeded"] is True
        assert data["checks"]["roles_count"] >= 4

    def test_health_full_categories_check(self, client):
        """Verifica check das categorias (R15)."""
        response = client.get("/api/v1/health/full")
        
        assert response.status_code == 200
        data = response.json()
        
        # Deve ter pelo menos 6 categorias
        assert data["checks"]["categories_seeded"] is True
        assert data["checks"]["categories_count"] >= 6


class TestRequestIDMiddleware:
    """Testes do middleware de Request ID."""

    def test_request_id_generated(self, client):
        """Verifica que Request ID é gerado automaticamente."""
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200
        assert "X-Request-ID" in response.headers
        
        # UUID format check
        request_id = response.headers["X-Request-ID"]
        assert len(request_id) == 36  # UUID v4 format

    def test_request_id_preserved(self, client):
        """Verifica que Request ID fornecido é preservado."""
        custom_id = "custom-test-request-id-123"
        response = client.get(
            "/api/v1/health",
            headers={"X-Request-ID": custom_id}
        )
        
        assert response.status_code == 200
        assert response.headers["X-Request-ID"] == custom_id


class TestSecurityHeaders:
    """Testes dos headers de segurança."""

    def test_security_headers_present(self, client):
        """Verifica que headers de segurança estão presentes."""
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        
        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"
        
        assert "X-XSS-Protection" in response.headers
        assert response.headers["X-XSS-Protection"] == "1; mode=block"
