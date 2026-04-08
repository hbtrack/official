from __future__ import annotations
from typing import Optional
from uuid import UUID

from ninja import Router
from ninja.errors import HttpError
from django.http import HttpRequest

# CODEGEN CUTOVER — generated use cases linked
from .generated.application import use_cases as _gen_use_cases  # noqa: F401
from .generated.infrastructure import repository as _gen_repository  # noqa: F401


from .schemas import (
    SnapshotOut, SnapshotListOut, CreateSnapshotIn,
    DashboardOut, DashboardListOut,
    QueryRequestIn, QueryResponseOut, ErrorOut,

)
from .domain.entities import AnalyticsQueryRequest
from .domain.rules import RoleLabel, InsufficientPrivilege, SnapshotNotFound
from .infrastructure.repository import AnalyticsRepository
from .application.use_cases import (
    ListAnalyticsSnapshots, CreateAnalyticsSnapshot, GetAnalyticsSnapshot,
    ListAnalyticsDashboards, QueryAnalyticsData,
)

router = Router()
_repo = AnalyticsRepository()
_list_uc = ListAnalyticsSnapshots(_repo)
_create_uc = CreateAnalyticsSnapshot(_repo)
_get_uc = GetAnalyticsSnapshot(_repo)
_dashboards_uc = ListAnalyticsDashboards(_repo)
_query_uc = QueryAnalyticsData(_repo)

def _role(request: HttpRequest) -> RoleLabel:
    """Extrai RoleLabel do JWT validado."""
    role = getattr(request, "_actor_role", None)
    if role:
        try:
            return RoleLabel(role)
        except ValueError:
            return RoleLabel.MEMBER
    raise HttpError(401, "Unauthenticated")

def _uid(request: HttpRequest) -> UUID:
    """Extrai actor_id do JWT validado."""
    actor_id = getattr(request, "_actor_id", None)
    if actor_id:
        return UUID(str(actor_id))
    raise HttpError(401, "Unauthenticated")

@router.get("/snapshots", response={200: SnapshotListOut, 401: ErrorOut, 403: ErrorOut, 422: ErrorOut})
def list_snapshots(
    request: HttpRequest,
    sourceModule: Optional[str] = None,
    metricKey: Optional[str] = None,
    timeWindow: Optional[str] = None,
    granularity: Optional[str] = None,
    dateFrom: Optional[str] = None,
    dateTo: Optional[str] = None,
    pageSize: int = 20,
    pageToken: Optional[str] = None,
):
    try:
        role = _role(request)
        requester_id = _uid(request)
        snapshots, next_token = _list_uc.execute(
            role=role, requester_id=requester_id,
            source_module=sourceModule, metric_key=metricKey,
            time_window=timeWindow, granularity=granularity,
            date_from=dateFrom, date_to=dateTo,
            page_size=pageSize, page_token=pageToken,
        )
        return 200, SnapshotListOut(
            data=[SnapshotOut.from_domain(s) for s in snapshots],
            nextPageToken=next_token,
        )
    except InsufficientPrivilege as e:
        return 403, ErrorOut(detail=str(e))
    except ValueError as e:
        return 422, ErrorOut(detail=str(e))

@router.post("/snapshots", response={201: SnapshotOut, 400: ErrorOut, 401: ErrorOut, 403: ErrorOut, 422: ErrorOut})
def create_snapshot(request: HttpRequest, payload: CreateSnapshotIn):
    try:
        role = _role(request)
        requester_id = _uid(request)
        snapshot = _create_uc.execute(
            role=role, requester_id=requester_id,
            metric_key=payload.metricKey,
            source_module_labels=payload.sourceModuleLabels,
            time_window_label=payload.timeWindowLabel,
            granularity_label=payload.granularityLabel,
            refresh_mode_label=payload.refreshModeLabel,
            filter_summary=payload.filterSummary,
            projection_key=payload.projectionKey,
        )
        return 201, SnapshotOut.from_domain(snapshot)
    except InsufficientPrivilege as e:
        return 403, ErrorOut(detail=str(e))
    except ValueError as e:
        return 422, ErrorOut(detail=str(e))

@router.get("/snapshots/{snapshot_id}", response={200: SnapshotOut, 401: ErrorOut, 403: ErrorOut, 404: ErrorOut})
def get_snapshot(request: HttpRequest, snapshot_id: UUID):
    try:
        role = _role(request)
        requester_id = _uid(request)
        snapshot = _get_uc.execute(role=role, requester_id=requester_id, snapshot_id=snapshot_id)
        return 200, SnapshotOut.from_domain(snapshot)
    except SnapshotNotFound as e:
        return 404, ErrorOut(detail=str(e))
    except InsufficientPrivilege as e:
        return 403, ErrorOut(detail=str(e))

@router.get("/dashboards", response={200: DashboardListOut, 401: ErrorOut, 403: ErrorOut})
def list_dashboards(
    request: HttpRequest,
    projectionType: Optional[str] = None,
    pageSize: int = 20,
    pageToken: Optional[str] = None,
):
    try:
        role = _role(request)
        dashboards, next_token = _dashboards_uc.execute(
            role=role, projection_type=projectionType,
            page_size=pageSize, page_token=pageToken,
        )
        return 200, DashboardListOut(
            data=[DashboardOut.from_domain(d) for d in dashboards],
            nextPageToken=next_token,
        )
    except InsufficientPrivilege as e:
        return 403, ErrorOut(detail=str(e))

@router.post("/query", response={200: QueryResponseOut, 400: ErrorOut, 401: ErrorOut, 403: ErrorOut, 422: ErrorOut, 409: ErrorOut})
def query_analytics(request: HttpRequest, payload: QueryRequestIn):
    try:
        role = _role(request)
        filters_dict = {}
        if payload.filters.teamIds is not None:
            filters_dict["teamIds"] = [str(t) for t in payload.filters.teamIds]
        if payload.filters.athleteIds is not None:
            filters_dict["athleteIds"] = [str(a) for a in payload.filters.athleteIds]
        query = AnalyticsQueryRequest(
            scope=payload.scope,
            source_modules=payload.sourceModules,
            metric_keys=payload.metricKeys,
            time_window=payload.timeWindow,
            granularity=payload.granularity,
            filters=filters_dict,
            date_from=payload.dateFrom,
            date_to=payload.dateTo,
        )
        result = _query_uc.execute(role=role, request=query)
        return 200, QueryResponseOut(**result)
    except InsufficientPrivilege as e:
        return 403, ErrorOut(detail=str(e))
    except ValueError as e:
        return 422, ErrorOut(detail=str(e))
