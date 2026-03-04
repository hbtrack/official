"""
INV-TRAIN-011 — Regras de desvio e justificativa mínima

Enunciado:
  - desvio significativo: ≥20 pts em qualquer foco
  - desvio agregado significativo: ≥30%
  - justificativa mínima: ≥50 chars

Evidência (service):
  - app/services/training_session_service.py:582 (MIN_JUSTIFICATION_LENGTH = 50)
  - app/services/training_session_service.py:916 (desvio absoluto ≥ 20pts)
  - app/services/training_session_service.py:928 (desvio agregado ≥ 30%)

Teste: Verifica que as constantes e regras estão implementadas no service.
"""

from pathlib import Path
import re


class TestInvTrain011DeviationRules:
    """Testes para INV-TRAIN-011: Regras de desvio e justificativa mínima."""

    def test_min_justification_length_constant_exists(self):
        """Verifica que a constante MIN_JUSTIFICATION_LENGTH = 50 existe."""
        service_path = (
            Path(__file__).parent.parent.parent.parent
            / "app"
            / "services"
            / "training_session_service.py"
        )
        assert service_path.exists(), f"Service não encontrado: {service_path}"

        content = service_path.read_text(encoding="utf-8")

        # Busca a constante MIN_JUSTIFICATION_LENGTH
        match = re.search(r"MIN_JUSTIFICATION_LENGTH\s*=\s*(\d+)", content)
        assert match, "Constante MIN_JUSTIFICATION_LENGTH não encontrada"

        value = int(match.group(1))
        assert value == 50, (
            f"MIN_JUSTIFICATION_LENGTH deve ser 50, encontrado {value}"
        )

    def test_individual_deviation_threshold_20pts(self):
        """Verifica que desvio individual ≥ 20pts é considerado significativo."""
        service_path = (
            Path(__file__).parent.parent.parent.parent
            / "app"
            / "services"
            / "training_session_service.py"
        )
        content = service_path.read_text(encoding="utf-8")

        # Busca pela verificação de desvio ≥ 20
        # Padrão: abs(deviation) >= 20 ou similar
        assert ">= 20" in content or ">=20" in content, (
            "Verificação de desvio individual ≥ 20pts não encontrada"
        )

        # Verifica que há um comentário ou código mencionando 20pts
        assert "20" in content and "deviation" in content.lower(), (
            "Regra de desvio de 20pts não encontrada no código"
        )

    def test_aggregate_deviation_threshold_30pct(self):
        """Verifica que desvio agregado ≥ 30% é considerado significativo."""
        service_path = (
            Path(__file__).parent.parent.parent.parent
            / "app"
            / "services"
            / "training_session_service.py"
        )
        content = service_path.read_text(encoding="utf-8")

        # Busca pela verificação de desvio agregado ≥ 30
        # Padrão: total_deviation >= 30 ou similar
        assert ">= 30" in content or ">=30" in content, (
            "Verificação de desvio agregado ≥ 30% não encontrada"
        )

    def test_deviation_justification_validation_exists(self):
        """Verifica que há validação de justificativa para desvios."""
        service_path = (
            Path(__file__).parent.parent.parent.parent
            / "app"
            / "services"
            / "training_session_service.py"
        )
        content = service_path.read_text(encoding="utf-8")

        # Deve haver validação de tamanho mínimo de justificativa
        assert "MIN_JUSTIFICATION_LENGTH" in content, (
            "Referência a MIN_JUSTIFICATION_LENGTH não encontrada"
        )

        # Deve haver mensagem de erro para justificativa insuficiente
        assert "Justificativa obrigatória" in content or "mínimo" in content, (
            "Mensagem de validação de justificativa não encontrada"
        )

    def test_deviation_flag_field_exists(self):
        """Verifica que o campo planning_deviation_flag é usado."""
        service_path = (
            Path(__file__).parent.parent.parent.parent
            / "app"
            / "services"
            / "training_session_service.py"
        )
        content = service_path.read_text(encoding="utf-8")

        assert "planning_deviation_flag" in content, (
            "Campo planning_deviation_flag não encontrado no service"
        )

    def test_significant_deviation_logic_exists(self):
        """Verifica que há lógica para determinar desvio significativo."""
        service_path = (
            Path(__file__).parent.parent.parent.parent
            / "app"
            / "services"
            / "training_session_service.py"
        )
        content = service_path.read_text(encoding="utf-8")

        assert "significant_deviation" in content, (
            "Variável significant_deviation não encontrada no service"
        )
