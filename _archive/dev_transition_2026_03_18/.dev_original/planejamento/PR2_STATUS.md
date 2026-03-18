# PR2: ENDURECIMENTO DE SCRIPTS/HB
> Refatoração Determinística — Fase 1-3 (CLI e State Model)

**Status**: ✅ **COMPLETA**  
**Data**: 2026-03-17  
**Testes**: 11 PASSED (incluindo 3 CLI virados GREEN), 1 FAILED (hook — PR4)

---

## Objetivo da PR2

Eliminar **defaults implícitos** de `scripts/hb`. Fazer CLI **obrigatório** fornecer:
- `hb verify --task-type <task> --module <mod>` (eram env vars opcionais)
- `hb check --module <mod>` (era env var opcional)
- `hb artifact <path>` com hash SHA-256 para detectar pós-validação stale

---

## Artefatos Criados/Modificados

### 1. `scripts/hb` v2 (Python, determinístico)
**Localização:** `/home/davis/HB-TRACK/scripts/hb`

**Mudanças:**
- ✅ Reescrito em Python (era bash com defaults implícitos)
- ✅ Carrega SSOTs na inicialização (BOOT_PROFILES, TASK_CATALOG, session_start.schema)
- ✅ Validação determinística **antes** de executar

**Comandos:**

| Comando | Mudança | Status |
|---------|---------|--------|
| `hb verify --task-type <task> --module <mod>` | ✅ OBRIGATÓRIO (era `${HB_TASK_TYPE:-unknown}`) | GREEN |
| `hb check --module <mod>` | ✅ OBRIGATÓRIO (era `${HB_MODULE:-unknown}`) | GREEN |
| `hb artifact <path>` | ✅ Upsert com SHA-256 | GREEN |
| `hb reset` | ✅ NOVO: limpar sessão | GREEN |
| `hb status` | ✅ Mostrar estado completo | GREEN |

**Validações implementadas:**

```python
# Phase 0 (verify)
1. task_type em TASK_CATALOG.yaml? else BLOCKED
   └─ status = active? else BLOCKED (frozen/disabled)
   └─ worker_path existe? else BLOCKED
2. module em 16 canônicos? else BLOCKED
3. session_start.json válido contra schema? else BLOCKED
4. Boot profile carregável? else BLOCKED

# Phase 1 (check)
1. Sessão foi inicializada (tem session_id)?
2. module corresponde entre CLI e session?
3. task_type foi validado em phase 0?

# Phase 2 (artifact)
1. Arquivo existe?
2. Calcular SHA-256
3. Upsert ou atualizar entry em stage2_artifacts
4. Salvar session_start.json com hash (para detectar stale)
```

**Fluxo Típico:**

```bash
# Phase 0: Boot + validação
hb verify --task-type new_contract --module training
# Saída:
# ✅ task_type='new_contract' (active, worker exists)
# ✅ module='training' (canonical)
# ✅ session_start.json criado com schema válido
# DONE = exitcode 0  |  atual exitcode = 0

# Phase 1: Module readiness
hb check --module training
# Saída:
# ✅ Sessão validada
# DONE = exitcode 0  |  atual exitcode = 0

# Phase 2: Per-artifact validation
hb artifact contracts/openapi/paths/training/session.yaml
# Saída:
# ✅ Novo artefato
# Artefato adicionado a stage2_artifacts com hash SHA-256: abc123def...
# DONE = exitcode 0  |  atual exitcode = 0

# Diagnosticar
hb status
# Saída:
# Session ID: 550e8400-...
# Task Type: new_contract
# Module: training
# Phase 0 (boot): ✅ PASS
# Phase 1 (discovery): ✅ PASS
# Phase 2 (artifacts): 1 artefato(s)
#   ✅ contracts/openapi/paths/training/session.yaml (hash: abc123de...)

# Limpar para nova sessão
hb reset
# ✅ session_start.json removido
# ✅ Sessão limpa
```

---

## Testes Atualizados

### Testes que viraram GREEN (eram RED em PR1):

| Teste | Antes | Depois | Delta |
|-------|-------|--------|-------|
| `test_hb_verify_without_task_type_should_fail` | 🔴 RED (passava com unknown) | 🟢 GREEN (falha com código 1) | CLI agora obriga --task-type |
| `test_hb_verify_without_module_should_fail` | 🔴 RED (passava com unknown) | 🟢 GREEN (falha com código 1) | CLI agora obriga --module |
| `test_hb_check_without_module_should_fail` | 🔴 RED (passava sem arg) | 🟢 GREEN (falha com código 1) | CLI agora obriga --module |

### Testes que permanecem GREEN:
```
✅ test_session_start_json_with_unknown_task_type_is_invalid
✅ test_session_start_json_with_unknown_module_is_invalid
✅ test_session_start_json_missing_required_fields
✅ test_task_type_not_in_catalog_should_block
✅ test_session_hash_divergence_misses_detection
✅ test_boot_profiles_yaml_is_valid
✅ test_task_catalog_yaml_is_valid
✅ test_session_start_schema_is_valid_json_schema
```

### Teste que permanece RED (esperado — PR4):
```
🔴 test_git_hook_divergence
   Razão: Hook versionado (bash) ≠ hook instalado (python)
   PR4 irá: Unificar via core.hooksPath
```

**Resultado Final:**
```
11 passed, 1 failed in 0.51s
```

---

## Integração com SSOTs

```
scripts/hb v2
   ├─ Carrega BOOT_PROFILES.yaml na inicialização
   ├─ Valida task_type contra TASK_CATALOG.yaml
   ├─ Valida session contra session_start.schema.json
   └─ Upsert stage2_artifacts com SHA-256 para detectar stale

_reports/session_start.json (agora determinístico)
   ├─ task_type: validado (não pode ser "unknown")
   ├─ module: validado (16 canônicos)
   ├─ stage: progressão explícita (0, 1, 2)
   ├─ write_scope: concreto (contracts/docs/migrations/etc)
   └─ stage2_artifacts[].sha256: detecta pós-validação stale
```

---

## Bloqueios Fechados

| Bloqueio | Status | Details |
|----------|--------|---------|
| PIPELINE_NONDETERMINISTIC (hb verify/check defaults) | ✅ FECHADO | CLI v2 obriga args |
| IMPLICIT_DEFAULTS_PHASE_0 | ✅ FECHADO | Sem `${VAR:-unknown}` |
| IMPLICIT_DEFAULTS_PHASE_1 | ✅ FECHADO | CLI não permite omissão |

---

## Próximas Ações (PR3-PR6)

| PR | Fase | Objetivo | Entregas |
|----|------|----------|----------|
| PR2 | 1-3 | ✅ COMPLETA | scripts/hb v2 com validação determinística |
| PR3 | 4 | Validator determinístico | validate_contracts.py consome GATES_REGISTRY |
| PR4 | 5 | Hook único | Instalar via core.hooksPath |
| PR5 | 6 | Limpeza legado | Remover boot_resolution_report, agent_execution/latest |
| PR6 | 7-8 | CI + regressão | Testes de paridade local↔CI, budgets |

---

## Definição de Done para PR2

- ✅ scripts/hb reescrito em Python com validações SSOT
- ✅ `hb verify --task-type --module` obrigatório
- ✅ `hb check --module` obrigatório
- ✅ `hb artifact <path>` com SHA-256 e upsert
- ✅ `hb reset` para limpeza de sessão
- ✅ `hb status` para diagnóstico
- ✅ 11/12 testes passam (3 CLI virados GREEN + 8 GREEN anteriores)
- ✅ 1 teste RED (git hook — será PR4)
- ✅ SESSION_HANDOFF.md atualizado

**PR2 está COMPLETA e pronta para PR3.**

---

## Notas Importantes

- **Sem mais defaults** — a CLI v2 não permite silenciosamente `task_type=unknown` ou `module=unknown`
- **Validação SSOT-first** — carrega SSOTs na inicialização, falha rapidamente se inválidos
- **Determinismo garantido** — mesma entrada → mesmo output sempre
- **Hash-based stale detection** — artefatos alterados pós-validação são detectados pelo hash SHA-256
- **Próximo:** PR3 vai alinhar `validate_contracts.py` com `GATES_REGISTRY.yaml`
