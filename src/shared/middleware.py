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

    # UUID v4 regex canônico
    _UUID_V4_RE = __import__("re").compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        raw_flow_id = request.headers.get("X-Flow-ID", "")
        # SEGURANÇA (F10): validar X-Flow-ID como UUID v4. Valores inválidos ou
        # maliciosos (quebras de linha, scripts, strings arbitrárias) são
        # descartados e substituídos por UUID gerado internamente.
        # Isso previne log injection via header de cliente.
        flow_id = self._sanitize_flow_id(raw_flow_id)
        request.flow_id = flow_id  # expõe para views e testes
        set_flow_id(flow_id)
        response = self.get_response(request)
        response["X-Flow-ID"] = flow_id
        return response

    def _sanitize_flow_id(self, value: str) -> str:
        """Aceita apenas UUID v4 canônico lowercase. Qualquer outra coisa → novo UUID."""
        if value and self._UUID_V4_RE.match(value.lower()):
            return value.lower()
        return str(uuid.uuid4())


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

