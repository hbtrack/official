from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional


@dataclass
class MedicalRecord:
    """
    Entidade principal — registro médico clínico de atleta.
    INV-MED-001: id, athlete_user_id, record_date, record_label obrigatórios.
    INV-MED-002: return_to_play_authorized=True implica return_to_training_authorized=True.
    INV-MED-003: medical não absorve autenticação/autorização técnica.
    INV-MED-004: dados PHI sob governança de privacidade e auditoria.
    DR-MED-003: autorizações de treino e jogo são decisões distintas.
    """

    id: uuid.UUID
    athlete_user_id: uuid.UUID
    record_date: date
    record_label: str

    team_id: Optional[uuid.UUID] = None
    assessment_summary: Optional[str] = None
    restriction_summary: Optional[str] = None
    return_to_training_authorized: Optional[bool] = None
    return_to_play_authorized: Optional[bool] = None
    clinical_notes: Optional[str] = None
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now())
    updated_at: datetime = field(default_factory=lambda: datetime.now())

    def validate_invariants(self) -> None:
        """Verifica INV-MED-001 e INV-MED-002."""
        # INV-MED-001: campos obrigatórios
        if not self.athlete_user_id:
            raise ValueError("INV-MED-001: athlete_user_id é obrigatório.")
        if not self.record_date:
            raise ValueError("INV-MED-001: record_date é obrigatório.")
        if not self.record_label:
            raise ValueError("INV-MED-001: record_label é obrigatório.")
        if len(self.record_label) > 120:
            raise ValueError("record_label excede 120 caracteres.")

        # INV-MED-002: return_to_play=True implica return_to_training=True
        if self.return_to_play_authorized is True and self.return_to_training_authorized is not True:
            raise ValueError(
                "INV-MED-002: returnToPlayAuthorized=true requer returnToTrainingAuthorized=true."
            )

        # Limites de texto
        if self.assessment_summary and len(self.assessment_summary) > 1000:
            raise ValueError("assessment_summary excede 1000 caracteres.")
        if self.restriction_summary and len(self.restriction_summary) > 1000:
            raise ValueError("restriction_summary excede 1000 caracteres.")
        if self.clinical_notes and len(self.clinical_notes) > 2000:
            raise ValueError("clinical_notes excede 2000 caracteres.")
