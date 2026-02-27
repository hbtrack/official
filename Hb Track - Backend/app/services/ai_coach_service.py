"""
Service de IA Coach para o módulo de Treinos.

Implementa guards/invariantes:
- INV-072: ai_suggestion_not_order
    tone guard: bloqueia mensagens com tom imperativo
    publish guard: bloqueia autopublicação de treino pela IA — toda geração de treino
    pela IA passa por "editar antes" do treinador.
- INV-073: ai_privacy_no_intimate_content
    privacy filter: filtra conteúdo íntimo do atleta antes de qualquer exposição
    ao treinador — o treinador só recebe alertas/resumos de risco.
- INV-074: ai_educational_content_independent
    educational module: responde perguntas educativas (regras, táticas) sem
    alterar treino/agendamento — conteúdo informativo apenas.
- INV-075: ai_extra_training_draft_only
    draft guard: treino extra solicitado via IA chega SEMPRE como rascunho
    (status=draft, source=ai_athlete_request) e NUNCA é publicado/agendado
    automaticamente. Publicação somente após ação explícita do treinador.

Âncoras canônicas:
- docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md — INV-072, INV-073, INV-074, INV-075
- AR_162 (write scope: app/services/ai_coach_service.py)
- AR_163 (write scope: app/services/ai_coach_service.py)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Union

# ---------------------------------------------------------------------------
# INV-072 — Tone guard: tom imperativo proibido
# ---------------------------------------------------------------------------

# Marcadores de tom imperativo em português (insensível a maiúsculas)
IMPERATIVE_TONE_MARKERS: List[str] = [
    "você deve ",
    "você precisa ",
    "faça ",
    "execute ",
    "complete ",
    "realize ",
    "vá treinar",
    "treine agora",
    "é obrigatório",
    "é necessário que você",
]


@dataclass
class SuggestionApproved:
    """Mensagem da IA aprovada — tom de sugestão/apoio válido."""

    message: str
    reason: str = "tone_validated"


@dataclass
class SuggestionBlocked:
    """Mensagem da IA bloqueada — tom imperativo detectado."""

    original_message: str
    reason: str = "imperative_tone_detected"
    markers_found: List[str] = field(default_factory=list)


SuggestionResult = Union[SuggestionApproved, SuggestionBlocked]


# ---------------------------------------------------------------------------
# INV-072 — Publish guard: autopublicação pela IA proibida
# ---------------------------------------------------------------------------


@dataclass
class PublishApproved:
    """Publicação autorizada — coach aprovou manualmente."""

    reason: str = "coach_approved"


@dataclass
class PublishBlocked:
    """Publicação bloqueada — sem aprovação do treinador."""

    reason: str = "ai_auto_publish_blocked"
    detail: str = "Training must be reviewed and approved by coach before publishing"


PublishResult = Union[PublishApproved, PublishBlocked]


# ---------------------------------------------------------------------------
# INV-073 — Privacy filter: conteúdo íntimo não exposto ao treinador
# ---------------------------------------------------------------------------

# Padrões associados a conteúdo íntimo que NÃO devem ser expostos ao treinador
INTIMATE_CONTENT_PATTERNS: List[str] = [
    "sinto muito",
    "estou triste",
    "emoção",
    "medo de",
    "ansiedade",
    "deprimido",
    "problema familiar",
    "relacionamento",
    "briga em casa",
    "não me sinto bem",
    "choro",
    "chore",
    "autoestima",
    "abuso",
]

# Padrões de risco (safety) que devem gerar alerta sem expor o texto íntimo
RISK_SIGNAL_PATTERNS: List[str] = [
    "não consigo dormir",
    "dor persistente",
    "lesão",
    "machuquei",
    "me machuco",
    "tontura",
    "febre",
    "nausea",
    "náusea",
    "vomit",
    "desmaio",
    "falta de ar",
]


@dataclass
class PrivacyFilterResult:
    """Resultado do filtro de privacidade sobre mensagem do atleta."""

    content_exposed: bool  # False = seguro; nunca expõe texto íntimo ao treinador
    has_risk_signal: bool  # True = gerar alerta ao treinador (sem texto íntimo)
    risk_summary: str  # resumo curto de risco — SEM texto íntimo do atleta


# ---------------------------------------------------------------------------
# INV-074 — Educational module: conteúdo educativo independente do treino
# ---------------------------------------------------------------------------

# Tópicos educativos reconhecidos pelo módulo
EDUCATIONAL_TOPICS = {
    "2_minutos",
    "superioridade_numerica",
    "inferioridade_numerica",
    "7_metros",
    "7m",
    "penalti",
    "tatica",
    "tática",
    "regras",
    "principios",
    "princípios",
    "posicoes",
    "posições",
    "arbitragem",
    "goleiro",
    "pivot",
    "pivô",
    "armador",
    "ala",
    "ponta",
}


@dataclass
class EducationalResponse:
    """Resposta educativa da IA sobre regras/táticas de handebol."""

    topic: str
    content: str
    affects_training: bool = False  # SEMPRE False — invariante INV-074
    affects_scheduling: bool = False  # SEMPRE False — invariante INV-074


@dataclass
class EducationalTopicNotFound:
    """Tópico educativo não reconhecido."""

    requested_topic: str
    reason: str = "topic_not_recognized"


EducationalResult = Union[EducationalResponse, EducationalTopicNotFound]


# ---------------------------------------------------------------------------
# INV-075 — Draft guard: treino extra via IA nunca é publicado automaticamente
# ---------------------------------------------------------------------------


@dataclass
class ExtraTrainingDraft:
    """
    Rascunho de treino extra gerado pela IA a pedido do atleta.

    INV-075: status DEVE ser 'draft' e source DEVE ser 'ai_athlete_request'.
    O sistema NUNCA publica/agenda automaticamente.
    Publicação somente após ação explícita do treinador.
    """

    title: str
    source: str = "ai_athlete_request"  # INV-075: SEMPRE este valor
    status: str = "draft"               # INV-075: SEMPRE draft — nunca publicado
    requires_coach_approval: bool = True  # INV-075: treinador DEVE aprovar


@dataclass
class ExtraTrainingBlocked:
    """Solicitação de treino extra rejeitada — título inválido ou vazio."""

    reason: str = "invalid_title"
    detail: str = "Extra training title must be a non-empty string"


ExtraTrainingResult = Union[ExtraTrainingDraft, ExtraTrainingBlocked]


# ---------------------------------------------------------------------------
# INV-077 — Feedback pós-treino conversacional
# ---------------------------------------------------------------------------


@dataclass
class PostTrainingFeedback:
    """
    INV-077: Feedback gerado ao concluir pós-treino conversacional.

    DEVE conter:
    - 1 reconhecimento (esforço/consistência)
    - 1 orientação prática (técnica/tática/recuperação)
    """

    recognition: str          # 1 reconhecimento (esforço/consistência)
    guidance: str             # 1 orientação prática (técnica/tática/recuperação)
    source: str = "virtual_coach"  # INV-077: SEMPRE este valor


@dataclass
class FeedbackNotGenerated:
    """INV-077: Pós-treino não concluído — feedback NÃO gerado."""

    reason: str = "post_training_not_completed"


PostTrainingFeedbackResult = Union[PostTrainingFeedback, FeedbackNotGenerated]


# ---------------------------------------------------------------------------
# AICoachService — orquestra os guards de INV-072, INV-073, INV-074, INV-075, INV-077
# ---------------------------------------------------------------------------


class AICoachService:
    """
    Service principal do IA Coach para o módulo de Treinos HB Track.

    Orquestra os guards das invariantes:
    - INV-072: check_suggestion_tone(), check_auto_publish()
    - INV-073: filter_privacy()
    - INV-074: get_educational_content()
    - INV-075: request_extra_training()
    - INV-077: generate_post_training_feedback()

    Não acessa DB diretamente — é um service de lógica de negócio (Classe C1).
    """

    # -----------------------------------------------------------------------
    # INV-072: Tone guard
    # -----------------------------------------------------------------------

    def check_suggestion_tone(self, message: str) -> SuggestionResult:
        """
        INV-072 — tone guard.
        Verifica se a mensagem da IA usa tom de sugestão/apoio.
        Bloqueia mensagens com tom imperativo.

        Args:
            message: texto da mensagem a ser enviada pela IA ao atleta.

        Returns:
            SuggestionApproved se o tom é adequado.
            SuggestionBlocked se tom imperativo detectado.
        """
        lower_msg = message.lower()
        found_markers = [
            m for m in IMPERATIVE_TONE_MARKERS if m.lower() in lower_msg
        ]
        if found_markers:
            return SuggestionBlocked(
                original_message=message,
                markers_found=found_markers,
            )
        return SuggestionApproved(message=message)

    # -----------------------------------------------------------------------
    # INV-072: Publish guard
    # -----------------------------------------------------------------------

    def check_auto_publish(
        self,
        is_ai_generated: bool,
        approved_by_coach: bool,
    ) -> PublishResult:
        """
        INV-072 — publish guard.
        A IA NÃO PODE criar/publicar treino oficial automaticamente.
        Toda geração de treino pela IA passa por aprovação do treinador.

        Args:
            is_ai_generated: True se o treino foi gerado pela IA.
            approved_by_coach: True se o treinador aprovou manualmente.

        Returns:
            PublishApproved somente se approved_by_coach=True OU is_ai_generated=False.
            PublishBlocked se a IA gerou o treino SEM aprovação do treinador.
        """
        if is_ai_generated and not approved_by_coach:
            return PublishBlocked()
        return PublishApproved()

    # -----------------------------------------------------------------------
    # INV-073: Privacy filter
    # -----------------------------------------------------------------------

    def filter_privacy(self, athlete_message: str) -> PrivacyFilterResult:
        """
        INV-073 — privacy filter.
        Analisa mensagem do atleta e determina se há sinal de risco (safety)
        sem expor o texto íntimo ao treinador.
        O conteúdo bruto NUNCA é exposto ao treinador.

        Args:
            athlete_message: mensagem completa do atleta à IA.

        Returns:
            PrivacyFilterResult com content_exposed=False sempre,
            has_risk_signal=True se sinal de risco detectado,
            risk_summary com texto genérico (sem citar o texto íntimo).
        """
        lower_msg = athlete_message.lower()

        has_risk = any(p in lower_msg for p in RISK_SIGNAL_PATTERNS)

        if has_risk:
            risk_summary = (
                "Atleta relatou sintoma físico ou sinal de alerta na conversa. "
                "Verifique o bem-estar do atleta antes do próximo treino."
            )
        else:
            risk_summary = ""

        return PrivacyFilterResult(
            content_exposed=False,  # INV-073: NUNCA expõe à treinador
            has_risk_signal=has_risk,
            risk_summary=risk_summary,
        )

    # -----------------------------------------------------------------------
    # INV-074: Educational module
    # -----------------------------------------------------------------------

    def get_educational_content(self, topic: str) -> EducationalResult:
        """
        INV-074 — educational module.
        Retorna conteúdo educativo sobre regras/táticas de handebol.
        Conteúdo educativo NÃO altera treino nem agendamento — apenas informativo.

        Args:
            topic: tópico solicitado (ex: "2_minutos", "7_metros", "tatica").

        Returns:
            EducationalResponse com affects_training=False e affects_scheduling=False.
            EducationalTopicNotFound se tópico não reconhecido.
        """
        normalized = topic.lower().replace(" ", "_")
        if normalized not in EDUCATIONAL_TOPICS:
            return EducationalTopicNotFound(requested_topic=topic)

        content = _EDUCATIONAL_CONTENT.get(
            normalized,
            f"Conteúdo educativo sobre '{topic}' disponível mediante consulta ao treinador.",
        )

        return EducationalResponse(
            topic=normalized,
            content=content,
            affects_training=False,    # INV-074: NUNCA altera treino
            affects_scheduling=False,  # INV-074: NUNCA altera agendamento
        )


    # -----------------------------------------------------------------------
    # INV-075: Draft guard
    # -----------------------------------------------------------------------

    def request_extra_training(self, title: str) -> ExtraTrainingResult:
        """
        INV-075 — draft guard.
        Gera rascunho de treino extra solicitado pelo atleta via IA.
        O rascunho NUNCA é publicado/agendado automaticamente.
        Requer aprovação explícita do treinador.

        Args:
            title: descrição/título do treino extra solicitado.

        Returns:
            ExtraTrainingDraft com status='draft' e source='ai_athlete_request'.
            ExtraTrainingBlocked se título for inválido/vazio.
        """
        if not title or not title.strip():
            return ExtraTrainingBlocked()

        return ExtraTrainingDraft(
            title=title.strip(),
            source="ai_athlete_request",  # INV-075: SEMPRE este valor
            status="draft",               # INV-075: NUNCA publicado automaticamente
            requires_coach_approval=True,
        )

    # -----------------------------------------------------------------------
    # INV-077: Feedback imediato pós-treino conversacional
    # -----------------------------------------------------------------------

    def generate_post_training_feedback(
        self,
        conversation_completed: bool,
        session_rpe: "int | None" = None,
    ) -> PostTrainingFeedbackResult:
        """
        INV-077 — feedback imediato pós conversacional.
        Gera feedback curto somente se o pós-treino conversacional foi concluído.
        Se não concluído, retorna FeedbackNotGenerated (nunca lança exceção).

        Args:
            conversation_completed: True se atleta concluiu o fluxo conversacional.
            session_rpe: RPE declarado pelo atleta (1–10) ou None.

        Returns:
            PostTrainingFeedback com recognition + guidance se concluído.
            FeedbackNotGenerated caso contrário.

        Evidence: app/services/ai_coach_service.py :: generate_post_training_feedback
        """
        if not conversation_completed:
            return FeedbackNotGenerated()

        # Reconhecimento baseado no esforço declarado (RPE)
        if session_rpe is not None and session_rpe >= 8:
            recognition = (
                "Excelente esforço na sessão de hoje — intensidade alta exige comprometimento."
            )
        elif session_rpe is not None and session_rpe >= 5:
            recognition = (
                "Bom trabalho! Consistência é a base do desenvolvimento no handebol."
            )
        else:
            recognition = (
                "Presença e dedicação contam — cada treino é um passo na sua evolução."
            )

        guidance = (
            "Para o próximo treino: foque na recuperação ativa (alongamento + hidratação) "
            "e revise sua posição defensiva básica."
        )
        return PostTrainingFeedback(
            recognition=recognition,
            guidance=guidance,
            source="virtual_coach",  # INV-077: SEMPRE este valor
        )


# ---------------------------------------------------------------------------
# Banco de conteúdo educativo (INV-074)
# ---------------------------------------------------------------------------

_EDUCATIONAL_CONTENT: dict[str, str] = {
    "2_minutos": (
        "Suspensão de 2 minutos: o árbitro aplica quando um jogador comete falta grave "
        "ou antiesportiva. O time fica com um jogador a menos durante o período. "
        "O jogador suspenso pode retornar após cumprida a suspensão."
    ),
    "superioridade_numerica": (
        "Superioridade numérica: ocorre quando o time adversário tem um jogador suspenso "
        "(2 min). O time em vantagem tem 7 jogadores em campo (6 + goleiro) contra 6. "
        "Momento ideal para explorar espaços e executar jogadas ensaiadas."
    ),
    "inferioridade_numerica": (
        "Inferioridade numérica: o time tem um jogador suspenso. Foco em defesa compacta "
        "e recomposição rápida. O goleiro pode sair para igualar o número em campo."
    ),
    "7_metros": (
        "Tiro de 7 metros (penalti): cobrado quando falta clara de gol for cometida "
        "dentro da área. Apenas o cobrador e o goleiro participam da jogada. "
        "O cobrador deve lançar dentro de 3 segundos após o apito."
    ),
    "7m": (
        "Tiro de 7 metros (penalti): cobrado quando falta clara de gol for cometida "
        "dentro da área. Apenas o cobrador e o goleiro participam da jogada."
    ),
    "tatica": (
        "Princípios táticos básicos do handebol: ataque posicional (6x0, 5x1, 4x2), "
        "contra-ataque, defesa em zona, marcação individual. "
        "A escolha depende do perfil do adversário e dos jogadores disponíveis."
    ),
    "tática": (
        "Princípios táticos básicos do handebol: ataque posicional (6x0, 5x1, 4x2), "
        "contra-ataque, defesa em zona, marcação individual."
    ),
    "regras": (
        "Regras básicas: partida com 2 tempos de 30 min (adulto), bola tocada com mãos "
        "apenas (exceto goleiro), 3 passos sem quicar são permitidos, área do goleiro "
        "reservada (jogadores de linha não podem entrar), gol válido somente se lançado "
        "de fora da área ou em salto antes da linha."
    ),
    "principios": (
        "Princípios do jogo: criação de superioridade numérica e espacial no ataque, "
        "transição rápida defesa→ataque, comunicação entre jogadores, leitura do jogo."
    ),
    "princípios": (
        "Princípios do jogo: criação de superioridade numérica e espacial no ataque, "
        "transição rápida defesa→ataque, comunicação entre jogadores, leitura do jogo."
    ),
    "goleiro": (
        "Goleiro: único jogador autorizado a entrar na área (6m). Pode usar pés e corpo "
        "inteiro para defender. Tempo limite de 3s com a bola em mãos antes de arremessar "
        "ou sair da área. Pode participar do ataque como jogador de linha."
    ),
    "pivot": (
        "Pivô: posição de linha, geralmente posicionado próximo à área adversária. "
        "Função: criar espaço, bloquear defensores, receber passes rápidos para finalizar."
    ),
    "pivô": (
        "Pivô: posição de linha, geralmente posicionado próximo à área adversária. "
        "Função: criar espaço, bloquear defensores, receber passes rápidos para finalizar."
    ),
    "armador": (
        "Armador (meia): organiza o ataque posicional, distribui a bola, define o ritmo "
        "do jogo. Geralmente ocupa a posição central na linha de ataque."
    ),
    "ala": (
        "Alas (esquerda e direita): jogadores nas extremidades do ataque. "
        "Exploram o corredor lateral, finalizam em ângulo e participam na transição."
    ),
    "ponta": (
        "Pontas: jogadores que ocupam as posições mais avançadas nas laterais. "
        "Velocidade e capacidade de finalização em ângulo são suas principais qualidades."
    ),
    "posicoes": (
        "Posições no handebol: Goleiro, Armador Central, Armador Esquerdo, Armador Direito, "
        "Ala Esquerda, Ala Direita, Pivô. Cada posição tem função específica no sistema "
        "de ataque e de defesa."
    ),
    "posições": (
        "Posições no handebol: Goleiro, Armador Central, Armador Esquerdo, Armador Direito, "
        "Ala Esquerda, Ala Direita, Pivô."
    ),
    "arbitragem": (
        "Arbitragem: 2 árbitros principais (em diagonal) + cronometrista e anotador. "
        "Sinais: apito + gestos manuais padronizados pela IHF. "
        "Advertências progressivas: amarelo → 2min → vermelho (exclusão definitiva)."
    ),
}
