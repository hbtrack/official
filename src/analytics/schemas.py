from __future__ import annotations
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from ninja import Schema

# CODEGEN CUTOVER — generated layer linked
from .generated import schemas as _gen_schemas  # noqa: F401


class SnapshotOut(Schema):
    id: UUID
    metric_key: str
    source_module_labels: List[str]
    time_window_label: Optional[str] = None
    granularity_label: Optional[str] = None
    filter_summary: Optional[str] = None
    projection_key: Optional[str] = None
    refresh_mode_label: Optional[str] = None
    computed_at: datetime
    created_by_user_id: UUID

    @classmethod
    def from_domain(cls, snapshot) -> "SnapshotOut":
        return cls(
            id=snapshot.id,
            metric_key=snapshot.metric_key,
            source_module_labels=snapshot.source_module_labels,
            time_window_label=snapshot.time_window_label,
            granularity_label=snapshot.granularity_label,
            filter_summary=snapshot.filter_summary,
            projection_key=snapshot.projection_key,
            refresh_mode_label=snapshot.refresh_mode_label,
            computed_at=snapshot.computed_at,
            created_by_user_id=snapshot.created_by_user_id,
        )

class SnapshotListOut(Schema):
    data: List[SnapshotOut]
    nextPageToken: Optional[str] = None

class CreateSnapshotIn(Schema):
    metricKey: str
    sourceModuleLabels: List[str]
    timeWindowLabel: str
    granularityLabel: str
    refreshModeLabel: str
    filterSummary: Optional[str] = None
    projectionKey: Optional[str] = None

class DashboardOut(Schema):
    projectionKey: str
    projectionType: str
    displayName: str
    description: str
    sourceModuleLabels: List[str]

    @classmethod
    def from_domain(cls, d) -> "DashboardOut":
        return cls(
            projectionKey=d.projection_key,
            projectionType=d.projection_type,
            displayName=d.display_name,
            description=d.description,
            sourceModuleLabels=d.source_module_labels,
        )

class DashboardListOut(Schema):
    data: List[DashboardOut]
    nextPageToken: Optional[str] = None

class QueryFiltersIn(Schema):
    teamIds: Optional[List[UUID]] = None
    athleteIds: Optional[List[UUID]] = None

class QueryRequestIn(Schema):
    scope: str
    sourceModules: List[str]
    metricKeys: List[str]
    timeWindow: str
    granularity: str
    filters: QueryFiltersIn
    dateFrom: Optional[str] = None
    dateTo: Optional[str] = None

class QueryRowOut(Schema):
    metricKey: str
    scope: str
    teamId: Optional[UUID] = None
    athleteId: Optional[UUID] = None
    bucketStartDate: str
    bucketEndDate: str
    granularity: str
    value: float
    sourceModuleLabels: List[str]
    computedAt: str

class QueryResponseOut(Schema):
    data: List[QueryRowOut]
    resultCount: int
    computedAt: str

class ErrorOut(Schema):
    detail: str
