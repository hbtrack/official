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
        if not secret:
            raise RuntimeError(
                "[SEGURANÇA] JWT_SECRET não configurado. "
                "Defina JWT_SECRET com um valor gerado seguro para usar HS256. "
                "Exemplo: python -c \"import secrets; print(secrets.token_urlsafe(50))\""
            )
        return secret
    # RS256/ES256: requer chave privada explícita — nunca gera chave efêmera
    private_key = _decode_key(os.environ.get("JWT_PRIVATE_KEY", ""))
    if not private_key:
        raise RuntimeError(
            "[SEGURANÇA] JWT_PRIVATE_KEY não configurada para RS256. "
            "Gere um par RSA e defina JWT_PRIVATE_KEY (PEM ou base64) e JWT_PUBLIC_KEY no ambiente."
        )
    return private_key


def _verification_key() -> str:
    """Retorna a chave de verificação correta para o algoritmo configurado."""
    alg = _get_algorithm()
    if alg in ("HS256", "HS384", "HS512"):
        secret = os.environ.get("JWT_SECRET", "")
        if not secret:
            raise RuntimeError(
                "[SEGURANÇA] JWT_SECRET não configurado. "
                "Defina JWT_SECRET com um valor gerado seguro para usar HS256."
            )
        return secret
    public_key = _decode_key(os.environ.get("JWT_PUBLIC_KEY", ""))
    if not public_key:
        raise RuntimeError(
            "[SEGURANÇA] JWT_PUBLIC_KEY não configurada. "
            "Defina JWT_PRIVATE_KEY e JWT_PUBLIC_KEY para usar RS256 em produção."
        )
    return public_key


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
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
