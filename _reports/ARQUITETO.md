# ARQUITETO.md — Handoff para Executor

<!-- PLAN_HANDOFF -->

**Protocolo**: 1.3.0
**AR IDs**: [232, 900]
**Branch**: dev-changes-2
**HEAD**: b452cbf
**Data Planejamento**: 2026-03-04
**Status**: PLAN_HANDOFF
**OPS SSOT**: docs/invariantes/INVARIANTS_OPERACIONAIS_HBTRACK.md (v1.4.0)

---

## 0. PRE-FLIGHT / STOP CONDITIONS

```
PRE-FLIGHT obrigatório antes de qualquer edição:
  git status                     # workspace clean = sem tracked-unstaged
  git diff --name-only           # deve estar vazio

STOP CONDITIONS (abortar e reportar exit code):
  BLOCKED_INPUT  (exit 4) — AR não existe, plano ilegível, dependência não VERIFICADA
  ERROR_INFRA    (exit 3) — hb plan/report retorna stack trace ou erro de infraestrutura
  FAIL_ACTIONABLE (exit 2) — AC falhou, hb verify < 3/3, hash divergente
```

---

## 1. Contexto

**Batch 22 — AR_232 (AR-TRAIN-051)**: Done Gate §10 formal do módulo TRAINING.

Substitui AR-TRAIN-043 (OBSOLETA). Fecha o módulo TRAINING com §10 formal, bump TEST_MATRIX→v3.0.0 e declaração `DONE_GATE_TRAINING_v3.md`. **Zero toque em Backend ou Frontend.**

**AR_232 (AR-TRAIN-051) SEALED** (hb seal 2026-03-03) — Done Gate §10 formal do módulo TRAINING concluído.

**CORS Hardening** (AR_233–235): diagnóstico do backend FastAPI revelou 4 gaps críticos que serão corrigidos em 3 ARs sequenciais:

| Gap | Severidade |
|---|---|
| Branch dev usa `allow_headers=["*"]` + `credentials=True` (browser bloqueia por spec) | CRÍTICO |
| `CORS_ALLOW_CREDENTIALS` da env não é lido — campo inexistente em `Settings` (`extra="ignore"`) | ALTO |
| `CORS_ORIGINS` da env ignorada em dev/staging — origens hardcoded | ALTO |
| `X-CSRF-Token` e `Accept` ausentes em `allow_headers` de produção | MÉDIO |
| Zero testes de preflight/headers CORS | CRÍTICO (DoD) |

**SSOTs verificados antes do plano:**
- `docs/ssot/schema.sql`, `openapi.json`, `alembic_state.txt` — não tocados (CORS não altera banco)
- `Hb Track - Backend/app/core/config.py` — lido integralmente (134 linhas)
- `Hb Track - Backend/app/main.py` — bloco CORS identificado nas linhas 89–131
- `Hb Track - Backend/app/middleware/csrf.py` — confirmado: `UNSAFE_METHODS = {POST,PUT,PATCH,DELETE}` (OPTIONS exempt)
- `Hb Track - Backend/app/api/v1/routers/health.py` — confirmado: `/health/liveness` público e sem banco
- `Hb Track - Backend/app/api/v1/routers/auth.py` — confirmado: cookie auth real (`hb_access_token`, HttpOnly, SameSite=Lax) → `credentials=True` mandatório

**Plano gerado:** `docs/_canon/planos/ar_cors_hardening_233.json`
**Dry-run:** ✅ `3 ARs seriam criados, 0 seriam pulados. Todas as validações passaram.`

---

## 2. Planos Materializados

| AR | Plano JSON | Dependência | Dry-Run |
|---|---|---|---|
| **AR_233** | `docs/_canon/planos/ar_cors_hardening_233.json` (task 233) | AR_232 SEALED ✅ | ✅ PASS |
| **AR_234** | `docs/_canon/planos/ar_cors_hardening_233.json` (task 234) | AR_233 staged | ✅ PASS |
| **AR_235** | `docs/_canon/planos/ar_cors_hardening_233.json` (task 235) | AR_234 staged | ✅ PASS |

> **Atenção**: As 3 tasks estão em um único Plan JSON. O Executor materializa todas com `hb plan ar_cors_hardening_233.json` e executa em sequência.

---

## 3. Ordem de Execução

```
AR_233 (config.py + .env.example)
    → AR_234 (main.py — depende de Settings novos de AR_233)
        → AR_235 (tests/test_cors.py — depende de app refatorado de AR_234)
```

**Sequencial estrito**: cada AR deve ter `hb report` + staging antes da próxima iniciar.

---

## 4. Diagnóstico por AR

### AR_233 — Centralizar config CORS em config.py + validação fail-fast

**write_scope:**
```
Hb Track - Backend/app/core/config.py
Hb Track - Backend/.env.example
```

**validation_command:**
```bash
cd "Hb Track - Backend" && pytest -q tests/unit/test_config.py
```

**Campos novos em Settings:**
```python
CORS_ALLOW_CREDENTIALS: bool = True
CORS_ALLOW_ORIGIN_REGEX: Optional[str] = None
CORS_ALLOW_HEADERS: str = "Authorization,Content-Type,Accept,X-CSRF-Token,X-Request-ID,X-Organization-ID"
CORS_ALLOW_METHODS: str = "GET,POST,PUT,PATCH,DELETE,OPTIONS"
CORS_EXPOSE_HEADERS: str = "X-Request-ID"
CORS_MAX_AGE: int = 600
```

**model_validator fail-fast:**
- Regra 1: `credentials=True` + `"*"` em origins → ValueError ("wildcard")
- Regra 2: `credentials=True` + `CORS_ALLOW_ORIGIN_REGEX is not None` → ValueError ("REGEX")

**cors_origins_list corrigido** — filtrar itens vazios (tolera trailing comma):
```python
return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]
```

**Critérios de aceite:**
- AC-001: `Settings(credentials=True, origins="*")` → ValidationError/ValueError com "wildcard"
- AC-002: `Settings(credentials=True, regex=".*")` → ValidationError/ValueError com "REGEX"
- AC-003: `Settings(origins="http://a.test, http://b.test,").cors_origins_list == ["http://a.test","http://b.test"]`
- AC-004: Settings válido sobe sem erro
- AC-005: `pytest tests/unit/test_config.py` passa

**Riscos:**
- `model_validator` requer `from pydantic import model_validator` (pydantic v2 ✅)
- Filtrar vazios pode afetar testes que dependam de lista com strings vazias (verificar)
- Se renomear `CORS_ORIGINS` para `CORS_ALLOW_ORIGINS` no .env, atualizar `.env` de produção — documentar no log

---

### AR_234 — Refatorar CORSMiddleware em main.py

**Dependência:** AR_233 staged

**write_scope:**
```
Hb Track - Backend/app/main.py
```

**validation_command:**
```bash
cd "Hb Track - Backend" && python -c "from app.main import app; print('OK')"
```

**Substituição principal** (remover bloco if/else ~linhas 89–110, inserir):
```python
# CORS — Política determinística lida de settings (AR_234)
# Starlette: middleware adicionado PRIMEIRO = INNERMOST (LIFO).
# Preflight OPTIONS: CSRFMiddleware só intercepta UNSAFE_METHODS → OPTIONS passa livre.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.cors_allow_methods_list,
    allow_headers=settings.cors_allow_headers_list,
    expose_headers=settings.cors_expose_headers_list,
    max_age=settings.CORS_MAX_AGE,
    **({"allow_origin_regex": settings.CORS_ALLOW_ORIGIN_REGEX}
       if settings.CORS_ALLOW_ORIGIN_REGEX else {}),
)
```

**Log de startup:**
```python
logger.info(
    "CORS config: origins=%s credentials=%s methods=%s headers=%s",
    settings.cors_origins_list,
    settings.CORS_ALLOW_CREDENTIALS,
    settings.cors_allow_methods_list,
    settings.cors_allow_headers_list,
)
```

**Proxy Canary — obrigatório no executor_main.log (saída COMPLETA, não truncar):**

```bash
# Curl 1 — Preflight direto
curl -si -X OPTIONS http://localhost:8000/api/v1/health/liveness \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: Authorization, X-CSRF-Token"

# Curl 2 — Request real direto
curl -si http://localhost:8000/api/v1/health/liveness \
  -H "Origin: http://localhost:3000" \
  -H "Authorization: Bearer dummy_token_for_cors_test"

# Curl 3 — Via domínio público (opcional, se disponível)
curl -si -X OPTIONS https://<dominio>/api/v1/health/liveness \
  -H "Origin: <origin_esperada>" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: Authorization, X-CSRF-Token"
```

Cada curl deve registrar: **status line**, `access-control-allow-origin`, `access-control-allow-methods`, `access-control-allow-headers`, `access-control-allow-credentials`, `vary`.

Se Curl 1 tem headers CORS mas Curl 3 não → **abrir AR de infra separada** (não bloqueia AR_234).

**Critérios de aceite:**
- AC-001: Import do app sem erro
- AC-002: Bloco `if settings.is_production` removido da seção CORS
- AC-003: Todos os parâmetros de `CORSMiddleware` lidos de `settings.*`
- AC-004: `executor_main.log` com Curl 1 + Curl 2 integrais
- AC-005: Log de startup contém `"CORS config: origins="`

**Riscos:**
- `.env` deve ter config válida antes de AR_234 (fail-fast de AR_233 impede boot com wildcard)
- Staging/CI sem `CORS_ALLOW_ORIGINS` herdará default de Settings — verificar

---

### AR_235 — Criar tests/test_cors.py

**Dependência:** AR_234 staged

**write_scope:**
```
Hb Track - Backend/tests/test_cors.py
```

**validation_command:**
```bash
cd "Hb Track - Backend" && pytest -q tests/test_cors.py
```

**Rota alvo:** `GET /api/v1/health/liveness` — público, sem banco (`{"status":"alive"}`)
*(NÃO usar `/health` linha 23 — faz `healthcheck_db()`)*

**Testes:**

| Função | AC |
|---|---|
| `test_preflight_allowed_origin` | AC-001: allow-origin, allow-methods(GET), allow-headers(Authorization+X-CSRF-Token), allow-credentials=true |
| `test_preflight_blocked_origin` | AC-002: header `access-control-allow-origin` ausente (sem checar status code) |
| `test_real_request_allowed_origin` | AC-003: GET com Origin permitida → allow-origin correto |
| `test_credentials_wildcard_fail_fast` | AC-004: `Settings(origins="*", credentials=True)` → ValidationError/ValueError |
| `test_origins_read_from_env_with_spaces` | AC-005: `"http://a.test, http://b.test,"` → `["http://a.test","http://b.test"]` |
| `pytest -q` | AC-006: 5 passed, 0 failed, 0 error |

**Preflight request** (enviar `Access-Control-Request-Headers` explícito):
```
Origin: http://allowed.test
Access-Control-Request-Method: GET
Access-Control-Request-Headers: Authorization, X-CSRF-Token
```

**Riscos:**
- Fixture com `importlib.reload` pode ter efeitos colaterais — usar `scope="module"` + isolamento
- `test_credentials_wildcard_fail_fast` precisa de `JWT_SECRET` override para evitar ValidationError de campo obrigatório unrelated
- Se lifespan disparar `healthcheck_db` no TestClient → mockar o startup ou usar `TestClient(app, raise_server_exceptions=False)` com mock de DB

---

## 5. Comando de materialização

```bash
cd "c:\HB TRACK"
python scripts/run/hb_cli.py plan docs/_canon/planos/ar_cors_hardening_233.json
```

*(sem `--dry-run` — já validado ✅)*

---

## 6. Rollback por AR

| AR | Rollback |
|---|---|
| AR_233 | Reverter `app/core/config.py` (remover campos novos + model_validator) e `.env.example` |
| AR_234 | Reverter `app/main.py` para bloco `if settings.is_production` original |
| AR_235 | Remover `tests/test_cors.py` |

Logs e evidências mantidos mesmo em rollback.

---

*Arquiteto — 2026-03-03 — CORS Hardening AR_233–235 planejado, dry-run ✅*

---

## AR_900 — E2E: Verificação pipeline DoD (GOVERNANCE_ONLY)

**Objetivo**: Provar que o ciclo DoD (DOC-GATE-019/020/021 + DOD-TABLE/V1 + strict verify + gen_test_matrix) está operacional end-to-end.

**CLASS**: GOVERNANCE_ONLY — zero toque em código de produto.

**PROOF**: `Hb Track - Backend/tests/training/contracts/test_e2e_dod_pipeline.py::test_wellness_rankings_route_contract_declared`

**TRACE**: `docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md` (§8 CONTRACT-TRAIN-073 → COBERTO via gen_test_matrix --update-matrix)

**write_scope**: `Hb Track - Backend/tests/training/contracts/test_e2e_dod_pipeline.py`

*AR_900 adicionada em 2026-03-04 — E2E controlado do pipeline DoD*
