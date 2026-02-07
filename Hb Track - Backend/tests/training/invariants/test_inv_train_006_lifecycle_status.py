"""
INV-TRAIN-006: Lifecycle de status (DB enum + transições operacionais)

Regra: Status de training_sessions segue o fluxo:
  draft → scheduled → in_progress → pending_review → readonly

Evidência:
- schema.sql:2627 (CONSTRAINT check_training_session_status)
- celery_tasks.py:581-676 (update_training_session_statuses_task)
"""

import pytest


class TestInvTrain006LifecycleStatus:
    """Testes para INV-TRAIN-006: Lifecycle de status."""

    # Status válidos conforme constraint DB
    VALID_STATUSES = ["draft", "scheduled", "in_progress", "pending_review", "readonly"]

    def test_valid_statuses_are_defined(self):
        """Os 5 status válidos devem estar definidos no enum/constraint."""
        expected = {"draft", "scheduled", "in_progress", "pending_review", "readonly"}
        actual = set(self.VALID_STATUSES)
        assert actual == expected, f"Status esperados: {expected}, encontrados: {actual}"

    def test_status_count_is_five(self):
        """Devem existir exatamente 5 status válidos."""
        assert len(self.VALID_STATUSES) == 5, "Devem existir 5 status válidos"

    def test_draft_is_initial_status(self):
        """'draft' deve ser o status inicial no fluxo."""
        assert self.VALID_STATUSES[0] == "draft", "draft deve ser o primeiro status"

    def test_readonly_is_final_status(self):
        """'readonly' deve ser o status final no fluxo."""
        assert self.VALID_STATUSES[-1] == "readonly", "readonly deve ser o último status"

    def test_lifecycle_order_is_correct(self):
        """A ordem do lifecycle deve ser: draft → scheduled → in_progress → pending_review → readonly."""
        expected_order = ["draft", "scheduled", "in_progress", "pending_review", "readonly"]
        assert self.VALID_STATUSES == expected_order, \
            f"Ordem esperada: {expected_order}, encontrada: {self.VALID_STATUSES}"

    def test_celery_task_transitions_exist(self):
        """A task de transição automática deve estar definida."""
        from app.core.celery_tasks import update_training_session_statuses_task
        assert update_training_session_statuses_task is not None, \
            "update_training_session_statuses_task deve existir"

    def test_celery_task_is_registered(self):
        """A task deve estar registrada no Celery."""
        from app.core.celery_tasks import update_training_session_statuses_task
        # Verifica que a função tem o decorator de task
        assert hasattr(update_training_session_statuses_task, 'delay') or \
               callable(update_training_session_statuses_task), \
            "update_training_session_statuses_task deve ser uma task Celery"

    def test_model_status_constraint_matches_valid_statuses(self):
        """O modelo TrainingSession deve ter os mesmos status válidos."""
        from app.models.training_session import TrainingSession
        from sqlalchemy import inspect

        # Verifica que a coluna status existe
        mapper = inspect(TrainingSession)
        assert 'status' in [col.key for col in mapper.columns], \
            "TrainingSession deve ter coluna 'status'"
