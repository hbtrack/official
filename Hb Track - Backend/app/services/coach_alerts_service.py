"""
Service de alertas do treinador — módulo de Treinos HB Track.

Implementa:
- INV-073: ai_privacy_no_intimate_content — summarizer
    Gera alertas/resumos de risco para o treinador sem expor texto íntimo
    das conversas do atleta com a IA.
    O atleta é dono do conteúdo da conversa; o treinador recebe apenas
    informação acionável (tipo de alerta + nível de risco + resumo genérico).

Âncoras canônicas:
- docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md — INV-073
- AR_162 (write scope: app/services/coach_alerts_service.py)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List


# ---------------------------------------------------------------------------
# Enums de classificação de alerta
# ---------------------------------------------------------------------------


class AlertRiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class AlertType(str, Enum):
    SAFETY = "safety"       # risco físico/saúde
    WELLNESS = "wellness"   # bem-estar emocional
    PERFORMANCE = "performance"  # queda de desempenho sinalizada


# ---------------------------------------------------------------------------
# Tipos de saída
# ---------------------------------------------------------------------------


@dataclass
class CoachAlertSummary:
    """
    Resumo de alerta enviado ao treinador.

    INV-073: 'intimate_content_exposed' é SEMPRE False.
    O treinador recebe apenas:
    - tipo do alerta (AlertType)
    - nível de risco (AlertRiskLevel)
    - resumo genérico sem citar texto íntimo do atleta

    Nunca inclui: transcrições, frases do atleta, nome de pessoas
    mencionadas em contexto íntimo.
    """

    risk_level: AlertRiskLevel
    alert_type: AlertType
    summary_text: str           # resumo genérico, sem texto íntimo
    intimate_content_exposed: bool = False  # INV-073: SEMPRE False
    athlete_message_excerpt: str = ""       # INV-073: DEVE ser "" — nunca preenchido


@dataclass
class NoAlertRequired:
    """Nenhum sinal de risco detectado — nenhum alerta para o treinador."""

    reason: str = "no_risk_signal"


CoachAlertResult = CoachAlertSummary | NoAlertRequired


# ---------------------------------------------------------------------------
# Padrões de risco por nível
# ---------------------------------------------------------------------------

_HIGH_RISK_PATTERNS: List[str] = [
    "dor no peito",
    "falta de ar",
    "desmaio",
    "desmaiei",
    "vomito",
    "vômito",
    "febre alta",
    "lesão grave",
    "não consigo andar",
    "abuso",
    "violência",
]

_MEDIUM_RISK_PATTERNS: List[str] = [
    "dor persistente",
    "não consigo dormir",
    "tontura",
    "tonturao",
    "náusea",
    "nausea",
    "machuquei",
    "me machuco",
    "lesão",
    "febre",
    "caí",
]

_WELLNESS_PATTERNS: List[str] = [
    "muito cansado",
    "esgotado",
    "não me sinto bem",
    "ansiedade",
    "deprimido",
    "desmotivado",
    "não quero treinar",
]


# ---------------------------------------------------------------------------
# CoachAlertsService
# ---------------------------------------------------------------------------


class CoachAlertsService:
    """
    Gera alertas de risco para o treinador sem expor conteúdo íntimo.

    INV-073: O treinador NÃO PODE ver o conteúdo íntimo das conversas do
    atleta com a IA. Este service garante que apenas resumos de risco
    (safety/wellness/performance) são gerados, sem expor o texto bruto.

    É um service de lógica de negócio (Classe C1) — sem acesso a DB.
    """

    def generate_risk_summary(
        self,
        athlete_messages: List[str],
    ) -> CoachAlertResult:
        """
        INV-073 — summarizer.
        Analisa lista de mensagens do atleta e, se houver sinal de risco,
        gera um resumo para o treinador SEM expor o texto íntimo original.

        Args:
            athlete_messages: lista de mensagens do atleta à IA.
                              Conteúdo NUNCA é repassado ao treinador.

        Returns:
            CoachAlertSummary com intimate_content_exposed=False se risco detectado.
            NoAlertRequired se nenhum sinal de risco.
        """
        combined = " ".join(athlete_messages).lower()

        # Verifica risco HIGH primeiro
        for pattern in _HIGH_RISK_PATTERNS:
            if pattern in combined:
                return CoachAlertSummary(
                    risk_level=AlertRiskLevel.HIGH,
                    alert_type=AlertType.SAFETY,
                    summary_text=(
                        "Sinal de alerta físico de alto risco detectado na conversa do atleta. "
                        "Avalie imediatamente a condição física antes do próximo treino."
                    ),
                    intimate_content_exposed=False,  # INV-073
                    athlete_message_excerpt="",       # INV-073: NUNCA expõe texto
                )

        # Verifica risco MEDIUM
        for pattern in _MEDIUM_RISK_PATTERNS:
            if pattern in combined:
                return CoachAlertSummary(
                    risk_level=AlertRiskLevel.MEDIUM,
                    alert_type=AlertType.SAFETY,
                    summary_text=(
                        "Sinal de alerta físico moderado detectado na conversa do atleta. "
                        "Verifique o bem-estar físico antes do próximo treino."
                    ),
                    intimate_content_exposed=False,
                    athlete_message_excerpt="",
                )

        # Verifica wellness
        for pattern in _WELLNESS_PATTERNS:
            if pattern in combined:
                return CoachAlertSummary(
                    risk_level=AlertRiskLevel.LOW,
                    alert_type=AlertType.WELLNESS,
                    summary_text=(
                        "Atleta sinalizou estado emocional/motivacional que pode "
                        "afetar o desempenho. Considere conversar brevemente antes do treino."
                    ),
                    intimate_content_exposed=False,
                    athlete_message_excerpt="",
                )

        return NoAlertRequired()

    def create_alert_for_coach(
        self,
        risk_level: AlertRiskLevel,
        alert_type: AlertType,
        summary_text: str,
    ) -> CoachAlertSummary:
        """
        Cria alerta estruturado para o treinador.
        Garante que intimate_content_exposed=False e athlete_message_excerpt=""
        — o treinador nunca recebe conteúdo íntimo.

        INV-073: método auxiliar para criação explícita de alertas.
        """
        return CoachAlertSummary(
            risk_level=risk_level,
            alert_type=alert_type,
            summary_text=summary_text,
            intimate_content_exposed=False,   # INV-073: enforced
            athlete_message_excerpt="",        # INV-073: enforced
        )
