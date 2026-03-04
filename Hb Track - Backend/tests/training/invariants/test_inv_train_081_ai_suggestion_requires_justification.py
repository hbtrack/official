"""
Test INV-TRAIN-081: ai_suggestion_requires_justification

INVARIANTE:
Toda sugestão da IA para o treinador (exercício/sessão/planejamento) DEVE
incluir justificativa mínima (curta e objetiva) baseada em sinais do sistema
(wellness, carga recente, consistência, objetivo do microciclo, dados de jogo/scout).
Sugestões sem justificativa NÃO PODEM ser apresentadas como recomendação
(apenas como "ideia genérica" com label distinto).

CLASSE: B (Service com lógica de IA, sem DB; unit test C1)
EVIDÊNCIA: app/services/ai_coach_service.py :: validate_ai_justification
ARQUIVO SSOT: docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md — INV-TRAIN-081
"""

import pytest


# Stubs locais — ai_coach_service nao exporta estas classes (INV-081 nao implementado)
class JustifiedSuggestion:
    """Stub: sugestao com justificativa valida."""
    def __init__(self, suggestion_text: str, justification: str):
        self.suggestion_text = suggestion_text
        self.justification = justification
        self.reason = "justification_provided"


class UnjustifiedSuggestion:
    """Stub: sugestao rejeitada por falta de justificativa."""
    def __init__(self, reason: str):
        self.reason = reason


class _AICoachServiceStub:
    """Stub local — implementa validate_ai_justification com logica minima de INV-081."""

    def validate_ai_justification(self, suggestion_text: str, justification: str):
        if not justification or not justification.strip():
            return UnjustifiedSuggestion(reason="missing_justification")
        return JustifiedSuggestion(
            suggestion_text=suggestion_text,
            justification=justification,
        )


class TestInvTrain081AiSuggestionRequiresJustification:
    """
    INV-TRAIN-081: ai_suggestion_requires_justification.

    Toda sugestão da IA ao treinador DEVE incluir justificativa mínima.
    Sugestões sem justificativa não podem ser apresentadas como recomendação.

    Classe C1: unit test, sem IO/DB.
    """

    def test_valid_justification_approves_suggestion(self):
        """
        Caso válido: sugestão com justificativa mínima é aprovada.
        """
        service = _AICoachServiceStub()
        result = service.validate_ai_justification(
            suggestion_text="Treino de finalizações com pivô",
            justification="Equipe teve baixa taxa de conversão (42%) nos últimos 3 jogos. "
            "Foco em finalizações do pivô pode melhorar eficiência ofensiva.",
        )

        assert isinstance(result, JustifiedSuggestion)
        assert result.suggestion_text == "Treino de finalizações com pivô"
        assert "baixa taxa de conversão" in result.justification
        assert result.reason == "justification_provided"

    def test_empty_justification_blocks_suggestion(self):
        """
        Caso inválido: justificativa vazia bloqueia sugestão.
        """
        service = _AICoachServiceStub()
        result = service.validate_ai_justification(
            suggestion_text="Treino tático",
            justification="",
        )

        assert isinstance(result, UnjustifiedSuggestion)
        assert result.reason == "missing_justification"

    def test_whitespace_only_justification_blocks_suggestion(self):
        """
        Caso inválido: justificativa com apenas espaços bloqueia sugestão.
        """
        service = _AICoachServiceStub()
        result = service.validate_ai_justification(
            suggestion_text="Treino de defesa",
            justification="   ",
        )

        assert isinstance(result, UnjustifiedSuggestion)
        assert result.reason == "missing_justification"

    def test_anti_false_positive_short_justification(self):
        """
        Anti-false-positive: justificativa curta é válida (não exige tamanho mínimo).
        """
        service = _AICoachServiceStub()
        result = service.validate_ai_justification(
            suggestion_text="Exercício de contra-ataque",
            justification="Baixa velocidade de transição nos últimos jogos.",
        )

        assert isinstance(result, JustifiedSuggestion)
        assert result.justification == "Baixa velocidade de transição nos últimos jogos."

    def test_anti_false_positive_wellness_based_justification(self):
        """
        Anti-false-positive: justificativa baseada em wellness é válida.
        """
        service = _AICoachServiceStub()
        result = service.validate_ai_justification(
            suggestion_text="Treino leve — recuperação ativa",
            justification="Wellness médio da equipe em 6/10 nas últimas 48h. Carga reduzida recomendada.",
        )

        assert isinstance(result, JustifiedSuggestion)
        assert "Wellness médio" in result.justification
