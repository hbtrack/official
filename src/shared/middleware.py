"""
FlowIDMiddleware — HB Track
Garante que todo request tenha um X-Flow-ID rastreável.
- Gera UUID v4 se o request não trazer o header.
- Propaga X-Flow-ID em todos os responses.
- Armazena em ContextVar (seguro para ASGI, Channels e Celery).
"""
from __future__ import annotations

import logging
import re
import uuid
from contextvars import ContextVar

logger = logging.getLogger(__name__)

_flow_id_var: ContextVar[str] = ContextVar("flow_id", default="")

_UUID4_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


def _sanitize_flow_id(value: str | None) -> str:
    """Retorna value se for UUID v4 válido; caso contrário gera um novo UUID."""
    if value and _UUID4_RE.match(value):
        return value
    return str(uuid.uuid4())


def get_current_flow_id() -> str:
    """Retorna o flow_id do contexto atual (ou gera um novo se não houver)."""
    fid = _flow_id_var.get()
    if not fid:
        fid = str(uuid.uuid4())
        _flow_id_var.set(fid)
    return fid


def set_flow_id(flow_id: str) -> None:
    _flow_id_var.set(flow_id)


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
        raw = request.headers.get("X-Flow-ID")
        flow_id = _sanitize_flow_id(raw)
        set_flow_id(flow_id)
        request.flow_id = flow_id
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
                from identity_access.infrastructure.jwt_adapter import JWTAdapter
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
            except (ValueError, KeyError) as exc:
                # Claims malformados (UUID inválido, campo ausente) — token rejeitado silenciosamente
                logger.info(
                    "JWTClaimsMiddleware: claims inválidos flow_id=%s erro=%s",
                    get_current_flow_id(),
                    type(exc).__name__,
                )
            except Exception as exc:  # noqa: BLE001
                # Falha de verificação (assinatura, expiração, chave) — logar e prosseguir sem claims
                logger.warning(
                    "JWTClaimsMiddleware: verificação falhou flow_id=%s erro=%s",
                    get_current_flow_id(),
                    type(exc).__name__,
                )

        return self.get_response(request)

