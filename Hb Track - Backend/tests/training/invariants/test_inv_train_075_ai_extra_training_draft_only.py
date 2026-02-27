"""
INV-TRAIN-075: ai_extra_training_draft_only
Classe C1 — Unit (sem IO, sem DB)
Evidência: app/services/ai_coach_service.py — AICoachService.request_extra_training()
Regra:
  - Se o atleta pedir "treino extra", a IA PODE gerar um rascunho, MAS o rascunho
    DEVE chegar ao treinador como "editar antes de aprovar".
  - O sistema NÃO PODE publicar/agendar automaticamente.
  - ExtraTrainingDraft.status DEVE ser 'draft' (invariante).
  - ExtraTrainingDraft.source DEVE ser 'ai_athlete_request' (invariante).
  - ExtraTrainingDraft.requires_coach_approval DEVE ser True (invariante).
  - Publicação só após ação explícita do treinador.
"""
import pytest

from app.services.ai_coach_service import (
    AICoachService,
    ExtraTrainingDraft,
    ExtraTrainingBlocked,
)


class TestInvTrain075AiExtraTrainingDraftOnly:
    """
    INV-TRAIN-075 — ai_extra_training_draft_only
    draft guard: AICoachService.request_extra_training()
    Evidência: app/services/ai_coach_service.py
    """

    # -----------------------------------------------------------------------
    # Caso 1: solicitação válida → sempre retorna ExtraTrainingDraft
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_extra_training_request_returns_draft(self):
        """
        INV-075 CASO 1: solicitação válida de treino extra →
        request_extra_training() DEVE retornar ExtraTrainingDraft.
        Nunca PublishApproved ou qualquer estado publicado.
        """
        svc = AICoachService()
        result = svc.request_extra_training("Treino de arremesso")

        assert isinstance(result, ExtraTrainingDraft), (
            "INV-075: solicitação válida DEVE retornar ExtraTrainingDraft"
        )

    # -----------------------------------------------------------------------
    # Caso 2: status SEMPRE 'draft' — invariante inquebrável
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_extra_training_status_always_draft(self):
        """
        INV-075 CASO 2: status do rascunho DEVE ser 'draft' — invariante.
        O sistema nunca retorna status='published', 'scheduled' ou equivalente.
        """
        svc = AICoachService()
        titles = [
            "Treino de arremesso",
            "Fortalecimento físico",
            "Trabalho tático de defesa",
            "Fundamentos de pivô",
        ]
        for title in titles:
            result = svc.request_extra_training(title)
            assert isinstance(result, ExtraTrainingDraft)
            assert result.status == "draft", (
                f"INV-075: status DEVE ser 'draft' para '{title}'. "
                f"Obtido: '{result.status}'. "
                "O sistema NÃO PODE publicar/agendar automaticamente."
            )

    # -----------------------------------------------------------------------
    # Caso 3: source SEMPRE 'ai_athlete_request' — invariante inquebrável
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_extra_training_source_always_ai_athlete_request(self):
        """
        INV-075 CASO 3: source do rascunho DEVE ser 'ai_athlete_request' — invariante.
        Rastreabilidade: o treinador sabe que o treino veio via IA a pedido do atleta.
        """
        svc = AICoachService()
        result = svc.request_extra_training("Treino de velocidade")

        assert isinstance(result, ExtraTrainingDraft)
        assert result.source == "ai_athlete_request", (
            "INV-075: source DEVE ser 'ai_athlete_request'. "
            f"Obtido: '{result.source}'."
        )

    # -----------------------------------------------------------------------
    # Caso 4: requires_coach_approval SEMPRE True — invariante inquebrável
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_extra_training_requires_coach_approval_always_true(self):
        """
        INV-075 CASO 4: requires_coach_approval DEVE ser True — invariante.
        O treinador é o gatekeeper: toda publicação exige sua ação explícita.
        """
        svc = AICoachService()
        result = svc.request_extra_training("Treino complementar de defesa")

        assert isinstance(result, ExtraTrainingDraft)
        assert result.requires_coach_approval is True, (
            "INV-075: requires_coach_approval DEVE ser True — "
            "treinador DEVE aprovar antes de publicar."
        )

    # -----------------------------------------------------------------------
    # Caso 5: título vazio/inválido → ExtraTrainingBlocked
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_empty_title_returns_blocked(self):
        """
        INV-075 CASO 5: título vazio ou apenas espaços →
        request_extra_training() DEVE retornar ExtraTrainingBlocked.
        Proteção mínima contra entradas inválidas.
        """
        svc = AICoachService()
        for bad_title in ["", "   ", None]:
            result = svc.request_extra_training(bad_title)
            assert isinstance(result, ExtraTrainingBlocked), (
                f"INV-075: título '{bad_title!r}' DEVE retornar ExtraTrainingBlocked"
            )

    # -----------------------------------------------------------------------
    # Caso 6: anti-false-positive — Draft e Blocked são tipos distintos
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_anti_false_positive_types_are_distinct(self):
        """
        INV-075 CASO 6 (anti-false-positive): ExtraTrainingDraft e
        ExtraTrainingBlocked são tipos distintos.
        Uma solicitação válida NUNCA pode ser confundida com bloqueada,
        e uma entrada inválida NUNCA pode produzir um Draft publicável.
        """
        svc = AICoachService()
        valid = svc.request_extra_training("Treino de resistência aeróbica")
        blocked = svc.request_extra_training("")

        assert isinstance(valid, ExtraTrainingDraft), (
            "INV-075: solicitação válida DEVE ser ExtraTrainingDraft"
        )
        assert isinstance(blocked, ExtraTrainingBlocked), (
            "INV-075: título vazio DEVE ser ExtraTrainingBlocked"
        )
        assert not isinstance(valid, ExtraTrainingBlocked), (
            "INV-075: ExtraTrainingDraft NÃO é ExtraTrainingBlocked"
        )
        # Rascunho válido: invariantes invioláveis mesmo no anti-false-positive
        assert valid.status == "draft", (
            "INV-075: status SEMPRE 'draft' — invariante inquebrável"
        )
        assert valid.source == "ai_athlete_request", (
            "INV-075: source SEMPRE 'ai_athlete_request' — invariante inquebrável"
        )
        assert valid.requires_coach_approval is True, (
            "INV-075: requires_coach_approval SEMPRE True — invariante inquebrável"
        )
