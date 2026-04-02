"""
JWTAdapter — implementação RS256/HS256 do JwtPort.
Usa PyJWT com par de chaves RS256 (produção) ou HS256 simétrico (dev).
Chaves configuradas via variáveis de ambiente:
  JWT_ALGORITHM   — "RS256" (padrão produção) ou "HS256" (dev)
  JWT_SECRET      — secret simétrico para HS256
  JWT_PRIVATE_KEY — PEM da chave privada (RS256, produção)
  JWT_PUBLIC_KEY  — PEM da chave pública  (RS256, produção)
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


def _get_algorithm() -> str:
    return os.environ.get("JWT_ALGORITHM", "RS256")


def _get_expiry() -> int:
    return int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRY_MINUTES", "60"))


def _signing_key() -> str:
    """Retorna a chave de assinatura correta para o algoritmo configurado."""
    alg = _get_algorithm()
    if alg in ("HS256", "HS384", "HS512"):
        secret = os.environ.get("JWT_SECRET", "")
        return secret or "dev-insecure-secret-change-in-production"
    # RS256/ES256: usa chave privada ou gera par RSA de dev (não usar em produção)
    private_key = _decode_key(os.environ.get("JWT_PRIVATE_KEY", ""))
    if private_key:
        return private_key
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.backends import default_backend
    key = rsa.generate_private_key(
        public_exponent=65537, key_size=2048, backend=default_backend()
    )
    return key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()


def _verification_key() -> str:
    """Retorna a chave de verificação correta para o algoritmo configurado."""
    alg = _get_algorithm()
    if alg in ("HS256", "HS384", "HS512"):
        secret = os.environ.get("JWT_SECRET", "")
        return secret or "dev-insecure-secret-change-in-production"
    public_key = _decode_key(os.environ.get("JWT_PUBLIC_KEY", ""))
    if public_key:
        return public_key
    raise RuntimeError(
        "JWT_PUBLIC_KEY não configurada. "
        "Defina JWT_PRIVATE_KEY e JWT_PUBLIC_KEY para usar RS256 real."
    )


class JWTAdapter:
    """Implementação do JwtPort usando PyJWT. Suporta RS256 (produção) e HS256 (dev)."""

    def issue_access_token(self, session: AuthSession) -> str:
        now = datetime.now(tz=timezone.utc)
        payload = {
            "sub": str(session.principal_user_id),
            "session_id": str(session.id),
            "scope": session.session_scope_label,
            "roles": session.role_labels or [],
            "iat": now,
            "exp": now + timedelta(minutes=_get_expiry()),
        }
        return jwt.encode(payload, _signing_key(), algorithm=_get_algorithm())

    def verify_access_token(self, token: str) -> Optional[dict]:
        try:
            return jwt.decode(
                token, _verification_key(), algorithms=[_get_algorithm()]
            )
        except RuntimeError:
            return None
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
