"""
INV-TRAIN-072: ai_suggestion_not_order
Classe C1 — Unit (sem IO, sem DB)
Evidência: app/services/ai_coach_service.py — check_suggestion_tone(), check_auto_publish()
Regra:
  - A IA PODE enviar mensagens ao atleta, mas SEMPRE como sugestão/apoio (tom
    não-imperativo). Mensagens com tom imperativo são BLOQUEADAS.
  - A IA NÃO PODE criar/publicar treino oficial automaticamente.
    Toda publicação de treino gerado pela IA requer aprovação do treinador.
"""
import pytest

from app.services.ai_coach_service import (
    AICoachService,
    SuggestionApproved,
    SuggestionBlocked,
    PublishApproved,
    PublishBlocked,
)


class TestInvTrain072AiSuggestionNotOrder:
    """
    INV-TRAIN-072 — ai_suggestion_not_order
    tone guard: check_suggestion_tone()
    publish guard: check_auto_publish()
    Evidência: app/services/ai_coach_service.py
    """

    # -----------------------------------------------------------------------
    # Tone guard — mensagens imperativas devem ser bloqueadas
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_imperative_tone_blocked(self):
        """
        INV-072 CASO 1: mensagem com marcador imperativo →
        check_suggestion_tone() deve retornar SuggestionBlocked.
        """
        svc = AICoachService()
        imperative_messages = [
            "Você deve completar os exercícios hoje.",
            "Faça 3 séries de 10 repetições agora.",
            "Execute o treino conforme planejado.",
            "É obrigatório comparecer ao treino amanhã.",
        ]
        for msg in imperative_messages:
            result = svc.check_suggestion_tone(msg)
            assert isinstance(result, SuggestionBlocked), (
                f"INV-072: mensagem imperativa deve ser bloqueada: '{msg}'"
            )
            assert result.original_message == msg
            assert len(result.markers_found) > 0, (
                f"INV-072: markers_found deve indicar qual marcador imperativo foi detectado"
            )

    @pytest.mark.asyncio
    async def test_suggestion_tone_approved(self):
        """
        INV-072 CASO 2: mensagem com tom de sugestão/apoio →
        check_suggestion_tone() deve retornar SuggestionApproved.
        """
        svc = AICoachService()
        suggestion_messages = [
            "Que tal tentar 3 séries de 10 repetições?",
            "Talvez valha a pena descansar entre os exercícios.",
            "Você pode experimentar incluir alongamento após o treino.",
            "Uma boa hidratação ajuda na recuperação.",
        ]
        for msg in suggestion_messages:
            result = svc.check_suggestion_tone(msg)
            assert isinstance(result, SuggestionApproved), (
                f"INV-072: tom de sugestão deve ser aprovado: '{msg}'"
            )
            assert result.message == msg

    @pytest.mark.asyncio
    async def test_anti_false_positive_suggestion_is_not_blocked(self):
        """
        INV-072 CASO 3 (anti-false-positive): SuggestionApproved NÃO é SuggestionBlocked.
        Tipos distintos — isinstance() deve distinguir claramente.
        """
        svc = AICoachService()
        result_ok = svc.check_suggestion_tone("Que tal tentar se alongar?")
        result_blocked = svc.check_suggestion_tone("Você deve se alongar agora.")

        assert isinstance(result_ok, SuggestionApproved), (
            "INV-072: sugestão não pode ser classificada como bloqueada"
        )
        assert isinstance(result_blocked, SuggestionBlocked), (
            "INV-072: imperativo não pode ser classificado como aprovado"
        )
        assert not isinstance(result_ok, SuggestionBlocked), (
            "INV-072: SuggestionApproved e SuggestionBlocked são tipos distintos"
        )

    # -----------------------------------------------------------------------
    # Publish guard — IA não pode autopublicar treino
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_ai_auto_publish_blocked_without_coach_approval(self):
        """
        INV-072 CASO 4: treino gerado pela IA sem aprovação do treinador →
        check_auto_publish() deve retornar PublishBlocked.
        A IA NÃO PODE criar/publicar treino oficial automaticamente.
        """
        svc = AICoachService()
        result = svc.check_auto_publish(
            is_ai_generated=True,
            approved_by_coach=False,
        )
        assert isinstance(result, PublishBlocked), (
            "INV-072: IA não pode autopublicar treino sem aprovação do treinador"
        )
        assert result.reason == "ai_auto_publish_blocked"

    @pytest.mark.asyncio
    async def test_ai_training_approved_by_coach_can_publish(self):
        """
        INV-072 CASO 5: treino gerado pela IA COM aprovação do treinador →
        check_auto_publish() deve retornar PublishApproved.
        O treinador é a autoridade — após revisão manual, publicação é permitida.
        """
        svc = AICoachService()
        result = svc.check_auto_publish(
            is_ai_generated=True,
            approved_by_coach=True,
        )
        assert isinstance(result, PublishApproved), (
            "INV-072: treino de IA aprovado pelo treinador pode ser publicado"
        )

    @pytest.mark.asyncio
    async def test_manual_training_not_ai_can_publish(self):
        """
        INV-072 CASO 6: treino NÃO gerado pela IA → publicação livre.
        A restrição de aprovação é APENAS para treinos gerados por IA.
        """
        svc = AICoachService()
        result = svc.check_auto_publish(
            is_ai_generated=False,
            approved_by_coach=False,
        )
        assert isinstance(result, PublishApproved), (
            "INV-072: treino manual (não criado por IA) não precisa de aprovação especial"
        )
