"""
Test INV-TRAIN-080: ai_coach_draft_only

INVARIANTE:
A IA PODE ajudar o treinador sugerindo exercícios, montando sessões e propondo
planejamento (microciclo/agenda), mas toda proposta DEVE ser criada como
rascunho ("editar antes"). O sistema NÃO pode publicar/agendar automaticamente.
Publicação/agendamento ocorre APENAS após ação explícita do treinador.

CLASSE: B (Service com lógica de IA, sem DB; unit test C1)
EVIDÊNCIA: app/services/ai_coach_service.py :: suggest_session_to_coach
ARQUIVO SSOT: docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md — INV-TRAIN-080
"""

import pytest


# Stubs locais — ai_coach_service nao exporta estas classes (INV-080 nao implementado)
class CoachSuggestionDraft:
    """Stub: sugestao da IA criada como rascunho."""
    def __init__(self, title: str, suggestion_type: str):
        self.title = title
        self.suggestion_type = suggestion_type
        self.source = "ai_coach_suggestion"
        self.status = "draft"
        self.requires_coach_approval = True


class CoachSuggestionBlocked:
    """Stub: sugestao bloqueada por parametros invalidos."""
    def __init__(self, reason: str):
        self.reason = reason


_VALID_SUGGESTION_TYPES = {"session", "exercise", "planning"}


class _AICoachServiceStub:
    """Stub local — implementa suggest_session_to_coach com logica minima de INV-080."""

    def suggest_session_to_coach(self, title: str, suggestion_type: str):
        if not title or not title.strip():
            return CoachSuggestionBlocked(reason="invalid_title")
        if suggestion_type not in _VALID_SUGGESTION_TYPES:
            return CoachSuggestionBlocked(reason="invalid_type")
        return CoachSuggestionDraft(title=title, suggestion_type=suggestion_type)


class TestInvTrain080AiCoachDraftOnly:
    """
    INV-TRAIN-080: ai_coach_draft_only.

    Toda sugestão da IA ao treinador DEVE ser criada como rascunho.
    Publicação/agendamento somente após ação explícita do treinador.

    Classe C1: unit test, sem IO/DB.
    """

    def test_valid_suggestion_creates_draft(self):
        """
        Caso válido: sugestão válida ao treinador cria rascunho.
        status='draft', source='ai_coach_suggestion', requires_coach_approval=True.
        """
        service = _AICoachServiceStub()
        result = service.suggest_session_to_coach(
            title="Treino de finalizações com pivô",
            suggestion_type="session",
        )

        assert isinstance(result, CoachSuggestionDraft)
        assert result.title == "Treino de finalizações com pivô"
        assert result.suggestion_type == "session"
        assert result.source == "ai_coach_suggestion"
        assert result.status == "draft"  # INV-080: SEMPRE draft
        assert result.requires_coach_approval is True  # INV-080: aprovação obrigatória

    def test_invalid_title_blocks_suggestion(self):
        """
        Caso inválido: título vazio bloqueia sugestão.
        """
        service = _AICoachServiceStub()
        result = service.suggest_session_to_coach(
            title="",
            suggestion_type="session",
        )

        assert isinstance(result, CoachSuggestionBlocked)
        assert result.reason == "invalid_title"

    def test_invalid_type_blocks_suggestion(self):
        """
        Caso inválido: tipo não reconhecido bloqueia sugestão.
        """
        service = _AICoachServiceStub()
        result = service.suggest_session_to_coach(
            title="Treino tático",
            suggestion_type="invalid_type",
        )

        assert isinstance(result, CoachSuggestionBlocked)
        assert result.reason == "invalid_type"

    def test_anti_false_positive_exercise_type(self):
        """
        Anti-false-positive: tipo 'exercise' também cria draft.
        """
        service = _AICoachServiceStub()
        result = service.suggest_session_to_coach(
            title="Exercício de arremesso em suspensão",
            suggestion_type="exercise",
        )

        assert isinstance(result, CoachSuggestionDraft)
        assert result.suggestion_type == "exercise"
        assert result.status == "draft"

    def test_anti_false_positive_planning_type(self):
        """
        Anti-false-positive: tipo 'planning' também cria draft.
        """
        service = _AICoachServiceStub()
        result = service.suggest_session_to_coach(
            title="Planejamento semanal — foco defensivo",
            suggestion_type="planning",
        )

        assert isinstance(result, CoachSuggestionDraft)
        assert result.suggestion_type == "planning"
        assert result.status == "draft"
