"""Paginação baseada em cursor — training.application.common.

Este módulo é framework-agnostic: NUNCA importar django.conf, ninja ou request.
O secret do codec é resolvido na borda HTTP (api/deps.py) e injetado aqui como bytes.

Componentes:
    PageRequest   — parâmetros de entrada de uma página.
    PageResult    — resultado de uma consulta paginada.
    CursorCodec   — serializa/deserializa cursores com HMAC-SHA256.

Design:
    O cursor codifica (session_at ISO, UUID) com assinatura HMAC para impedir
    adulteração ou enumeração de recursos. O receptor verifica a assinatura
    antes de aceitar o cursor.

Rollout retrocompatível:
    Para tokens legados emitidos antes da Fase 2 (formato: ISO session_at puro),
    configure a variável de ambiente ACCEPT_LEGACY_CURSOR=true na camada de
    infraestrutura. O CursorCodec.decode aceita o fallback se habilitado.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Generic, Optional, TypeVar

T = TypeVar("T")

# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PageRequest:
    """Parâmetros de paginação para qualquer consulta listável."""

    size: int
    cursor: Optional[str] = None


@dataclass
class PageResult(Generic[T]):
    """Resultado de uma consulta paginada."""

    items: list[T]
    next_cursor: Optional[str] = None

    def has_next(self) -> bool:
        return self.next_cursor is not None


# ---------------------------------------------------------------------------
# CursorCodec
# ---------------------------------------------------------------------------

class CursorCodec:
    """Codifica/decodifica cursores de paginação assinados com HMAC-SHA256.

    Formato do payload bruto (antes de base64):
        b"v1|<session_at_iso>|<uuid>|<hmac_sig_32bytes>"

    O campo <session_at_iso> segue RFC 3339 (com timezone UTC).

    Instanciar via CursorCodec(secret=...) — nunca ler django.conf aqui.
    """

    _VERSION = b"v1"
    _SEP = b"|"
    _SIG_LEN = 32  # SHA-256 digest = 32 bytes

    def __init__(self, secret: bytes) -> None:
        if not secret:
            raise ValueError("CursorCodec: secret não pode ser vazio")
        self._secret = secret

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def encode(self, session_at: datetime, id: uuid.UUID) -> str:
        """Serializa (session_at, id) → cursor URL-safe assinado."""
        at_iso = session_at.astimezone(timezone.utc).isoformat()
        payload = self._SEP.join([
            self._VERSION,
            at_iso.encode(),
            str(id).encode(),
        ])
        sig = self._sign(payload)
        raw = payload + self._SEP + sig
        return base64.urlsafe_b64encode(raw).decode()

    def decode(self, token: str) -> tuple[datetime, uuid.UUID]:
        """Deserializa cursor → (session_at, id).

        Lança ValueError com mensagem genérica se o cursor for inválido,
        expirado ou adulterado — nunca exponha detalhes de assinatura ao
        chamador HTTP.
        """
        # Tenta decode principal; se falhar e ACCEPT_LEGACY_CURSOR=true, usa fallback
        try:
            return self._decode_v1(token)
        except ValueError:
            if os.environ.get("ACCEPT_LEGACY_CURSOR", "").lower() == "true":
                return self._decode_legacy(token)
            raise

    def _decode_v1(self, token: str) -> tuple[datetime, uuid.UUID]:
        """Decode v1 com HMAC-SHA256."""
        try:
            raw = base64.urlsafe_b64decode(token.encode() + b"==")
        except Exception:
            raise ValueError("Cursor inválido")

        # Separar sig (32 bytes) do payload restante
        # payload + SEP + sig(32 bytes)
        sig_start = len(raw) - self._SIG_LEN
        sep_before_sig = sig_start - 1
        if sep_before_sig < 0 or raw[sep_before_sig : sig_start] != self._SEP:
            raise ValueError("Cursor inválido")

        payload = raw[:sep_before_sig]
        sig = raw[sig_start:]

        expected = self._sign(payload)
        if not hmac.compare_digest(sig, expected):
            raise ValueError("Cursor inválido")

        parts = payload.split(self._SEP)
        if len(parts) != 3 or parts[0] != self._VERSION:
            raise ValueError("Cursor inválido")

        try:
            session_at = datetime.fromisoformat(parts[1].decode())
            record_id = uuid.UUID(parts[2].decode())
        except (ValueError, AttributeError):
            raise ValueError("Cursor inválido")

        return session_at, record_id

    # ------------------------------------------------------------------
    # Legacy support (tokens pré-Fase 2: ISO session_at puro)
    # ------------------------------------------------------------------

    @staticmethod
    def _decode_legacy(token: str) -> tuple[datetime, uuid.UUID]:
        """Fallback para cursores no formato antigo (session_at.isoformat()).

        Aceito apenas se ACCEPT_LEGACY_CURSOR=true. O id retornado é um
        UUID nulo (usado somente para filtro por session_at no repo).
        """
        try:
            session_at = datetime.fromisoformat(token)
            return session_at, uuid.UUID(int=0)
        except ValueError:
            raise ValueError("Cursor inválido")

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _sign(self, payload: bytes) -> bytes:
        return hmac.new(self._secret, payload, hashlib.sha256).digest()
