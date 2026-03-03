"""
INV-TRAIN-024 — WebSocket broadcast e NotificationService para alerts/badges

Enunciado: Alertas críticos e badges conquistados geram notificações
via NotificationService e broadcast WebSocket para usuários relevantes.

Evidência (services):
  - app/services/training_alerts_service.py:364-413 (alertas críticos → NotificationService + broadcast)
  - app/services/wellness_gamification_service.py:328-387 (badges → NotificationService + broadcast)

Teste: Verifica que os métodos de notificação existem e usam WebSocket broadcast.
"""

from pathlib import Path
import re


class TestInvTrain024WebsocketBroadcast:
    """Testes para INV-TRAIN-024: WebSocket broadcast para alerts/badges."""

    def test_training_alerts_service_has_notification_method(self):
        """Verifica que training_alerts_service tem método de notificação."""
        service_path = (
            Path(__file__).parent.parent.parent
            / "app"
            / "services"
            / "training_alerts_service.py"
        )
        assert service_path.exists(), f"Service não encontrado: {service_path}"

        content = service_path.read_text(encoding="utf-8")
        assert "_send_critical_notification" in content, (
            "Método _send_critical_notification não encontrado"
        )

    def test_alerts_service_uses_notification_service(self):
        """Verifica que alertas usam NotificationService."""
        service_path = (
            Path(__file__).parent.parent.parent
            / "app"
            / "services"
            / "training_alerts_service.py"
        )
        content = service_path.read_text(encoding="utf-8")

        assert "notification_service" in content, (
            "Referência a notification_service não encontrada"
        )
        assert "notification_service.create" in content, (
            "Chamada notification_service.create não encontrada"
        )

    def test_alerts_service_broadcasts_to_user(self):
        """Verifica que alertas fazem broadcast via WebSocket."""
        service_path = (
            Path(__file__).parent.parent.parent
            / "app"
            / "services"
            / "training_alerts_service.py"
        )
        content = service_path.read_text(encoding="utf-8")

        assert "broadcast_to_user" in content, (
            "Chamada broadcast_to_user não encontrada em training_alerts_service"
        )

    def test_gamification_service_has_notification_method(self):
        """Verifica que wellness_gamification_service tem método de notificação."""
        service_path = (
            Path(__file__).parent.parent.parent
            / "app"
            / "services"
            / "wellness_gamification_service.py"
        )
        assert service_path.exists(), f"Service não encontrado: {service_path}"

        content = service_path.read_text(encoding="utf-8")
        assert "_create_badge_notification" in content, (
            "Método _create_badge_notification não encontrado"
        )

    def test_gamification_service_uses_notification_service(self):
        """Verifica que badges usam NotificationService."""
        service_path = (
            Path(__file__).parent.parent.parent
            / "app"
            / "services"
            / "wellness_gamification_service.py"
        )
        content = service_path.read_text(encoding="utf-8")

        assert "notification_service" in content, (
            "Referência a notification_service não encontrada"
        )
        assert "notification_service.create" in content, (
            "Chamada notification_service.create não encontrada"
        )

    def test_gamification_service_broadcasts_to_user(self):
        """Verifica que badges fazem broadcast via WebSocket."""
        service_path = (
            Path(__file__).parent.parent.parent
            / "app"
            / "services"
            / "wellness_gamification_service.py"
        )
        content = service_path.read_text(encoding="utf-8")

        assert "broadcast_to_user" in content, (
            "Chamada broadcast_to_user não encontrada em wellness_gamification_service"
        )

    def test_alerts_notification_includes_metadata(self):
        """Verifica que notificação de alertas inclui metadata relevante."""
        service_path = (
            Path(__file__).parent.parent.parent
            / "app"
            / "services"
            / "training_alerts_service.py"
        )
        content = service_path.read_text(encoding="utf-8")

        # Verifica que metadata inclui campos importantes
        assert "alert_id" in content, "Metadata deve incluir alert_id"
        assert "alert_type" in content, "Metadata deve incluir alert_type"
        assert "severity" in content, "Metadata deve incluir severity"

    def test_badges_notification_includes_metadata(self):
        """Verifica que notificação de badges inclui metadata relevante."""
        service_path = (
            Path(__file__).parent.parent.parent
            / "app"
            / "services"
            / "wellness_gamification_service.py"
        )
        content = service_path.read_text(encoding="utf-8")

        # Verifica que metadata inclui campos importantes
        assert "badge_type" in content, "Metadata deve incluir badge_type"
        assert "month_reference" in content, "Metadata deve incluir month_reference"
        assert "response_rate" in content, "Metadata deve incluir response_rate"

    def test_broadcast_to_user_pattern_consistent(self):
        """Verifica que ambos os services usam broadcast_to_user (padrão unificado)."""
        alerts_path = (
            Path(__file__).parent.parent.parent
            / "app"
            / "services"
            / "training_alerts_service.py"
        )
        gamification_path = (
            Path(__file__).parent.parent.parent
            / "app"
            / "services"
            / "wellness_gamification_service.py"
        )
        alerts_content = alerts_path.read_text(encoding="utf-8")
        gamification_content = gamification_path.read_text(encoding="utf-8")

        # Ambos devem usar o mesmo padrão de broadcast
        assert "broadcast_to_user" in alerts_content, (
            "training_alerts_service deve usar broadcast_to_user"
        )
        assert "broadcast_to_user" in gamification_content, (
            "wellness_gamification_service deve usar broadcast_to_user"
        )

    def test_websocket_manager_imported_in_alerts(self):
        """Verifica que training_alerts_service importa websocket_manager ou ConnectionManager."""
        service_path = (
            Path(__file__).parent.parent.parent
            / "app"
            / "services"
            / "training_alerts_service.py"
        )
        content = service_path.read_text(encoding="utf-8")

        # Deve ter referência ao websocket manager
        has_ws = (
            "websocket" in content.lower()
            or "ConnectionManager" in content
            or "ws_manager" in content
            or "manager" in content.lower()
        )
        assert has_ws, "training_alerts_service deve referenciar WebSocket manager"
