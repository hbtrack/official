from __future__ import annotations
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from ..domain.entities import (
    AnalyticsSnapshot, AnalyticsDashboard, AnalyticsQueryRequest,
    VALID_SOURCE_MODULES, VALID_METRIC_KEYS,
)
from ..domain.rules import (
    RoleLabel, InsufficientPrivilege, SnapshotNotFound,
    assert_can_create_snapshot, assert_can_list_snapshots,
    assert_can_get_snapshot, assert_can_list_dashboards,
    assert_can_query_analytics,
)
from ..infrastructure.repository import AnalyticsRepository


class ListAnalyticsSnapshots:
    def __init__(self, repo: AnalyticsRepository):
        self.repo = repo

    def execute(
        self, role: RoleLabel, requester_id: UUID,
        source_module: Optional[str] = None,
        metric_key: Optional[str] = None,
        time_window: Optional[str] = None,
        granularity: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        page_size: int = 20,
        page_token: Optional[str] = None,
    ):
        assert_can_list_snapshots(role)
        is_athlete = role == RoleLabel.ATHLETE
        return self.repo.list_snapshots(
            requester_id=requester_id,
            is_athlete=is_athlete,
            source_module=source_module,
            metric_key=metric_key,
            time_window=time_window,
            granularity=granularity,
            date_from=date_from,
            date_to=date_to,
            page_size=page_size,
            page_token=page_token,
        )


class CreateAnalyticsSnapshot:
    def __init__(self, repo: AnalyticsRepository):
        self.repo = repo

    def execute(
        self, role: RoleLabel, requester_id: UUID,
        metric_key: str,
        source_module_labels: List[str],
        time_window_label: str,
        granularity_label: str,
        refresh_mode_label: str,
        filter_summary: Optional[str] = None,
        projection_key: Optional[str] = None,
    ) -> AnalyticsSnapshot:
        assert_can_create_snapshot(role)
        snapshot = AnalyticsSnapshot(
            id=uuid.uuid4(),
            metric_key=metric_key,
            source_module_labels=source_module_labels,
            time_window_label=time_window_label,
            granularity_label=granularity_label,
            filter_summary=filter_summary,
            projection_key=projection_key,
            refresh_mode_label=refresh_mode_label,
            computed_at=datetime.now(timezone.utc),
            created_by_user_id=requester_id,
        )
        snapshot.validate_invariants()
        return self.repo.save(snapshot)


class GetAnalyticsSnapshot:
    def __init__(self, repo: AnalyticsRepository):
        self.repo = repo

    def execute(self, role: RoleLabel, requester_id: UUID, snapshot_id: UUID) -> AnalyticsSnapshot:
        snapshot = self.repo.get_by_id(snapshot_id)
        if snapshot is None:
            raise SnapshotNotFound(f"Snapshot {snapshot_id} not found")
        assert_can_get_snapshot(role, snapshot, requester_id)
        return snapshot


class ListAnalyticsDashboards:
    def __init__(self, repo: AnalyticsRepository):
        self.repo = repo

    def execute(
        self, role: RoleLabel,
        projection_type: Optional[str] = None,
        page_size: int = 20,
        page_token: Optional[str] = None,
    ):
        assert_can_list_dashboards(role)
        return self.repo.list_dashboards(
            projection_type=projection_type,
            page_size=page_size,
            page_token=page_token,
        )


class QueryAnalyticsData:
    def __init__(self, repo: AnalyticsRepository):
        self.repo = repo

    def execute(
        self, role: RoleLabel,
        request: AnalyticsQueryRequest,
    ) -> dict:
        assert_can_query_analytics(role)
        request.validate_invariants()
        # DR-ANL-008: deterministic fixed envelope; returns empty rows for now
        # (full cross-module computation is out-of-scope for this implementation phase)
        computed_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        return {
            "data": [],
            "resultCount": 0,
            "computedAt": computed_at,
        }
