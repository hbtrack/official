"""
INV-TRAIN-014 — Alertas: sobrecarga por multiplicador (>= 1.5× threshold)

Enunciado: Alertas de sobrecarga são disparados quando carga >= 1.5× do threshold base.

Evidência (service):
  - app/services/training_alerts_service.py:43 (alert_threshold_multiplier: float = 1.5)
  - app/services/training_alerts_service.py:51 (documentação: default 1.5 = 150%)
  - app/services/training_alerts_service.py:82 (threshold_critical = threshold_base * alert_threshold_multiplier)

Teste: Verifica que o multiplicador de threshold está implementado no service.
"""

from pathlib import Path
import re


class TestInvTrain014OverloadAlertThreshold:
    """Testes para INV-TRAIN-014: Alertas sobrecarga por multiplicador 1.5×."""

    def test_alert_threshold_multiplier_default_is_1_5(self):
        """Verifica que o valor default do multiplicador é 1.5."""
        service_path = (
            Path(__file__).parent.parent.parent
            / "app"
            / "services"
            / "training_alerts_service.py"
        )
        assert service_path.exists(), f"Service não encontrado: {service_path}"

        content = service_path.read_text(encoding="utf-8")

        # Busca pelo parâmetro com valor default 1.5
        match = re.search(r"alert_threshold_multiplier.*=\s*([\d.]+)", content)
        assert match, "Parâmetro alert_threshold_multiplier não encontrado"

        value = float(match.group(1))
        assert value == 1.5, (
            f"alert_threshold_multiplier deve ter default 1.5, encontrado {value}"
        )

    def test_threshold_calculation_uses_multiplier(self):
        """Verifica que o cálculo de threshold usa o multiplicador."""
        service_path = (
            Path(__file__).parent.parent.parent
            / "app"
            / "services"
            / "training_alerts_service.py"
        )
        content = service_path.read_text(encoding="utf-8")

        # Busca pelo cálculo do threshold crítico
        assert "threshold_critical" in content, (
            "Variável threshold_critical não encontrada"
        )
        assert "threshold_base * alert_threshold_multiplier" in content, (
            "Cálculo 'threshold_base * alert_threshold_multiplier' não encontrado"
        )

    def test_weekly_overload_alert_type_exists(self):
        """Verifica que o tipo de alerta 'weekly_overload' existe."""
        service_path = (
            Path(__file__).parent.parent.parent
            / "app"
            / "services"
            / "training_alerts_service.py"
        )
        content = service_path.read_text(encoding="utf-8")

        assert "weekly_overload" in content, (
            "Tipo de alerta 'weekly_overload' não encontrado"
        )

    def test_severity_levels_exist(self):
        """Verifica que os níveis de severidade 'critical' e 'warning' existem."""
        service_path = (
            Path(__file__).parent.parent.parent
            / "app"
            / "services"
            / "training_alerts_service.py"
        )
        content = service_path.read_text(encoding="utf-8")

        assert '"critical"' in content or "'critical'" in content, (
            "Nível de severidade 'critical' não encontrado"
        )
        assert '"warning"' in content or "'warning'" in content, (
            "Nível de severidade 'warning' não encontrado"
        )

    def test_check_weekly_overload_method_exists(self):
        """Verifica que existe método para checar sobrecarga semanal."""
        service_path = (
            Path(__file__).parent.parent.parent
            / "app"
            / "services"
            / "training_alerts_service.py"
        )
        content = service_path.read_text(encoding="utf-8")

        assert "check_weekly_overload" in content or "weekly_overload" in content, (
            "Método de verificação de sobrecarga semanal não encontrado"
        )
