from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from uuid import UUID

VALID_METRIC_KEYS = frozenset(["READINESS_SCORE", "DROPOUT_RISK_SIGNAL", "ENGAGEMENT_SIGNAL"])
VALID_SOURCE_MODULES = frozenset(["TRAINING", "WELLNESS"])
VALID_TIME_WINDOWS = frozenset(["LAST_7_DAYS", "LAST_14_DAYS", "LAST_28_DAYS", "LAST_90_DAYS", "LAST_YEAR", "CUSTOM"])
VALID_GRANULARITIES = frozenset(["DAILY", "WEEKLY", "MONTHLY"])
VALID_REFRESH_MODES = frozenset(["scheduled", "on_demand", "streaming"])
VALID_PROJECTION_TYPES = frozenset(["team_overview", "athlete_readiness", "injury_risk", "training_load", "performance_trend"])
VALID_QUERY_SCOPES = frozenset(["TEAM", "ATHLETE"])


@dataclass
class AnalyticsSnapshot:
    id: UUID
    metric_key: str
    computed_at: datetime
    created_by_user_id: UUID
    source_module_labels: List[str] = field(default_factory=list)
    time_window_label: Optional[str] = None
    granularity_label: Optional[str] = None
    filter_summary: Optional[str] = None
    projection_key: Optional[str] = None
    refresh_mode_label: Optional[str] = None

    def validate_invariants(self) -> None:
        if not self.id:
            raise ValueError("INV-ANL-001: id is required")
        if not self.metric_key:
            raise ValueError("INV-ANL-001: metricKey is required")
        if not self.computed_at:
            raise ValueError("INV-ANL-001: computedAt is required")
        if self.metric_key not in VALID_METRIC_KEYS:
            raise ValueError("INV-ANL-005: metricKey not in canonical catalog")
        if len(self.source_module_labels) != len(set(self.source_module_labels)):
            raise ValueError("INV-ANL-002: sourceModuleLabels must have no duplicates")
        for label in self.source_module_labels:
            if label not in VALID_SOURCE_MODULES:
                raise ValueError("DR-ANL-009: sourceModule not in canonical catalog")


@dataclass
class AnalyticsDashboard:
    projection_key: str
    projection_type: str
    display_name: str
    description: str
    source_module_labels: List[str]


@dataclass
class AnalyticsQueryRequest:
    scope: str
    source_modules: List[str]
    metric_keys: List[str]
    time_window: str
    granularity: str
    filters: dict
    date_from: Optional[str] = None
    date_to: Optional[str] = None

    def validate_invariants(self) -> None:
        if self.time_window == "CUSTOM":
            if not self.date_from or not self.date_to:
                raise ValueError("INV-ANL-006: timeWindow=CUSTOM requires dateFrom and dateTo")
        else:
            if self.date_from or self.date_to:
                raise ValueError("INV-ANL-006: dateFrom/dateTo only allowed with timeWindow=CUSTOM")
        if self.scope == "TEAM" and "teamIds" not in self.filters:
            raise ValueError("INV-ANL-007: scope=TEAM requires filters.teamIds")
        if self.scope == "ATHLETE" and "athleteIds" not in self.filters:
            raise ValueError("INV-ANL-007: scope=ATHLETE requires filters.athleteIds")
        for key in self.metric_keys:
            if key not in VALID_METRIC_KEYS:
                raise ValueError("INV-ANL-005: metricKey not in canonical catalog")
        for mod in self.source_modules:
            if mod not in VALID_SOURCE_MODULES:
                raise ValueError("DR-ANL-009: sourceModule not supported")
