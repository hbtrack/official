"""
INV-TRAIN-071: check_content_access — gate de conteúdo por wellness obrigatório
Classe C1 — Unit (sem DB, corrotinas reais substituem delegado has_completed_daily_wellness)
Evidência: app/services/athlete_content_gate_service.py — check_content_access()
Regra: sem wellness diário completo → AccessGated(allows_minimum=True);
       com wellness completo → AccessGranted.
       allows_minimum=True permite ver conteúdo mínimo (horário) mas NÃO conteúdo completo.
"""
import pytest
from uuid import uuid4

from app.services.athlete_content_gate_service import (
    AthleteContentGateService,
    AccessGranted,
    AccessGated,
)


class TestInvTrain071:
    """
    INV-TRAIN-071 — check_content_access() retorna AccessGated(allows_minimum=True)
    quando wellness diário não completado; AccessGranted quando completo.
    Evidência: app/services/athlete_content_gate_service.py — check_content_access
    """

    @pytest.mark.asyncio
    async def test_no_wellness_returns_gated_with_minimum_access(self):
        """
        INV-071 CASO 1: sem wellness_pre hoje →
        check_content_access() deve retornar AccessGated com allows_minimum=True.
        O atleta pode ver conteúdo mínimo (ex: horário) mas NÃO conteúdo completo.
        """
        svc = AthleteContentGateService(db=None)

        async def _fake_no_wellness(*args, **kwargs):
            return (False, ["wellness_pre_hoje"])

        svc.has_completed_daily_wellness = _fake_no_wellness

        result = await svc.check_content_access(athlete_id=uuid4())

        assert isinstance(result, AccessGated), (
            "INV-071: sem wellness deve retornar AccessGated, não AccessGranted"
        )
        assert result.allows_minimum is True, (
            "INV-071: AccessGated para conteúdo deve ter allows_minimum=True "
            "(atleta vê conteúdo mínimo como horário do próximo treino)"
        )
        assert "wellness_pre_hoje" in result.missing_items, (
            "INV-071: missing_items deve conter 'wellness_pre_hoje'"
        )

    @pytest.mark.asyncio
    async def test_wellness_complete_returns_granted(self):
        """
        INV-071 CASO 2: com wellness completo →
        check_content_access() deve retornar AccessGranted.
        """
        svc = AthleteContentGateService(db=None)

        async def _fake_complete(*args, **kwargs):
            return (True, [])

        svc.has_completed_daily_wellness = _fake_complete

        result = await svc.check_content_access(athlete_id=uuid4())

        assert isinstance(result, AccessGranted), (
            "INV-071: wellness completo deve retornar AccessGranted"
        )
        assert result.reason == "wellness_complete", (
            "INV-071: AccessGranted.reason deve ser 'wellness_complete'"
        )

    @pytest.mark.asyncio
    async def test_anti_false_positive_gated_is_not_granted(self):
        """
        INV-071 CASO 3 (anti-false-positive): AccessGated(allows_minimum=True) NÃO é
        equivalente a AccessGranted. Tipos distintos — isinstance() deve distinguir.
        Garante que código downstream não confunda allows_minimum=True com acesso total.
        """
        svc = AthleteContentGateService(db=None)

        async def _fake_no_wellness(*args, **kwargs):
            return (False, ["wellness_pre_hoje"])

        svc.has_completed_daily_wellness = _fake_no_wellness

        result = await svc.check_content_access(athlete_id=uuid4())

        # O resultado NÃO deve ser AccessGranted
        assert not isinstance(result, AccessGranted), (
            "INV-071 anti-FP: AccessGated(allows_minimum=True) NÃO é AccessGranted — "
            "acesso mínimo != acesso total"
        )
        # Confirmar que é realmente AccessGated
        assert isinstance(result, AccessGated)
        # Confirmar que allows_minimum=True AINDA não significa acesso completo
        assert result.allows_minimum is True
        assert len(result.missing_items) > 0, (
            "INV-071 anti-FP: missing_items deve ser não-vazio quando gated"
        )
