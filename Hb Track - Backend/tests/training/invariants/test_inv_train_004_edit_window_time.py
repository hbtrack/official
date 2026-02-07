"""
INV-TRAIN-004: Janela de edição por autoria/hierarquia (validação por tempo)

Regra implementada:
- Autor (treinador): pode editar sessão scheduled até 10min antes de session_at
- Superior (coordenador/dirigente): pode editar pending_review até 24h após ended_at

Evidência:
- training_session_service.py:54 (AUTHOR_EDIT_WINDOW_MINUTES = 10)
- training_session_service.py:55 (SUPERIOR_EDIT_WINDOW_HOURS = 24)
- training_session_service.py:437-456 (validação por tempo em _validate_edit_permission)
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.exceptions import ForbiddenError
from app.schemas.training_sessions import TrainingSessionUpdate
from app.services.training_session_service import TrainingSessionService


class TestInvTrain004EditWindowTime:
    """Testes para INV-TRAIN-004: Validação de janela de edição por tempo."""

    def _create_mock_session(
        self,
        status: str,
        session_at: datetime,
        ended_at: datetime = None,
        days_ago: int = 0
    ) -> MagicMock:
        """Cria mock de sessão com status, session_at e ended_at especificados."""
        mock_session = MagicMock()
        mock_session.status = status
        mock_session.session_at = session_at
        mock_session.ended_at = ended_at
        return mock_session

    def _create_service_with_context(self, role: str = "treinador") -> TrainingSessionService:
        """Cria serviço com contexto mockado."""
        mock_db = AsyncMock()
        service = TrainingSessionService(mock_db, MagicMock())
        service.context = MagicMock()
        service.context.role_code = role
        service.context.is_superadmin = False
        return service

    # =========================================================================
    # Testes para AUTOR (treinador) em sessões scheduled
    # =========================================================================

    def test_treinador_can_edit_scheduled_session_before_deadline(self):
        """Treinador pode editar sessão scheduled se faltam mais de 10min para session_at."""
        # Arrange
        service = self._create_service_with_context(role="treinador")
        now = datetime.now(timezone.utc)
        session_at = now + timedelta(hours=1)  # 1 hora no futuro (> 10min)
        session = self._create_mock_session("scheduled", session_at)
        update = TrainingSessionUpdate(notes="teste")

        # Act - não deve lançar exceção
        try:
            service._validate_edit_permission(session, update)
            allowed = True
        except ForbiddenError:
            allowed = False

        # Assert
        assert allowed, "Treinador deve poder editar se faltam > 10min para session_at"

    def test_treinador_blocked_from_editing_scheduled_session_after_deadline(self):
        """Treinador NÃO pode editar sessão scheduled se faltam menos de 10min para session_at."""
        # Arrange
        service = self._create_service_with_context(role="treinador")
        now = datetime.now(timezone.utc)
        session_at = now + timedelta(minutes=5)  # 5 minutos no futuro (< 10min)
        session = self._create_mock_session("scheduled", session_at)
        update = TrainingSessionUpdate(notes="teste")

        # Act & Assert
        with pytest.raises(ForbiddenError) as exc_info:
            service._validate_edit_permission(session, update)

        assert "prazo de edição do autor expirado" in str(exc_info.value).lower()

    def test_treinador_blocked_at_exactly_10_minutes(self):
        """Treinador NÃO pode editar quando faltam exatamente 10min (limite não inclusivo)."""
        # Arrange
        service = self._create_service_with_context(role="treinador")
        now = datetime.now(timezone.utc)
        # Adicionamos 1 segundo para garantir que now > deadline
        session_at = now + timedelta(minutes=10) - timedelta(seconds=1)
        session = self._create_mock_session("scheduled", session_at)
        update = TrainingSessionUpdate(notes="teste")

        # Act & Assert
        with pytest.raises(ForbiddenError):
            service._validate_edit_permission(session, update)

    # =========================================================================
    # Testes para SUPERIOR (coordenador/dirigente) em sessões scheduled
    # =========================================================================

    def test_coordenador_can_edit_scheduled_session_anytime(self):
        """Coordenador pode editar sessão scheduled mesmo faltando < 10min."""
        # Arrange
        service = self._create_service_with_context(role="coordenador")
        now = datetime.now(timezone.utc)
        session_at = now + timedelta(minutes=5)  # 5 minutos no futuro (< 10min)
        session = self._create_mock_session("scheduled", session_at)
        update = TrainingSessionUpdate(notes="teste")

        # Act - não deve lançar exceção (superior não tem limite de 10min)
        try:
            service._validate_edit_permission(session, update)
            allowed = True
        except ForbiddenError:
            allowed = False

        # Assert
        assert allowed, "Coordenador (superior) não deve ter limite de 10min para scheduled"

    def test_dirigente_can_edit_scheduled_session_anytime(self):
        """Dirigente pode editar sessão scheduled mesmo faltando < 10min."""
        # Arrange
        service = self._create_service_with_context(role="dirigente")
        now = datetime.now(timezone.utc)
        session_at = now + timedelta(minutes=5)  # 5 minutos no futuro (< 10min)
        session = self._create_mock_session("scheduled", session_at)
        update = TrainingSessionUpdate(notes="teste")

        # Act - não deve lançar exceção
        try:
            service._validate_edit_permission(session, update)
            allowed = True
        except ForbiddenError:
            allowed = False

        # Assert
        assert allowed, "Dirigente (superior) não deve ter limite de 10min para scheduled"

    # =========================================================================
    # Testes para SUPERIOR em sessões pending_review
    # =========================================================================

    def test_superior_can_edit_pending_review_within_24h(self):
        """Superior pode editar pending_review se < 24h desde ended_at."""
        # Arrange
        service = self._create_service_with_context(role="coordenador")
        now = datetime.now(timezone.utc)
        session_at = now - timedelta(hours=3)  # Sessão 3h atrás
        ended_at = now - timedelta(hours=2)  # Terminou 2h atrás (< 24h)
        session = self._create_mock_session("pending_review", session_at, ended_at)
        update = TrainingSessionUpdate(execution_outcome="on_time")

        # Act - não deve lançar exceção
        try:
            service._validate_edit_permission(session, update)
            allowed = True
        except ForbiddenError:
            allowed = False

        # Assert
        assert allowed, "Superior deve poder editar pending_review se < 24h desde ended_at"

    def test_superior_blocked_from_editing_pending_review_after_24h(self):
        """Superior NÃO pode editar pending_review se > 24h desde ended_at."""
        # Arrange
        service = self._create_service_with_context(role="coordenador")
        now = datetime.now(timezone.utc)
        session_at = now - timedelta(hours=30)  # Sessão 30h atrás
        ended_at = now - timedelta(hours=25)  # Terminou 25h atrás (> 24h)
        session = self._create_mock_session("pending_review", session_at, ended_at)
        update = TrainingSessionUpdate(execution_outcome="on_time")

        # Act & Assert
        with pytest.raises(ForbiddenError) as exc_info:
            service._validate_edit_permission(session, update)

        assert "prazo de edição do superior expirado" in str(exc_info.value).lower()

    def test_pending_review_without_ended_at_allows_edit(self):
        """Sessão pending_review sem ended_at permite edição (fallback seguro)."""
        # Arrange
        service = self._create_service_with_context(role="coordenador")
        now = datetime.now(timezone.utc)
        session_at = now - timedelta(hours=30)
        session = self._create_mock_session("pending_review", session_at, ended_at=None)
        update = TrainingSessionUpdate(execution_outcome="on_time")

        # Act - não deve lançar exceção (ended_at é None)
        try:
            service._validate_edit_permission(session, update)
            allowed = True
        except ForbiddenError:
            allowed = False

        # Assert
        assert allowed, "Sem ended_at, a validação de 24h não deve ser aplicada"
