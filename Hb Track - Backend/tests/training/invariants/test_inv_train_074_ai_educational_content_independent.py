"""
INV-TRAIN-074: ai_educational_content_independent
Classe C1 — Unit (sem IO, sem DB)
Evidência: app/services/ai_coach_service.py — get_educational_content()
Regra:
  - A IA PODE explicar regras e situações de jogo (2 minutos, superioridade
    numérica, 7m, princípios táticos) mesmo que o treino do dia não cite o tema.
  - Conteúdo educativo NÃO altera treino/agendamento; é apenas informativo.
  - EducationalResponse.affects_training DEVE ser False (invariante).
  - EducationalResponse.affects_scheduling DEVE ser False (invariante).
"""
import pytest

from app.services.ai_coach_service import (
    AICoachService,
    EducationalResponse,
    EducationalTopicNotFound,
)


class TestInvTrain074AiEducationalContentIndependent:
    """
    INV-TRAIN-074 — ai_educational_content_independent
    educational module: AICoachService.get_educational_content()
    Evidência: app/services/ai_coach_service.py
    """

    # -----------------------------------------------------------------------
    # Tópicos reconhecidos — conteúdo retornado sem afetar treino
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_educational_content_does_not_affect_training(self):
        """
        INV-074 CASO 1: tópico educativo reconhecido →
        EducationalResponse.affects_training DEVE ser False.
        EducationalResponse.affects_scheduling DEVE ser False.
        Conteúdo educativo é APENAS informativo.
        """
        svc = AICoachService()
        recognized_topics = [
            "2_minutos",
            "superioridade_numerica",
            "7_metros",
            "tatica",
            "regras",
            "goleiro",
            "pivot",
        ]
        for topic in recognized_topics:
            result = svc.get_educational_content(topic)
            assert isinstance(result, EducationalResponse), (
                f"INV-074: tópico '{topic}' deve retornar EducationalResponse"
            )
            assert result.affects_training is False, (
                f"INV-074: affects_training DEVE ser False para tópico '{topic}'. "
                "Conteúdo educativo não pode alterar treino."
            )
            assert result.affects_scheduling is False, (
                f"INV-074: affects_scheduling DEVE ser False para tópico '{topic}'. "
                "Conteúdo educativo não pode alterar agendamento."
            )

    @pytest.mark.asyncio
    async def test_educational_content_returns_non_empty_content(self):
        """
        INV-074 CASO 2: tópicos conhecidos devem retornar conteúdo não vazio.
        O módulo educativo responde perguntas reais sobre handebol.
        """
        svc = AICoachService()
        result = svc.get_educational_content("2_minutos")

        assert isinstance(result, EducationalResponse)
        assert result.content.strip() != "", (
            "INV-074: conteúdo educativo sobre '2_minutos' não pode ser vazio"
        )
        assert result.topic == "2_minutos"

    @pytest.mark.asyncio
    async def test_educational_topics_handball_specific(self):
        """
        INV-074 CASO 3: tópicos de handebol específicos (7m, superioridade, regras)
        devem ser reconhecidos e retornar EducationalResponse.
        """
        svc = AICoachService()
        specific_topics = ["7_metros", "superioridade_numerica", "regras", "arbitragem"]

        for topic in specific_topics:
            result = svc.get_educational_content(topic)
            assert isinstance(result, EducationalResponse), (
                f"INV-074: tópico de handebol '{topic}' deve ser reconhecido"
            )
            assert result.affects_training is False
            assert result.affects_scheduling is False

    # -----------------------------------------------------------------------
    # Tópico não reconhecido
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_unknown_topic_returns_not_found(self):
        """
        INV-074 CASO 4: tópico não reconhecido →
        get_educational_content() deve retornar EducationalTopicNotFound.
        O módulo não inventa conteúdo para tópicos desconhecidos.
        """
        svc = AICoachService()
        result = svc.get_educational_content("culinaria")

        assert isinstance(result, EducationalTopicNotFound), (
            "INV-074: tópico não relacionado a handebol deve retornar EducationalTopicNotFound"
        )
        assert result.requested_topic == "culinaria"

    @pytest.mark.asyncio
    async def test_empty_topic_returns_not_found(self):
        """
        INV-074 CASO 5: tópico vazio/inválido → EducationalTopicNotFound.
        """
        svc = AICoachService()
        result = svc.get_educational_content("")

        assert isinstance(result, EducationalTopicNotFound), (
            "INV-074: tópico vazio deve retornar EducationalTopicNotFound"
        )

    # -----------------------------------------------------------------------
    # Anti-false-positive: EducationalResponse vs EducationalTopicNotFound
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_anti_false_positive_types_are_distinct(self):
        """
        INV-074 CASO 6 (anti-false-positive): EducationalResponse e
        EducationalTopicNotFound são tipos distintos.
        Código downstream não pode confundir os dois.
        """
        svc = AICoachService()
        result_ok = svc.get_educational_content("tatica")
        result_not_found = svc.get_educational_content("astronomia")

        assert isinstance(result_ok, EducationalResponse), (
            "INV-074: tópico válido deve ser EducationalResponse"
        )
        assert isinstance(result_not_found, EducationalTopicNotFound), (
            "INV-074: tópico inválido deve ser EducationalTopicNotFound"
        )
        assert not isinstance(result_ok, EducationalTopicNotFound), (
            "INV-074: EducationalResponse NÃO é EducationalTopicNotFound"
        )
        # Garantir que mesmo um resultado "ok" mantém affects_training=False
        assert result_ok.affects_training is False, (
            "INV-074: affects_training SEMPRE False — invariante inquebrável"
        )
        assert result_ok.affects_scheduling is False, (
            "INV-074: affects_scheduling SEMPRE False — invariante inquebrável"
        )
