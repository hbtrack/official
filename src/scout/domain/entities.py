from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID

VALID_EVENT_LABELS = frozenset({
    "GOAL", "SHOT_ON_TARGET", "SHOT_OFF_TARGET", "SHOT_BLOCKED",
    "FAST_BREAK", "BREAKTHROUGH", "PIVOT_PLAY", "WING_PLAY",
    "ASSIST", "SEVEN_METER_THROW",
    "STEAL", "BLOCK", "INTERCEPTION", "GOALKEEPER_SAVE",
    "TURNOVER", "TECHNICAL_FAULT", "BAD_PASS",
    "TWO_MINUTE_SUSPENSION", "YELLOW_CARD", "RED_CARD", "BLUE_CARD",
    "TIMEOUT", "EMPTY_GOAL", "SUBSTITUTION",
    "DEFENSIVE_SYSTEM_CHANGE", "OFFENSIVE_SYSTEM_CHANGE",
})

VALID_TAG_LABELS = frozenset({
    "left-wing", "right-wing", "left-back", "right-back",
    "center-back", "pivot", "six-meter", "nine-meter",
    "fast-break", "positional-attack", "power-play", "man-down",
    "equal-strength", "first-half", "second-half", "overtime",
})

VALID_CODING_SCHEMA_LABELS = frozenset({
    "match-event-v1", "match-review-v1",
})


@dataclass
class ScoutEvent:
    id: UUID
    match_id: UUID
    event_label: str
    recorded_at: datetime
    athlete_user_id: Optional[UUID] = None
    team_id: Optional[UUID] = None
    tag_labels: list = field(default_factory=list)
    clip_asset_refs: list = field(default_factory=list)
    coding_schema_label: Optional[str] = None
    tactical_aggregation_label: Optional[str] = None
    session_id: Optional[UUID] = None
    position_x: Optional[float] = None
    position_y: Optional[float] = None
    duration_ms: Optional[int] = None
    notes: Optional[str] = None
    metadata: Optional[dict] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def validate_invariants(self) -> None:
        if self.id is None:
            raise ValueError("id e obrigatorio")
        if self.match_id is None:
            raise ValueError("matchId e obrigatorio")
        if not self.event_label:
            raise ValueError("eventLabel e obrigatorio")
        if self.recorded_at is None:
            raise ValueError("recordedAt e obrigatorio")
        if self.event_label not in VALID_EVENT_LABELS:
            raise ValueError(f"eventLabel '{self.event_label}' nao pertence a taxonomia canonica")
        for tag in self.tag_labels:
            if tag not in VALID_TAG_LABELS:
                raise ValueError(f"tagLabel '{tag}' nao pertence a taxonomia canonica")
        if self.coding_schema_label is not None:
            if self.coding_schema_label not in VALID_CODING_SCHEMA_LABELS:
                raise ValueError(f"codingSchemaLabel '{self.coding_schema_label}' nao pertence a taxonomia canonica")
        if len(self.tag_labels) != len(set(self.tag_labels)):
            raise ValueError("tagLabels nao pode conter duplicatas")
        if len(self.clip_asset_refs) != len(set(self.clip_asset_refs)):
            raise ValueError("clipAssetRefs nao pode conter duplicatas")
