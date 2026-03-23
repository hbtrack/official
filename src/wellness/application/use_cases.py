from __future__ import annotations
import uuid
from dataclasses import dataclass
from datetime import date, datetime, timezone, timedelta
from decimal import Decimal
from typing import List, Optional

from wellness.domain.entities import WellnessEntry, WellnessSummary
from wellness.domain.rules import (
    RoleLabel, WellnessEntryNotFound, InsufficientPrivilege,
    assert_can_create_entry, assert_can_read_entry, assert_can_read_athlete_wellness,
    check_high_pain_alert,
)
from wellness.infrastructure.repository import WellnessEntryRepository


@dataclass
class CreateWellnessEntryInput:
    actor_role: RoleLabel
    actor_user_id: uuid.UUID
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


class CreateWellnessEntry:
    def __init__(self, repo: WellnessEntryRepository):
        self._repo = repo

    def execute(self, inp: CreateWellnessEntryInput) -> WellnessEntry:
        assert_can_create_entry(inp.actor_role, inp.actor_user_id, inp.athlete_user_id)
        entry = WellnessEntry(
            id=uuid.uuid4(),
            athlete_user_id=inp.athlete_user_id,
            training_session_id=inp.training_session_id,
            questionnaire_date=inp.questionnaire_date,
            questionnaire_label=inp.questionnaire_label,
            readiness_score=inp.readiness_score,
            fatigue_score=inp.fatigue_score,
            pain_score=inp.pain_score,
            recovery_score=inp.recovery_score,
            sleep_hours=inp.sleep_hours,
            notes=inp.notes,
        )
        entry.validate_invariants()
        # PERM-WEL-004: pain_score >= 7 — alerta registrado no domínio
        if check_high_pain_alert(entry.pain_score):
            # Integração com training.attention_queue é feita externamente
            pass
        return self._repo.save(entry)


@dataclass
class ListWellnessEntriesInput:
    actor_role: RoleLabel
    actor_user_id: uuid.UUID
    athlete_user_id: Optional[uuid.UUID] = None
    questionnaire_date: Optional[date] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    questionnaire_label: Optional[str] = None
    actor_team_athlete_ids: Optional[List[uuid.UUID]] = None
    page: int = 1
    page_size: int = 20


@dataclass
class ListWellnessEntriesOutput:
    data: List[WellnessEntry]
    page: int
    page_size: int
    total: int


class ListWellnessEntries:
    def __init__(self, repo: WellnessEntryRepository):
        self._repo = repo

    def execute(self, inp: ListWellnessEntriesInput) -> ListWellnessEntriesOutput:
        # Aplicar BOLA: restringir athleteUserId ao próprio se athlete
        effective_athlete_id = inp.athlete_user_id
        if inp.actor_role == RoleLabel.ATHLETE:
            effective_athlete_id = inp.actor_user_id
        elif inp.actor_role == RoleLabel.MEMBER:
            raise InsufficientPrivilege("member não pode acessar entradas de wellness.")
        page_size = min(max(inp.page_size, 1), 100)
        items, total = self._repo.list_entries(
            athlete_user_id=effective_athlete_id,
            questionnaire_date=inp.questionnaire_date,
            date_from=inp.date_from,
            date_to=inp.date_to,
            questionnaire_label=inp.questionnaire_label,
            page=inp.page,
            page_size=page_size,
        )
        return ListWellnessEntriesOutput(data=items, page=inp.page, page_size=page_size, total=total)


class GetWellnessEntry:
    def __init__(self, repo: WellnessEntryRepository):
        self._repo = repo

    def execute(
        self,
        role: RoleLabel,
        actor_user_id: uuid.UUID,
        entry_id: uuid.UUID,
        actor_team_athlete_ids: Optional[List[uuid.UUID]] = None,
    ) -> WellnessEntry:
        entry = self._repo.get_by_id(entry_id)
        if entry is None:
            raise WellnessEntryNotFound(f"Entrada {entry_id} não encontrada.")
        assert_can_read_entry(role, actor_user_id, entry.athlete_user_id, actor_team_athlete_ids)
        return entry


@dataclass
class ListAthleteWellnessEntriesInput:
    actor_role: RoleLabel
    actor_user_id: uuid.UUID
    target_athlete_id: uuid.UUID
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    questionnaire_label: Optional[str] = None
    actor_team_athlete_ids: Optional[List[uuid.UUID]] = None
    page: int = 1
    page_size: int = 20


class ListAthleteWellnessEntries:
    def __init__(self, repo: WellnessEntryRepository):
        self._repo = repo

    def execute(self, inp: ListAthleteWellnessEntriesInput) -> ListWellnessEntriesOutput:
        assert_can_read_athlete_wellness(
            inp.actor_role, inp.actor_user_id, inp.target_athlete_id, inp.actor_team_athlete_ids
        )
        page_size = min(max(inp.page_size, 1), 100)
        items, total = self._repo.list_entries(
            athlete_user_id=inp.target_athlete_id,
            date_from=inp.date_from,
            date_to=inp.date_to,
            questionnaire_label=inp.questionnaire_label,
            page=inp.page,
            page_size=page_size,
        )
        return ListWellnessEntriesOutput(data=items, page=inp.page, page_size=page_size, total=total)


class GetAthleteWellnessSummary:
    def __init__(self, repo: WellnessEntryRepository):
        self._repo = repo

    def execute(
        self,
        role: RoleLabel,
        actor_user_id: uuid.UUID,
        target_athlete_id: uuid.UUID,
        date_from: Optional[date],
        date_to: Optional[date],
        actor_team_athlete_ids: Optional[List[uuid.UUID]] = None,
    ) -> WellnessSummary:
        assert_can_read_athlete_wellness(
            role, actor_user_id, target_athlete_id, actor_team_athlete_ids
        )
        from datetime import date as _date
        today = _date.today()
        df = date_from or (today - timedelta(days=7))
        dt = date_to or today
        return self._repo.compute_summary(target_athlete_id, df, dt)
