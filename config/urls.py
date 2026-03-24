"""
URL configuration — HB Track
Monta os routers Django Ninja de cada módulo.
"""
import json

from django.http import HttpResponse
from django.urls import path
from ninja import NinjaAPI

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

    payload = json.dumps({"status": "ok" if http_status == 200 else "degraded", "db": db_status, "redis": redis_status})
    return HttpResponse(payload, content_type="application/json", status=http_status)


urlpatterns = [
    path("health", health_check),
    path("api/", api.urls),
]
