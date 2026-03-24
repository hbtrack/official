"""
TokenAuthMiddlewareStack — middleware para autenticação JWT em WebSocket.
Extrai o token do query string (?token=...) e popula scope["user_id"].
"""
from __future__ import annotations

from urllib.parse import parse_qs

from channels.middleware import BaseMiddleware
from channels.auth import AuthMiddlewareStack


class TokenAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode()
        params = parse_qs(query_string)
        token_list = params.get("token", [])
        if token_list:
            token = token_list[0]
            from identity_access.infrastructure.jwt_adapter import JWTAdapter
            payload = JWTAdapter().verify_access_token(token)
            if payload:
                scope["user_id"] = payload.get("sub")
        return await super().__call__(scope, receive, send)


def TokenAuthMiddlewareStack(inner):
    return TokenAuthMiddleware(AuthMiddlewareStack(inner))
