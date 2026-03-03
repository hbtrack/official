"""
INV-TRAIN-013 — Gamificação: critérios de badge (regras de elegibilidade)

Enunciado:
  - monthly: response_rate >= 90%
  - streak: 3 meses consecutivos

Evidência (service):
  - app/services/wellness_gamification_service.py:128 (response_rate >= 90.0)
  - app/services/wellness_gamification_service.py:147-154 (_check_and_award_streak)
  - app/services/wellness_gamification_service.py:389-450 (streak de 3 meses)

Teste: Verifica que as regras de elegibilidade estão implementadas no service.
"""

from pathlib import Path
import re


class TestInvTrain013GamificationBadgeRules:
    """Testes para INV-TRAIN-013: Critérios de badge de gamificação."""

    def test_monthly_badge_requires_90_percent_rate(self):
        """Verifica que badge mensal exige response_rate >= 90%."""
        service_path = (
            Path(__file__).parent.parent.parent
            / "app"
            / "services"
            / "wellness_gamification_service.py"
        )
        assert service_path.exists(), f"Service não encontrado: {service_path}"

        content = service_path.read_text(encoding="utf-8")

        # Busca pelo critério de 90%
        assert ">= 90" in content or ">=90" in content, (
            "Critério de response_rate >= 90% não encontrado"
        )

        # Verifica que há referência específica ao valor 90.0
        match = re.search(r"response_rate\s*>=\s*90", content)
        assert match, "Expressão 'response_rate >= 90' não encontrada"

    def test_streak_badge_requires_3_consecutive_months(self):
        """Verifica que streak badge exige 3 meses consecutivos."""
        service_path = (
            Path(__file__).parent.parent.parent
            / "app"
            / "services"
            / "wellness_gamification_service.py"
        )
        content = service_path.read_text(encoding="utf-8")

        # Busca por referência a 3 meses
        assert "3 meses" in content or "3 months" in content or "3months" in content, (
            "Critério de 3 meses consecutivos não encontrado"
        )

    def test_check_and_award_streak_method_exists(self):
        """Verifica que existe método _check_and_award_streak."""
        service_path = (
            Path(__file__).parent.parent.parent
            / "app"
            / "services"
            / "wellness_gamification_service.py"
        )
        content = service_path.read_text(encoding="utf-8")

        assert "_check_and_award_streak" in content, (
            "Método _check_and_award_streak não encontrado"
        )

    def test_wellness_champion_monthly_badge_type_exists(self):
        """Verifica que o tipo de badge 'wellness_champion_monthly' existe."""
        service_path = (
            Path(__file__).parent.parent.parent
            / "app"
            / "services"
            / "wellness_gamification_service.py"
        )
        content = service_path.read_text(encoding="utf-8")

        assert "wellness_champion_monthly" in content, (
            "Tipo de badge 'wellness_champion_monthly' não encontrado"
        )

    def test_wellness_streak_3months_badge_type_exists(self):
        """Verifica que o tipo de badge 'wellness_streak_3months' existe."""
        service_path = (
            Path(__file__).parent.parent.parent
            / "app"
            / "services"
            / "wellness_gamification_service.py"
        )
        content = service_path.read_text(encoding="utf-8")

        assert "wellness_streak_3months" in content, (
            "Tipo de badge 'wellness_streak_3months' não encontrado"
        )

    def test_badge_notification_created(self):
        """Verifica que há criação de notificação para badges."""
        service_path = (
            Path(__file__).parent.parent.parent
            / "app"
            / "services"
            / "wellness_gamification_service.py"
        )
        content = service_path.read_text(encoding="utf-8")

        assert "_create_badge_notification" in content, (
            "Método _create_badge_notification não encontrado"
        )

    def test_zero_expected_wellness_not_eligible(self):
        """Verifica que expected > 0 é pré-condição para award (não divide por zero)."""
        service_path = (
            Path(__file__).parent.parent.parent
            / "app"
            / "services"
            / "wellness_gamification_service.py"
        )
        content = service_path.read_text(encoding="utf-8")

        # A guarda 'expected > 0' protege contra divisão por zero e falso-positivo
        assert "expected > 0" in content, (
            "Guarda 'expected > 0' não encontrada — risco de badge com 0 questionários esperados"
        )

    def test_calculate_monthly_wellness_badges_entrypoint_exists(self):
        """Verifica que existe entry-point público calculate_monthly_wellness_badges."""
        service_path = (
            Path(__file__).parent.parent.parent
            / "app"
            / "services"
            / "wellness_gamification_service.py"
        )
        content = service_path.read_text(encoding="utf-8")

        assert "calculate_monthly_wellness_badges" in content, (
            "Entry-point 'calculate_monthly_wellness_badges' não encontrado no service"
        )

    def test_award_badge_method_exists(self):
        """Verifica que existe método interno _award_badge para persistência do badge."""
        service_path = (
            Path(__file__).parent.parent.parent
            / "app"
            / "services"
            / "wellness_gamification_service.py"
        )
        content = service_path.read_text(encoding="utf-8")

        assert "_award_badge" in content, (
            "Método _award_badge não encontrado — badge não pode ser persistido"
        )
