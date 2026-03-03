"""
INV-TRAIN-025 — Export LGPD via endpoints OpenAPI + Celery async + cleanup de jobs

Enunciado: Exports de analytics PDF e dados LGPD são expostos via endpoints
REST + Celery async para processamento em background + cleanup automático.

Evidência (router + celery):
  - app/api/v1/routers/exports.py:32-170 (export PDF analytics + status/list/rate-limit)
  - app/api/v1/routers/athlete_export.py:29-120 (LGPD export /athletes/me/export-data)
  - app/core/celery_tasks.py:400-556 (generate_analytics_pdf_task + cleanup_expired_export_jobs_task)

Teste: Verifica que endpoints e tasks Celery existem.
"""

from pathlib import Path
import re


class TestInvTrain025ExportLgpdEndpoints:
    """Testes para INV-TRAIN-025: Export LGPD endpoints + Celery."""

    def test_exports_router_exists(self):
        """Verifica que o router exports.py existe."""
        router_path = (
            Path(__file__).parent.parent.parent.parent
            / "app"
            / "api"
            / "v1"
            / "routers"
            / "exports.py"
        )
        assert router_path.exists(), f"Router não encontrado: {router_path}"

    def test_export_pdf_endpoint_exists(self):
        """Verifica endpoint POST /analytics/export-pdf."""
        router_path = (
            Path(__file__).parent.parent.parent.parent
            / "app"
            / "api"
            / "v1"
            / "routers"
            / "exports.py"
        )
        content = router_path.read_text(encoding="utf-8")

        assert "/analytics/export-pdf" in content, (
            "Endpoint /analytics/export-pdf não encontrado"
        )
        assert "request_analytics_pdf_export" in content, (
            "Função request_analytics_pdf_export não encontrada"
        )

    def test_export_status_endpoint_exists(self):
        """Verifica endpoint GET /analytics/exports/{job_id}."""
        router_path = (
            Path(__file__).parent.parent.parent.parent
            / "app"
            / "api"
            / "v1"
            / "routers"
            / "exports.py"
        )
        content = router_path.read_text(encoding="utf-8")

        assert "/analytics/exports/{job_id}" in content, (
            "Endpoint /analytics/exports/{job_id} não encontrado"
        )
        assert "get_export_job_status" in content, (
            "Função get_export_job_status não encontrada"
        )

    def test_export_list_endpoint_exists(self):
        """Verifica endpoint GET /analytics/exports."""
        router_path = (
            Path(__file__).parent.parent.parent.parent
            / "app"
            / "api"
            / "v1"
            / "routers"
            / "exports.py"
        )
        content = router_path.read_text(encoding="utf-8")

        assert "list_user_exports" in content, (
            "Função list_user_exports não encontrada"
        )

    def test_athlete_export_router_exists(self):
        """Verifica que o router athlete_export.py existe."""
        router_path = (
            Path(__file__).parent.parent.parent.parent
            / "app"
            / "api"
            / "v1"
            / "routers"
            / "athlete_export.py"
        )
        assert router_path.exists(), f"Router não encontrado: {router_path}"

    def test_lgpd_export_endpoint_exists(self):
        """Verifica endpoint GET /athletes/me/export-data."""
        router_path = (
            Path(__file__).parent.parent.parent.parent
            / "app"
            / "api"
            / "v1"
            / "routers"
            / "athlete_export.py"
        )
        content = router_path.read_text(encoding="utf-8")

        assert "/me/export-data" in content, (
            "Endpoint /me/export-data não encontrado"
        )
        assert "export_athlete_data" in content, (
            "Função export_athlete_data não encontrada"
        )

    def test_celery_pdf_task_exists(self):
        """Verifica que task generate_analytics_pdf_task existe."""
        celery_path = (
            Path(__file__).parent.parent.parent.parent
            / "app"
            / "core"
            / "celery_tasks.py"
        )
        assert celery_path.exists(), f"Celery tasks não encontrado: {celery_path}"

        content = celery_path.read_text(encoding="utf-8")
        assert "generate_analytics_pdf_task" in content, (
            "Task generate_analytics_pdf_task não encontrada"
        )

    def test_celery_cleanup_task_exists(self):
        """Verifica que task cleanup_expired_export_jobs_task existe."""
        celery_path = (
            Path(__file__).parent.parent.parent.parent
            / "app"
            / "core"
            / "celery_tasks.py"
        )
        content = celery_path.read_text(encoding="utf-8")

        assert "cleanup_expired_export_jobs_task" in content, (
            "Task cleanup_expired_export_jobs_task não encontrada"
        )

    def test_lgpd_endpoint_mentions_art_18(self):
        """Verifica que endpoint LGPD menciona Art. 18 da LGPD."""
        router_path = (
            Path(__file__).parent.parent.parent.parent
            / "app"
            / "api"
            / "v1"
            / "routers"
            / "athlete_export.py"
        )
        content = router_path.read_text(encoding="utf-8")

        assert "LGPD" in content, "Endpoint deve mencionar LGPD"
        assert "Art. 18" in content or "Art 18" in content, (
            "Endpoint deve mencionar Art. 18 da LGPD"
        )
