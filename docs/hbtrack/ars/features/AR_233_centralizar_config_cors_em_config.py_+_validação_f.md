# AR_233 — Centralizar config CORS em config.py + validação fail-fast

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Adicionar campos CORS explícitos à classe Settings em app/core/config.py e implementar validação fail-fast via model_validator.

## 1) Novos campos em Settings (app/core/config.py)

Adicionar após o campo CORS_ORIGINS existente:

```python
# CORS — política determinística
# CORS_ORIGINS já existe como str; os campos abaixo complementam
CORS_ALLOW_CREDENTIALS: bool = True
CORS_ALLOW_ORIGIN_REGEX: Optional[str] = None
CORS_ALLOW_HEADERS: str = "Authorization,Content-Type,Accept,X-CSRF-Token,X-Request-ID,X-Organization-ID"
CORS_ALLOW_METHODS: str = "GET,POST,PUT,PATCH,DELETE,OPTIONS"
CORS_EXPOSE_HEADERS: str = "X-Request-ID"
CORS_MAX_AGE: int = 600
```

## 2) Corrigir cors_origins_list + novas properties

Substituir a property cors_origins_list existente para filtrar itens vazios (tolera trailing comma):

```python
@property
def cors_origins_list(self) -> list[str]:
    """Converte CORS_ORIGINS de string para lista, com strip e filtro de vazios."""
    return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

@property
def cors_allow_headers_list(self) -> list[str]:
    return [h.strip() for h in self.CORS_ALLOW_HEADERS.split(",") if h.strip()]

@property
def cors_allow_methods_list(self) -> list[str]:
    return [m.strip() for m in self.CORS_ALLOW_METHODS.split(",") if m.strip()]

@property
def cors_expose_headers_list(self) -> list[str]:
    return [h.strip() for h in self.CORS_EXPOSE_HEADERS.split(",") if h.strip()]
```

## 3) Validação fail-fast — @model_validator(mode="after")

Adicionar após as properties, antes de model_config:

```python
@model_validator(mode="after")
def validate_cors_policy(self) -> "Settings":
    """Regras de segurança CORS — fail-fast no boot."""
    if self.CORS_ALLOW_CREDENTIALS:
        # Regra 1: credentials=True + wildcard é inválido (browser bloqueia, RFC 6454)
        if "*" in self.cors_origins_list:
            raise ValueError(
                "CORS inseguro: CORS_ALLOW_CREDENTIALS=True é incompatível com "
                "wildcard em CORS_ALLOW_ORIGINS. Use lista explícita de origens."
            )
        # Regra 2: credentials=True + regex — somente lista explícita é auditável
        if self.CORS_ALLOW_ORIGIN_REGEX is not None:
            raise ValueError(
                "CORS inseguro: CORS_ALLOW_CREDENTIALS=True é incompatível com "
                "CORS_ALLOW_ORIGIN_REGEX. Use CORS_ALLOW_ORIGINS com lista explícita."
            )
    return self
```

Adicionar import: `from pydantic import model_validator`

## 4) Atualizar .env.example — seção CORS

Substituir a seção CORS atual por:

```dotenv
# ============================================================================
# CORS — Política Determinística (AR_233)
# allow_credentials=True requer origens explícitas (nunca wildcard)
# ============================================================================
CORS_ALLOW_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
CORS_ALLOW_CREDENTIALS=true
# CORS_ALLOW_ORIGIN_REGEX=  # Proibido quando CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_HEADERS=Authorization,Content-Type,Accept,X-CSRF-Token,X-Request-ID,X-Organization-ID
CORS_ALLOW_METHODS=GET,POST,PUT,PATCH,DELETE,OPTIONS
CORS_EXPOSE_HEADERS=X-Request-ID
CORS_MAX_AGE=600
```

Nota: o campo CORS_ORIGINS legado (Settings) é mantido temporariamente para compatibilidade — main.py (AR_234) passará a usar CORS_ALLOW_ORIGINS via cors_origins_list. Ambos apontam para a mesma env var (CORS_ALLOW_ORIGINS no .env), lidos pelo mesmo campo renomeado em AR_234.

## Critérios de Aceite
AC-001: Settings instanciado com CORS_ALLOW_CREDENTIALS=True e CORS_ALLOW_ORIGINS='*' levanta ValidationError/ValueError com mensagem contendo 'wildcard'.
AC-002: Settings instanciado com CORS_ALLOW_CREDENTIALS=True e CORS_ALLOW_ORIGIN_REGEX='.*' levanta ValidationError/ValueError com mensagem contendo 'REGEX'.
AC-003: Settings(CORS_ALLOW_ORIGINS='http://a.test, http://b.test').cors_origins_list == ['http://a.test', 'http://b.test'] (strip + filtro).
AC-004: Settings instanciado com valores válidos (CORS_ALLOW_CREDENTIALS=True + origens explícitas) sobe sem erro.
AC-005: pytest tests/unit/test_config.py passa sem falhas após as alterações.

## Write Scope
- Hb Track - Backend/app/core/config.py
- Hb Track - Backend/.env.example

## Validation Command (Contrato)
```
cd "Hb Track - Backend" && pytest -q tests/unit/test_config.py
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_233/executor_main.log`

## Notas do Arquiteto
CORS_ORIGINS (campo legado) será mantido em Settings até AR_234 renomear para CORS_ALLOW_ORIGINS no .env. A property cors_origins_list continua lendo CORS_ORIGINS; em AR_234 o .env passa a ter CORS_ALLOW_ORIGINS mapeado para o mesmo campo — ou, se preferir zero-rename, manter CORS_ORIGINS como nome canônico e ajustar os novos campos com prefixo CORS_. O Executor deve escolher a abordagem de menor disrupção e documentar no executor_main.log.

## Riscos
- model_validator(mode='after') requer import de model_validator de pydantic — verificar se pydantic v2 está em uso (pydantic-settings 2.12.0 usa pydantic v2).
- Filtrar itens vazios em cors_origins_list pode mudar comportamento se algum teste atual depende da lista incluir strings vazias.
- Renomear CORS_ORIGINS para CORS_ALLOW_ORIGINS (se o Executor optar por isso) implica atualizar .env de produção — planejar rollback de env.

## Análise de Impacto

**Data:** 2026-03-03 | **Executor:** EXECUTOR

### Arquivos modificados
| Arquivo | Tipo de mudança |
|---|---|
| `Hb Track - Backend/app/core/config.py` | Adição: 6 campos CORS + 4 properties + model_validator + import model_validator |
| `Hb Track - Backend/.env.example` | Atualização: seção CORS expandida com campos canônicos |

### Decisão de nomenclatura
Mantido `CORS_ORIGINS` como nome do campo em Settings (zero-rename) para não quebrar `.env` de produção. Novos campos seguem padrão `CORS_ALLOW_*`. Env var `CORS_ORIGINS` no `.env` inalterada.

### Impacto em testes existentes
`test_settings_cors_origins_is_list` (test_config.py L28-33): valida `isinstance(settings.CORS_ORIGINS, str)` e `cors_origins_list` como lista não-vazia — compatível, semântica mantida. Nenhum teste depende de itens vazios na lista.

### Impacto em boot
`settings = Settings()` lê `.env` com `CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000` e `CORS_ALLOW_CREDENTIALS=true`. Com novos campos, `CORS_ALLOW_CREDENTIALS` passa a ser lido (antes `extra="ignore"`). Sem regressão — fail-fast não é ativado (origins explícitas, sem wildcard).

### Impacto em imports
Adicionado `model_validator` ao import de pydantic. pydantic-settings 2.12.0 usa pydantic v2 ✅.

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em b452cbf
**Status Executor**: ❌ FALHA
**Comando**: `cd "Hb Track - Backend" && pytest -q tests/unit/test_config.py`
**Exit Code**: 1
**Timestamp UTC**: 2026-03-04T02:52:53.020672+00:00
**Behavior Hash**: 7dd61878e05bc59654cfc9b8800883417e109c31f5c9fd61bdce6107249ddf51
**Evidence File**: `docs/hbtrack/evidence/AR_233/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em b452cbf
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `cd "Hb Track - Backend" && pytest -q tests/unit/test_config.py`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-04T02:54:11.701031+00:00
**Behavior Hash**: 587eb9944a62713d98b410b446e1e73556376eb2ac190395cf12a189bb3bc6d9
**Evidence File**: `docs/hbtrack/evidence/AR_233/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em b452cbf
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `cd "Hb Track - Backend" && pytest -q tests/unit/test_config.py`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-04T03:04:05.819257+00:00
**Behavior Hash**: 587eb9944a62713d98b410b446e1e73556376eb2ac190395cf12a189bb3bc6d9
**Evidence File**: `docs/hbtrack/evidence/AR_233/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em b452cbf
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `cd "Hb Track - Backend" && pytest -q tests/unit/test_config.py`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-04T03:06:42.735571+00:00
**Behavior Hash**: 587eb9944a62713d98b410b446e1e73556376eb2ac190395cf12a189bb3bc6d9
**Evidence File**: `docs/hbtrack/evidence/AR_233/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em b452cbf
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_233_b452cbf/result.json`

### Selo Humano em b452cbf
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-03-04T12:59:23.295222+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_233_b452cbf/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_233/executor_main.log`
