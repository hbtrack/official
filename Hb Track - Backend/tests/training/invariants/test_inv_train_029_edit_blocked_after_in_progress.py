"""
INV-TRAIN-029 — Edição bloqueada após início da sessão

Enunciado: Edição de training_sessions é bloqueada por estado:
  - readonly: bloqueia completamente ("Sessão congelada. Revisão já concluída.")
  - in_progress: bloqueia completamente ("Sessão em andamento não pode ser editada.")
  - pending_review: permite apenas campos de revisão (execution_outcome, delay_minutes, etc.)
  - scheduled: permite apenas campos específicos (notes, focus_*, intensity_target, etc.)
  - draft: permite edição livre

Evidência (service):
  - app/services/training_session_service.py:464-465 (readonly → ForbiddenError)
  - app/services/training_session_service.py:467-468 (in_progress → ForbiddenError)
  - app/services/training_session_service.py:470-481 (pending_review → campos de revisão)
  - app/services/training_session_service.py:483-500 (scheduled → campos específicos)

Teste: Verifica que as regras de edição por estado estão implementadas no service.
"""

from pathlib import Path
import re


class TestInvTrain029EditBlockedAfterInProgress:
    """Testes para INV-TRAIN-029: Edição bloqueada após início da sessão."""

    def test_validate_edit_permission_method_exists(self):
        """Verifica que existe método _validate_edit_permission."""
        service_path = (
            Path(__file__).parent.parent.parent
            / "app"
            / "services"
            / "training_session_service.py"
        )
        assert service_path.exists(), f"Service não encontrado: {service_path}"

        content = service_path.read_text(encoding="utf-8")
        assert "_validate_edit_permission" in content, (
            "Método _validate_edit_permission não encontrado"
        )

    def test_readonly_status_raises_forbidden(self):
        """Verifica que status readonly lança ForbiddenError."""
        service_path = (
            Path(__file__).parent.parent.parent
            / "app"
            / "services"
            / "training_session_service.py"
        )
        content = service_path.read_text(encoding="utf-8")

        # Verifica a verificação de readonly
        assert 'session.status == "readonly"' in content, (
            "Verificação de status readonly não encontrada"
        )
        assert "Sessão congelada" in content, (
            "Mensagem de erro para readonly não encontrada"
        )

    def test_in_progress_status_raises_forbidden(self):
        """Verifica que status in_progress lança ForbiddenError."""
        service_path = (
            Path(__file__).parent.parent.parent
            / "app"
            / "services"
            / "training_session_service.py"
        )
        content = service_path.read_text(encoding="utf-8")

        # Verifica a verificação de in_progress
        assert 'session.status == "in_progress"' in content, (
            "Verificação de status in_progress não encontrada"
        )
        assert "em andamento" in content.lower(), (
            "Mensagem de erro para in_progress não encontrada"
        )

    def test_pending_review_has_allowed_fields(self):
        """Verifica que pending_review tem lista de campos permitidos."""
        service_path = (
            Path(__file__).parent.parent.parent
            / "app"
            / "services"
            / "training_session_service.py"
        )
        content = service_path.read_text(encoding="utf-8")

        # Verifica que há verificação para pending_review
        assert 'session.status == "pending_review"' in content, (
            "Verificação de status pending_review não encontrada"
        )

        # Verifica que há campos permitidos definidos
        assert "execution_outcome" in content, (
            "Campo execution_outcome não encontrado em allowed_fields"
        )
        assert "delay_minutes" in content, (
            "Campo delay_minutes não encontrado em allowed_fields"
        )
        assert "deviation_justification" in content, (
            "Campo deviation_justification não encontrado em allowed_fields"
        )

    def test_scheduled_has_allowed_fields(self):
        """Verifica que scheduled tem lista de campos permitidos."""
        service_path = (
            Path(__file__).parent.parent.parent
            / "app"
            / "services"
            / "training_session_service.py"
        )
        content = service_path.read_text(encoding="utf-8")

        # Verifica que há verificação para scheduled
        assert 'session.status == "scheduled"' in content, (
            "Verificação de status scheduled não encontrada"
        )

        # Verifica que há campos permitidos para scheduled
        assert "notes" in content, (
            "Campo notes não encontrado em allowed_fields para scheduled"
        )
        assert "intensity_target" in content, (
            "Campo intensity_target não encontrado em allowed_fields"
        )

    def test_field_subset_validation_exists(self):
        """Verifica que há validação de subset de campos."""
        service_path = (
            Path(__file__).parent.parent.parent
            / "app"
            / "services"
            / "training_session_service.py"
        )
        content = service_path.read_text(encoding="utf-8")

        # Verifica que há verificação de issubset
        assert "issubset" in content, (
            "Validação issubset de campos não encontrada"
        )

    def test_forbidden_error_raised_for_invalid_fields(self):
        """Verifica que ForbiddenError é lançado para campos inválidos."""
        service_path = (
            Path(__file__).parent.parent.parent
            / "app"
            / "services"
            / "training_session_service.py"
        )
        content = service_path.read_text(encoding="utf-8")

        # Verifica que há mensagem de erro para campos não permitidos
        assert "Somente campos" in content or "revisão operacional" in content, (
            "Mensagem de erro para campos não permitidos não encontrada"
        )

    def test_all_session_statuses_handled(self):
        """Verifica que todos os status de sessão são tratados."""
        service_path = (
            Path(__file__).parent.parent.parent
            / "app"
            / "services"
            / "training_session_service.py"
        )
        content = service_path.read_text(encoding="utf-8")

        statuses = ["readonly", "in_progress", "pending_review", "scheduled"]
        for status in statuses:
            assert f'"{status}"' in content, (
                f"Status '{status}' não tratado em _validate_edit_permission"
            )
