"""
URL configuration — HB Track
Monta os routers Django Ninja de cada módulo.
"""
import json
import uuid

from django.http import HttpResponse
from django.urls import path
from ninja import NinjaAPI
from ninja.errors import HttpError, ValidationError as NinjaValidationError

from shared.middleware import get_current_flow_id

from video.api import router as video_router
from identity_access.api import router as identity_access_router
from users.api import router as users_router
from teams.api import router as teams_router
from seasons.api import router as seasons_router
from training.api import router as training_router
from competitions.api import router as competitions_router
from wellness.api import router as wellness_router
from medical.api import router as medical_router
from matches.api import router as matches_router
from scout.api import router as scout_router
from exercises.api import router as exercises_router
from analytics.api import router as analytics_router
from reports.api import router as reports_router
from ai_ingestion.api import router as ingestion_router
from audit.api import router as audit_router
from notifications.api import router as notifications_router

api = NinjaAPI(title="HB Track API", version="1.0.0")

# ---------------------------------------------------------------------------
# Exception handlers globais — garante que TODOS os erros retornam RFC 9457
# ProblemOut com Content-Type: application/problem+json, conforme os contratos
# OpenAPI declaram para respostas 4xx/5xx.
# ---------------------------------------------------------------------------

_HTTP_STATUS_TITLES: dict[int, str] = {
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    409: "Conflict",
    422: "Unprocessable Entity",
    429: "Too Many Requests",
    500: "Internal Server Error",
}


def _problem_response(status: int, detail: str) -> HttpResponse:
    title = _HTTP_STATUS_TITLES.get(status, "Error")
    flow_id = get_current_flow_id()
    body = json.dumps({
        "type": f"https://hbtrack.app/errors/{status}",
        "title": title,
        "status": status,
        "traceId": flow_id,
        "detail": detail,
    })
    return HttpResponse(body, content_type="application/problem+json", status=status)


@api.exception_handler(HttpError)
def _on_http_error(request, exc: HttpError) -> HttpResponse:
    """Converte HttpError para ProblemOut RFC 9457."""
    return _problem_response(exc.status_code, str(exc.message))


@api.exception_handler(NinjaValidationError)
def _on_validation_error(request, exc: NinjaValidationError) -> HttpResponse:
    """Converte erros de validação Pydantic/Ninja para ProblemOut RFC 9457.

    O campo ``detail`` é uma string legível (RFC 9457 §3.1), não uma lista.
    """
    errors = exc.errors if hasattr(exc, "errors") else []
    parts: list[str] = []
    for e in errors if isinstance(errors, list) else []:
        if isinstance(e, dict):
            loc = ".".join(str(segment) for segment in e.get("loc", []))
            msg = e.get("msg", "")
            parts.append(f"{loc}: {msg}" if loc else msg)
        else:
            parts.append(str(e))
    detail = "; ".join(parts) or "Validation failed"
    return _problem_response(422, detail)

api.add_router("/video", video_router)
api.add_router("/auth", identity_access_router)
api.add_router("/users", users_router)
api.add_router("/teams", teams_router)
api.add_router("/seasons", seasons_router)
api.add_router("/training", training_router)
api.add_router("/competitions", competitions_router)
api.add_router("/wellness", wellness_router)
api.add_router("/medical", medical_router)
api.add_router("/matches", matches_router)
api.add_router("/scout", scout_router)
api.add_router("/exercises", exercises_router)
api.add_router("/analytics", analytics_router)
api.add_router("/reports", reports_router)
api.add_router("/ingestion", ingestion_router)
api.add_router("/audit", audit_router)
api.add_router("/notifications", notifications_router)


def health_check(request):
    """GET /health — verifica PostgreSQL e Redis."""
    import django.db
    import redis as redis_lib
    import os

    db_status = "ok"
    redis_status = "ok"
    http_status = 200

    try:
        django.db.connection.ensure_connection()
    except Exception:
        db_status = "error"
        http_status = 503

    try:
        redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
        r = redis_lib.from_url(redis_url, socket_connect_timeout=2)
        r.ping()
    except Exception:
        redis_status = "error"
        http_status = 503

    payload = json.dumps({
        "status": "ok" if http_status == 200 else "degraded",
        "db": db_status,
        "redis": redis_status,
        "buildSha": os.environ.get("HB_BUILD_SHA", "unknown"),
    })
    return HttpResponse(payload, content_type="application/json", status=http_status)


urlpatterns = [
    path("health", health_check),
    path("api/", api.urls),
]
