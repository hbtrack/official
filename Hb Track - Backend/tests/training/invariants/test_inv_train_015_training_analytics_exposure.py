"""
INV-TRAIN-015 — Training Analytics (FR-012) exposto e ancorado em router/service

Enunciado: O módulo Training Analytics expõe endpoints via router e ancora em services,
incluindo threshold dinâmico via team.alert_threshold_multiplier.

Evidência (router/service):
  - Router: app/api/v1/routers/training_analytics.py:30-204 (4 endpoints)
  - Services: app/services/training_analytics_service.py:29-38
  - Services: app/services/prevention_effectiveness_service.py:17-20
  - Threshold dinâmico: app/services/training_analytics_service.py:190-191

Teste: Verifica que router, services e threshold dinâmico estão implementados.
"""

from pathlib import Path
import re


class TestInvTrain015TrainingAnalyticsExposure:
    """Testes para INV-TRAIN-015: Training Analytics exposto e ancorado."""

    def test_training_analytics_router_exists(self):
        """Verifica que o router training_analytics.py existe."""
        router_path = (
            Path(__file__).parent.parent.parent.parent
            / "app"
            / "api"
            / "v1"
            / "routers"
            / "training_analytics.py"
        )
        assert router_path.exists(), f"Router não encontrado: {router_path}"

    def test_router_has_team_summary_endpoint(self):
        """Verifica endpoint GET /team/{team_id}/summary."""
        router_path = (
            Path(__file__).parent.parent.parent.parent
            / "app"
            / "api"
            / "v1"
            / "routers"
            / "training_analytics.py"
        )
        content = router_path.read_text(encoding="utf-8")

        assert "/team/{team_id}/summary" in content, (
            "Endpoint /team/{team_id}/summary não encontrado"
        )
        assert "get_team_summary" in content, (
            "Função get_team_summary não encontrada"
        )

    def test_router_has_weekly_load_endpoint(self):
        """Verifica endpoint GET /team/{team_id}/weekly-load."""
        router_path = (
            Path(__file__).parent.parent.parent.parent
            / "app"
            / "api"
            / "v1"
            / "routers"
            / "training_analytics.py"
        )
        content = router_path.read_text(encoding="utf-8")

        assert "/team/{team_id}/weekly-load" in content, (
            "Endpoint /team/{team_id}/weekly-load não encontrado"
        )
        assert "get_weekly_load" in content, (
            "Função get_weekly_load não encontrada"
        )

    def test_router_has_deviation_analysis_endpoint(self):
        """Verifica endpoint GET /team/{team_id}/deviation-analysis."""
        router_path = (
            Path(__file__).parent.parent.parent.parent
            / "app"
            / "api"
            / "v1"
            / "routers"
            / "training_analytics.py"
        )
        content = router_path.read_text(encoding="utf-8")

        assert "/team/{team_id}/deviation-analysis" in content, (
            "Endpoint /team/{team_id}/deviation-analysis não encontrado"
        )
        assert "get_deviation_analysis" in content, (
            "Função get_deviation_analysis não encontrada"
        )

    def test_router_has_prevention_effectiveness_endpoint(self):
        """Verifica endpoint GET /team/{team_id}/prevention-effectiveness."""
        router_path = (
            Path(__file__).parent.parent.parent.parent
            / "app"
            / "api"
            / "v1"
            / "routers"
            / "training_analytics.py"
        )
        content = router_path.read_text(encoding="utf-8")

        assert "/team/{team_id}/prevention-effectiveness" in content, (
            "Endpoint /team/{team_id}/prevention-effectiveness não encontrado"
        )
        assert "get_prevention_effectiveness" in content, (
            "Função get_prevention_effectiveness não encontrada"
        )

    def test_training_analytics_service_exists(self):
        """Verifica que TrainingAnalyticsService existe."""
        service_path = (
            Path(__file__).parent.parent.parent.parent
            / "app"
            / "services"
            / "training_analytics_service.py"
        )
        assert service_path.exists(), f"Service não encontrado: {service_path}"

        content = service_path.read_text(encoding="utf-8")
        assert "class TrainingAnalyticsService" in content, (
            "Classe TrainingAnalyticsService não encontrada"
        )

    def test_prevention_effectiveness_service_exists(self):
        """Verifica que PreventionEffectivenessService existe."""
        service_path = (
            Path(__file__).parent.parent.parent.parent
            / "app"
            / "services"
            / "prevention_effectiveness_service.py"
        )
        assert service_path.exists(), f"Service não encontrado: {service_path}"

        content = service_path.read_text(encoding="utf-8")
        assert "class PreventionEffectivenessService" in content, (
            "Classe PreventionEffectivenessService não encontrada"
        )

    def test_services_imported_in_router(self):
        """Verifica que os services são importados no router."""
        router_path = (
            Path(__file__).parent.parent.parent.parent
            / "app"
            / "api"
            / "v1"
            / "routers"
            / "training_analytics.py"
        )
        content = router_path.read_text(encoding="utf-8")

        assert "from app.services.training_analytics_service import" in content, (
            "TrainingAnalyticsService não importado no router"
        )
        assert "from app.services.prevention_effectiveness_service import" in content, (
            "PreventionEffectivenessService não importado no router"
        )

    def test_dynamic_threshold_uses_team_multiplier(self):
        """Verifica que threshold dinâmico usa team.alert_threshold_multiplier."""
        service_path = (
            Path(__file__).parent.parent.parent.parent
            / "app"
            / "services"
            / "training_analytics_service.py"
        )
        content = service_path.read_text(encoding="utf-8")

        # Busca uso do threshold_multiplier do team
        assert "alert_threshold_multiplier" in content, (
            "Referência a alert_threshold_multiplier não encontrada no service"
        )

        # Verifica que é usado no contexto do team
        match = re.search(r"team\.alert_threshold_multiplier", content)
        assert match, (
            "Uso de team.alert_threshold_multiplier não encontrado"
        )

    def test_router_requires_authentication(self):
        """Verifica que os endpoints requerem autenticação."""
        router_path = (
            Path(__file__).parent.parent.parent.parent
            / "app"
            / "api"
            / "v1"
            / "routers"
            / "training_analytics.py"
        )
        content = router_path.read_text(encoding="utf-8")

        # Verifica uso de permission_dep com roles
        assert "permission_dep" in content, (
            "permission_dep não encontrado no router"
        )
        assert 'roles=["dirigente","coordenador","treinador"]' in content, (
            "Roles de permissão não definidas corretamente"
        )
