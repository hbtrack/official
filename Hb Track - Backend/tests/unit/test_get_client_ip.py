"""
Testes unitários para a função canônica get_client_ip.

Cobre:
- IP ausente (sem headers, sem request.client)
- String vazia
- IP inválido
- IPv4 válido
- IPv6 válido
- X-Forwarded-For com lista
- X-Forwarded-For com único IP
- X-Real-IP como fallback
- request.client.host como fallback final
- Garante que nunca retorna "" para evitar erro em coluna INET
"""
import pytest
from unittest.mock import MagicMock

from app.core.logging import get_client_ip


def _make_request(
    xff: str | None = None,
    x_real_ip: str | None = None,
    client_host: str | None = "__absent__",
) -> MagicMock:
    """Cria um mock de Request com headers e client configuráveis."""
    request = MagicMock()
    headers = {}
    if xff is not None:
        headers["x-forwarded-for"] = xff
    if x_real_ip is not None:
        headers["x-real-ip"] = x_real_ip
    request.headers.get = lambda key, default=None: headers.get(key.lower(), default)

    if client_host == "__absent__":
        request.client = None
    elif client_host is None:
        # client presente mas host causa exceção
        request.client = MagicMock()
        request.client.host = None
    else:
        request.client = MagicMock()
        request.client.host = client_host

    return request


class TestGetClientIpNeverReturnsEmpty:
    """Garante que a função nunca retorna string vazia."""

    def test_no_headers_no_client_returns_none(self):
        req = _make_request()
        result = get_client_ip(req)
        assert result is None, "Sem IP disponível deve retornar None"

    def test_empty_xff_returns_none(self):
        req = _make_request(xff="")
        result = get_client_ip(req)
        assert result is None

    def test_empty_string_client_host_returns_none(self):
        req = _make_request(client_host="")
        result = get_client_ip(req)
        assert result is None, "String vazia em client.host deve retornar None, nunca ''"

    def test_invalid_ip_returns_none(self):
        req = _make_request(client_host="not-an-ip")
        result = get_client_ip(req)
        assert result is None

    def test_garbage_xff_returns_none(self):
        req = _make_request(xff="garbage-value")
        result = get_client_ip(req)
        assert result is None

    def test_result_is_never_empty_string(self):
        """Propriedade central: nunca retorna '' (causaria erro INET no PG)."""
        for host in ["", "   ", "invalid", "999.999.999.999", None]:
            req = _make_request(client_host=host)
            result = get_client_ip(req)
            assert result != "", f"Para host={host!r}, get_client_ip retornou '' — isso quebraria coluna INET"


class TestGetClientIpIPv4:
    def test_valid_ipv4_from_client_host(self):
        req = _make_request(client_host="192.168.1.100")
        assert get_client_ip(req) == "192.168.1.100"

    def test_valid_ipv4_from_xff(self):
        req = _make_request(xff="10.0.0.1")
        assert get_client_ip(req) == "10.0.0.1"

    def test_valid_ipv4_from_x_real_ip(self):
        req = _make_request(x_real_ip="203.0.113.42")
        assert get_client_ip(req) == "203.0.113.42"

    def test_loopback_ipv4(self):
        req = _make_request(client_host="127.0.0.1")
        assert get_client_ip(req) == "127.0.0.1"


class TestGetClientIpIPv6:
    def test_valid_ipv6_full(self):
        req = _make_request(client_host="2001:db8::1")
        assert get_client_ip(req) == "2001:db8::1"

    def test_valid_ipv6_loopback(self):
        req = _make_request(client_host="::1")
        assert get_client_ip(req) == "::1"

    def test_valid_ipv6_from_xff(self):
        req = _make_request(xff="2001:db8:85a3::8a2e:370:7334")
        assert get_client_ip(req) == "2001:db8:85a3::8a2e:370:7334"


class TestGetClientIpXForwardedFor:
    def test_xff_list_uses_first_ip(self):
        """Quando X-Forwarded-For é lista, deve usar apenas o primeiro IP."""
        req = _make_request(xff="1.2.3.4, 5.6.7.8, 9.10.11.12")
        assert get_client_ip(req) == "1.2.3.4"

    def test_xff_list_with_spaces(self):
        req = _make_request(xff="  10.0.0.2  , 192.168.1.1")
        assert get_client_ip(req) == "10.0.0.2"

    def test_xff_preferred_over_x_real_ip(self):
        """X-Forwarded-For tem prioridade sobre X-Real-IP."""
        req = _make_request(xff="1.1.1.1", x_real_ip="2.2.2.2")
        assert get_client_ip(req) == "1.1.1.1"

    def test_xff_preferred_over_client_host(self):
        """X-Forwarded-For tem prioridade sobre request.client.host."""
        req = _make_request(xff="1.1.1.1", client_host="3.3.3.3")
        assert get_client_ip(req) == "1.1.1.1"

    def test_xff_invalid_first_ip_returns_none(self):
        """Se o primeiro IP do XFF for inválido, retorna None."""
        req = _make_request(xff="invalid-ip, 1.2.3.4")
        assert get_client_ip(req) is None

    def test_xff_empty_string_falls_through(self):
        """XFF vazio deve cair para próximo fallback."""
        # XFF vazio → fallback para client.host
        req = _make_request(xff="", client_host="192.0.2.1")
        # XFF vazio — como headers.get retorna "" que é falsy, cuidado
        # O comportamento correto: "" em xFF não é usado, cai para client.host
        result = get_client_ip(req)
        assert result == "192.0.2.1"


class TestGetClientIpFallbackPriority:
    def test_x_real_ip_fallback_when_no_xff(self):
        """X-Real-IP usado quando não há X-Forwarded-For."""
        req = _make_request(x_real_ip="172.16.0.1", client_host="10.0.0.1")
        assert get_client_ip(req) == "172.16.0.1"

    def test_client_host_fallback_final(self):
        """request.client.host é o último fallback."""
        req = _make_request(client_host="198.51.100.5")
        assert get_client_ip(req) == "198.51.100.5"

    def test_all_absent_returns_none(self):
        req = _make_request()
        assert get_client_ip(req) is None

    def test_x_real_ip_invalid_returns_none(self):
        req = _make_request(x_real_ip="not-an-ip")
        assert get_client_ip(req) is None


class TestGetClientIpEdgeCases:
    def test_client_host_raises_exception_returns_none(self):
        """Se request.client.host lançar exceção, deve retornar None."""
        request = MagicMock()
        request.headers.get = lambda key, default=None: None
        request.client = MagicMock()
        type(request.client).host = property(lambda self: (_ for _ in ()).throw(Exception("broken")))
        result = get_client_ip(request)
        assert result is None

    def test_xff_with_ipv6_in_list(self):
        req = _make_request(xff="2001:db8::1, 10.0.0.1")
        assert get_client_ip(req) == "2001:db8::1"

    def test_255_255_255_255_broadcast_is_valid(self):
        """255.255.255.255 é tecnicamente um IPv4 válido."""
        req = _make_request(client_host="255.255.255.255")
        assert get_client_ip(req) == "255.255.255.255"

    def test_999_ip_invalid_returns_none(self):
        req = _make_request(client_host="999.999.999.999")
        assert get_client_ip(req) is None
