"""
INV-TRAIN-003: Deadline Wellness Pós (até 24h após criação)

Regra: wellness_post é bloqueado se NOW > created_at + 24h.

Evidência:
- schema.sql:2828 (coluna `locked_at` em wellness_post)
- schema.sql:2863 (COMMENT: "post editável até 24h após submission")
- wellness_post_service.py:96-102 (_check_edit_window)
- wellness_post_service.py:262-263 (ValidationError quando fora da janela)
"""

from datetime import datetime, timedelta, timezone

import pytest

from app.models.wellness_post import WellnessPost
from app.services.wellness_post_service import WellnessPostService


class TestInvTrain003WellnessPostDeadline:
    """Testes para INV-TRAIN-003: Deadline Wellness Pós até 24h após criação."""

    @pytest.mark.asyncio
    async def test_check_edit_window_within_24h_returns_true(self):
        """Wellness criado há menos de 24h deve permitir edição."""
        # Arrange — _check_edit_window é puro: só lê wellness.created_at, sem DB
        service = WellnessPostService(None)
        wellness = WellnessPost(created_at=datetime.now(timezone.utc) - timedelta(hours=23))

        # Act
        result = await service._check_edit_window(wellness)

        # Assert
        assert result is True, "Deve permitir edição quando NOW < created_at + 24h"

    @pytest.mark.asyncio
    async def test_check_edit_window_past_24h_returns_false(self):
        """Wellness criado há mais de 24h deve bloquear edição."""
        # Arrange
        service = WellnessPostService(None)
        wellness = WellnessPost(created_at=datetime.now(timezone.utc) - timedelta(hours=25))

        # Act
        result = await service._check_edit_window(wellness)

        # Assert
        assert result is False, "Deve bloquear edição quando NOW >= created_at + 24h"

    @pytest.mark.asyncio
    async def test_check_edit_window_exactly_at_24h_returns_false(self):
        """Wellness exatamente em 24h deve bloquear (limite não inclusivo)."""
        # Arrange
        service = WellnessPostService(None)
        wellness = WellnessPost(created_at=datetime.now(timezone.utc) - timedelta(hours=24))

        # Act
        result = await service._check_edit_window(wellness)

        # Assert
        # NOW < deadline significa que quando NOW == deadline, retorna False
        assert result is False, "Deve bloquear quando NOW == created_at + 24h (limite não inclusivo)"

    @pytest.mark.asyncio
    async def test_check_edit_window_just_created_returns_true(self):
        """Wellness recém criado deve permitir edição."""
        # Arrange
        service = WellnessPostService(None)
        wellness = WellnessPost(created_at=datetime.now(timezone.utc))

        # Act
        result = await service._check_edit_window(wellness)

        # Assert
        assert result is True, "Deve permitir edição para wellness recém criado"

    @pytest.mark.asyncio
    async def test_check_edit_window_created_12h_ago_returns_true(self):
        """Wellness criado há 12h deve permitir edição (metade da janela)."""
        # Arrange
        service = WellnessPostService(None)
        wellness = WellnessPost(created_at=datetime.now(timezone.utc) - timedelta(hours=12))

        # Act
        result = await service._check_edit_window(wellness)

        # Assert
        assert result is True, "Deve permitir edição quando criado há 12h (metade da janela)"
