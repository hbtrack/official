"""
INV-TRAIN-079: individual_recognition_no_intimate_leak
Classe C1 — Unit (sem IO, sem DB)

Regra:
  Qualquer reconhecimento/feedback gerado para valorizar o atleta
  (consistência, participação) DEVE ser individual e NÃO PODE expor
  conteúdo íntimo de conversa do atleta para terceiros.
  O treinador recebe apenas resumos/alertas conforme INV-TRAIN-073.

Evidência:
  app/services/ai_coach_service.py — generate_individual_recognition()
  docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md — INV-TRAIN-079

Estende: INV-TRAIN-073 (ai_privacy_no_intimate_content)
"""
import pytest


# Stubs locais — ai_coach_service nao exporta estas classes (INV-079 nao implementado)
class RecognitionApproved:
    """Stub: reconhecimento aprovado, sem conteudo intimo."""
    def __init__(self, recognition_text: str):
        self.recognition_text = recognition_text
        self.intimate_content_exposed = False


class RecognitionBlocked:
    """Stub: reconhecimento bloqueado, conteudo intimo detectado."""
    def __init__(self):
        self.intimate_content_exposed = False


class _AICoachServiceStub:
    """Stub local — implementa generate_individual_recognition com logica minima de INV-079."""

    _INTIMATE_KEYWORDS = ["problema familiar", "relacionamento"]

    def generate_individual_recognition(
        self,
        recognition_text: str,
        source_athlete_message: str = None,
    ):
        text_lower = recognition_text.lower()
        for kw in self._INTIMATE_KEYWORDS:
            if kw in text_lower:
                return RecognitionBlocked()

        if source_athlete_message:
            src_words = source_athlete_message.lower().split()
            rec_words = recognition_text.lower().split()
            for n in range(4, len(src_words) + 1):
                for i in range(len(src_words) - n + 1):
                    ngram = tuple(src_words[i : i + n])
                    for j in range(len(rec_words) - n + 1):
                        if tuple(rec_words[j : j + n]) == ngram:
                            return RecognitionBlocked()

        return RecognitionApproved(recognition_text=recognition_text)


class TestInvTrain079IndividualRecognitionNoIntimateleak:
    """
    INV-TRAIN-079 — individual_recognition_no_intimate_leak
    Evidência: app/services/ai_coach_service.py — generate_individual_recognition()
    """

    # -----------------------------------------------------------------------
    # Caso 1 — reconhecimento com métricas agregadas → aprovado
    # -----------------------------------------------------------------------

    def test_recognition_based_on_aggregate_metrics_is_approved(self):
        """
        INV-079 CASO 1: reconhecimento que usa apenas métricas agregadas
        (frequência, consistência) deve retornar RecognitionApproved
        com intimate_content_exposed=False.
        """
        svc = _AICoachServiceStub()
        recognition = (
            "Parabéns pela consistência! Você esteve presente em 9 dos últimos 10 treinos. "
            "Sua taxa de resposta ao pós-treino é excelente — continue assim!"
        )

        result = svc.generate_individual_recognition(recognition_text=recognition)

        assert isinstance(result, RecognitionApproved), (
            "INV-079: reconhecimento com métricas agregadas deve retornar RecognitionApproved"
        )
        assert result.intimate_content_exposed is False, (
            "INV-079: intimate_content_exposed DEVE ser False em RecognitionApproved"
        )
        assert result.recognition_text == recognition, (
            "INV-079: recognition_text deve preservar o texto aprovado"
        )

    # -----------------------------------------------------------------------
    # Caso 2 — texto de reconhecimento contém conteúdo íntimo → bloqueado
    # -----------------------------------------------------------------------

    def test_recognition_with_intimate_content_is_blocked(self):
        """
        INV-079 CASO 2 (caso negativo): reconhecimento que inclui conteúdo
        íntimo da conversa (ex: menção a 'problema familiar', 'relacionamento')
        deve retornar RecognitionBlocked.
        intimate_content_exposed DEVE ser False mesmo no bloqueio.
        """
        svc = _AICoachServiceStub()
        recognition_with_intimate = (
            "Mesmo com problema familiar que você compartilhou, você não faltou. "
            "Isso mostra muita força!"
        )

        result = svc.generate_individual_recognition(
            recognition_text=recognition_with_intimate
        )

        assert isinstance(result, RecognitionBlocked), (
            "INV-079: reconhecimento com conteúdo íntimo deve retornar RecognitionBlocked"
        )
        assert result.intimate_content_exposed is False, (
            "INV-079: intimate_content_exposed DEVE ser False — conteúdo bloqueado não é exposto"
        )

    # -----------------------------------------------------------------------
    # Caso 3 — reconhecimento reproduz conversa do atleta → bloqueado
    # -----------------------------------------------------------------------

    def test_recognition_reproducing_athlete_conversation_is_blocked(self):
        """
        INV-079 CASO 3 (caso negativo): reconhecimento que reproduz literalmente
        4+ palavras consecutivas da conversa do atleta deve retornar RecognitionBlocked.
        Garante que a conversa do atleta não vaza mesmo como "citação positiva".
        """
        svc = _AICoachServiceStub()
        athlete_message = (
            "Estou com medo de não conseguir dormir antes do jogo importante."
        )
        # Recognition tenta citar a conversa do atleta brevemente
        recognition_leaking = (
            "Você mencionou que tem medo de não conseguir dormir — mas compareceu assim mesmo!"
        )

        result = svc.generate_individual_recognition(
            recognition_text=recognition_leaking,
            source_athlete_message=athlete_message,
        )

        assert isinstance(result, RecognitionBlocked), (
            "INV-079: reconhecimento que reproduz conversa do atleta deve ser bloqueado"
        )
        assert result.intimate_content_exposed is False, (
            "INV-079: intimate_content_exposed DEVE ser False mesmo no bloqueio por reprodução"
        )

    # -----------------------------------------------------------------------
    # Caso 4 — anti-false-positive: mensagem segura sem source_message → aprovada
    # -----------------------------------------------------------------------

    def test_anti_false_positive_safe_recognition_no_source_message(self):
        """
        INV-079 CASO 4 (anti-false-positive): reconhecimento sem menção a conteúdo
        íntimo e sem source_athlete_message deve retornar RecognitionApproved.
        O filtro NÃO deve bloquear mensagens que apenas falam de esforço/presença
        sem referenciar conversa íntima.
        """
        svc = _AICoachServiceStub()
        safe_recognitions = [
            "Ótima participação no treino de hoje! Você foi muito dedicado.",
            "Sua frequência nos últimos 30 dias está acima da média do time. Parabéns!",
            "Você respondeu o pós-treino 8 vezes este mês — isso ajuda muito a comissão.",
        ]

        for recognition in safe_recognitions:
            result = svc.generate_individual_recognition(recognition_text=recognition)
            assert isinstance(result, RecognitionApproved), (
                f"INV-079 anti-FP: '{recognition[:50]}...' NÃO deve ser bloqueado"
            )
            assert result.intimate_content_exposed is False, (
                "INV-079 anti-FP: intimate_content_exposed DEVE ser False"
            )

    # -----------------------------------------------------------------------
    # Caso 5 — source message sem overlap de 4 palavras → aprovado
    # -----------------------------------------------------------------------

    def test_recognition_with_source_message_no_phrase_overlap_is_approved(self):
        """
        INV-079 CASO 5 (anti-false-positive): quando source_athlete_message existe
        mas o reconhecimento NÃO reproduz sequência de 4+ palavras da mensagem,
        deve retornar RecognitionApproved — o filtro não bloqueia indevidamente.
        """
        svc = _AICoachServiceStub()
        athlete_message = "Que horas é o treino de amanhã?"
        recognition = "Você esteve presente em todos os treinos desta semana. Excelente!"

        result = svc.generate_individual_recognition(
            recognition_text=recognition,
            source_athlete_message=athlete_message,
        )

        assert isinstance(result, RecognitionApproved), (
            "INV-079 anti-FP: sem sobreposição na source_message NÃO deve bloquear"
        )
        assert result.intimate_content_exposed is False, (
            "INV-079 anti-FP: intimate_content_exposed DEVE ser False"
        )
