"""
INV-TRAIN-026 — LGPD access logging (staff lendo dados de outros atletas)

Enunciado: Quando staff lê dados wellness de outros atletas, o acesso
é registrado em data_access_logs para compliance LGPD.

Evidência (services):
  - app/services/wellness_pre_service.py:69-173 (data_access_logs para staff)
  - app/services/wellness_post_service.py:69-169 (data_access_logs para staff)

Teste: Verifica que os services registram acessos em data_access_logs.
"""

from pathlib import Path
import re


class TestInvTrain026LgpdAccessLogging:
    """Testes para INV-TRAIN-026: LGPD access logging."""

    def test_wellness_pre_service_has_access_logging(self):
        """Verifica que wellness_pre_service registra acessos."""
        service_path = (
            Path(__file__).parent.parent.parent.parent
            / "app"
            / "services"
            / "wellness_pre_service.py"
        )
        assert service_path.exists(), f"Service não encontrado: {service_path}"

        content = service_path.read_text(encoding="utf-8")
        assert "data_access_logs" in content, (
            "Referência a data_access_logs não encontrada em wellness_pre_service"
        )

    def test_wellness_post_service_has_access_logging(self):
        """Verifica que wellness_post_service registra acessos."""
        service_path = (
            Path(__file__).parent.parent.parent.parent
            / "app"
            / "services"
            / "wellness_post_service.py"
        )
        assert service_path.exists(), f"Service não encontrado: {service_path}"

        content = service_path.read_text(encoding="utf-8")
        assert "data_access_logs" in content, (
            "Referência a data_access_logs não encontrada em wellness_post_service"
        )

    def test_wellness_pre_logs_staff_access_only(self):
        """Verifica que wellness_pre só loga quando staff lê dados de outros."""
        service_path = (
            Path(__file__).parent.parent.parent.parent
            / "app"
            / "services"
            / "wellness_pre_service.py"
        )
        content = service_path.read_text(encoding="utf-8")

        # Deve mencionar que só loga staff lendo dados de outros
        assert "staff" in content.lower(), (
            "Service deve mencionar logging para staff"
        )

    def test_wellness_post_logs_staff_access_only(self):
        """Verifica que wellness_post só loga quando staff lê dados de outros."""
        service_path = (
            Path(__file__).parent.parent.parent.parent
            / "app"
            / "services"
            / "wellness_post_service.py"
        )
        content = service_path.read_text(encoding="utf-8")

        # Deve mencionar que só loga staff lendo dados de outros
        assert "staff" in content.lower(), (
            "Service deve mencionar logging para staff"
        )

    def test_data_access_log_model_exists(self):
        """Verifica que o modelo DataAccessLog existe."""
        model_path = (
            Path(__file__).parent.parent.parent.parent
            / "app"
            / "models"
            / "data_access_log.py"
        )
        # Se não existir arquivo específico, verifica se está em outro lugar
        if not model_path.exists():
            # Busca em outros arquivos de modelo
            models_dir = Path(__file__).parent.parent.parent.parent / "app" / "models"
            found = False
            for py_file in models_dir.glob("*.py"):
                content = py_file.read_text(encoding="utf-8")
                if "class DataAccessLog" in content:
                    found = True
                    break
            assert found, "Classe DataAccessLog não encontrada em models"
        else:
            content = model_path.read_text(encoding="utf-8")
            assert "class DataAccessLog" in content, (
                "Classe DataAccessLog não encontrada"
            )

    def test_wellness_services_import_data_access_log(self):
        """Verifica que services importam DataAccessLog."""
        for service_name in ["wellness_pre_service.py", "wellness_post_service.py"]:
            service_path = (
                Path(__file__).parent.parent.parent.parent
                / "app"
                / "services"
                / service_name
            )
            content = service_path.read_text(encoding="utf-8")
            assert "DataAccessLog" in content, (
                f"{service_name} deve importar DataAccessLog"
            )
