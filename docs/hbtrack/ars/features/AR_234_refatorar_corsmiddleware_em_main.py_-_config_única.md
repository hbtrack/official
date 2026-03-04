# AR_234 — Refatorar CORSMiddleware em main.py — config única via settings

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Remover o bloco if/else is_production que duplica configuração CORS e substituir por um único add_middleware lendo de settings. Adicionar log de evidência no startup. Corrigir comentário de ordem invertido.

## Dependência
AR_233 staged (config.py com novos campos CORS em Settings).

## 1) Remover bloco if/else CORS (linhas ~89–110 de main.py)

Substituir:
```python
# CORS - Adicionar PRIMEIRO para ser executado por ÚLTIMO (mais externo)
# Isso garante que o CORS processe OPTIONS antes de qualquer autenticação
if settings.is_production:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID", "X-Organization-ID"],
        expose_headers=["X-Request-ID"],
        max_age=600,
    )
else:
    # Dev mode: permite localhost E 127.0.0.1
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )
```

Por:
```python
# CORS — Política determinística lida de settings (AR_234)
# Starlette processa middlewares em ordem LIFO: o adicionado PRIMEIRO é o INNERMOST
# (processa resposta primeiro; recebe request por último).
# Preflight OPTIONS é seguro: CSRFMiddleware só intercepta UNSAFE_METHODS
# (POST/PUT/PATCH/DELETE) — OPTIONS passa diretamente para o CORSMiddleware.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.cors_allow_methods_list,
    allow_headers=settings.cors_allow_headers_list,
    expose_headers=settings.cors_expose_headers_list,
    max_age=settings.CORS_MAX_AGE,
    **({
        "allow_origin_regex": settings.CORS_ALLOW_ORIGIN_REGEX
    } if settings.CORS_ALLOW_ORIGIN_REGEX else {}),
)
```

## 2) Log de evidência no startup/lifespan

No bloco de startup (lifespan ou @app.on_event('startup')), adicionar após o healthcheck:

```python
logger.info(
    "CORS config: origins=%s credentials=%s methods=%s headers=%s",
    settings.cors_origins_list,
    settings.CORS_ALLOW_CREDENTIALS,
    settings.cors_allow_methods_list,
    settings.cors_allow_headers_list,
)
```

Não logar CORS_ALLOW_ORIGIN_REGEX (pode conter padrão sensível), tokens ou valores de headers de request.

## 3) Verificação proxy canary (obrigatória no executor_main.log)

Após o app subir, o Executor deve rodar e anexar a saída COMPLETA (não truncar) no executor_main.log:

**Curl 1 — Preflight direto no backend (porta local):**
```
curl -si -X OPTIONS http://localhost:8000/api/v1/health/liveness \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: Authorization, X-CSRF-Token"
```

**Curl 2 — Request real direto no backend:**
```
curl -si http://localhost:8000/api/v1/health/liveness \
  -H "Origin: http://localhost:3000" \
  -H "Authorization: Bearer dummy_token_for_cors_test"
```

**Curl 3 (opcional, se domínio público disponível) — Preflight via domínio:**
```
curl -si -X OPTIONS https://<dominio_stg_ou_prod>/api/v1/health/liveness \
  -H "Origin: <origin_esperada>" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: Authorization, X-CSRF-Token"
```

A saída de cada curl deve incluir integralmente:
- Status line (ex.: HTTP/1.1 200 OK ou HTTP/2 200)
- access-control-allow-origin
- access-control-allow-methods
- access-control-allow-headers
- access-control-allow-credentials
- vary (se presente)

Se Curl 1 tem headers CORS e Curl 3 não → evidência de proxy removendo headers → abrir AR de infra separada (não bloqueia AR_234).

## Critérios de Aceite
AC-001: python -c "from app.main import app; print('OK')" executa sem erro (app sobe com nova config).
AC-002: O bloco if settings.is_production não existe mais na seção CORS de main.py.
AC-003: Todos os parâmetros de CORSMiddleware lidos de settings.* (nenhum valor hardcoded).
AC-004: executor_main.log contém saída completa de pelo menos Curl 1 e Curl 2, incluindo status line e headers access-control-*.
AC-005: Log de startup contém linha 'CORS config: origins=' com valores efetivos.

## Write Scope
- Hb Track - Backend/app/main.py

## Validation Command (Contrato)
```
cd "Hb Track - Backend" && python -c "from app.main import app; print('OK')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_234/executor_main.log`

## Notas do Arquiteto
O allow_origin_regex condicional (**{} if None) garante que o campo só é passado ao CORSMiddleware quando configurado — evita Starlette receber None para regex. Starlette 0.50.0 aceita allow_origin_regex=None mas melhor ser explícito.

## Riscos
- Se CORS_ALLOW_CREDENTIALS=true no .env e CORS_ALLOW_ORIGINS contiver wildcard, o fail-fast de AR_233 impedirá o boot — necessário .env válido antes de AR_234.
- Remover branch dev muda comportamento: staging/CI que não define CORS_ALLOW_ORIGINS herdará o default de Settings — verificar se default é suficiente.
- Proxy/CDN pode remover headers CORS — Curl 3 no executor_main.log evidencia isso sem bloquear a AR.

## Análise de Impacto

**Arquivo modificado:** `Hb Track - Backend/app/main.py`

**Mudança:** Remoção do bloco `if settings.is_production / else` (~linhas 91–111) que duplicava a configuração CORS com valores hardcoded. Substituição por um único `app.add_middleware(CORSMiddleware, ...)` lendo todos os parâmetros de `settings.*` (campos providos por AR_233).

**Adição:** `logger.info("CORS config: origins=%s ...")` no bloco `startup_event()`, após o log de background tasks, para evidência canônica em startup.

**Impacto zero em:** Backend/Frontend além do `main.py`; banco de dados; rotas; schemas. Sem alteração em `config.py` (AR_233), `tests/` (AR_235), ou qualquer outro arquivo fora do write_scope.

**Risco mitigado:** `.env` local herda defaults de Settings (AR_233): `CORS_ALLOW_CREDENTIALS=true`, `CORS_ALLOW_ORIGINS=http://localhost:3000,http://localhost:3001,...`. Fail-fast de AR_233 impedirá boot se wildcard + credentials — não aplicável aqui.

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em b452cbf
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `cd "Hb Track - Backend" && python -c "from app.main import app; print('OK')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-04T13:03:03.649468+00:00
**Behavior Hash**: d6913e35a48fbda2cab914089cbbae790f406f5857def0cc0b0cdc22d08e9713
**Evidence File**: `docs/hbtrack/evidence/AR_234/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em b452cbf
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_234_b452cbf/result.json`

### Selo Humano em b452cbf
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-03-04T13:07:15.023335+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_234_b452cbf/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_234/executor_main.log`
