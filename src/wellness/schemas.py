from __future__ import annotations
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from ninja import Schema


class WellnessEntryOut(Schema):
    entryId: uuid.UUID
    athleteUserId: uuid.UUID
    trainingSessionId: Optional[uuid.UUID] = None
    questionnaireDate: date
    questionnaireLabel: Optional[str] = None
    readinessScore: int
    fatigueScore: Optional[int] = None
    painScore: Optional[int] = None
    recoveryScore: Optional[int] = None
    sleepHours: Optional[Decimal] = None
    notes: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime

    @classmethod
    def from_domain(cls, e) -> "WellnessEntryOut":
        return cls(
            entryId=e.id,
            athleteUserId=e.athlete_user_id,
            trainingSessionId=e.training_session_id,
            questionnaireDate=e.questionnaire_date,
            questionnaireLabel=e.questionnaire_label,
            readinessScore=e.readiness_score,
            fatigueScore=e.fatigue_score,
            painScore=e.pain_score,
            recoveryScore=e.recovery_score,
            sleepHours=e.sleep_hours,
            notes=e.notes,
            createdAt=e.created_at,
            updatedAt=e.updated_at,
        )


class WellnessEntryListOut(Schema):
    data: List[WellnessEntryOut]
    page: int
    pageSize: int
    total: int


class CreateWellnessEntryIn(Schema):
    athleteUserId: uuid.UUID
    questionnaireDate: date
    readinessScore: int
    trainingSessionId: Optional[uuid.UUID] = None
    questionnaireLabel: Optional[str] = None
    fatigueScore: Optional[int] = None
    painScore: Optional[int] = None
    recoveryScore: Optional[int] = None
    sleepHours: Optional[Decimal] = None
    notes: Optional[str] = None


class WellnessSummaryOut(Schema):
    athleteUserId: uuid.UUID
    dateFrom: date
    dateTo: date
    entryCount: int
    avgReadiness: Optional[Decimal] = None
    avgFatigue: Optional[Decimal] = None
    avgPain: Optional[Decimal] = None
    avgRecovery: Optional[Decimal] = None
    avgSleepHours: Optional[Decimal] = None
    readinessTrend: Optional[str] = None
    highPainAlert: bool = False

    @classmethod
    def from_domain(cls, s) -> "WellnessSummaryOut":
        return cls(
            athleteUserId=s.athlete_user_id,
            dateFrom=s.date_from,
            dateTo=s.date_to,
            entryCount=s.entry_count,
            avgReadiness=s.avg_readiness,
            avgFatigue=s.avg_fatigue,
            avgPain=s.avg_pain,
            avgRecovery=s.avg_recovery,
            avgSleepHours=s.avg_sleep_hours,
            readinessTrend=s.readiness_trend,
            highPainAlert=s.high_pain_alert,
        )


class ErrorOut(Schema):
    detail: str
