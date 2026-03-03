"""
INV-TRAIN-073: ai_privacy_no_intimate_content
Classe C1 — Unit (sem IO, sem DB)
Evidência:
  app/services/ai_coach_service.py — filter_privacy()
  app/services/coach_alerts_service.py — generate_risk_summary(), create_alert_for_coach()
Regra:
  - O treinador NÃO PODE ver conteúdo íntimo das conversas do atleta com a IA.
  - O treinador só recebe alertas/resumos de RISCO (safety), sem expor texto íntimo.
  - O atleta é dono do conteúdo da conversa.
  - intimate_content_exposed DEVE ser False em todos os resultados.
  - athlete_message_excerpt DEVE ser "" (string vazia) em todos os alertas.
"""
import pytest

from app.services.ai_coach_service import (
    AICoachService,
    PrivacyFilterResult,
)
from app.services.coach_alerts_service import (
    CoachAlertsService,
    CoachAlertSummary,
    NoAlertRequired,
    AlertRiskLevel,
    AlertType,
)


class TestInvTrain073AiPrivacyNoIntimateContent:
    """
    INV-TRAIN-073 — ai_privacy_no_intimate_content
    filter_privacy: AICoachService.filter_privacy()
    summarizer: CoachAlertsService.generate_risk_summary(), create_alert_for_coach()
    Evidência: app/services/ai_coach_service.py, app/services/coach_alerts_service.py
    """

    # -----------------------------------------------------------------------
    # filter_privacy — nunca expõe conteúdo íntimo ao treinador
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_privacy_filter_never_exposes_content(self):
        """
        INV-073 CASO 1: qualquer mensagem do atleta →
        filter_privacy() DEVE retornar content_exposed=False.
        O conteúdo bruto NUNCA é exposto ao treinador.
        """
        svc = AICoachService()
        intimate_message = (
            "Estou muito mal, briguei em casa e meu relacionamento está péssimo. "
            "Tenho medo de não conseguir dormir direito."
        )
        result = svc.filter_privacy(intimate_message)

        assert isinstance(result, PrivacyFilterResult), (
            "INV-073: filter_privacy deve retornar PrivacyFilterResult"
        )
        assert result.content_exposed is False, (
            "INV-073: content_exposed DEVE ser False — conteúdo íntimo nunca exposto"
        )

    @pytest.mark.asyncio
    async def test_privacy_filter_detects_risk_signal(self):
        """
        INV-073 CASO 2: mensagem com sinal de risco físico →
        filter_privacy() deve retornar has_risk_signal=True
        e risk_summary sem citar o texto íntimo.
        """
        svc = AICoachService()
        message_with_risk = "Sinto tontura desde ontem, não consigo dormir direito."

        result = svc.filter_privacy(message_with_risk)

        assert result.has_risk_signal is True, (
            "INV-073: mensagem com sinal físico deve gerar has_risk_signal=True"
        )
        assert result.content_exposed is False, (
            "INV-073: mesmo com sinal de risco, conteúdo íntimo nunca é exposto"
        )
        assert result.risk_summary != "", (
            "INV-073: risk_summary deve conter resumo genérico de risco"
        )
        # Verifica que o resumo não cita a mensagem original do atleta
        assert "tontura" not in result.risk_summary, (
            "INV-073: risk_summary NÃO DEVE citar texto íntimo do atleta"
        )
        assert "não consigo dormir" not in result.risk_summary, (
            "INV-073: risk_summary NÃO DEVE reproduzir frase da mensagem do atleta"
        )

    @pytest.mark.asyncio
    async def test_privacy_filter_no_risk_signal(self):
        """
        INV-073 CASO 3: mensagem sem sinal de risco →
        filter_privacy() retorna has_risk_signal=False e risk_summary vazio.
        """
        svc = AICoachService()
        safe_message = "Que horas é o treino de amanhã?"

        result = svc.filter_privacy(safe_message)

        assert result.has_risk_signal is False, (
            "INV-073: mensagem sem risco não deve gerar alerta"
        )
        assert result.content_exposed is False, (
            "INV-073: content_exposed sempre False"
        )
        assert result.risk_summary == "", (
            "INV-073: sem risco, risk_summary deve ser string vazia"
        )

    # -----------------------------------------------------------------------
    # CoachAlertsService — resumos sem texto íntimo
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_alert_intimate_content_never_exposed(self):
        """
        INV-073 CASO 4: generate_risk_summary() com mensagem de alto risco →
        CoachAlertSummary.intimate_content_exposed DEVE ser False.
        CoachAlertSummary.athlete_message_excerpt DEVE ser "" (vazio).
        """
        svc = CoachAlertsService()
        high_risk_messages = [
            "Sinto dor no peito desde o treino.",
            "Quase desmaiei durante o aquecimento.",
        ]

        result = svc.generate_risk_summary(high_risk_messages)

        assert isinstance(result, CoachAlertSummary), (
            "INV-073: alto risco deve gerar CoachAlertSummary"
        )
        assert result.intimate_content_exposed is False, (
            "INV-073: intimate_content_exposed DEVE ser False — invariante de privacidade"
        )
        assert result.athlete_message_excerpt == "", (
            "INV-073: athlete_message_excerpt DEVE ser '' — treinador não vê texto íntimo"
        )
        assert result.risk_level == AlertRiskLevel.HIGH, (
            "INV-073: dor no peito/desmaio deve gerar risco HIGH"
        )

    @pytest.mark.asyncio
    async def test_alert_summary_text_generic_no_athlete_phrases(self):
        """
        INV-073 CASO 5: risk_summary gerado NÃO DEVE conter frases do atleta.
        O treinador recebe apenas informação acionável genérica.
        """
        svc = CoachAlertsService()
        sensitive_messages = [
            "Machuquei o tornozelo e sinto muita dor persistente.",
        ]

        result = svc.generate_risk_summary(sensitive_messages)

        assert isinstance(result, CoachAlertSummary), (
            "INV-073: mensagem de risco físico deve gerar alerta"
        )
        # Texto íntimo NÃO deve aparecer no resumo
        assert "tornozelo" not in result.summary_text, (
            "INV-073: summary_text NÃO DEVE mencionar detalhes da mensagem do atleta"
        )
        assert "machuquei" not in result.summary_text.lower(), (
            "INV-073: summary_text NÃO DEVE reproduzir frase do atleta"
        )
        assert result.intimate_content_exposed is False

    @pytest.mark.asyncio
    async def test_no_alert_when_safe(self):
        """
        INV-073 CASO 6: mensagens sem sinal de risco → NoAlertRequired.
        O treinador não recebe alerta desnecessário.
        """
        svc = CoachAlertsService()
        safe_messages = [
            "Estou animado para o treino de hoje!",
            "Que exercício vamos fazer na próxima sessão?",
        ]

        result = svc.generate_risk_summary(safe_messages)

        assert isinstance(result, NoAlertRequired), (
            "INV-073: sem risco, deve retornar NoAlertRequired"
        )

    @pytest.mark.asyncio
    async def test_create_alert_enforces_privacy_invariant(self):
        """
        INV-073 CASO 7 (anti-false-positive): create_alert_for_coach() DEVE
        garantir always intimate_content_exposed=False e athlete_message_excerpt="".
        Mesmo que quem chamar o método tente fornecer excerpt, o guard ignora.
        """
        svc = CoachAlertsService()
        alert = svc.create_alert_for_coach(
            risk_level=AlertRiskLevel.MEDIUM,
            alert_type=AlertType.WELLNESS,
            summary_text="Atleta sinalizou cansaço antes do treino.",
        )

        assert alert.intimate_content_exposed is False, (
            "INV-073: create_alert_for_coach() deve garantir intimate_content_exposed=False"
        )
        assert alert.athlete_message_excerpt == "", (
            "INV-073: athlete_message_excerpt DEVE ser '' — never populated"
        )
        assert isinstance(alert, CoachAlertSummary)
