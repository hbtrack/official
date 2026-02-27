"""
INV-TRAIN-077 — Feedback imediato pós-treino conversacional.

Classe C1 (Unit, sem IO, sem DB).

Evidence canônica:
  - app/services/ai_coach_service.py :: generate_post_training_feedback
  - app/services/ai_coach_service.py :: PostTrainingFeedback
  - app/services/ai_coach_service.py :: FeedbackNotGenerated
  - AR_164
"""

import pytest

from app.services.ai_coach_service import (
    AICoachService,
    FeedbackNotGenerated,
    PostTrainingFeedback,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def service() -> AICoachService:
    return AICoachService()


# ---------------------------------------------------------------------------
# Casos de teste
# ---------------------------------------------------------------------------


class TestInvTrain077ImmediateVirtualCoachFeedback:
    """INV-TRAIN-077: ao concluir pós-treino conversacional, DEVE gerar feedback."""

    # -----------------------------------------------------------------------
    # Caso 1 — Concluído com RPE alto → gera PostTrainingFeedback
    # -----------------------------------------------------------------------
    def test_completed_high_rpe_generates_feedback(self, service: AICoachService) -> None:
        """Caso 1: conversation_completed=True, rpe=9 → PostTrainingFeedback."""
        result = service.generate_post_training_feedback(
            conversation_completed=True,
            session_rpe=9,
        )
        assert isinstance(result, PostTrainingFeedback), (
            f"Esperado PostTrainingFeedback, obtido {type(result).__name__}"
        )

    # -----------------------------------------------------------------------
    # Caso 2 — Concluído com RPE médio → gera PostTrainingFeedback
    # -----------------------------------------------------------------------
    def test_completed_medium_rpe_generates_feedback(self, service: AICoachService) -> None:
        """Caso 2: conversation_completed=True, rpe=6 → PostTrainingFeedback."""
        result = service.generate_post_training_feedback(
            conversation_completed=True,
            session_rpe=6,
        )
        assert isinstance(result, PostTrainingFeedback), (
            f"Esperado PostTrainingFeedback, obtido {type(result).__name__}"
        )

    # -----------------------------------------------------------------------
    # Caso 3 — Concluído sem RPE → gera PostTrainingFeedback
    # -----------------------------------------------------------------------
    def test_completed_no_rpe_generates_feedback(self, service: AICoachService) -> None:
        """Caso 3: conversation_completed=True, rpe=None → PostTrainingFeedback."""
        result = service.generate_post_training_feedback(
            conversation_completed=True,
            session_rpe=None,
        )
        assert isinstance(result, PostTrainingFeedback), (
            f"Esperado PostTrainingFeedback, obtido {type(result).__name__}"
        )

    # -----------------------------------------------------------------------
    # Caso 4 — NÃO concluído → FeedbackNotGenerated (INV-077 negativo)
    # -----------------------------------------------------------------------
    def test_not_completed_returns_not_generated(self, service: AICoachService) -> None:
        """Caso 4: conversation_completed=False → FeedbackNotGenerated (feedback NÃO gerado)."""
        result = service.generate_post_training_feedback(
            conversation_completed=False,
            session_rpe=8,
        )
        assert isinstance(result, FeedbackNotGenerated), (
            f"INV-077 violado: feedback gerado sem pós-treino concluído. "
            f"Obtido {type(result).__name__}"
        )

    # -----------------------------------------------------------------------
    # Caso 5 — Anti-falso-positivo: tipo exato (não subclasse ambígua)
    # -----------------------------------------------------------------------
    def test_anti_false_positive_type_check(self, service: AICoachService) -> None:
        """Caso 5: resultado concluído NÃO deve ser FeedbackNotGenerated."""
        result = service.generate_post_training_feedback(
            conversation_completed=True,
            session_rpe=7,
        )
        assert not isinstance(result, FeedbackNotGenerated), (
            "Anti-falso-positivo falhou: PostTrainingFeedback não deve ser FeedbackNotGenerated"
        )

    # -----------------------------------------------------------------------
    # Caso 6 — Source invariante: DEVE ser "virtual_coach"
    # -----------------------------------------------------------------------
    def test_source_is_virtual_coach(self, service: AICoachService) -> None:
        """Caso 6: INV-077 — source DEVE ser 'virtual_coach'."""
        result = service.generate_post_training_feedback(
            conversation_completed=True,
            session_rpe=5,
        )
        assert isinstance(result, PostTrainingFeedback)
        assert result.source == "virtual_coach", (
            f"INV-077 violado: source='{result.source}', esperado 'virtual_coach'"
        )

    # -----------------------------------------------------------------------
    # Caso 7 — recognition e guidance não vazios
    # -----------------------------------------------------------------------
    def test_recognition_and_guidance_non_empty(self, service: AICoachService) -> None:
        """Caso 7: recognition e guidance DEVEM ser strings não-vazias."""
        result = service.generate_post_training_feedback(
            conversation_completed=True,
            session_rpe=None,
        )
        assert isinstance(result, PostTrainingFeedback)
        assert len(result.recognition) > 0, "recognition está vazio"
        assert len(result.guidance) > 0, "guidance está vazio"
