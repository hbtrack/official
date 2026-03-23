from __future__ import annotations
import uuid
from datetime import date, datetime
from typing import List, Optional

from ninja import Schema

from medical.domain.entities import MedicalRecord


class MedicalRecordOut(Schema):
    id: uuid.UUID
    athleteUserId: uuid.UUID
    teamId: Optional[uuid.UUID] = None
    recordDate: date
    recordLabel: str
    assessmentSummary: Optional[str] = None
    restrictionSummary: Optional[str] = None
    returnToTrainingAuthorized: Optional[bool] = None
    returnToPlayAuthorized: Optional[bool] = None
    clinicalNotes: Optional[str] = None
    isDeleted: bool
    createdAt: datetime
    updatedAt: datetime

    @classmethod
    def from_domain(cls, r: MedicalRecord) -> "MedicalRecordOut":
        return cls(
            id=r.id,
            athleteUserId=r.athlete_user_id,
            teamId=r.team_id,
            recordDate=r.record_date,
            recordLabel=r.record_label,
            assessmentSummary=r.assessment_summary,
            restrictionSummary=r.restriction_summary,
            returnToTrainingAuthorized=r.return_to_training_authorized,
            returnToPlayAuthorized=r.return_to_play_authorized,
            clinicalNotes=r.clinical_notes,
            isDeleted=r.is_deleted,
            createdAt=r.created_at,
            updatedAt=r.updated_at,
        )


class MedicalRecordListOut(Schema):
    data: List[MedicalRecordOut]
    nextPageToken: Optional[str] = None


class CreateMedicalRecordIn(Schema):
    athleteUserId: uuid.UUID
    teamId: Optional[uuid.UUID] = None
    recordDate: date
    recordLabel: str
    assessmentSummary: Optional[str] = None
    restrictionSummary: Optional[str] = None
    returnToTrainingAuthorized: Optional[bool] = None
    returnToPlayAuthorized: Optional[bool] = None
    clinicalNotes: Optional[str] = None


class UpdateMedicalRecordIn(Schema):
    recordDate: Optional[date] = None
    recordLabel: Optional[str] = None
    assessmentSummary: Optional[str] = None
    restrictionSummary: Optional[str] = None
    returnToTrainingAuthorized: Optional[bool] = None
    returnToPlayAuthorized: Optional[bool] = None
    clinicalNotes: Optional[str] = None


class ErrorOut(Schema):
    detail: str
