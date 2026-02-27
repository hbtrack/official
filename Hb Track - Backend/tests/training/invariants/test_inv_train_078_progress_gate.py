"""
INV-TRAIN-078: check_progress_access — gate de telas de progresso/relatório
Classe C1 — Unit (AsyncMock, sem DB)
Evidência: app/services/athlete_content_gate_service.py — check_progress_access()
Regra: sem wellness diário completo → AccessGated(allows_minimum=False);
       com wellness completo → AccessGranted.
       allows_minimum=False significa bloqueio total (telas de progresso/relatório)
       diferente de check_content_access que usa allows_minimum=True.
"""
import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from app.services.athlete_content_gate_service import (
    AthleteContentGateService,
    AccessGranted,
    AccessGated,
)


class TestInvTrain078:
    """
    INV-TRAIN-078 — check_progress_access() retorna AccessGated(allows_minimum=False)
    quando wellness diário não completado; AccessGranted quando completo.
    Telas de progresso/relatório são mais restritas: nenhum acesso mínimo sem wellness.
    Evidência: app/services/athlete_content_gate_service.py — check_progress_access
    """

    @pytest.mark.asyncio
    async def test_no_wellness_returns_gated_without_minimum_access(self):
        """
        INV-078 CASO 1: sem wellness completo →
        check_progress_access() deve retornar AccessGated com allows_minimum=False.
        Telas de progresso bloqueadas completamente (sem acesso mínimo).
        """
        svc = AthleteContentGateService(db=AsyncMock())
        svc.has_completed_daily_wellness = AsyncMock(
            return_value=(False, ["wellness_pre_hoje"])
        )

        result = await svc.check_progress_access(athlete_id=uuid4())

        assert isinstance(result, AccessGated), (
            "INV-078: sem wellness deve retornar AccessGated, não AccessGranted"
        )
        assert result.allows_minimum is False, (
            "INV-078: AccessGated para progresso deve ter allows_minimum=False "
            "(telas de progresso completamente bloqueadas)"
        )

    @pytest.mark.asyncio
    async def test_wellness_complete_returns_granted(self):
        """
        INV-078 CASO 2: com wellness completo →
        check_progress_access() deve retornar AccessGranted.
        """
        svc = AthleteContentGateService(db=AsyncMock())
        svc.has_completed_daily_wellness = AsyncMock(return_value=(True, []))

        result = await svc.check_progress_access(athlete_id=uuid4())

        assert isinstance(result, AccessGranted), (
            "INV-078: wellness completo deve retornar AccessGranted"
        )
        assert result.reason == "wellness_complete", (
            "INV-078: AccessGranted.reason deve ser 'wellness_complete'"
        )

    @pytest.mark.asyncio
    async def test_anti_false_positive_progress_gate_stricter_than_content_gate(self):
        """
        INV-078 CASO 3 (anti-false-positive): check_progress_access retorna
        AccessGated(allows_minimum=False), enquanto check_content_access retorna
        AccessGated(allows_minimum=True). São semanticamente diferentes.
        Garante que progress gate é MAIS restritivo que content gate.
        """
        db_mock = AsyncMock()
        svc = AthleteContentGateService(db=db_mock)
        # Tanto 071 quanto 078: wellness incompleto
        incomplete = (False, ["wellness_pre_hoje"])

        svc.has_completed_daily_wellness = AsyncMock(return_value=incomplete)
        progress_result = await svc.check_progress_access(athlete_id=uuid4())

        svc.has_completed_daily_wellness = AsyncMock(return_value=incomplete)
        content_result = await svc.check_content_access(athlete_id=uuid4())

        # Ambos são AccessGated
        assert isinstance(progress_result, AccessGated)
        assert isinstance(content_result, AccessGated)

        # Mas differs em allows_minimum
        assert progress_result.allows_minimum is False, (
            "INV-078 anti-FP: progress gate deve ter allows_minimum=False"
        )
        assert content_result.allows_minimum is True, (
            "INV-078 anti-FP: content gate deve ter allows_minimum=True"
        )
        assert progress_result.allows_minimum != content_result.allows_minimum, (
            "INV-078 anti-FP: progress gate e content gate devem ter allows_minimum diferentes"
        )
