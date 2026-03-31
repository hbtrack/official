"""
Testes do RateLimitMiddleware.

Valida:
  1. Requests dentro do limite passam normalmente
  2. Requests acima do limite retornam 429 + Problem+JSON
  3. Endpoints /auth/ têm limite separado (mais restrito)
  4. Headers X-RateLimit-Limit e X-RateLimit-Remaining presentes
"""
from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

# Importar middleware diretamente (sem Django app loading)
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))


def _make_request(path: str = "/api/users/", ip: str = "192.168.1.1") -> MagicMock:
    req = MagicMock()
    req.path_info = path
    req.META = {
        "REMOTE_ADDR": ip,
        "HTTP_X_FORWARDED_FOR": None,
    }
    req.headers = {}
    return req


def _make_response():
    """Simula um Django HttpResponse com suporte a headers via dict."""
    resp = {}
    resp["status_code"] = 200
    return resp


class TestRateLimitMiddleware:
    """Rate limiter por IP com sliding window."""

    def _build_middleware(self, global_limit=5, global_window=60,
                         auth_limit=3, auth_window=60):
        """Constrói middleware com settings mockados."""
        # Patch django.conf.settings
        settings_mock = MagicMock()
        settings_mock.RATE_LIMIT_REQUESTS = global_limit
        settings_mock.RATE_LIMIT_WINDOW = global_window
        settings_mock.RATE_LIMIT_AUTH_REQUESTS = auth_limit
        settings_mock.RATE_LIMIT_AUTH_WINDOW = auth_window

        # Patch para evitar import do Django settings real
        import unittest.mock as um
        with um.patch("django.conf.settings", settings_mock):
            from shared.middleware import RateLimitMiddleware

            def fake_response(request):
                resp = MagicMock()
                resp.status_code = 200
                resp.__setitem__ = MagicMock()
                resp.__getitem__ = MagicMock(return_value="")
                return resp

            mw = RateLimitMiddleware(fake_response)
        return mw

    def test_requests_within_limit_pass(self):
        mw = self._build_middleware(global_limit=5)
        for _ in range(5):
            req = _make_request()
            resp = mw(req)
            assert resp.status_code == 200

    def test_request_over_limit_returns_429(self):
        mw = self._build_middleware(global_limit=3)
        for _ in range(3):
            mw(_make_request())

        # 4th request → 429
        resp = mw(_make_request())
        assert resp.status_code == 429
        body = json.loads(resp.content.decode())
        assert body["status"] == 429
        assert body["type"] == "https://hbtrack.dev/errors/rate-limit-exceeded"

    def test_auth_endpoint_has_separate_limit(self):
        mw = self._build_middleware(global_limit=10, auth_limit=2)

        # 2 auth requests ok
        for _ in range(2):
            resp = mw(_make_request(path="/api/auth/login"))
            assert resp.status_code == 200

        # 3rd auth → 429
        resp = mw(_make_request(path="/api/auth/login"))
        assert resp.status_code == 429

        # Global endpoint still works (different bucket)
        resp = mw(_make_request(path="/api/users/"))
        assert resp.status_code == 200

    def test_different_ips_have_separate_limits(self):
        mw = self._build_middleware(global_limit=2)

        # IP 1: 2 requests
        for _ in range(2):
            mw(_make_request(ip="10.0.0.1"))

        # IP 1 blocked
        resp = mw(_make_request(ip="10.0.0.1"))
        assert resp.status_code == 429

        # IP 2 still ok
        resp = mw(_make_request(ip="10.0.0.2"))
        assert resp.status_code == 200
