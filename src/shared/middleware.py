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
