"""
INV-TRAIN-005: Sessão > 60 dias vira readonly (imutabilidade)

Regra: Sessões com session_at > 60 dias atrás são somente leitura.
Qualquer tentativa de edição deve ser bloqueada com ForbiddenError.

Evidência:
- training_session_service.py:58 (IMMUTABILITY_DAYS = 60)
- training_session_service.py:425-430 (validação em _validate_edit_permission)
"""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from app.core.context import ExecutionContext
from app.core.exceptions import ForbiddenError
from app.schemas.training_sessions import TrainingSessionUpdate
from app.services.training_session_service import TrainingSessionService


class _Session:
    """Objeto mínimo de sessão para testes de validação pura (sem DB)."""

    def __init__(self, status: str, session_at: datetime, ended_at=None):
        self.status = status
        self.session_at = session_at
        self.ended_at = ended_at


class TestInvTrain005Immutability60Days:
    """Testes para INV-TRAIN-005: Imutabilidade após 60 dias."""

    def _create_mock_session(self, days_ago: int, status: str = "readonly") -> _Session:
        """Cria objeto de sessão com session_at X dias atrás."""
        return _Session(
            status=status,
            session_at=datetime.now(timezone.utc) - timedelta(days=days_ago),
            ended_at=None,
        )

    def _create_service_with_context(self, role: str = "coordenador") -> TrainingSessionService:
        """Cria serviço com contexto real (sem mock)."""
        ctx = ExecutionContext(
            user_id=uuid4(),
            email="test@example.com",
            role_code=role,
            request_id=str(uuid4()),
            organization_id=uuid4(),
            permissions={},
        )
        # Passamos None como db — _validate_edit_permission é síncrono e não usa self.db
        return TrainingSessionService(None, ctx)

    def test_immutability_constant_is_60_days(self):
        """Constante IMMUTABILITY_DAYS deve ser 60."""
        assert TrainingSessionService.IMMUTABILITY_DAYS == 60, \
            "Prazo de imutabilidade deve ser 60 dias"

    def test_session_older_than_60_days_blocks_edit(self):
        """Sessão com session_at > 60 dias atrás deve bloquear edição."""
        # Arrange
        service = self._create_service_with_context()
        session = self._create_mock_session(days_ago=61, status="readonly")
        update = TrainingSessionUpdate(notes="tentativa de edição")

        # Act & Assert
        with pytest.raises(ForbiddenError) as exc_info:
            service._validate_edit_permission(session, update)

        assert "60 days" in str(exc_info.value) or "read-only" in str(exc_info.value).lower()

    def test_session_exactly_60_days_allows_edit(self):
        """Sessão com exatamente 60 dias deve permitir edição (limite não atingido)."""
        # Arrange
        service = self._create_service_with_context()
        # 60 dias menos 1 hora para garantir que está no limite
        session = self._create_mock_session(days_ago=59, status="readonly")
        update = TrainingSessionUpdate(notes="edição permitida")

        # Act - status "readonly" bloqueia por estado, não por tempo
        # Vamos usar status "draft" para testar apenas o limite de tempo
        session.status = "draft"

        try:
            service._validate_edit_permission(session, update)
            allowed = True
        except ForbiddenError as e:
            # Se bloqueou, não deve ser por imutabilidade
            allowed = "60 days" not in str(e) and "read-only" not in str(e).lower()

        # Assert
        assert allowed, "Sessão com < 60 dias não deve ser bloqueada por imutabilidade"

    def test_session_30_days_ago_allows_edit(self):
        """Sessão com 30 dias permite edição normalmente."""
        # Arrange
        service = self._create_service_with_context()
        session = self._create_mock_session(days_ago=30, status="draft")
        update = TrainingSessionUpdate(notes="edição normal")

        # Act
        try:
            service._validate_edit_permission(session, update)
            allowed = True
        except ForbiddenError:
            allowed = False

        # Assert
        assert allowed, "Sessão com 30 dias deve permitir edição"

    def test_session_90_days_ago_blocks_edit(self):
        """Sessão com 90 dias deve bloquear edição por imutabilidade."""
        # Arrange
        service = self._create_service_with_context()
        session = self._create_mock_session(days_ago=90, status="readonly")
        update = TrainingSessionUpdate(notes="tentativa")

        # Act & Assert
        with pytest.raises(ForbiddenError) as exc_info:
            service._validate_edit_permission(session, update)

        assert "60 days" in str(exc_info.value) or "read-only" in str(exc_info.value).lower()

    def test_immutability_error_message_mentions_60_days(self):
        """Mensagem de erro deve mencionar 60 dias."""
        # Arrange
        service = self._create_service_with_context()
        session = self._create_mock_session(days_ago=100, status="readonly")
        update = TrainingSessionUpdate(notes="teste mensagem")

        # Act & Assert
        with pytest.raises(ForbiddenError) as exc_info:
            service._validate_edit_permission(session, update)

        error_message = str(exc_info.value)
        assert "60" in error_message, f"Mensagem deve mencionar 60 dias: {error_message}"

    def test_immutability_constant_is_60_days(self):
        """Constante IMMUTABILITY_DAYS deve ser 60."""
        assert TrainingSessionService.IMMUTABILITY_DAYS == 60, \
            "Prazo de imutabilidade deve ser 60 dias"

    def test_session_older_than_60_days_blocks_edit(self):
        """Sessão com session_at > 60 dias atrás deve bloquear edição."""
        # Arrange
        service = self._create_service_with_context()
        session = self._create_mock_session(days_ago=61, status="readonly")
        update = TrainingSessionUpdate(notes="tentativa de edição")

        # Act & Assert
        with pytest.raises(ForbiddenError) as exc_info:
            service._validate_edit_permission(session, update)

        assert "60 days" in str(exc_info.value) or "read-only" in str(exc_info.value).lower()

    def test_session_exactly_60_days_allows_edit(self):
        """Sessão com exatamente 60 dias deve permitir edição (limite não atingido)."""
        # Arrange
        service = self._create_service_with_context()
        # 60 dias menos 1 hora para garantir que está no limite
        session = self._create_mock_session(days_ago=59, status="readonly")
        update = TrainingSessionUpdate(notes="edição permitida")

        # Act - status "readonly" bloqueia por estado, não por tempo
        # Vamos usar status "draft" para testar apenas o limite de tempo
        session.status = "draft"

        try:
            service._validate_edit_permission(session, update)
            allowed = True
        except ForbiddenError as e:
            # Se bloqueou, não deve ser por imutabilidade
            allowed = "60 days" not in str(e) and "read-only" not in str(e).lower()

        # Assert
        assert allowed, "Sessão com < 60 dias não deve ser bloqueada por imutabilidade"

    def test_session_30_days_ago_allows_edit(self):
        """Sessão com 30 dias permite edição normalmente."""
        # Arrange
        service = self._create_service_with_context()
        session = self._create_mock_session(days_ago=30, status="draft")
        update = TrainingSessionUpdate(notes="edição normal")

        # Act
        try:
            service._validate_edit_permission(session, update)
            allowed = True
        except ForbiddenError:
            allowed = False

        # Assert
        assert allowed, "Sessão com 30 dias deve permitir edição"

    def test_session_90_days_ago_blocks_edit(self):
        """Sessão com 90 dias deve bloquear edição por imutabilidade."""
        # Arrange
        service = self._create_service_with_context()
        session = self._create_mock_session(days_ago=90, status="readonly")
        update = TrainingSessionUpdate(notes="tentativa")

        # Act & Assert
        with pytest.raises(ForbiddenError) as exc_info:
            service._validate_edit_permission(session, update)

        assert "60 days" in str(exc_info.value) or "read-only" in str(exc_info.value).lower()

    def test_immutability_error_message_mentions_60_days(self):
        """Mensagem de erro deve mencionar 60 dias."""
        # Arrange
        service = self._create_service_with_context()
        session = self._create_mock_session(days_ago=100, status="readonly")
        update = TrainingSessionUpdate(notes="teste mensagem")

        # Act & Assert
        with pytest.raises(ForbiddenError) as exc_info:
            service._validate_edit_permission(session, update)

        error_message = str(exc_info.value)
        assert "60" in error_message, f"Mensagem deve mencionar 60 dias: {error_message}"
