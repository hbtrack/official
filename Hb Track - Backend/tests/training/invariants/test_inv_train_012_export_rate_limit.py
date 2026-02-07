"""
INV-TRAIN-012 — Rate limiting de export LGPD

Enunciado:
  - PDF: máx 5/dia
  - Athlete export: máx 3/dia

Evidência (service):
  - app/services/export_service.py:30 (ANALYTICS_PDF_DAILY_LIMIT = 5)
  - app/services/export_service.py:31 (ATHLETE_DATA_DAILY_LIMIT = 3)

Teste: Verifica que as constantes de rate limit existem e têm valores corretos.
"""

from pathlib import Path
import re


class TestInvTrain012ExportRateLimit:
    """Testes para INV-TRAIN-012: Rate limiting de export LGPD."""

    def test_analytics_pdf_daily_limit_exists(self):
        """Verifica que a constante ANALYTICS_PDF_DAILY_LIMIT = 5 existe."""
        service_path = (
            Path(__file__).parent.parent.parent
            / "app"
            / "services"
            / "export_service.py"
        )
        assert service_path.exists(), f"Service não encontrado: {service_path}"

        content = service_path.read_text(encoding="utf-8")

        # Busca a constante
        match = re.search(r"ANALYTICS_PDF_DAILY_LIMIT\s*=\s*(\d+)", content)
        assert match, "Constante ANALYTICS_PDF_DAILY_LIMIT não encontrada"

        value = int(match.group(1))
        assert value == 5, (
            f"ANALYTICS_PDF_DAILY_LIMIT deve ser 5, encontrado {value}"
        )

    def test_athlete_data_daily_limit_exists(self):
        """Verifica que a constante ATHLETE_DATA_DAILY_LIMIT = 3 existe."""
        service_path = (
            Path(__file__).parent.parent.parent
            / "app"
            / "services"
            / "export_service.py"
        )
        content = service_path.read_text(encoding="utf-8")

        # Busca a constante
        match = re.search(r"ATHLETE_DATA_DAILY_LIMIT\s*=\s*(\d+)", content)
        assert match, "Constante ATHLETE_DATA_DAILY_LIMIT não encontrada"

        value = int(match.group(1))
        assert value == 3, (
            f"ATHLETE_DATA_DAILY_LIMIT deve ser 3, encontrado {value}"
        )

    def test_check_rate_limit_method_exists(self):
        """Verifica que existe método check_rate_limit no ExportService."""
        service_path = (
            Path(__file__).parent.parent.parent
            / "app"
            / "services"
            / "export_service.py"
        )
        content = service_path.read_text(encoding="utf-8")

        assert "async def check_rate_limit" in content, (
            "Método check_rate_limit não encontrado no ExportService"
        )

    def test_export_service_class_exists(self):
        """Verifica que a classe ExportService existe."""
        service_path = (
            Path(__file__).parent.parent.parent
            / "app"
            / "services"
            / "export_service.py"
        )
        content = service_path.read_text(encoding="utf-8")

        assert "class ExportService" in content, (
            "Classe ExportService não encontrada"
        )
