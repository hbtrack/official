"""
JWTAdapter — implementação RS256 do JwtPort.
Usa PyJWT com par de chaves RS256.
Chaves configuradas via variáveis de ambiente:
  JWT_PRIVATE_KEY — PEM da chave privada (REQUIRED em produção)
  JWT_PUBLIC_KEY  — PEM da chave pública  (REQUIRED em produção)
  JWT_ALGORITHM   — padrão "RS256"
  JWT_ACCESS_TOKEN_EXPIRY_MINUTES — padrão 60
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt

from ..domain.entities import AuthSession


import base64 as _b64

def _decode_key(val: str) -> str:
    """Aceita PEM direto ou base64(PEM) — permite .env sem caracteres especiais."""
    if not val:
        return val
    if val.startswith("-----"):
        return val
    try:
        return _b64.b64decode(val).decode()
    except Exception:
        return val

_ALGORITHM = os.environ.get("JWT_ALGORITHM", "RS256")
_EXPIRY_MINUTES = int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRY_MINUTES", "60"))
_PRIVATE_KEY = _decode_key(os.environ.get("JWT_PRIVATE_KEY", ""))
_PUBLIC_KEY = _decode_key(os.environ.get("JWT_PUBLIC_KEY", ""))


class JWTAdapter:
    """Implementação do JwtPort usando PyJWT + RS256."""

    def issue_access_token(self, session: AuthSession) -> str:
        now = datetime.now(tz=timezone.utc)
        payload = {
            "sub": str(session.principal_user_id),
            "session_id": str(session.id),
            "scope": session.session_scope_label,
            "roles": session.role_labels or [],
            "iat": now,
            "exp": now + timedelta(minutes=_EXPIRY_MINUTES),
        }
        key = _PRIVATE_KEY or self._dev_private_key()
        return jwt.encode(payload, key, algorithm=_ALGORITHM)

    def verify_access_token(self, token: str) -> Optional[dict]:
        try:
            key = _PUBLIC_KEY or self._dev_public_key()
            return jwt.decode(token, key, algorithms=[_ALGORITHM])
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    # ── Chaves de dev apenas — NUNCA usar em produção ─────────────────────────

    @staticmethod
    def _dev_private_key() -> str:
        """Gera/retorna chave privada RSA de desenvolvimento (em memória)."""
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.backends import default_backend

        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend(),
        )
        return key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode()

    @staticmethod
    def _dev_public_key() -> str:
        raise RuntimeError(
            "JWT_PUBLIC_KEY não configurada. "
            "Defina JWT_PRIVATE_KEY e JWT_PUBLIC_KEY para usar RS256 real."
        )
