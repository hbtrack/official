from __future__ import annotations
from uuid import UUID
from typing import List, Optional, Tuple
from datetime import datetime, timezone

from ..domain.entities import (
    AnalyticsSnapshot, AnalyticsDashboard, VALID_PROJECTION_TYPES,
)
from .models import AnalyticsSnapshotModel

# Static catalog of platform-defined dashboards (DR-ANL-001: analytics owns projections)
BUILTIN_DASHBOARDS: List[AnalyticsDashboard] = [
    AnalyticsDashboard(
        projection_key="team-load-overview",
        projection_type="team_overview",
        display_name="Team Load Overview",
        description="Weekly training load and readiness signals for the full squad.",
        source_module_labels=["TRAINING", "WELLNESS"],
    ),
    AnalyticsDashboard(
        projection_key="athlete-readiness-tracker",
        projection_type="athlete_readiness",
        display_name="Athlete Readiness Tracker",
        description="Individual readiness and engagement trends per athlete.",
        source_module_labels=["WELLNESS", "TRAINING"],
    ),
    AnalyticsDashboard(
        projection_key="dropout-risk-monitor",
        projection_type="injury_risk",
        display_name="Dropout Risk Monitor",
        description="Early-signal dropout risk dashboard derived from training and wellness data.",
        source_module_labels=["TRAINING", "WELLNESS"],
    ),
    AnalyticsDashboard(
        projection_key="training-load-distribution",
        projection_type="training_load",
        display_name="Training Load Distribution",
        description="Load distribution and progression trends across training sessions.",
        source_module_labels=["TRAINING"],
    ),
    AnalyticsDashboard(
        projection_key="performance-trend-analysis",
        projection_type="performance_trend",
        display_name="Performance Trend Analysis",
        description="Multi-metric trend analysis for performance evaluation.",
        source_module_labels=["TRAINING", "WELLNESS"],
    ),
]


def _snapshot_from_model(m: AnalyticsSnapshotModel) -> AnalyticsSnapshot:
    return AnalyticsSnapshot(
        id=m.id,
        metric_key=m.metric_key,
        source_module_labels=m.source_module_labels or [],
        time_window_label=m.time_window_label,
        granularity_label=m.granularity_label,
        filter_summary=m.filter_summary,
        projection_key=m.projection_key,
        refresh_mode_label=m.refresh_mode_label,
        computed_at=m.computed_at,
        created_by_user_id=m.created_by_user_id,
    )


class AnalyticsRepository:
    def save(self, snapshot: AnalyticsSnapshot) -> AnalyticsSnapshot:
        obj, _ = AnalyticsSnapshotModel.objects.update_or_create(
            id=snapshot.id,
            defaults={
                "metric_key": snapshot.metric_key,
                "source_module_labels": snapshot.source_module_labels,
                "time_window_label": snapshot.time_window_label,
                "granularity_label": snapshot.granularity_label,
                "filter_summary": snapshot.filter_summary,
                "projection_key": snapshot.projection_key,
                "refresh_mode_label": snapshot.refresh_mode_label,
                "computed_at": snapshot.computed_at,
                "created_by_user_id": snapshot.created_by_user_id,
            },
        )
        return _snapshot_from_model(obj)

    def get_by_id(self, snapshot_id: UUID) -> Optional[AnalyticsSnapshot]:
        try:
            return _snapshot_from_model(AnalyticsSnapshotModel.objects.get(id=snapshot_id))
        except AnalyticsSnapshotModel.DoesNotExist:
            return None

    def list_snapshots(
        self,
        requester_id: Optional[UUID] = None,
        is_athlete: bool = False,
        source_module: Optional[str] = None,
        metric_key: Optional[str] = None,
        time_window: Optional[str] = None,
        granularity: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        page_size: int = 20,
        page_token: Optional[str] = None,
    ) -> Tuple[List[AnalyticsSnapshot], Optional[str]]:
        qs = AnalyticsSnapshotModel.objects.all()
        if is_athlete and requester_id:
            qs = qs.filter(created_by_user_id=requester_id)
        if source_module:
            qs = qs.filter(source_module_labels__contains=[source_module])
        if metric_key:
            qs = qs.filter(metric_key=metric_key)
        if time_window:
            qs = qs.filter(time_window_label=time_window)
        if granularity:
            qs = qs.filter(granularity_label=granularity)
        if date_from:
            qs = qs.filter(computed_at__date__gte=date_from)
        if date_to:
            qs = qs.filter(computed_at__date__lte=date_to)

        offset = 0
        if page_token:
            try:
                offset = int(page_token)
            except ValueError:
                offset = 0

        total = qs.count()
        items = qs[offset: offset + page_size]
        snapshots = [_snapshot_from_model(m) for m in items]
        next_token = str(offset + page_size) if (offset + page_size) < total else None
        return snapshots, next_token

    def list_dashboards(
        self,
        projection_type: Optional[str] = None,
        page_size: int = 20,
        page_token: Optional[str] = None,
    ) -> Tuple[List[AnalyticsDashboard], Optional[str]]:
        dashboards = BUILTIN_DASHBOARDS
        if projection_type:
            dashboards = [d for d in dashboards if d.projection_type == projection_type]
        offset = 0
        if page_token:
            try:
                offset = int(page_token)
            except ValueError:
                offset = 0
        page = dashboards[offset: offset + page_size]
        next_token = str(offset + page_size) if (offset + page_size) < len(dashboards) else None
        return page, next_token
