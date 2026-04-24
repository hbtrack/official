"""
TokenAuthMiddlewareStack — middleware para autenticação JWT em WebSocket.

Extrai o token do subprotocolo WebSocket (formato: "hbtrack-token.<jwt>")
ou do header de handshake "Authorization: Bearer <jwt>", evitando exposição
do JWT em query string (logs, proxies, browser history — OWASP A02).

Fallback para clientes que não suportam subprotocol:
  Cabeçalho de upgrade: Sec-WebSocket-Protocol: hbtrack-token.<jwt>

Popula scope["user_id"] quando o token for válido.
"""
from __future__ import annotations

import logging

from channels.middleware import BaseMiddleware
from channels.auth import AuthMiddlewareStack

logger = logging.getLogger(__name__)

_SUBPROTOCOL_PREFIX = "hbtrack-token."


def _extract_token_from_scope(scope: dict) -> str | None:
    """
    Tenta extrair o JWT em ordem de preferência:
      1. Subprotocolo WebSocket: "hbtrack-token.<jwt>"
      2. Header HTTP de upgrade: Authorization: Bearer <jwt>
    Retorna None se nenhum mecanismo fornecer token.
    """
    # 1. Subprotocol (mais seguro: não aparece em URLs)
    subprotocols = scope.get("subprotocols", [])
    for sp in subprotocols:
        if sp.startswith(_SUBPROTOCOL_PREFIX):
            return sp[len(_SUBPROTOCOL_PREFIX):]

    # 2. Header Authorization (handshake HTTP do WebSocket)
    headers = dict(scope.get("headers", []))
    auth_bytes = headers.get(b"authorization", b"")
    auth = auth_bytes.decode("latin-1") if isinstance(auth_bytes, bytes) else auth_bytes
    if auth.startswith("Bearer "):
        return auth[len("Bearer "):]

    return None


class TokenAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        token = _extract_token_from_scope(scope)
        if token:
            try:
                from identity_access.infrastructure.jwt_adapter import JWTAdapter
                payload = JWTAdapter().verify_access_token(token)
                if payload:
                    scope["user_id"] = payload.get("sub")
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "TokenAuthMiddleware: verificação JWT falhou erro=%s",
                    type(exc).__name__,
                )
        return await super().__call__(scope, receive, send)


def TokenAuthMiddlewareStack(inner):
    return TokenAuthMiddleware(AuthMiddlewareStack(inner))
