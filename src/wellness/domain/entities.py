"""
Entidades de domínio — módulo wellness.
Fonte: INVARIANTS_WELLNESS.md, DOMAIN_RULES_WELLNESS.md,
       contracts/openapi/paths/wellness.yaml
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Optional


# Campos proibidos por INV-WELL-004 (boundary wellness/medical)
_FORBIDDEN_FIELDS = {
    "diagnosis", "treatment", "prescription", "procedure",
    "medical_record", "clinical_note",
}


@dataclass
class WellnessEntry:
    """
    Entidade principal — entrada de wellness diário (auto-relato).
    INV-WELL-001: id, athlete_user_id, questionnaire_date, readiness_score obrigatórios.
    INV-WELL-002: readiness/fatigue/pain/recovery ∈ [0..10].
    INV-WELL-003: sleep_hours ∈ [0..24].
    INV-WELL-004: proibido campos clínicos (diagnosis, treatment, etc.).
    INV-WELL-005: training_session_id contextualiza mas não implica presença/autorização.
    DR-WELL-002: dados são auto-relato consultivo, não diagnóstico clínico.
    DR-WELL-005: notes é texto livre — não é nota clínica.
    """

    id: uuid.UUID
    athlete_user_id: uuid.UUID
    questionnaire_date: date
    readiness_score: int

    training_session_id: Optional[uuid.UUID] = None
    questionnaire_label: Optional[str] = None
    fatigue_score: Optional[int] = None
    pain_score: Optional[int] = None
    recovery_score: Optional[int] = None
    sleep_hours: Optional[Decimal] = None
    notes: Optional[str] = None

    created_at: datetime = field(default_factory=lambda: datetime.utcnow())
    updated_at: datetime = field(default_factory=lambda: datetime.utcnow())

    def validate_no_clinical_field(self, field_name: str) -> None:
        """INV-WELL-004: levanta ValueError se field_name for campo clínico proibido."""
        if field_name in _FORBIDDEN_FIELDS:
            raise ValueError(
                f"INV-WELL-004: campo clínico/clinical/forbidden '{field_name}' "
                "não é permitido no módulo wellness."
            )

    def validate_invariants(self) -> None:
        # INV-WELL-001: questionnaire_date obrigatória
        if self.questionnaire_date is None:
            raise ValueError("INV-WELL-001: questionnaire_date é obrigatório.")

        # INV-WELL-002: readiness_score ∈ [0..10]
        if not (0 <= self.readiness_score <= 10):
            raise ValueError(
                f"INV-WELL-002: readiness_score={self.readiness_score} deve estar em [0..10]."
            )

        # INV-WELL-002: fatigue_score ∈ [0..10]
        if self.fatigue_score is not None and not (0 <= self.fatigue_score <= 10):
            raise ValueError(
                f"INV-WELL-002: fatigue_score={self.fatigue_score} deve estar em [0..10]."
            )

        # INV-WELL-002: pain_score ∈ [0..10]
        if self.pain_score is not None and not (0 <= self.pain_score <= 10):
            raise ValueError(
                f"INV-WELL-002: pain_score={self.pain_score} deve estar em [0..10]."
            )

        # INV-WELL-002: recovery_score ∈ [0..10]
        if self.recovery_score is not None and not (0 <= self.recovery_score <= 10):
            raise ValueError(
                f"INV-WELL-002: recovery_score={self.recovery_score} deve estar em [0..10]."
            )

        # INV-WELL-003: sleep_hours ∈ [0..24]
        if self.sleep_hours is not None and not (Decimal("0") <= self.sleep_hours <= Decimal("24")):
            raise ValueError(
                f"INV-WELL-003: sleep_hours={self.sleep_hours} deve estar em [0..24]."
            )

        # questionnaire_label máx 80 chars (DR-WELL-004)
        if self.questionnaire_label is not None and len(self.questionnaire_label) > 80:
            raise ValueError("questionnaire_label excede 80 caracteres.")

        # notes máx 500 chars (DR-WELL-005, contrato)
        if self.notes is not None and len(self.notes) > 500:
            raise ValueError("DR-WELL-005: notes excede 500 caracteres.")


@dataclass
class WellnessSummary:
    """
    Resumo agregado de wellness para um atleta em um período.
    DR-WELL-002: insumo consultivo — NÃO é avaliação clínica.
    """

    athlete_user_id: uuid.UUID
    date_from: date
    date_to: date
    entry_count: int

    avg_readiness: Optional[Decimal] = None
    avg_fatigue: Optional[Decimal] = None
    avg_pain: Optional[Decimal] = None
    avg_recovery: Optional[Decimal] = None
    avg_sleep_hours: Optional[Decimal] = None
    readiness_trend: Optional[str] = None  # "improving", "stable", "declining"
    high_pain_alert: bool = False          # PERM-WEL-004: pain_score >= 7
