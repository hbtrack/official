"""
JWTAuthMiddleware — HB Track
Valida Bearer token JWT em cada request.
- Requests sem token recebem 401.
- Requests com token válido têm request.auth populado com o payload.
- Endpoints públicos (auth=None no Ninja) são ignorados pelo middleware Ninja.
"""
from __future__ import annotations

from typing import Any, Optional

from django.http import HttpRequest
from ninja.errors import AuthenticationError
from ninja.security import HttpBearer


class HTTPBearer(HttpBearer):
    """Autenticação JWT Bearer para Django Ninja/OpenAPI."""

    error_detail = "Token ausente ou inválido."

    def __call__(self, request: HttpRequest) -> Optional[Any]:
        auth_value = request.headers.get(self.header)
        if not auth_value:
            raise AuthenticationError(message=self.error_detail)

        parts = auth_value.split(" ")
        if parts[0].lower() != self.openapi_scheme:
            raise AuthenticationError(message=self.error_detail)

        token = " ".join(parts[1:])
        payload = self.authenticate(request, token)
        if payload is None:
            raise AuthenticationError(message=self.error_detail)
        return payload

    def authenticate(self, request, token: str) -> Optional[dict]:
        from .infrastructure.jwt_adapter import JWTAdapter
        adapter = JWTAdapter()
        try:
            payload = adapter.verify_access_token(token)
        except Exception:
            return None
        if payload is None:
            return None
        return payload


# Alias retrocompatível para referências antigas no repositório.
JWTBearer = HTTPBearer
