"""
Testes de hardening backend — validação das correções técnicas (backend.md)

Cobre 6 correções:
  C1 — notifications/tasks.py: bug no except (delivery não inicializado)
  C2 — shared/middleware.py: threading.local → contextvars (isolamento ASGI)
  C3 — shared/middleware.py: JWTClaimsMiddleware — import canônico + logging
  C4 — notifications/middleware.py: JWT não mais em query string
  C5 — infra/docker-compose.staging.yml: migrate/collectstatic separados da API
  C6 — Dockerfile: label org.opencontainers.image.source correto
"""
from __future__ import annotations

import asyncio
import importlib
import inspect
import pathlib
import re
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]


# ══════════════════════════════════════════════════════════════════════════════
# C1 — notifications/tasks.py: bug no bloco except
# ══════════════════════════════════════════════════════════════════════════════

class TestDeliverNotificationTask:
    """C1: bloco except não pode referenciar variável não inicializada."""

    def test_delivery_not_found_returns_not_found_without_nameerror(self):
        """
        Se DoesNotExist for levantado antes de `delivery` existir,
        a task deve retornar {"status": "not_found"} sem NameError.
        Import é lazy; patch feito no módulo de origem.
        """
        from notifications.tasks import deliver_notification

        fake_model = MagicMock()
        fake_model.DoesNotExist = Exception
        fake_model.objects.get.side_effect = fake_model.DoesNotExist("not found")

        # Import lazy — patch no módulo de origem; .run() executa com self=task
        with patch("notifications.infrastructure.models.NotificationDeliveryModel", fake_model):
            result = deliver_notification.run(str(uuid.uuid4()))

        assert result["status"] == "not_found"

    def test_send_failure_triggers_retry_without_nameerror(self):
        """
        Se o save() falhar após o get() ter sucesso, retry é agendado.
        O bloco except NÃO pode lançar NameError.
        """
        from notifications.tasks import deliver_notification

        delivery_mock = MagicMock()
        delivery_mock.save.side_effect = [RuntimeError("db write failed"), None]
        delivery_mock.retry_count = 0

        fake_model = MagicMock()
        fake_model.DoesNotExist = LookupError
        fake_model.objects.get.return_value = delivery_mock

        retry_exc = RuntimeError("celery retry sentinel")

        with patch("notifications.infrastructure.models.NotificationDeliveryModel", fake_model):
            # patch.object controla self.retry sem precisar injetar self_mock
            with patch.object(deliver_notification, "retry", side_effect=retry_exc):
                with pytest.raises(RuntimeError, match="celery retry sentinel"):
                    deliver_notification.run(str(uuid.uuid4()))

        # retry_count deve ter sido incrementado antes do retry ser levantado
        assert delivery_mock.retry_count == 1

    def test_successful_delivery_returns_sent(self):
        """Entrega bem-sucedida retorna status=sent."""
        from notifications.tasks import deliver_notification

        delivery_mock = MagicMock()
        fake_model = MagicMock()
        fake_model.DoesNotExist = LookupError
        fake_model.objects.get.return_value = delivery_mock

        with patch("notifications.infrastructure.models.NotificationDeliveryModel", fake_model):
            result = deliver_notification.run(str(uuid.uuid4()))

        assert result["status"] == "sent"

    def test_malformed_uuid_raises_value_error_not_nameerror(self):
        """
        delivery_id inválido (não é UUID) deve levantar ValueError imediatamente,
        NÃO NameError ou AttributeError mascarado.
        Garante que a Fase 1 falha por motivo correto (dado inválido).
        """
        from notifications.tasks import deliver_notification

        with pytest.raises(ValueError):
            deliver_notification.run("nao-eh-um-uuid")


# ══════════════════════════════════════════════════════════════════════════════
# C2 — shared/middleware.py: contextvars (não threading.local)
# ══════════════════════════════════════════════════════════════════════════════

class TestContextVarFlowID:
    """C2: flow_id deve ser isolado por contexto assíncrono, não por thread."""

    def test_threading_local_not_imported(self):
        """O módulo shared.middleware NÃO deve importar threading."""
        import shared.middleware as mod
        src = inspect.getsource(mod)
        assert "threading" not in src, (
            "shared/middleware.py ainda importa 'threading' — deve usar contextvars"
        )

    def test_contextvars_used(self):
        """O módulo shared.middleware deve usar ContextVar."""
        import shared.middleware as mod
        src = inspect.getsource(mod)
        assert "ContextVar" in src or "contextvars" in src

    def test_flow_ids_isolated_between_async_tasks(self):
        """
        Duas corotinas concorrentes NÃO devem compartilhar flow_id.
        Se threading.local fosse usado, a primeira task contaminaria a segunda
        caso rodem na mesma thread do event loop.
        """
        import asyncio
        from shared.middleware import set_flow_id, get_current_flow_id

        id_a = str(uuid.uuid4())
        id_b = str(uuid.uuid4())
        results: dict[str, str] = {}

        async def task_a():
            set_flow_id(id_a)
            await asyncio.sleep(0)  # cede para task_b
            results["a"] = get_current_flow_id()

        async def task_b():
            set_flow_id(id_b)
            await asyncio.sleep(0)
            results["b"] = get_current_flow_id()

        async def run():
            await asyncio.gather(
                asyncio.ensure_future(task_a()),
                asyncio.ensure_future(task_b()),
            )

        asyncio.run(run())

        assert results["a"] == id_a, (
            f"task_a leu flow_id='{results['a']}' mas esperava '{id_a}' "
            "— vazamento entre contextos assíncronos"
        )
        assert results["b"] == id_b, (
            f"task_b leu flow_id='{results['b']}' mas esperava '{id_b}'"
        )

    def test_flow_id_set_and_get_roundtrip(self):
        """set_flow_id/get_current_flow_id devem fazer roundtrip no mesmo contexto."""
        from shared.middleware import set_flow_id, get_current_flow_id
        fid = str(uuid.uuid4())
        set_flow_id(fid)
        assert get_current_flow_id() == fid

    def test_threading_local_would_contaminate_as_regression_proof(self):
        """
        PROVA DE REGRESSÃO: demonstra que threading.local CONTAMINA entre coroutines
        concorrentes no mesmo event loop.
        Se a implementação regredir para threading.local, este teste ainda passa (é
        um teste educacional), mas test_flow_ids_isolated_between_async_tasks falhará.
        Documenta por que a migração para ContextVar foi necessária.
        """
        import threading

        thread_store = threading.local()
        results: dict[str, str] = {}

        async def task_threading_a():
            thread_store.flow_id = "flow-A"
            await asyncio.sleep(0)  # cede para task_b
            results["a"] = getattr(thread_store, "flow_id", "MISSING")

        async def task_threading_b():
            thread_store.flow_id = "flow-B"
            await asyncio.sleep(0)
            results["b"] = getattr(thread_store, "flow_id", "MISSING")

        async def run():
            await asyncio.gather(
                asyncio.ensure_future(task_threading_a()),
                asyncio.ensure_future(task_threading_b()),
            )

        asyncio.run(run())

        # threading.local contamina: ambas as tasks leem o último valor escrito
        # (ambas rodam na mesma thread no event loop)
        contaminated = results.get("a") != "flow-A" or results.get("b") != "flow-B"
        assert contaminated, (
            "threading.local NÃO contaminou neste caso — o scheduler se comportou diferente do esperado. "
            "Verifique se o event loop mudou de comportamento."
        )


# ══════════════════════════════════════════════════════════════════════════════
# C2-bis — config/celery.py: propagação de flow_id via sinais Celery
# ══════════════════════════════════════════════════════════════════════════════

class TestCeleryFlowIDPropagation:
    """C2-bis: flow_id deve ser restaurado no worker via sinal task_prerun."""

    def test_task_prerun_restores_flow_id_from_headers(self):
        """
        O sinal task_prerun deve chamar set_flow_id() com o valor do
        header 'X-Flow-ID' da task, propagando o trace entre request e worker.
        """
        from config.celery import restore_flow_id_from_task_headers
        from shared.middleware import get_current_flow_id, set_flow_id

        expected_flow_id = str(uuid.uuid4())

        # Simula o objeto task Celery com request.headers
        task_mock = MagicMock()
        task_mock.request.headers = {"X-Flow-ID": expected_flow_id}

        # Chamar o handler do sinal diretamente (como o Celery faria)
        restore_flow_id_from_task_headers(task=task_mock)

        assert get_current_flow_id() == expected_flow_id, (
            f"flow_id não foi restaurado: esperado '{expected_flow_id}', "
            f"obtido '{get_current_flow_id()}'"
        )

    def test_task_prerun_without_flow_id_header_does_not_overwrite(self):
        """
        Se o header 'X-Flow-ID' não existir, o sinal não deve sobrescrever
        um flow_id já definido no contexto atual.
        """
        from config.celery import restore_flow_id_from_task_headers
        from shared.middleware import get_current_flow_id, set_flow_id

        original_flow_id = str(uuid.uuid4())
        set_flow_id(original_flow_id)

        task_mock = MagicMock()
        task_mock.request.headers = {}  # sem X-Flow-ID

        restore_flow_id_from_task_headers(task=task_mock)

        # Sem header → flow_id original deve permanecer intacto
        assert get_current_flow_id() == original_flow_id, (
            f"flow_id foi sobrescrito indevidamente: esperado '{original_flow_id}', "
            f"obtido '{get_current_flow_id()}'"
        )

    def test_before_task_publish_injects_flow_id_into_headers(self):
        """
        O sinal before_task_publish deve injetar o flow_id atual
        no dicionário de headers da task antes da publicação no broker.
        """
        from config.celery import inject_flow_id_into_task_headers
        from shared.middleware import set_flow_id

        flow_id = str(uuid.uuid4())
        set_flow_id(flow_id)

        headers: dict = {}
        inject_flow_id_into_task_headers(headers=headers)

        assert "X-Flow-ID" in headers, "X-Flow-ID não foi injetado nos headers da task"
        assert headers["X-Flow-ID"] == flow_id, (
            f"X-Flow-ID injetado incorretamente: esperado '{flow_id}', "
            f"obtido '{headers['X-Flow-ID']}'"
        )


# ══════════════════════════════════════════════════════════════════════════════
# C3 — JWTClaimsMiddleware: import canônico + logging de erros
# ══════════════════════════════════════════════════════════════════════════════

class TestJWTClaimsMiddleware:
    """C3: import sem 'src.' e falhas de JWT devem ser logadas, não silenciadas."""

    def test_no_src_prefix_in_import(self):
        """JWTClaimsMiddleware não pode importar de 'src.identity_access...'."""
        source_path = ROOT / "src" / "shared" / "middleware.py"
        source = source_path.read_text()
        assert "from src.identity_access" not in source, (
            "Import com prefixo 'src.' detectado em shared/middleware.py"
        )

    def test_jwt_failure_is_logged_not_silenced(self, caplog):
        """
        Claims malformados (ValueError) devem gerar log.info com 'JWTClaimsMiddleware',
        NÃO ser silenciados com except Exception: pass.
        Nível: INFO (path ValueError/KeyError do middleware).
        """
        import logging
        from django.test import RequestFactory
        from shared.middleware import JWTClaimsMiddleware

        rf = RequestFactory()
        request = rf.get("/", HTTP_AUTHORIZATION="Bearer token.invalido.aqui")

        called = []
        def fake_get_response(req):
            called.append(True)
            from django.http import HttpResponse
            return HttpResponse()

        middleware = JWTClaimsMiddleware(fake_get_response)

        fake_adapter = MagicMock()
        # ValueError → capturado por except (ValueError, KeyError) → logger.info
        fake_adapter.return_value.verify_access_token.side_effect = ValueError("bad token")

        with patch("identity_access.infrastructure.jwt_adapter.JWTAdapter", fake_adapter):
            # Capturar INFO (não apenas WARNING — ValueError usa logger.info)
            with caplog.at_level(logging.INFO, logger="shared.middleware"):
                middleware(request)

        # O request deve ter sido processado (get_response chamado)
        assert called, "get_response não foi chamado após falha JWT"
        # Log DEVE ter sido emitido — qualquer coisa silenciosa é falha de observabilidade
        assert caplog.records, (
            "Nenhum log emitido após ValueError — falha JWT está sendo silenciada"
        )
        assert any("JWTClaimsMiddleware" in r.message for r in caplog.records), (
            f"Log não menciona JWTClaimsMiddleware. Records: {[r.message for r in caplog.records]}"
        )

    def test_jwt_exception_is_logged_at_warning(self, caplog):
        """
        Falha de verificação JWT (RuntimeError — assinatura inválida, expiração, chave errada)
        deve ser logada em WARNING, não silenciada.
        Nível: WARNING (path except Exception do middleware).
        """
        import logging
        from django.test import RequestFactory
        from shared.middleware import JWTClaimsMiddleware

        rf = RequestFactory()
        request = rf.get("/", HTTP_AUTHORIZATION="Bearer valid.looking.token")

        def fake_get_response(req):
            from django.http import HttpResponse
            return HttpResponse()

        middleware = JWTClaimsMiddleware(fake_get_response)

        fake_adapter = MagicMock()
        # RuntimeError → capturado por except Exception → logger.warning
        fake_adapter.return_value.verify_access_token.side_effect = RuntimeError("signature invalid")

        with patch("identity_access.infrastructure.jwt_adapter.JWTAdapter", fake_adapter):
            with caplog.at_level(logging.WARNING, logger="shared.middleware"):
                middleware(request)

        assert caplog.records, (
            "Nenhum log WARNING emitido após RuntimeError — falha de verificação JWT silenciada"
        )
        warning_records = [r for r in caplog.records if r.levelno >= logging.WARNING]
        assert warning_records, (
            f"Log emitido mas não em WARNING ou acima. Records: {[(r.levelname, r.message) for r in caplog.records]}"
        )
        assert any("JWTClaimsMiddleware" in r.message for r in warning_records)

    def test_valid_token_populates_actor_id(self):
        """Token válido deve popular request._actor_id."""
        from django.test import RequestFactory
        from shared.middleware import JWTClaimsMiddleware

        actor_id = str(uuid.uuid4())
        session_id = str(uuid.uuid4())

        rf = RequestFactory()
        request = rf.get("/", HTTP_AUTHORIZATION="Bearer valid.token.here")

        def fake_get_response(req):
            from django.http import HttpResponse
            return HttpResponse()

        middleware = JWTClaimsMiddleware(fake_get_response)

        fake_adapter = MagicMock()
        fake_adapter.return_value.verify_access_token.return_value = {
            "sub": actor_id,
            "session_id": session_id,
            "roles": ["coach"],
        }

        with patch("identity_access.infrastructure.jwt_adapter.JWTAdapter", fake_adapter):
            middleware(request)

        assert str(getattr(request, "_actor_id", "")) == actor_id
        assert getattr(request, "_actor_role", "") == "coach"


# ══════════════════════════════════════════════════════════════════════════════
# C4 — notifications/middleware.py: JWT NÃO em query string
# ══════════════════════════════════════════════════════════════════════════════

class TestTokenAuthMiddlewareNoQueryString:
    """C4: o token JWT não deve ser aceito via query string."""

    def test_query_string_token_ignored(self):
        """
        Scope com ?token=<jwt> na query string NÃO deve popular user_id.
        Garantia: JWT não vaza via URL.
        """
        import asyncio
        from notifications.middleware import TokenAuthMiddleware

        scope = {
            "type": "websocket",
            "query_string": b"token=fake-jwt-in-qs",
            "subprotocols": [],
            "headers": [],
        }
        inner = AsyncMock()
        mw = TokenAuthMiddleware(inner)

        async def run():
            await mw(scope, AsyncMock(), AsyncMock())

        asyncio.run(run())
        # user_id NÃO deve ter sido definido via query string
        assert "user_id" not in scope, (
            "TokenAuthMiddleware ainda aceita token via query string — vulnerabilidade de exposição"
        )

    def test_subprotocol_token_accepted(self):
        """
        Token via subprotocol 'hbtrack-token.<jwt>' deve popular user_id.
        """
        import asyncio
        from notifications.middleware import TokenAuthMiddleware

        actor_id = str(uuid.uuid4())
        scope = {
            "type": "websocket",
            "query_string": b"",
            "subprotocols": [f"hbtrack-token.valid-jwt"],
            "headers": [],
        }
        inner = AsyncMock()

        fake_adapter = MagicMock()
        fake_adapter.return_value.verify_access_token.return_value = {"sub": actor_id}

        async def run():
            with patch("identity_access.infrastructure.jwt_adapter.JWTAdapter", fake_adapter):
                mw = TokenAuthMiddleware(inner)
                await mw(scope, AsyncMock(), AsyncMock())

        asyncio.run(run())
        assert scope.get("user_id") == actor_id

    def test_authorization_header_token_accepted(self):
        """
        Token via header Authorization: Bearer <jwt> no handshake deve popular user_id.
        """
        import asyncio
        from notifications.middleware import TokenAuthMiddleware

        actor_id = str(uuid.uuid4())
        scope = {
            "type": "websocket",
            "query_string": b"",
            "subprotocols": [],
            "headers": [(b"authorization", b"Bearer valid-jwt-header")],
        }
        inner = AsyncMock()

        fake_adapter = MagicMock()
        fake_adapter.return_value.verify_access_token.return_value = {"sub": actor_id}

        async def run():
            with patch("identity_access.infrastructure.jwt_adapter.JWTAdapter", fake_adapter):
                mw = TokenAuthMiddleware(inner)
                await mw(scope, AsyncMock(), AsyncMock())

        asyncio.run(run())
        assert scope.get("user_id") == actor_id

    def test_invalid_token_does_not_set_user_id(self):
        """Token inválido (verify retorna None) não deve popular user_id."""
        import asyncio
        from notifications.middleware import TokenAuthMiddleware

        scope = {
            "type": "websocket",
            "query_string": b"",
            "subprotocols": ["hbtrack-token.invalid-jwt"],
            "headers": [],
        }
        inner = AsyncMock()

        fake_adapter = MagicMock()
        fake_adapter.return_value.verify_access_token.return_value = None

        async def run():
            with patch("identity_access.infrastructure.jwt_adapter.JWTAdapter", fake_adapter):
                mw = TokenAuthMiddleware(inner)
                await mw(scope, AsyncMock(), AsyncMock())

        asyncio.run(run())
        assert "user_id" not in scope


# ══════════════════════════════════════════════════════════════════════════════
# C5 — infra/docker-compose.staging.yml: migrate separado da API
# ══════════════════════════════════════════════════════════════════════════════

class TestDockerComposeStagingBootstrap:
    """C5: migrate/collectstatic devem estar no serviço 'bootstrap', não na API."""

    def _parse_compose(self) -> dict:
        import yaml
        compose_path = ROOT / "infra" / "docker-compose.staging.yml"
        return yaml.safe_load(compose_path.read_text())

    def test_api_entrypoint_has_no_migrate(self):
        """Entrypoint do serviço 'api' não deve conter 'migrate'."""
        compose = self._parse_compose()
        api = compose["services"]["api"]
        entrypoint = " ".join(api.get("entrypoint", []))
        assert "migrate" not in entrypoint, (
            "Serviço 'api' ainda executa migrate no entrypoint — deve ser separado"
        )

    def test_api_entrypoint_has_no_collectstatic(self):
        """Entrypoint do serviço 'api' não deve conter 'collectstatic'."""
        compose = self._parse_compose()
        api = compose["services"]["api"]
        entrypoint = " ".join(api.get("entrypoint", []))
        assert "collectstatic" not in entrypoint

    def test_bootstrap_service_exists(self):
        """Serviço 'bootstrap' deve existir para executar migrate/collectstatic."""
        compose = self._parse_compose()
        assert "bootstrap" in compose["services"], (
            "Serviço 'bootstrap' ausente no docker-compose.staging.yml"
        )

    def test_bootstrap_runs_migrate(self):
        """Serviço 'bootstrap' deve executar migrate."""
        compose = self._parse_compose()
        bootstrap = compose["services"]["bootstrap"]
        entrypoint = " ".join(bootstrap.get("entrypoint", []))
        assert "migrate" in entrypoint

    def test_api_depends_on_bootstrap(self):
        """Serviço 'api' deve depender do 'bootstrap' com condition service_completed_successfully."""
        compose = self._parse_compose()
        api = compose["services"]["api"]
        depends = api.get("depends_on", {})
        if isinstance(depends, list):
            assert "bootstrap" in depends
        else:
            assert "bootstrap" in depends
            cond = depends["bootstrap"].get("condition", "")
            assert cond == "service_completed_successfully", (
                f"Condição de dependência incorreta: '{cond}'"
            )


# ══════════════════════════════════════════════════════════════════════════════
# C6 — Dockerfile: label org.opencontainers.image.source correto
# ══════════════════════════════════════════════════════════════════════════════

class TestDockerfileLabel:
    """C6: label de source deve apontar para o repositório auditado."""

    def test_image_source_label_is_correct(self):
        """LABEL org.opencontainers.image.source deve ser hbtrack/official."""
        dockerfile_path = ROOT / "Dockerfile"
        content = dockerfile_path.read_text()
        # Deve conter hbtrack/official (não hbtrack/hb-track)
        assert "hbtrack/official" in content, (
            "Dockerfile label 'org.opencontainers.image.source' aponta para repositório errado"
        )

    def test_image_source_label_not_old_value(self):
        """Label não deve mais apontar para hbtrack/hb-track."""
        dockerfile_path = ROOT / "Dockerfile"
        content = dockerfile_path.read_text()
        assert "hbtrack/hb-track" not in content, (
            "Label antigo 'hbtrack/hb-track' ainda presente no Dockerfile"
        )
