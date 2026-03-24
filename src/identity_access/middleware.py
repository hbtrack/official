"""
JWTAuthMiddleware — HB Track
Valida Bearer token JWT em cada request.
- Requests sem token recebem 401.
- Requests com token válido têm request.auth populado com o payload.
- Endpoints públicos (auth=None no Ninja) são ignorados pelo middleware Ninja.
"""
from __future__ import annotations

import os
from typing import Any, Optional

from ninja.security import HttpBearer


class JWTBearer(HttpBearer):
    """Autenticação JWT Bearer para Django Ninja."""

    def authenticate(self, request, token: str) -> Optional[dict]:
        from .infrastructure.jwt_adapter import JWTAdapter
        adapter = JWTAdapter()
        payload = adapter.verify_access_token(token)
        if payload is None:
            return None
        return payload
