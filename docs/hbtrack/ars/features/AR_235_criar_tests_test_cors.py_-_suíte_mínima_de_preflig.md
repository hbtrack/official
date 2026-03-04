# AR_235 — Criar tests/test_cors.py — suíte mínima de preflight e request real

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Criar arquivo tests/test_cors.py com 5 testes de integração leves (sem banco) cobrindo preflight, request real, origem bloqueada, fail-fast e strip de env.

## Dependência
AR_234 staged.

## Rota alvo
`GET /api/v1/health/liveness` — confirmado público, sem banco, retorna {status: alive}.

## Fixture

```python
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

@pytest.fixture(scope="module")
def cors_client():
    """App com CORS configurado para http://allowed.test — sem dependência de banco."""
    with patch.dict("os.environ", {
        "CORS_ALLOW_ORIGINS": "http://allowed.test",
        "CORS_ALLOW_CREDENTIALS": "true",
        "CORS_ALLOW_HEADERS": "Authorization,Content-Type,Accept,X-CSRF-Token,X-Request-ID,X-Organization-ID",
        "CORS_ALLOW_METHODS": "GET,POST,PUT,PATCH,DELETE,OPTIONS",
        "CORS_EXPOSE_HEADERS": "X-Request-ID",
        "CORS_MAX_AGE": "600",
        "ENV": "test",
        "JWT_SECRET": "test_secret_for_cors_tests",
    }):
        # Re-importar settings com os novos valores de env
        import importlib
        import app.core.config as cfg_module
        importlib.reload(cfg_module)
        from app.core.config import Settings
        test_settings = Settings()

        from app.main import create_app  # ou importar app diretamente
        # Se não houver factory, usar a instância global com override
        from app import main as main_module
        importlib.reload(main_module)
        app_instance = main_module.app
        client = TestClient(app_instance, raise_server_exceptions=False)
        yield client
```

Nota: Se o app não tiver factory (create_app), o Executor deve usar override de settings via dependency_overrides ou via importlib.reload do módulo — adaptar conforme estrutura real do main.py.

## Testes

### test_preflight_allowed_origin
```python
def test_preflight_allowed_origin(cors_client):
    """Preflight de origem permitida retorna headers CORS completos."""
    response = cors_client.options(
        "/api/v1/health/liveness",
        headers={
            "Origin": "http://allowed.test",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Authorization, X-CSRF-Token",
        }
    )
    assert response.headers.get("access-control-allow-origin") == "http://allowed.test"
    assert "GET" in response.headers.get("access-control-allow-methods", "")
    assert "authorization" in response.headers.get("access-control-allow-headers", "").lower()
    assert "x-csrf-token" in response.headers.get("access-control-allow-headers", "").lower()
    assert response.headers.get("access-control-allow-credentials") == "true"
```

### test_preflight_blocked_origin
```python
def test_preflight_blocked_origin(cors_client):
    """Preflight de origem não-permitida não retorna Access-Control-Allow-Origin."""
    response = cors_client.options(
        "/api/v1/health/liveness",
        headers={
            "Origin": "http://evil.test",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Authorization",
        }
    )
    # Starlette responde sem o header (não necessariamente 403)
    assert "access-control-allow-origin" not in response.headers
```

### test_real_request_allowed_origin
```python
def test_real_request_allowed_origin(cors_client):
    """Request real com Origin permitida retorna Access-Control-Allow-Origin correto."""
    response = cors_client.get(
        "/api/v1/health/liveness",
        headers={
            "Origin": "http://allowed.test",
            "Authorization": "Bearer dummy_for_cors_test",
        }
    )
    assert response.headers.get("access-control-allow-origin") == "http://allowed.test"
```

### test_credentials_wildcard_fail_fast
```python
def test_credentials_wildcard_fail_fast():
    """Settings com credentials=True + wildcard deve levantar ValidationError."""
    import pytest
    from pydantic import ValidationError
    from app.core.config import Settings
    with pytest.raises((ValidationError, ValueError)):
        Settings(
            CORS_ALLOW_ORIGINS="*",
            CORS_ALLOW_CREDENTIALS=True,
            JWT_SECRET="test_secret",
        )
```

### test_origins_read_from_env_with_spaces
```python
def test_origins_read_from_env_with_spaces():
    """cors_origins_list faz strip e filtra itens vazios."""
    from app.core.config import Settings
    s = Settings(
        CORS_ALLOW_ORIGINS="http://a.test, http://b.test,",
        CORS_ALLOW_CREDENTIALS=False,
        JWT_SECRET="test_secret",
    )
    assert s.cors_origins_list == ["http://a.test", "http://b.test"]
```

## Critérios de Aceite
AC-001: test_preflight_allowed_origin — response tem access-control-allow-origin=http://allowed.test, allow-methods contém GET, allow-headers contém Authorization e X-CSRF-Token, allow-credentials=true.
AC-002: test_preflight_blocked_origin — access-control-allow-origin ausente na response de origin não listada.
AC-003: test_real_request_allowed_origin — GET com Origin permitida retorna access-control-allow-origin correto.
AC-004: test_credentials_wildcard_fail_fast — ValidationError ou ValueError levantado.
AC-005: test_origins_read_from_env_with_spaces — lista resultante é ['http://a.test', 'http://b.test'] (strip + filtro de vazio).
AC-006: pytest -q tests/test_cors.py retorna 5 passed, 0 failed, 0 error.

## Write Scope
- Hb Track - Backend/tests/test_cors.py

## Validation Command (Contrato)
```
cd "Hb Track - Backend" && pytest -q tests/test_cors.py
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_235/executor_main.log`

## Notas do Arquiteto
Rota alvo confirmada: health.py linha 47 — GET /api/v1/health/liveness retorna {status:alive} sem tocar banco. Preflight envia Access-Control-Request-Headers: Authorization, X-CSRF-Token para validar que allow-headers cobre os casos reais do sistema (cookie auth + CSRF). Blocked origin: asserção é ausência do header, não status code específico — Starlette retorna 200 sem header CORS para origins não listadas. Se o Executor precisar de override de settings sem importlib.reload (ex.: app usa settings como singleton injetado), usar app.dependency_overrides com get_settings() ou equivalent.

## Riscos
- Fixture com importlib.reload pode ter efeitos colaterais se outros testes rodarem em paralelo — usar scope='module' e garantir isolamento.
- Se app não tem factory create_app, o reload de main.py pode falhar se houver efeitos colaterais no import (ex.: conexão de banco no startup). Nesse caso, usar TestClient com lifespan=False ou mock do startup.
- test_credentials_wildcard_fail_fast instancia Settings diretamente — precisa ser executado sem .env ativo ou com override explícito de JWT_SECRET para evitar ValidationError por campo obrigatório unrelated.

## Análise de Impacto

**Arquivos criados:**
- `Hb Track - Backend/tests/test_cors.py` — novo arquivo; sem impacto em código de produção.

**Decisão de fixture (adaptação da Nota do Arquiteto):**
- `app.main` NÃO tem `create_app` factory; startup chama `warmup_database()` (IO real).
- Estratégia adotada: mini-app isolada (fresh `FastAPI()` + `CORSMiddleware` + rota liveness inline) com `importlib.reload(app.core.config)` dentro de `patch.dict` para obter `Settings` com env de teste.
- `importlib.reload(main_module)` NÃO executado — evita startup DB.
- Scope `module` garante que o reload não impacta outros módulos em paralelo.

**Variáveis de env injetadas no patch.dict (somente durante fixture):**
- `CORS_ORIGINS=http://allowed.test` (campo real confirmado em config.py L76)
- `CORS_ALLOW_CREDENTIALS=true`, `CORS_ALLOW_HEADERS`, `CORS_ALLOW_METHODS`, `CORS_EXPOSE_HEADERS`, `CORS_MAX_AGE`, `ENV=test`, `JWT_SECRET`

**AC-004 / AC-005:** Instanciam `Settings()` diretamente sem `.env` — campo `JWT_SECRET` passado explicitamente para evitar `ValidationError` por campo obrigatório não-relacionado.

**Riscos mitigados:**
- Nenhuma dependência de banco, Redis ou serviços externos nos 5 testes.
- Fixture restaura `cfg_module` no teardown (reload sem patch) para não contaminar outros testes.

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em b452cbf
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `cd "Hb Track - Backend" && pytest -q tests/test_cors.py`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-04T13:12:59.455289+00:00
**Behavior Hash**: 5a5373c01870b99752b2596a177623dfa35c0edafe1a983401b48710a2d53421
**Evidence File**: `docs/hbtrack/evidence/AR_235/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em b452cbf
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `cd "Hb Track - Backend" && pytest -q tests/test_cors.py`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-04T13:13:51.957929+00:00
**Behavior Hash**: 5a5373c01870b99752b2596a177623dfa35c0edafe1a983401b48710a2d53421
**Evidence File**: `docs/hbtrack/evidence/AR_235/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em b452cbf
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `cd "Hb Track - Backend" && pytest -q tests/test_cors.py`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-04T13:15:09.569626+00:00
**Behavior Hash**: 5a5373c01870b99752b2596a177623dfa35c0edafe1a983401b48710a2d53421
**Evidence File**: `docs/hbtrack/evidence/AR_235/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em b452cbf
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_235_b452cbf/result.json`

### Selo Humano em b452cbf
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-03-04T13:30:23.031750+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_235_b452cbf/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_235/executor_main.log`
