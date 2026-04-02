"""
FlowIDMiddleware — HB Track
Garante que todo request tenha um X-Flow-ID rastreável.
- Gera UUID v4 se o request não trazer o header.
- Propaga X-Flow-ID em todos os responses.
- Armazena no thread-local para ser usado em tasks Celery e logs.
"""
from __future__ import annotations

import threading
import uuid

_flow_store = threading.local()


def get_current_flow_id() -> str:
    """Retorna o flow_id da thread atual (ou gera um novo se não houver)."""
    fid = getattr(_flow_store, "flow_id", None)
    if not fid:
        fid = str(uuid.uuid4())
        _flow_store.flow_id = fid
    return fid


def set_flow_id(flow_id: str) -> None:
    _flow_store.flow_id = flow_id


class SecurityHeadersMiddleware:
    """
    Middleware que adiciona security headers em todos os responses Django.
    Complementa os headers já configurados no Nginx (HSTS é Nginx-only).
    OWASP API Security — headers de defesa em profundidade.
    """

    _HEADERS = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Referrer-Policy": "no-referrer-when-downgrade",
        "X-XSS-Protection": "1; mode=block",
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        for header, value in self._HEADERS.items():
            response.setdefault(header, value)
        return response


class FlowIDMiddleware:
    """Middleware Django ASGI/WSGI que propaga X-Flow-ID em cada request."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        flow_id = request.headers.get("X-Flow-ID") or str(uuid.uuid4())
        set_flow_id(flow_id)
        response = self.get_response(request)
        response["X-Flow-ID"] = flow_id
        return response


class JWTClaimsMiddleware:
    """
    Middleware Django que extrai claims do Bearer JWT e popula atributos do request.
    Deve vir DEPOIS do FlowIDMiddleware na cadeia.

    Popula (quando token válido):
      request._actor_id          — UUID do sub (para users/api.py)
      request._principal_user_id — mesmo UUID (para identity_access/api.py)
      request._session_id        — UUID da sessão do token
      request._actor_role        — primeiro role ou None
      request._role_labels       — lista de roles
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[len("Bearer "):]
            try:
                from src.identity_access.infrastructure.jwt_adapter import JWTAdapter
                import uuid as _uuid

                payload = JWTAdapter().verify_access_token(token)
                if payload:
                    sub = payload.get("sub")
                    session_id = payload.get("session_id")
                    roles = payload.get("roles") or []

                    if sub:
                        actor_uuid = _uuid.UUID(str(sub))
                        request._actor_id = actor_uuid
                        request._principal_user_id = actor_uuid
                    if session_id:
                        request._session_id = _uuid.UUID(str(session_id))
                    request._role_labels = roles
                    request._actor_role = roles[0] if roles else None
            except Exception:
                pass  # token inválido → atributos não preenchidos → 401 nos endpoints

        return self.get_response(request)


# ── Rate Limiting ─────────────────────────────────────────────────────────────

import time
from collections import defaultdict
from django.http import JsonResponse


class RateLimitMiddleware:
    """
    Rate limiter in-memory por IP (sliding window).

    Configuração via settings:
      RATE_LIMIT_REQUESTS  — máximo de requests por janela (default: 100)
      RATE_LIMIT_WINDOW    — segundos da janela (default: 60)
      RATE_LIMIT_AUTH_REQUESTS — máximo para /auth/ (default: 20)
      RATE_LIMIT_AUTH_WINDOW   — janela para /auth/ (default: 60)

    Retorna 429 + Problem+JSON (RFC 9457) quando excedido.
    OWASP API4:2023 — Unrestricted Resource Consumption.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self._buckets: dict[str, list[float]] = defaultdict(list)

        from django.conf import settings
        self._global_limit = getattr(settings, "RATE_LIMIT_REQUESTS", 100)
        self._global_window = getattr(settings, "RATE_LIMIT_WINDOW", 60)
        self._auth_limit = getattr(settings, "RATE_LIMIT_AUTH_REQUESTS", 20)
        self._auth_window = getattr(settings, "RATE_LIMIT_AUTH_WINDOW", 60)

    def _get_client_ip(self, request) -> str:
        # Usar o último hop de X-Forwarded-For, que é adicionado pelo proxy
        # confiável (Nginx via $proxy_add_x_forwarded_for). O primeiro hop é
        # controlado pelo cliente e pode ser forjado para bypassar rate limiting.
        # OWASP API4:2023 — X-Forwarded-For spoofing mitigation.
        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        if xff:
            return xff.split(",")[-1].strip()
        return request.META.get("REMOTE_ADDR", "unknown")

    def _is_rate_limited(self, key: str, limit: int, window: int) -> bool:
        now = time.monotonic()
        bucket = self._buckets[key]

        # Remover timestamps fora da janela
        cutoff = now - window
        self._buckets[key] = [ts for ts in bucket if ts > cutoff]
        bucket = self._buckets[key]

        if len(bucket) >= limit:
            return True

        bucket.append(now)
        return False

    def __call__(self, request):
        ip = self._get_client_ip(request)
        path = request.path_info

        # Endpoints de autenticação têm limite mais restrito
        if path.startswith("/api/auth/"):
            key = f"auth:{ip}"
            limit, window = self._auth_limit, self._auth_window
        else:
            key = f"global:{ip}"
            limit, window = self._global_limit, self._global_window

        if self._is_rate_limited(key, limit, window):
            return JsonResponse(
                {
                    "type": "https://hbtrack.dev/errors/rate-limit-exceeded",
                    "title": "Too Many Requests",
                    "status": 429,
                    "detail": f"Rate limit exceeded. Try again in {window}s.",
                    "traceId": get_current_flow_id(),
                },
                status=429,
                content_type="application/problem+json",
            )

        response = self.get_response(request)
        response["X-RateLimit-Limit"] = str(limit)
        response["X-RateLimit-Remaining"] = str(
            max(0, limit - len(self._buckets.get(key, [])))
        )
        return response

