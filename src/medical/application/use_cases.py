from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional

from medical.domain.entities import MedicalRecord
from medical.domain.rules import (
    RoleLabel, MedicalRecordNotFound, InsufficientPrivilege,
    assert_can_create_record, assert_can_read_record,
    assert_can_update_record, assert_can_delete_record,
)
from medical.infrastructure.repository import MedicalRecordRepository


# ---------------------------------------------------------------------------
# Input DTOs
# ---------------------------------------------------------------------------

@dataclass
class CreateMedicalRecordInput:
    actor_role: RoleLabel
    actor_user_id: uuid.UUID
    athlete_user_id: uuid.UUID
    record_date: date
    record_label: str
    team_id: Optional[uuid.UUID] = None
    assessment_summary: Optional[str] = None
    restriction_summary: Optional[str] = None
    return_to_training_authorized: Optional[bool] = None
    return_to_play_authorized: Optional[bool] = None
    clinical_notes: Optional[str] = None


@dataclass
class UpdateMedicalRecordInput:
    actor_role: RoleLabel
    actor_user_id: uuid.UUID
    actor_team_athlete_ids: List[uuid.UUID] = field(default_factory=list)
    record_date: Optional[date] = None
    record_label: Optional[str] = None
    assessment_summary: Optional[str] = None
    restriction_summary: Optional[str] = None
    return_to_training_authorized: Optional[bool] = None
    return_to_play_authorized: Optional[bool] = None
    clinical_notes: Optional[str] = None


@dataclass
class ListMedicalRecordsInput:
    actor_role: RoleLabel
    actor_user_id: uuid.UUID
    actor_team_athlete_ids: List[uuid.UUID] = field(default_factory=list)
    athlete_user_id: Optional[uuid.UUID] = None
    team_id: Optional[uuid.UUID] = None
    record_date_from: Optional[date] = None
    record_date_to: Optional[date] = None
    authorization_status: Optional[str] = None
    page_token: Optional[str] = None
    page_size: int = 20


@dataclass
class ListMedicalRecordsResult:
    data: List[MedicalRecord]
    next_page_token: Optional[str]


# ---------------------------------------------------------------------------
# Use cases
# ---------------------------------------------------------------------------

class CreateMedicalRecord:
    def __init__(self, repo: MedicalRecordRepository):
        self._repo = repo

    def execute(self, inp: CreateMedicalRecordInput) -> MedicalRecord:
        assert_can_create_record(inp.actor_role)
        record = MedicalRecord(
            id=uuid.uuid4(),
            athlete_user_id=inp.athlete_user_id,
            team_id=inp.team_id,
            record_date=inp.record_date,
            record_label=inp.record_label,
            assessment_summary=inp.assessment_summary,
            restriction_summary=inp.restriction_summary,
            return_to_training_authorized=inp.return_to_training_authorized,
            return_to_play_authorized=inp.return_to_play_authorized,
            clinical_notes=inp.clinical_notes,
        )
        record.validate_invariants()
        return self._repo.save(record)


class ListMedicalRecords:
    def __init__(self, repo: MedicalRecordRepository):
        self._repo = repo

    def execute(self, inp: ListMedicalRecordsInput) -> ListMedicalRecordsResult:
        athlete_filter = inp.athlete_user_id
        # BOLA: athlete só vê seus próprios registros
        if inp.actor_role == RoleLabel.ATHLETE:
            athlete_filter = inp.actor_user_id
        elif inp.actor_role == RoleLabel.MEMBER:
            raise InsufficientPrivilege("PERM-MED: member não pode listar registros médicos.")

        records, next_token = self._repo.list_records(
            athlete_user_id=athlete_filter,
            team_id=inp.team_id,
            record_date_from=inp.record_date_from,
            record_date_to=inp.record_date_to,
            authorization_status=inp.authorization_status,
            page_token=inp.page_token,
            page_size=inp.page_size,
        )

        # BOLA pós-leitura: coach filtra apenas atletas do seu time
        if inp.actor_role == RoleLabel.COACH:
            records = [r for r in records if r.athlete_user_id in inp.actor_team_athlete_ids]

        return ListMedicalRecordsResult(data=records, next_page_token=next_token)


class GetMedicalRecord:
    def __init__(self, repo: MedicalRecordRepository):
        self._repo = repo

    def execute(
        self,
        role: RoleLabel,
        actor_user_id: uuid.UUID,
        record_id: uuid.UUID,
        actor_team_athlete_ids: Optional[List[uuid.UUID]] = None,
    ) -> MedicalRecord:
        record = self._repo.get_by_id(record_id)
        if record is None:
            raise MedicalRecordNotFound(f"Registro médico {record_id} não encontrado.")
        assert_can_read_record(role, actor_user_id, record.athlete_user_id, actor_team_athlete_ids)
        return record


class UpdateMedicalRecord:
    def __init__(self, repo: MedicalRecordRepository):
        self._repo = repo

    def execute(self, record_id: uuid.UUID, inp: UpdateMedicalRecordInput) -> MedicalRecord:
        assert_can_update_record(inp.actor_role)
        record = self._repo.get_by_id(record_id)
        if record is None:
            raise MedicalRecordNotFound(f"Registro médico {record_id} não encontrado.")
        assert_can_read_record(
            inp.actor_role, inp.actor_user_id, record.athlete_user_id, inp.actor_team_athlete_ids
        )
        # Aplicar campos opcionais
        if inp.record_date is not None:
            record.record_date = inp.record_date
        if inp.record_label is not None:
            record.record_label = inp.record_label
        if inp.assessment_summary is not None:
            record.assessment_summary = inp.assessment_summary
        if inp.restriction_summary is not None:
            record.restriction_summary = inp.restriction_summary
        if inp.return_to_training_authorized is not None:
            record.return_to_training_authorized = inp.return_to_training_authorized
        if inp.return_to_play_authorized is not None:
            record.return_to_play_authorized = inp.return_to_play_authorized
        if inp.clinical_notes is not None:
            record.clinical_notes = inp.clinical_notes
        record.validate_invariants()
        return self._repo.save(record)


class DeleteMedicalRecord:
    def __init__(self, repo: MedicalRecordRepository):
        self._repo = repo

    def execute(self, role: RoleLabel, record_id: uuid.UUID) -> None:
        assert_can_delete_record(role)
        found = self._repo.soft_delete(record_id)
        if not found:
            raise MedicalRecordNotFound(f"Registro médico {record_id} não encontrado.")
