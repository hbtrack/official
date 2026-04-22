"""Testes unitários da Fase 2 — AccessContext + CursorCodec.

Cobre:
- AccessContext: criação, imutabilidade, helpers de consulta
- CursorCodec: round-trip encode/decode, rejeição de cursor adulterado,
  fallback legado com ACCEPT_LEGACY_CURSOR=true
- test_layer_separation: paging.py não importa django.conf
- test_list_training_sessions_cursor_pagination: integração do use case
  com cursor opaco
"""
from __future__ import annotations

import ast
import base64
import uuid
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock

import pytest


# ---------------------------------------------------------------------------
# AccessContext
# ---------------------------------------------------------------------------

class TestAccessContext:
    def test_importable(self):
        from training.application.common.access import AccessContext  # noqa: F401

    def test_fields(self):
        from training.application.common.access import AccessContext
        from training.domain.rules import RoleLabel

        actor_id = uuid.uuid4()
        ctx = AccessContext(actor_id=actor_id, role=RoleLabel.COACH)
        assert ctx.actor_id == actor_id
        assert ctx.role == RoleLabel.COACH
        assert ctx.organization_id is None
        assert ctx.team_ids == ()
        assert ctx.athlete_ids == ()

    def test_frozen(self):
        from training.application.common.access import AccessContext
        from training.domain.rules import RoleLabel

        ctx = AccessContext(actor_id=uuid.uuid4(), role=RoleLabel.COACH)
        with pytest.raises((TypeError, AttributeError)):
            ctx.role = RoleLabel.ATHLETE  # type: ignore[misc]

    def test_helpers(self):
        from training.application.common.access import AccessContext
        from training.domain.rules import RoleLabel

        coach = AccessContext(actor_id=uuid.uuid4(), role=RoleLabel.COACH)
        athlete = AccessContext(actor_id=uuid.uuid4(), role=RoleLabel.ATHLETE)
        assert coach.is_coach() is True
        assert coach.is_athlete() is False
        assert coach.is_staff() is True
        assert athlete.is_coach() is False
        assert athlete.is_athlete() is True
        assert athlete.is_staff() is False

    def test_no_django_import(self):
        """AccessContext não deve importar django nem ninja."""
        path = Path("src/training/application/common/access.py")
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                module = getattr(node, "module", "") or ""
                names = [a.name for a in getattr(node, "names", [])]
                forbidden = {"django", "ninja"}
                assert not any(m in module for m in forbidden), (
                    f"access.py importa módulo proibido: {module}"
                )
                assert not any(n in forbidden for n in names), (
                    f"access.py importa símbolo proibido: {names}"
                )


# ---------------------------------------------------------------------------
# CursorCodec
# ---------------------------------------------------------------------------

class TestCursorCodec:
    _SECRET = b"test-secret-32-bytes-padded-here"

    def _codec(self):
        from training.application.common.paging import CursorCodec
        return CursorCodec(self._SECRET)

    def _sample(self) -> tuple[datetime, uuid.UUID]:
        return datetime(2025, 6, 15, 10, 30, 0, tzinfo=timezone.utc), uuid.uuid4()

    def test_round_trip(self):
        codec = self._codec()
        at, id_ = self._sample()
        token = codec.encode(at, id_)
        at_dec, id_dec = codec.decode(token)
        assert at_dec.isoformat() == at.isoformat()
        assert id_dec == id_

    def test_token_is_urlsafe(self):
        codec = self._codec()
        token = codec.encode(*self._sample())
        assert all(c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_=" for c in token), (
            f"Token não é URL-safe: {token}"
        )

    def test_tampered_payload_rejected(self):
        from training.application.common.paging import CursorCodec
        codec = self._codec()
        token = codec.encode(*self._sample())
        raw = base64.urlsafe_b64decode(token.encode() + b"==")
        # Inverter um byte no meio do payload
        tampered = bytearray(raw)
        tampered[5] ^= 0xFF
        bad_token = base64.urlsafe_b64encode(bytes(tampered)).decode().rstrip("=")
        with pytest.raises(ValueError, match="Cursor inválido"):
            codec.decode(bad_token)

    def test_wrong_secret_rejected(self):
        from training.application.common.paging import CursorCodec
        codec1 = CursorCodec(b"secret-a")
        codec2 = CursorCodec(b"secret-b")
        token = codec1.encode(*self._sample())
        with pytest.raises(ValueError, match="Cursor inválido"):
            codec2.decode(token)

    def test_garbage_token_rejected(self):
        codec = self._codec()
        with pytest.raises(ValueError, match="Cursor inválido"):
            codec.decode("nao-e-base64-valido!!!")

    def test_empty_secret_raises(self):
        from training.application.common.paging import CursorCodec
        with pytest.raises(ValueError):
            CursorCodec(b"")

    def test_legacy_fallback_accepted(self, monkeypatch):
        """Com ACCEPT_LEGACY_CURSOR=true, token legado (ISO string) é aceito."""
        from training.application.common.paging import CursorCodec
        monkeypatch.setenv("ACCEPT_LEGACY_CURSOR", "true")
        codec = CursorCodec(b"any-secret")
        legacy_token = "2025-06-15T10:30:00+00:00"
        at, id_ = codec.decode(legacy_token)
        assert at.year == 2025
        assert id_ == uuid.UUID(int=0)  # UUID nulo para tokens legados

    def test_legacy_fallback_rejected_when_disabled(self, monkeypatch):
        """Sem ACCEPT_LEGACY_CURSOR, token legado levanta ValueError."""
        from training.application.common.paging import CursorCodec
        monkeypatch.delenv("ACCEPT_LEGACY_CURSOR", raising=False)
        codec = CursorCodec(b"any-secret")
        legacy_token = "2025-06-15T10:30:00+00:00"
        with pytest.raises(ValueError, match="Cursor inválido"):
            codec.decode(legacy_token)

    def test_no_django_import(self):
        """paging.py nunca deve importar django.conf."""
        path = Path("src/training/application/common/paging.py")
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                module = getattr(node, "module", "") or ""
                names = [a.name for a in getattr(node, "names", [])]
                assert "django" not in module, (
                    f"paging.py importa django: {module}"
                )
                assert "django" not in names, (
                    f"paging.py importa django: {names}"
                )


# ---------------------------------------------------------------------------
# ListTrainingSessionsUseCase — cursor opaco
# ---------------------------------------------------------------------------

class TestListTrainingSessionsWithCursor:
    """Verifica que o use case emite e aceita cursores opacos."""

    _SECRET = b"cursor-test-secret-minimum-32-bytes!"

    def _codec(self):
        from training.application.common.paging import CursorCodec
        return CursorCodec(self._SECRET)

    def _make_session(self, session_at: datetime) -> MagicMock:
        s = MagicMock()
        s.id = uuid.uuid4()
        s.session_at = session_at
        return s

    def test_cursor_emitted_when_full_page(self):
        from training.application.use_cases import (
            ListTrainingSessionsInput,
            ListTrainingSessionsUseCase,
        )
        from training.domain.rules import RoleLabel

        codec = self._codec()
        at = datetime(2025, 6, 15, tzinfo=timezone.utc)
        items = [self._make_session(at)] * 20

        repo = MagicMock()
        repo.list.return_value = items

        uc = ListTrainingSessionsUseCase(repo, cursor_codec=codec)
        result = uc.execute(
            ListTrainingSessionsInput(
                actor_role=RoleLabel.COACH,
                actor_id=uuid.uuid4(),
                page_size=20,
            )
        )
        assert result.next_page_token is not None
        # Deve ser decodificável
        session_at_dec, _ = codec.decode(result.next_page_token)
        assert session_at_dec.year == 2025

    def test_no_cursor_when_partial_page(self):
        from training.application.use_cases import (
            ListTrainingSessionsInput,
            ListTrainingSessionsUseCase,
        )
        from training.domain.rules import RoleLabel

        codec = self._codec()
        at = datetime(2025, 6, 15, tzinfo=timezone.utc)
        items = [self._make_session(at)] * 5  # < 20 → sem próxima página

        repo = MagicMock()
        repo.list.return_value = items

        uc = ListTrainingSessionsUseCase(repo, cursor_codec=codec)
        result = uc.execute(
            ListTrainingSessionsInput(
                actor_role=RoleLabel.COACH,
                actor_id=uuid.uuid4(),
                page_size=20,
            )
        )
        assert result.next_page_token is None

    def test_invalid_cursor_ignored_returns_first_page(self):
        """Cursor adulterado → silently ignorado, retorna primeira página."""
        from training.application.use_cases import (
            ListTrainingSessionsInput,
            ListTrainingSessionsUseCase,
        )
        from training.domain.rules import RoleLabel

        codec = self._codec()
        repo = MagicMock()
        repo.list.return_value = []

        uc = ListTrainingSessionsUseCase(repo, cursor_codec=codec)
        result = uc.execute(
            ListTrainingSessionsInput(
                actor_role=RoleLabel.COACH,
                actor_id=uuid.uuid4(),
                page_token="cursor-adulterado",
            )
        )
        # repo foi chamado sem page_token (None)
        call_kwargs = repo.list.call_args.kwargs
        assert call_kwargs.get("page_token") is None
        assert result.items == []

    def test_no_codec_falls_back_to_legacy(self):
        """Sem codec, fallback legado funciona (ISO string pura)."""
        from training.application.use_cases import (
            ListTrainingSessionsInput,
            ListTrainingSessionsUseCase,
        )
        from training.domain.rules import RoleLabel

        at = datetime(2025, 6, 15, tzinfo=timezone.utc)
        items = [self._make_session(at)] * 20

        repo = MagicMock()
        repo.list.return_value = items

        uc = ListTrainingSessionsUseCase(repo, cursor_codec=None)
        result = uc.execute(
            ListTrainingSessionsInput(
                actor_role=RoleLabel.COACH,
                actor_id=uuid.uuid4(),
                page_size=20,
            )
        )
        # Deve emitir token legado (ISO string) sem explodir
        assert result.next_page_token is not None
        assert "2025" in result.next_page_token
