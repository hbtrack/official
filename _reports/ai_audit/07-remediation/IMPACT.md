# IMPACT.md — Análise de Impacto REM-1E: wellness-pre Payload Canônico

**Decisão final**: contrato + runtime devem aceitar e retornar exatamente o mesmo payload canônico
enriquecido — `sleepQuality`, `sleepHours`, `readiness`, `mood`, `fatigue`, `muscleSoreness`, `notes`
— com `additionalProperties: false` mantido.

**Data da análise**: 2026-04-23 (v1) / 2026-04-23 (v2 — auditoria profunda)  
**Branch verificada**: `patch/wellness-pre-sleep-hours`  
**Analista**: Copilot (Modo ROADMAP / verificação pré-merge)

> ⚠️ **VERSÃO 2 — AUDITORIA PROFUNDA**: Esta versão substitui a v1. Foram identificados 4 gaps
> adicionais críticos ausentes na v1, incluindo dois erros silenciosos de validação confirmados por
> teste end-to-end, uma divergência sistêmica de naming camelCase/snake_case entre contrato e runtime,
> e um gap de enforcement de campos obrigatórios. Veja seção 2B.

---

## 1. Estado verificado pós-branch

> **SNAPSHOT HISTÓRICO** — estado *antes* dos PASSOs de remediação. A coluna **Estado atual** mostra o status após PASSOs 1–10 (2026-04-23).

| Camada | Arquivo | Estado inicial (pré-PASSO) | Estado atual | Campos presentes |
|--------|---------|--------------------------|--------------|-----------------|
| Schema de resposta (contrato) | `contracts/openapi/components/schemas/training/wellness_pre.yaml` | ⚠️ **GAP** | ✅ **OK** (PASSO 5) | `id`, `trainingSessionId`, `athleteId`, `sleepQuality`, `sleepHours`, `readiness`, `mood`, `fatigue`, `muscleSoreness`, `notes`, `createdAt`, `updatedAt`, `deletedAt`, `deletedReason` |
| RequestBody POST (contrato) | `contracts/openapi/paths/training.yaml` — `submitWellnessPre` | ⚠️ **GAP** | ✅ **OK** (PASSO 6) | `athleteId` (required), `sleepQuality` (required), `sleepHours` (required), `readiness`, `mood`, `fatigue`, `muscleSoreness`, `notes` |
| RequestBody PATCH (contrato) | `contracts/openapi/paths/training.yaml` — `updateWellnessPre` | ⚠️ **GAP** | ✅ **OK** (PASSO 6) | `sleepQuality`, `sleepHours`, `readiness`, `mood`, `fatigue`, `muscleSoreness`, `notes` |
| Source master POST | `docs/hbtrack/modulos/training/graph/openapi_paths.yaml` — `submitWellnessPre` | ⚠️ **GAP** | ✅ **OK** (PASSO 7) | Idêntico ao `training.yaml` acima |
| Source master PATCH | `docs/hbtrack/modulos/training/graph/openapi_paths.yaml` — `updateWellnessPre` | ⚠️ **GAP** | ✅ **OK** (PASSO 7) | Idêntico ao `training.yaml` acima |
| Schema Pydantic (saída) | `src/training/schemas/wellness.py` — `WellnessPreOut` | ✅ OK | ✅ **OK + camelCase** (PASSO 2) | Todos os 7 campos + `id`, `session_id` (alias `trainingSessionId`), `athlete_id`, `created_at`, `updated_at` — `alias_generator=to_camel`, `by_alias=True` via CamelRouter |
| Schema Pydantic (entrada POST) | `src/training/schemas/wellness.py` — `SubmitWellnessPreIn` | ✅ OK (campos opcionais) | ✅ **OK + required** (PASSO 4) | `athlete_id` + `sleep_quality` (**required**) + `sleep_hours` (**required**) + 5 campos opcionais com `Field(ge=,le=)` |
| Schema Pydantic (entrada PATCH) | `src/training/schemas/wellness.py` — `UpdateWellnessPreIn` | ✅ OK | ✅ **OK** | Todos os 7 campos opcionais |
| Entidade de domínio | `src/training/domain/entities/wellness.py` — `WellnessPre` | ✅ OK | ✅ **OK + invariante** (PASSO 3) | Todos os 7 campos; `validate_invariants()` valida `sleep_hours ∈ [0, 24]` |
| DTO de aplicação | `src/training/application/wellness/dto.py` | ✅ OK | ✅ OK | Todos os 7 campos |
| Commands | `src/training/application/wellness/commands.py` | ✅ OK | ✅ OK | Propagação completa |
| ORM Model | `src/training/infrastructure/models/wellness.py` — `WellnessPreModel` | ✅ OK | ✅ OK | `sleep_hours = DecimalField` + demais campos |
| Repository | `src/training/infrastructure/repository/wellness.py` | ✅ OK | ✅ OK | `save()` + `_to_domain()` completos |
| Mapper | `src/training/api/mappers.py` — `_wellness_pre_to_out()` | ✅ OK | ✅ OK | Todos os 7 campos mapeados |
| Handler API | `src/training/api/wellness.py` | ✅ OK | ✅ OK | Todos os campos propagados |
| Migration | `src/training/migrations/0009_add_sleep_hours_to_wellness_pre.py` | ✅ CRIADA | ✅ **APLICADA** (PASSO 1) | `sleep_hours DecimalField(max_digits=4, decimal_places=1, null=True)` |
| DB (aplicação) | PostgreSQL — tabela `training_wellness_pre` | ❌ **NÃO APLICADA** | ✅ **APLICADA** (PASSO 1) | Coluna `sleep_hours numeric` presente — verificado via `information_schema.columns` |

---

### GAP-1 — CRÍTICO: Migration não aplicada ao banco de dados
**Causa**: `0009_add_sleep_hours_to_wellness_pre.py` foi criada mas `manage.py migrate` não foi executado.  
**Efeito**: Qualquer chamada ao endpoint `/wellness-pre` levanta `UndefinedColumn: column training_wellness_pre.sleep_hours does not exist` → HTTP 500.  
**Evidência**: `test_get_and_update_wellness_pre` falhando com exatamente esse erro.  
**Risco em produção**: Todos os endpoints de wellness-pre quebram — POST, GET e PATCH.  
**Status v2**: ✅ **RESOLVIDO** — `manage.py migrate` aplicado em 2026-04-23. Testes: 402 passed, 0 failed.  
**Ação**: ~~Executar `python3 manage.py migrate`.~~ FEITO.

---

### GAP-2 — CRÍTICO: Contract/runtime divergência no schema de resposta

**Causa**: `wellness_pre.yaml` (contrato de resposta) não declara `readiness`, `mood`, `fatigue`, `muscleSoreness`, `notes`.  

**Efeito**: Com `additionalProperties: false` no schema do contrato, qualquer cliente que valide a resposta contra o OpenAPI (Prism, SDK gerado, testes de contrato) irá rejeitar as respostas legítimas que contêm esses 5 campos. O servidor retorna campos que o contrato proíbe.  

**Risco**: Silent failure em clientes SDK gerados automaticamente; falha em testes Pact/Prism; campos silenciosamente descartados por clientes que respeitam o schema.  

**Ação**: Adicionar `readiness`, `mood`, `fatigue`, `muscleSoreness`, `notes` em `wellness_pre.yaml`.

---

### GAP-3 — CRÍTICO: `additionalProperties: false` no requestBody bloqueia 5 campos canonicamente válidos

**Causa**: `training.yaml` + `openapi_paths.yaml` definem o requestBody do POST/PATCH com `additionalProperties: false` e apenas `sleepQuality`/`sleepHours` (+ `athleteId` no POST).  

**Efeito**: Clientes que seguem o contrato (SDKs gerados, mock servers, testes de contrato) **não podem** enviar `readiness`, `mood`, `fatigue`, `muscleSoreness`, `notes` — campos que são aceitos pelo runtime. O comportamento real diverge do contrato em 5 campos por operação.  

**Risco**: Clientes SDK gerados nunca enviam esses campos → dados críticos de performance esportiva (fadiga, disposição) nunca chegam ao sistema.  

**Ação**: Adicionar os 5 campos ao requestBody de POST e PATCH em ambos os arquivos.

---

### GAP-4 — MODERADO: Teste `test_get_and_update_wellness_pre` não cobre payload completo
**Causa**: O teste existente valida apenas `sleep_quality` e `readiness` no POST, e `sleep_quality` + `notes` no PATCH. Não envia nem verifica `sleepHours`, `mood`, `fatigue`, `muscleSoreness`.  
**Efeito**: Cobertura insuficiente — a introdução de `sleep_hours` no modelo passou sem regressão de teste.  
**Ação**: Expandir o teste para cobrir todos os 7 campos canônicos no POST e PATCH, e verificar todos no GET.

---

### GAP-5 — BAIXO: Source master (`openapi_paths.yaml`) em sincronia com `training.yaml` mas ambos divergem da decisão
**Causa**: Os dois arquivos (`contracts/openapi/paths/training.yaml` e `docs/hbtrack/modulos/training/graph/openapi_paths.yaml`) estão sincronizados entre si — ambos têm os mesmos gaps.  
**Efeito**: Sem conflito de drift entre os dois, mas ambos precisam ser atualizados simultaneamente.  
**Ação**: Atualizar ambos na mesma operação.

---

### GAP-6 — INFORMATIVO: Sem conflito de migration
**Causa**: A suposição de que havia `0005_add_sleep_hours_to_wellness_pre.py` estava incorreta. A migration existente é `0009_add_sleep_hours_to_wellness_pre.py` e `0005` é `attendance_record_model.py`.  
**Efeito**: Nenhum conflito de numeração. Nenhuma deduplicação necessária.  
**Ação**: Nenhuma — ~~apenas aplicar `migrate`~~. FEITO.

---

### GAP-7 — INFORMATIVO: Pipeline CDD STATUS: PASS não detecta divergência campo-a-campo
**Causa**: O `validate_contracts.py` valida SHA256 dos manifests, coerência do handoff e presença de gates registrados — não faz diff semântico entre runtime Pydantic e OpenAPI YAML.  
**Efeito**: Pipeline passou (PASS) mesmo com os gaps 2 e 3 acima.  
**Ação**: Configurar o `validate_contracts.py` para validar SHA256 dos manifests, coerência do handoff e presença de gates registrados e diff semântico entre runtime Pydantic e OpenAPI YAML, para detectar divergências campo-a-campo.

---

## 2B. Gaps adicionais identificados na auditoria profunda (v2)

> Estes gaps são **ausentes na v1** e foram encontrados por teste end-to-end e leitura profunda de código.
> Três deles envolvem erros silenciosos confirmados por execução real.

---

### GAP-NEW-1 — 🔴 GRITANTE SILENCIOSO: Divergência sistêmica de naming camelCase (contrato) vs snake_case (runtime)

**Confirmado por execução real.**

O contrato OpenAPI usa `camelCase` (`sleepQuality`, `athleteId`, `trainingSessionId`, `createdAt`, `muscleSoreness`).  
O runtime Django Ninja **não converte** — serializa em `snake_case` puro: `sleep_quality`, `athlete_id`, `session_id`, `created_at`, `muscle_soreness`.

```
# Teste executado 2026-04-23:
GET /training-sessions/{id}/wellness-pre/{athleteId}
# Contrato diz:  trainingSessionId, athleteId, sleepQuality, sleepHours, muscleSoreness, createdAt
# Runtime retorna: session_id,      athlete_id, sleep_quality, sleep_hours, muscle_soreness, created_at
```

Agravante: `trainingSessionId` (contrato) ≠ `session_id` (runtime) — não é só case, é nome diferente.

**Impactos em cascata:**
1. Qualquer SDK gerado a partir do OpenAPI não funciona com a API real — todas as propriedades chegam com nome errado
2. Clientes que usam o SDK gerado nunca conseguem ler `sleepQuality`, `athleteId`, `createdAt` — recebem `undefined`/`null` silenciosamente
3. Testes que usam `_pick(data, snake, camel)` **mascaram** este bug — passam em ambos os formatos, escondendo a divergência
4. Prism mock server e testes de contrato rejeitam respostas com snake_case
5. O contrato é inútil como fonte de verdade para geração de código

**Causa raiz**: `NinjaAPI` foi instanciado sem `by_alias=True` e os schemas Pydantic não têm `alias_generator=to_camel` nem `model_config = ConfigDict(populate_by_name=True, alias_generator=...)`. Pydantic v2 serializa pelo nome do campo, não pelo alias.

**Ação obrigatória** (escolher uma estratégia — impacta TODA a API training):
- **Opção A (recomendada para maturidade de produto)**: Adicionar `model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)` a todos os schemas de saída; configurar NinjaAPI com `by_alias=True`; atualizar contratos para usar o naming que o runtime realmente produz.


- **Opção B (pragmática de curto prazo)**: Atualizar o contrato para usar snake_case — alinha com o que a API realmente retorna; abandona a convenção REST camelCase mas é honesto.
- **Opção C (não recomendada)**: Manter o helper `_pick()` nos testes — mascara o problema sem resolver.

**Escopo**: Afeta todos os 12 handlers do módulo training, não só wellness-pre. Bloqueante para qualquer integração com frontend/SDK.

---

### GAP-NEW-2 — 🔴 CRÍTICO SILENCIOSO: `sleep_hours` fora de [0,24] é aceito sem erro (INV-TRAIN-033 não implementado)

**Confirmado por execução real.**

O domínio `WellnessPre.validate_invariants()` valida `readiness`, `sleep_quality`, `mood`, `fatigue`, `muscle_soreness` em [1,5] — mas **não valida** `sleep_hours` em [0,24].

```
# Teste executado 2026-04-23:
POST .../wellness-pre {"sleep_quality": 3, "sleep_hours": 25.0}  → 201 ✅ (DEVERIA SER 422)
POST .../wellness-pre {"sleep_quality": 3, "sleep_hours": -1.0}  → 201 ✅ (DEVERIA SER 422)
```

O contrato declara `minimum: 0, maximum: 24` e o doc referencia `INV-TRAIN-033`. A invariante está documentada mas não implementada no código. O banco (`DecimalField(max_digits=4, decimal_places=1)`) permite até 999.9.

**Impacto**: Dados biomédicos inválidos são persistidos silenciosamente. Um atleta que registra `sleep_hours=30` ou `sleep_hours=-5` passa pela API sem erro. O índice de Hooper calculado com esses dados se torna cientificamente inválido.

**Ação**: Adicionar a validação em `WellnessPre.validate_invariants()`:
```python
if self.sleep_hours is not None and not (0 <= self.sleep_hours <= 24):
    raise ValueError("sleepHours deve estar em [0, 24]")
```
E adicionar teste que confirme 422 para sleep_hours=25 e sleep_hours=-1.

---

### GAP-NEW-3 — 🔴 CRÍTICO SILENCIOSO: `sleepQuality` e `sleepHours` são `required` no contrato mas aceitos como `null` pelo runtime

**Confirmado por execução real.**

O contrato exige `required: [athleteId, sleepQuality, sleepHours]`. O Pydantic tem `sleep_quality: Optional[int] = None` e `sleep_hours: Optional[float] = None`.

```
# Teste executado 2026-04-23:
POST .../wellness-pre {"athlete_id": "..."}  → 201 com sleep_quality=null, sleep_hours=null
```

**Impacto**: 
1. O banco aceita registros onde os dois campos mais importantes clinicamente estão `null` — torna o registro de wellness completamente inútil para análise de carga
2. Viola INV-TRAIN-034 (`sleepQuality` obrigatório) e SS-TRAIN-006 (`sleepHours` obrigatório para índice de Hooper)
3. Qualquer cálculo de índice de Hooper que dependa de `sleepQuality` e `sleepHours` quebra silenciosamente com divisão por null ou NaN

**Ação**: Tornar obrigatório no Pydantic para o schema de entrada POST:
```python
class SubmitWellnessPreIn(Schema):
    athlete_id: uuid.UUID
    sleep_quality: int = Field(..., ge=1, le=5)   # required
    sleep_hours: float = Field(..., ge=0, le=24)  # required
    readiness: Optional[int] = Field(None, ge=1, le=5)
    mood: Optional[int] = Field(None, ge=1, le=5)
    fatigue: Optional[int] = Field(None, ge=1, le=5)
    muscle_soreness: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None
```
Usar `Field(ge=, le=)` também resolve o GAP-NEW-2 para os campos inteiros — os ranges passam a ser validados pelo Pydantic antes de chegar ao domínio.

---

### GAP-NEW-4 — ✅ RESOLVIDO: PATCH tri-state — ausente / valor / null explícito

**Confirmado por execução real e corrigido em 2026-04-24.**

O problema original: `UpdateWellnessPreUseCase` usava `if value is not None: setattr(...)` — tornando impossível limpar um campo já preenchido via PATCH, porque `null` e "campo ausente" resultavam no mesmo `None` no DTO.

**Solução implementada (tri-state via `model_fields_set`):**

```
                        campo AUSENTE    campo com VALOR    campo com NULL
UpdateWellnessPreUseCase  → não altera      → altera          → limpa
```

Implementação em 4 camadas:

1. **`UpdateWellnessPreInput` (DTO)** — campo `provided_fields: frozenset` carrega os nomes dos campos explicitamente presentes no JSON:
   ```python
   provided_fields: frozenset = field(default_factory=frozenset)
   ```

2. **Handler (`api/wellness.py`)** — passa `provided_fields=frozenset(body.model_fields_set)`. Pydantic v2 `model_fields_set` retorna nomes Python (snake_case); campos ausentes não entram no set.

3. **Use case (`commands.py`)** — substituição do `if value is not None` pelo loop com presença:
   ```python
   _PATCHABLE = frozenset({"readiness", "sleep_quality", "sleep_hours", "mood", "fatigue", "muscle_soreness", "notes"})
   for field_name in _PATCHABLE:
       if field_name in inp.provided_fields:
           value = getattr(inp, field_name)
           if field_name == "notes" and value is None:
               value = ""   # ORM notes não tem null=True — null → "" (limpar)
           setattr(wellness, field_name, value)
   ```

4. **Contrato OpenAPI PATCH** — campos atualizados para `type: [integer/number/string, "null"]` (OAS 3.1), permitindo null explícito sem quebrar validação do contrato.

**Detalhe de `notes`:** o campo ORM tem `TextField(blank=True, default="")` sem `null=True`. Null explícito é traduzido para `""` (string vazia) na camada de use case, evitando uma migration desnecessária. Esta decisão é documentada explicitamente — "limpar notes" = gravar `""`.

**Detalhe de `sleep_quality`/`sleep_hours`:** são required no POST mas clearable no PATCH. Tecnicamente válido em todas as camadas (domínio `Optional`, ORM `null=True`, `validate_invariants()` com guards `if not None`). A assimetria é intencional — a criação exige valores, a correção permite limpeza.

**Testes (3 cenários):**
```
# test_wellness_pre_patch_null_field — 3 cenários:
# 1. campo ausente  → não altera                     ✅ PASSA
# 2. campo com valor → altera                         ✅ PASSA
# 3. campo com null  → limpa (notes="", mood=None)   ✅ PASSA
```

**Arquivos alterados:** `dto.py`, `commands.py`, `api/wellness.py`, `contracts/openapi/paths/training.yaml`, `test_training_api.py` (`test_wellness_pre_patch_null_field` expandido).

---

## 3. Cadeia de impacto da decisão final

> **Nota**: Esta seção descreve o estado **pré-implementação** (antes dos PASSOs 1-10). As anotações `[GAP-*]` indicam o que estava quebrado. O estado atual pós-implementação está na Seção 10.

```
Decisão canônica (7 campos)
        │
        ├── wellness_pre.yaml (resposta)        ← ✅ RESOLVIDO [GAP-2] — 14 campos incluindo 5 novos
        │                                         ✅ RESOLVIDO [GAP-NEW-1] — alias_generator=to_camel
        ├── training.yaml requestBody POST       ← ✅ RESOLVIDO [GAP-3] — 7 campos + required correto
        │                                         ✅ RESOLVIDO [GAP-NEW-3] — sleepQuality/sleepHours required
        ├── training.yaml requestBody PATCH      ← ✅ RESOLVIDO [GAP-3] — 7 campos opcionais
        ├── openapi_paths.yaml requestBody POST  ← ✅ RESOLVIDO [GAP-5] — espelhado
        ├── openapi_paths.yaml requestBody PATCH ← ✅ RESOLVIDO [GAP-5] — espelhado
        │
        ├── WellnessPreOut (Pydantic)            ← ✅ alias_generator=to_camel + Field(alias="trainingSessionId")
        ├── SubmitWellnessPreIn (Pydantic)       ← ✅ sleep_quality/sleep_hours required Field(...)
        │                                         ✅ Field(ge=,le=) para todos os ranges
        ├── UpdateWellnessPreIn (Pydantic)       ← ✅ Field(ge=,le=) para todos os ranges
        ├── WellnessPre.validate_invariants()    ← ✅ RESOLVIDO [GAP-NEW-2] — sleep_hours in [0,24]
        ├── WellnessPre (entidade domínio)       ← ✅ todos os campos presentes
        ├── UpdateWellnessPreUseCase             ← ✅ RESOLVIDO [GAP-NEW-4] — tri-state PATCH (provided_fields)
        ├── WellnessPreModel.Meta                ← ✅ RESOLVIDO [R8] — UniqueConstraint parcial (migration 0010)
        ├── WellnessPreModel (ORM)               ← ✅ todos os campos presentes
        ├── WellnessPreRepository (save + _to_domain) ← ✅ correto
        ├── _wellness_pre_to_out (mapper)        ← ✅ correto
        ├── wellness.py handlers (API)           ← ✅ CamelRouter + by_alias=True
        │
        ├── Migration 0009                       ← ✅ APLICADA — sleep_hours
        └── Migration 0010                       ← ✅ APLICADA — UniqueConstraint INV-TRAIN-009
```

**Módulo soberano `wellness`** (distinto de `training/wellness-pre`): Não foi tocado. Nenhuma ação necessária.

---

## 4. Atualizações necessárias

### 4.1 Contratos (CDD — authoring obrigatório antes de merge)

| Arquivo | Operação | Campos a adicionar |
|---------|----------|--------------------|
| `contracts/openapi/components/schemas/training/wellness_pre.yaml` | Adicionar propriedades ao schema de resposta | `readiness`, `mood`, `fatigue`, `muscleSoreness`, `notes` (+ decidir naming: manter camelCase alinhando contrato **OU** mudar para snake_case alinhando runtime — ver GAP-NEW-1) |
| `contracts/openapi/paths/training.yaml` — POST `/wellness-pre` | Adicionar campos ao requestBody; tornar `sleepQuality`/`sleepHours` required | 5 campos opcionais + revisão da seção `required` |
| `contracts/openapi/paths/training.yaml` — PATCH `/wellness-pre/{athleteId}` | Adicionar campos ao requestBody | 5 campos opcionais |
| `docs/hbtrack/modulos/training/graph/openapi_paths.yaml` — POST + PATCH | Espelhar mudança | Mesmos campos |

Após editar contratos: re-registrar com `python3 scripts/hb artifact <path>` e re-executar `validate_contracts.py`.

### 4.2 Banco de dados

```bash
# ✅ FEITO em 2026-04-23:
python3 manage.py migrate  # aplicou 0008 + 0009

# PENDENTE — migration para constraint de unicidade (GAP INF-TRAIN-009 race):
# (criação de nova migration — opcional por enquanto, mas obrigatória antes de produção)
```

### 4.3 Runtime — correções obrigatórias (novas)

| Arquivo | Correção |
|---------|----------|
| `src/training/domain/entities/wellness.py` — `validate_invariants()` | Adicionar range check `sleep_hours in [0, 24]` [GAP-NEW-2] |
| `src/training/schemas/wellness.py` — `SubmitWellnessPreIn` | Tornar `sleep_quality` e `sleep_hours` não-Optional (`Field(...)`) [GAP-NEW-3]; adicionar `ge`/`le` para todos os campos com range |
| `src/training/schemas/wellness.py` — naming | Decidir naming: adicionar `alias_generator=to_camel` [GAP-NEW-1] **OU** aceitar snake_case e corrigir contrato |

### 4.4 Testes (novos / modificados)

| Teste | Tipo | Ação |
|-------|------|------|
| `test_get_and_update_wellness_pre` | Integração | **Expandir**: POST com todos os 7 campos, GET verificando todos, PATCH verificando todos |
| `test_wellness_pre_sleep_hours_range` | Integração | **Criar**: verifica 422 para `sleep_hours=25` e `sleep_hours=-1` [GAP-NEW-2] |
| `test_wellness_pre_required_fields` | Integração | **Criar**: verifica 422 para POST sem `sleep_quality` ou sem `sleep_hours` [GAP-NEW-3] |
| `test_wellness_pre_patch_null_field` | Integração | **Criar**: documenta comportamento atual de PATCH com null [GAP-NEW-4] |

### 4.5 Configuração de gates / enforcement

Nenhum novo gate é necessário. O mecanismo de enforcement existe em dois níveis:
1. **Pydantic** — `SubmitWellnessPreIn` e `UpdateWellnessPreIn` definem allowlist explícita; campos extras rejeitados com 422.
2. **Contrato** — `additionalProperties: false` alinha o comportamento documentado com runtime.

**Recomendação futura**: `WELLNESS_CONTRACT_RUNTIME_PARITY_GATE` — diff automático entre campos Pydantic e schema YAML.

---

## 5. Riscos de erro silencioso

| # | Risco | Confirmado? | Impacto | Mitigação |
|---|-------|-------------|---------|-----------|
| R1 | **Dados biomédicos inválidos persistidos**: `sleep_hours=-1` ou `sleep_hours=25` aceitos | ✅ CONFIRMADO por teste | Índice de Hooper corrompido; dados de atleta sem sentido clínico | Adicionar range check em `validate_invariants()` + `Field(ge=0, le=24)` |
| R2 | **Registro sem dados obrigatórios**: POST sem `sleep_quality`/`sleep_hours` retorna 201 | ✅ CONFIRMADO por teste | Registros de wellness clinicamente vazios; cálculo de Hooper quebra silenciosamente | Tornar campos não-Optional no schema Pydantic |
| R3 | **SDK gerado usa camelCase, API retorna snake_case**: divergência total de naming | ✅ CONFIRMADO por teste | 100% das integrações com frontend/mobile via SDK falham silenciosamente — campos chegam como `undefined` | Decisão estratégica: adotar alias_generator **OU** padronizar contratos em snake_case |
| R4 | **`_pick(snake, camel)` mascara naming mismatch nos testes**: testes passam com qualquer naming | ✅ CONFIRMADO por leitura de código | Falso positivo nos testes — system broken em produção, testes verdes | Reescrever testes para usar apenas o naming que a API realmente usa |
| R5 | **PATCH com `null` ignorado silenciosamente**: campos não podem ser zerados | ✅ CONFIRMADO por teste | Dados incorretos não podem ser corrigidos; sem erro de retorno, cliente não sabe que ignorou | Documentar e testar explicitamente; ou implementar null-aware PATCH |
| R6 | **SDK gerado não envia campos opcionais**: contrato não declara `readiness`, `mood` etc. | ⚠️ Implícito | Atletas não conseguem enviar dados de fadiga/disposição mesmo que API aceite | Atualizar requestBody no contrato |
| R7 | **UndefinedColumn em produção**: deploy sem migrate | ✅ Ocorreu em dev | HTTP 500 em 100% das operações de wellness-pre | ~~Aplicar migrate ANTES do deploy.~~ FEITO em dev. |
| R8 | **Race condition em INV-TRAIN-009**: dois POST simultâneos criam registros duplicados | ⚠️ Implícito (sem UniqueConstraint) | Duplicidade de dados de atleta em mesma sessão; cálculo de índice usa o registro errado | Adicionar `UniqueConstraint` na `WellnessPreModel.Meta` |

---

## 6. Sequência de resolução determinística (atualizada v2)

---

### PASSO 1 — Aplicar migration `0009_add_sleep_hours_to_wellness_pre` [GAP-1]

**Descrição:**
`0009_add_sleep_hours_to_wellness_pre.py` foi criada mas `manage.py migrate` nunca foi executado. A coluna `sleep_hours` estava ausente da tabela `training_wellness_pre`, causando HTTP 500 em 100% das operações de wellness-pre.

**Arquivo-alvo:** `src/training/migrations/0009_add_sleep_hours_to_wellness_pre.py` — não editar, apenas aplicar.

**Correção:**
```bash
cd /home/davis/HB-TRACK && .venv/bin/python3 manage.py migrate
```

**Como validar:**
```bash
DJANGO_SETTINGS_MODULE=config.settings .venv/bin/python3 -m pytest src/training/tests/ -q
# Deve passar — sem UndefinedColumn
```

**Critérios de done:**
- [x] Coluna `sleep_hours DecimalField(max_digits=4, decimal_places=1, null=True)` existe na tabela `training_wellness_pre`
- [x] HTTP 500 eliminado — `POST /wellness-pre` retorna 201 sem `UndefinedColumn`
- [x] `pytest src/training/tests/ -q` → 0 failed

> **EVIDÊNCIA (2026-04-23):** Comando: `.venv/bin/python3 manage.py migrate` (< 3s). Output: `Applying training.0008_... OK` / `Applying training.0009_add_sleep_hours_to_wellness_pre OK`. Antes da migration: `POST /wellness-pre` → HTTP 500, `UndefinedColumn: column training_wellness_pre.sleep_hours does not exist`, teste `test_get_and_update_wellness_pre` falhando. Após a migration: HTTP 201, coluna persistida. Validação: `DJANGO_SETTINGS_MODULE=config.settings .venv/bin/python3 -m pytest src/training/tests/ -q` → `402 passed, 19 skipped, 109 warnings`. Zero regressões.

---

### PASSO 2 — Alinhar naming camelCase runtime ↔ contrato [GAP-NEW-1]

**Descrição:**
O contrato OpenAPI usa camelCase (`sleepQuality`, `athleteId`, `trainingSessionId`) mas o runtime retornava snake_case puro (`sleep_quality`, `athlete_id`, `session_id`). Qualquer SDK gerado funcionaria com nomes errados. Decisão: adotar camelCase no runtime via `alias_generator=to_camel` + `CamelRouter`.

Detalhe crítico: `to_camel("session_id") = "sessionId"` mas o contrato usa `trainingSessionId`. Solução: `Field(alias="trainingSessionId")` explícito em `WellnessPreOut.session_id` e `WellnessPostOut.session_id` — tem precedência sobre o `alias_generator`.

**Escopo:** 8 schemas + 12 sub-roteadores + 1 arquivo de testes. 53 endpoints afetados. Nenhum teste quebrou — `populate_by_name=True` mantém compatibilidade com snake_case na entrada.

**Arquivos modificados:**

| Arquivo | Alteração |
|---|---|
| `src/training/api/deps.py` | `CamelRouter(Router)` — override de get/post/patch/put/delete injetando `by_alias=True` |
| `src/training/schemas/wellness.py` | `model_config = _CAMEL` em todas as 6 classes; `Field(alias="trainingSessionId")` em `WellnessPreOut.session_id` e `WellnessPostOut.session_id` |
| `src/training/schemas/sessions.py` | `model_config = _CAMEL` em todas as 6 classes |
| `src/training/schemas/planning.py` | `model_config = _CAMEL` em todas as 6 classes |
| `src/training/schemas/execution.py` | `model_config = _CAMEL` em todas as 8 classes |
| `src/training/schemas/attendance.py` | `model_config = _CAMEL` em todas as 3 classes |
| `src/training/schemas/blocks.py` | `model_config = _CAMEL` em todas as 5 classes |
| `src/training/schemas/eligibility.py` | `model_config = _CAMEL` em todas as 2 classes |
| `src/training/schemas/communication.py` | `model_config = _CAMEL` em todas as 12 classes |
| `src/training/api/*.py` (12 arquivos) | `from .deps import CamelRouter` + `router = CamelRouter()` |
| `src/training/tests/integration/test_training_api.py` | Adicionado `test_wellness_pre_response_keys_are_camelcase` |

**Código adicionado:**
```python
# src/training/api/deps.py
class CamelRouter(Router):
    def get(self, path, **kwargs):
        kwargs.setdefault("by_alias", True)
        return super().get(path, **kwargs)
    # ... mesmo padrão para post, patch, put, delete

# src/training/schemas/*.py — padrão aplicado a todos os arquivos
_CAMEL = ConfigDict(alias_generator=to_camel, populate_by_name=True)

class WellnessPreOut(Schema):
    model_config = _CAMEL
    session_id: uuid.UUID = Field(alias="trainingSessionId")  # alias explícito
    ...
```

**Análise de impacto pré-implementação:**
- `_pick(data, snake, camel)` nos testes: NÃO QUEBRAM — camelCase agora funciona como primeiro argumento ✅
- Bodies de teste com snake_case (`{"sleep_quality": 3}`): NÃO QUEBRAM — `populate_by_name=True` ✅
- Campos sem underscore (`id`, `items`): NÃO MUDAM ✅
- `ProblemOut`/`ErrorOut`: SEGUROS — `to_camel("traceId") = "traceId"`, `to_camel("type") = "type"` ✅

**Gaps identificados que surgem após este passo:**

| ID | Descrição | Passo responsável |
|----|-----------|-------------------|
| P2-GAP-1 | Outros schemas (execution, blocks) podem ter `trainingSessionId` — verificar | PASSO 5/6/7 |
| P2-GAP-2 | Manifests em `generated/` precisam ser re-hashados após mudança OpenAPI | PASSO 9 |
| P2-GAP-3 | `_pick()` fica obsoleto — remover para evitar falsos positivos | PASSO 8 |

**Critérios de done:**
- [x] `WellnessPreOut.model_dump(by_alias=True)` retorna `trainingSessionId`, `sleepQuality`, `muscleSoreness`, `athleteId`, `createdAt`
- [x] `WellnessPreOut.model_dump(by_alias=True)` **não** retorna `session_id`, `sleep_quality`, `muscle_soreness`
- [x] Todos os 12 sub-roteadores usam `CamelRouter`
- [x] `pytest src/training/tests/ -q` → 0 failed

> **EVIDÊNCIA (2026-04-24):** Teste: `TestWellnessEndpoints::test_wellness_pre_response_keys_are_camelcase`. O que foi testado: `POST /training-sessions/{id}/wellness-pre` + `GET` da resposta — verificação de presença/ausência de chaves. Comando: `DJANGO_SETTINGS_MODULE=config.settings .venv/bin/python3 -m pytest src/training/tests/integration/test_training_api.py::TestWellnessEndpoints -v --tb=short` (2.38s). Resultado: `4 passed`. Chaves presentes confirmadas: `trainingSessionId=True`, `sleepQuality=True`, `muscleSoreness=True`, `athleteId=True`, `createdAt=True`. Chaves snake_case confirmadas ausentes: `session_id=False`, `sleep_quality=False`, `muscle_soreness=False`. Suite completo: `DJANGO_SETTINGS_MODULE=config.settings .venv/bin/python3 -m pytest src/training/tests/ -q` → `403 passed, 19 skipped, 109 warnings in 2.85s`. Zero regressões.

---

### PASSO 3 — Implementar INV-TRAIN-033: validação de `sleep_hours` em [0, 24] [GAP-NEW-2]

**Descrição:**
`WellnessPre.validate_invariants()` validava 5 campos inteiros em [1..5] mas ignorava `sleep_hours`. Valores biomédicos inválidos como `sleep_hours=25` ou `sleep_hours=-1` eram aceitos com HTTP 201 e persistidos silenciosamente no banco, corrompendo o índice de Hooper.

**Fluxo de execução verificado:**
```text
POST /wellness-pre → SubmitWellnessPreIn (Pydantic) → SubmitWellnessPreUseCase.execute()
  → WellnessPre(...)
  → wellness.validate_invariants()  ← NOVA VALIDAÇÃO ENTRA AQUI
  → sleep_hours inválido → ValueError("sleepHours deve estar em [0, 24]")
  → @map_exceptions → HttpError(422, ...)
  → HTTP 422 Unprocessable Entity
```

**Arquivo modificado:** `src/training/domain/entities/wellness.py` — `WellnessPre.validate_invariants()`

**Código adicionado:**
```python
# INV-TRAIN-033: sleepHours deve estar no intervalo fisiológico [0, 24]
if self.sleep_hours is not None and not (0 <= self.sleep_hours <= 24):
    raise ValueError("sleepHours deve estar em [0, 24]")
```

**Análise de impacto pré-implementação:**

| Teste existente | sleep_hours enviado | Impacto |
|-----------------|--------------------|----|
| `test_get_and_update_wellness_pre` | `None` (ausente) | **NENHUM** — `if val is not None` protege |
| `test_wellness_pre_response_keys_are_camelcase` | `None` (ausente) | **NENHUM** |
| Todos os outros 400+ testes | N/A | **NENHUM** — mudança é aditiva |

**Nota P3-GAP-2 (defense in depth):** Após PASSO 4, o schema Pydantic também validará com `Field(ge=0, le=24)`. As duas camadas devem coexistir: Pydantic filtra na entrada HTTP; domínio garante a invariante mesmo quando use cases são chamados diretamente.

**Critérios de done:**
- [x] `WellnessPre.validate_invariants()` lança `ValueError("sleepHours deve estar em [0, 24]")` para qualquer valor fora de [0, 24]
- [x] `sleep_hours=None` não lança exceção — campo continua opcional
- [x] Boundaries válidos (0.0, 12.5, 24.0) → HTTP 201
- [x] Boundaries inválidos (25.0, -1.0, 24.1, -0.1) → HTTP 422
- [x] PATCH com `sleep_hours=25.0` → HTTP 422 (P3-GAP-3: `update_wellness_pre` também valida)
- [x] `pytest src/training/tests/ -q` → 0 failed

> **EVIDÊNCIA (2026-04-24):** Testes: `TestWellnessEndpoints::test_wellness_pre_sleep_hours_range` (integração) + teste de domínio puro via script Python. O que foi testado: (a) domínio — 8 boundary values direto em `WellnessPre.validate_invariants()`; (b) integração — `POST` e `PATCH` via Django test client com cada boundary. Comando de integração: `DJANGO_SETTINGS_MODULE=config.settings .venv/bin/python3 -m pytest src/training/tests/integration/test_training_api.py::TestWellnessEndpoints::test_wellness_pre_sleep_hours_range -v -s --tb=long` (2.38s) → `PASSED`. Boundaries inválidos (422): `sleep_hours=25.0` — log `WARNING django.request: Unprocessable Entity: /api/training/training-sessions/{id}/wellness-pre`; `sleep_hours=-1.0` → 422; `sleep_hours=24.1` → 422; `sleep_hours=-0.1` → 422. Boundaries válidos (201): `sleep_hours=0.0` → 201; `sleep_hours=12.5` → 201; `sleep_hours=24.0` → 201. PATCH com `sleep_hours=25.0` → 422. Suite completo: `DJANGO_SETTINGS_MODULE=config.settings .venv/bin/python3 -m pytest src/training/tests/ -q --tb=short` (2.02s) → `404 passed, 19 skipped, 109 warnings`. Zero regressões.

---

### PASSO 4 — Tornar `sleepQuality` e `sleepHours` obrigatórios no schema Pydantic [GAP-NEW-3]

**Descrição:**
O contrato exige `required: [athleteId, sleepQuality, sleepHours]`, mas `SubmitWellnessPreIn` tem `sleep_quality: Optional[int] = None` e `sleep_hours: Optional[float] = None`. POST sem esses campos retorna 201 com valores null — viola INV-TRAIN-034 e SS-TRAIN-006 e torna o cálculo do índice de Hooper impossível.

**Arquivo-alvo:** `src/training/schemas/wellness.py` — `SubmitWellnessPreIn`

**Correção:**
```python
class SubmitWellnessPreIn(Schema):
    model_config = _CAMEL
    athlete_id: uuid.UUID
    sleep_quality: int = Field(..., ge=1, le=5)    # required — INV-TRAIN-034
    sleep_hours: float = Field(..., ge=0, le=24)   # required — SS-TRAIN-006
    readiness: Optional[int] = Field(None, ge=1, le=5)
    mood: Optional[int] = Field(None, ge=1, le=5)
    fatigue: Optional[int] = Field(None, ge=1, le=5)
    muscle_soreness: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None
```

**✅ Impacto nos testes existentes — RESOLVIDO:** `test_get_and_update_wellness_pre` e `test_wellness_pre_response_keys_are_camelcase` enviavam POST sem `sleep_hours`. Ambos foram atualizados com `"sleep_hours": 7.5`. Asserção de `detail` em `test_wellness_pre_sleep_hours_range` foi robustificada para suportar o formato lista do Pydantic/Ninja. Zero regressões confirmadas — 406 passed após a implementação.

**Análise de impacto (pré-implementação):**

| Teste | Linha | Tipo de quebra | Causa raiz | Ação necessária |
|---|---|---|---|---|
| `test_get_and_update_wellness_pre` | 123 | POST retorna 422 (era 201) | Body sem `sleep_hours` | Adicionar `"sleep_hours": 7.5` ao POST |
| `test_wellness_pre_response_keys_are_camelcase` | 153 | POST retorna 422 (era 201) | Body sem `sleep_hours` | Adicionar `"sleep_hours": 7.5` ao POST |
| `test_wellness_pre_sleep_hours_range` | 188–209 | `assert "sleepHours" in detail` falha | Pydantic rejeita antes do domínio; `detail` vira lista, não string | Converter `detail` para string antes de checar |

**Gaps descobertos durante análise — RESOLVIDOS no PASSO 4:**
- **P4-GAP-1** ✅ **RESOLVIDO**: `UpdateWellnessPreIn` agora tem `Field(None, ge=1, le=5)` em todos os campos inteiros opcionais e `Field(None, ge=0, le=24)` em `sleep_hours` — defense-in-depth presente no PATCH. Verificado em `src/training/schemas/wellness.py`.
- **P4-GAP-2** ✅ **RESOLVIDO**: Após PASSO 4, a validação Pydantic (`ge/le`) dispara ANTES de `validate_invariants()`. A asserção de detail em `test_wellness_pre_sleep_hours_range` foi robustificada: `detail_text = str(resp.json().get("detail", ""))` (linha 202) — suporta tanto formato lista (Ninja/Pydantic) quanto string (HttpError do domínio).

**Novos testes a criar junto com PASSO 4:**
- `test_wellness_pre_required_fields`: POST sem `sleep_quality` → 422; POST sem `sleep_hours` → 422; POST com `sleep_quality=0` → 422; POST com `sleep_quality=6` → 422
- `test_wellness_pre_patch_null_field`: documenta GAP-NEW-4 — PATCH com `null` em campo opcional não zera o valor

**Como validar:**
```bash
DJANGO_SETTINGS_MODULE=config.settings .venv/bin/python3 -m pytest src/training/tests/ -q
# Após atualizar os corpos de teste: 0 failed
```

**Critérios de done:**
- [x] `POST /wellness-pre` sem `sleepQuality` → HTTP 422
- [x] `POST /wellness-pre` sem `sleepHours` → HTTP 422
- [x] `POST /wellness-pre` com `sleepQuality=0` (abaixo de ge=1) → HTTP 422
- [x] `POST /wellness-pre` com `sleepHours=25` (acima de le=24) → HTTP 422 (dupla proteção com domínio)
- [x] `pytest src/training/tests/ -q` → 0 failed (após atualizar corpos dos testes)

> **EVIDÊNCIA (2026-04-24):** Testes: `TestWellnessEndpoints::test_wellness_pre_required_fields` (novo, 4 asserções) + `TestWellnessEndpoints::test_wellness_pre_patch_null_field` (novo, GAP-NEW-4) + testes anteriores corrigidos (`test_get_and_update_wellness_pre`, `test_wellness_pre_response_keys_are_camelcase` — adicionado `sleep_hours: 7.5` aos corpos POST) + asserção de detalhe em `test_wellness_pre_sleep_hours_range` corrigida para `str(detail).lower()` (suporta list Pydantic e string HttpError). O que foi testado: (a) POST sem `sleep_quality` → 422; (b) POST sem `sleep_hours` → 422; (c) POST com `sleep_quality=0` → 422; (d) POST com `sleep_quality=6` → 422; (e) 2 testes existentes corrigidos — não quebram mais. Arquivos alterados: `src/training/schemas/wellness.py` (`SubmitWellnessPreIn` campos `sleep_quality`/`sleep_hours` tornados `required` com `Field(..., ge=..., le=...)` + todos opcionais inteiros com `Field(None, ge=1, le=5)`; `UpdateWellnessPreIn` todos opcionais com `Field(None, ge=...)` — P4-GAP-1). Comando: `DJANGO_SETTINGS_MODULE=config.settings .venv/bin/python3 -m pytest src/training/tests/ -q --tb=short` (2.06s) → `406 passed, 19 skipped, 109 warnings`. Anteriormente: 404 passed. Delta: +2 novos testes confirmados passando. Zero regressões.

---

### PASSO 5 — Adicionar 5 campos canônicos ao schema de resposta [GAP-2]

**Arquivo-alvo:** `contracts/openapi/components/schemas/training/wellness_pre.yaml`

**Correção:** Adicionar `readiness`, `mood`, `fatigue`, `muscleSoreness`, `notes` às `properties` com tipos e constraints corretos. Naming: camelCase (alinhado com decisão do PASSO 2).

**Como validar:**
```bash
python3 scripts/hb artifact contracts/openapi/components/schemas/training/wellness_pre.yaml
python3 scripts/contracts/validate/validate_contracts.py
```

**Análise de impacto (pré-implementação):**

| Componente | Impacto | Ação necessária |
|---|---|---|
| Testes de integração existentes | **NENHUM** — mudança puramente aditiva; campos opcionais já retornados pelo runtime | Nenhuma |
| `generated/contracts/…/wellness_pre.yaml` | Deve espelhar o canonical (mesmo conteúdo) | Copiar manualmente após edição |
| Hashes em 17 manifests `*.traceability.yaml` | SHA-256 diverge após edição → `BLOCKED_TRACEABILITY_HASH_MISMATCH` em todos | Recalcular hash e atualizar todos os 17 manifests |
| `validate_contracts.py` | Falha em `DERIVED_DRIFT_GATE` até hashes atualizados | Executar após atualizar manifests |
| `additionalProperties: false` | Não bloqueia — campos adicionados serão declarados | Nenhuma |

**Campos a adicionar (derivados de `WellnessPreOut`):**
- `readiness`: `type: [integer, "null"]`, `minimum: 1`, `maximum: 5` — Hooper Index
- `mood`: `type: [integer, "null"]`, `minimum: 1`, `maximum: 5` — Hooper Index
- `fatigue`: `type: [integer, "null"]`, `minimum: 1`, `maximum: 5` — Hooper Index
- `muscleSoreness`: `type: [integer, "null"]`, `minimum: 1`, `maximum: 5` — Hooper Index (camelCase)
- `notes`: `type: [string, "null"]` — texto livre, opcional

**P5-GAP-1:** `validate_contracts.py` não atualiza hashes automaticamente — o `hb artifact` registra o arquivo na sessão mas os manifests de traceabilidade devem ser atualizados via script separado.

**Critérios de done:**
- [x] `wellness_pre.yaml` declara todos os 7 campos canônicos
- [x] `hb artifact` registrado sem erro — `STATUS: PASS`, `exit_code=0`. Gates passando: `AXIOM_INTEGRITY_GATE`, `PATH_CANONICALITY_GATE`, `PLACEHOLDER_RESIDUE_GATE`, `OPENAPI_ROOT_STRUCTURE_GATE`, `JSON_SCHEMA_VALIDATION_GATE`, `UI_DOC_VALIDATION_GATE`, `CROSS_MODULE_BOUNDARY_GATE`, `READINESS_SUMMARY_GATE`. Pré-requisito: SESSION_HANDOFF.md atualizado para `modo_operacao: CDD` + `task_type: contract_revision` + `boot_profile_id: contract_execution` (alinhado com o PASSO 5 que é tarefa CDD).
- [x] `validate_contracts.py` → `STATUS: PASS` — todos os gates passando: `DERIVED_DRIFT_GATE: PASS`, `HANDOFF_COHERENCE_GATE: PASS`, `MODULE_STATUS_COHERENCE_GATE: PASS`, `READINESS_SUMMARY_GATE: PASS`.

> **EVIDÊNCIA (2026-04-23):**
> 1. **Edição do contrato**: `contracts/openapi/components/schemas/training/wellness_pre.yaml` — 5 campos adicionados: `readiness`, `mood`, `fatigue`, `muscleSoreness`, `notes` (todos `type: [integer/"null"]` ou `[string/"null"]`, opcionais, não adicionados a `required`). Alinhado com `WellnessPreOut` Python schema.
> 2. **Hash sync**: SHA-256 novo `025bf1bf95aef4c4432f5863f50c54a98f6efd227c8b31acce36f538dc184b1c` (antigo: `948d23fd...`). Copiado para `generated/contracts/.../wellness_pre.yaml`. 34 hashes de entrada + 34 tree-hashes atualizados em 17 manifests `*.traceability.yaml`.
> 3. **SESSION_HANDOFF.md** atualizado para `modo_operacao: CDD` / `task_type: contract_revision` / `boot_profile_id: contract_execution` — alinhado com o trabalho CDD em andamento.
> 4. **`hb verify` → `STATUS: PASS`, `exit_code=0`** — `HANDOFF_COHERENCE_GATE: PASS` após alinhamento do SESSION_HANDOFF.md.
> 5. **`hb artifact contracts/openapi/components/schemas/training/wellness_pre.yaml` → `STATUS: PASS`, `exit_code=0`** — artefato registrado na sessão CDD.
> 6. **`validate_contracts.py` → `STATUS: PASS`** — `DERIVED_DRIFT_GATE: PASS`, `HANDOFF_COHERENCE_GATE: PASS`. Confirmado via `timeout 90 .venv/bin/python3 scripts/contracts/validate/validate_contracts.py`.
> 7. **`pytest`: `406 passed, 19 skipped, 109 warnings in 2.72s`** — zero regressões. Comando: `DJANGO_SETTINGS_MODULE=config.settings .venv/bin/python3 -m pytest src/training/tests/ -q`.

---

### PASSO 6 — Adicionar 5 campos ao requestBody POST e PATCH [GAP-3]

**Arquivo-alvo:** `contracts/openapi/paths/training.yaml` — operações `submitWellnessPre` e `updateWellnessPre`

**Correção:** POST requestBody: adicionar `readiness`, `mood`, `fatigue`, `muscleSoreness`, `notes` como opcionais; `sleepQuality` e `sleepHours` já estão na seção `required`. PATCH requestBody: mesmos 5 campos opcionais.

**Análise de impacto (pré-implementação):**

| Componente | Impacto | Ação necessária |
|---|---|---|
| Testes de integração existentes | **NENHUM** — mudança aditiva; campos opcionais não afetam testes que não os enviam | Nenhuma |
| `generated/contracts/openapi/paths/training.yaml` | SHA-256 diverge → `DERIVED_DRIFT_GATE: FAIL` | Copiar para `generated/` após edição |
| Hashes em 17 manifests `*.traceability.yaml` | `contracts/openapi/paths/training.yaml` aparece em todos os 17 manifests (2x por manifest = 34 entradas + 34 tree-hashes) | Recalcular e atualizar após edição |
| `docs/hbtrack/modulos/training/graph/openapi_paths.yaml` | Arquivo espelho — **não** rastreado pelos manifests de traceabilidade (ausente em todos os 17) | Editar de forma idêntica ao training.yaml; não gera impacto em manifests |
| `validate_contracts.py` | DERIVED_DRIFT_GATE falha até hashes sincronizados | Executar após sync |
| `additionalProperties: false` | POST e PATCH já têm `additionalProperties: false` — os novos campos precisam ser declarados para não serem rejeitados por clientes que respeitam o schema | Nenhuma ação extra — declarar campos resolve |
| Seção `required` do POST | `sleepQuality` e `sleepHours` já estão em `required` — não mudam | Nenhuma |
| Seção `required` do PATCH | PATCH não tem seção `required` — todos os campos são opcionais por design | Nenhuma |

**Hashes baseline (antes da edição):**
- `contracts/openapi/paths/training.yaml`: `b9ba2e5c36f4c99e2ace79e9e12326c92d3958ae4ddd22f40a22ae96ecb64d54`
- `generated/contracts/openapi/paths/training.yaml`: idêntico ao canonical (confirmado por diff)
- `docs/hbtrack/modulos/training/graph/openapi_paths.yaml`: `ef295adfede88f03639ce866edef40d32e58e6e9562d630b4b50c8a4260c5308` (não rastreado nos manifests)

**Campos a adicionar (idênticos em POST e PATCH, alinhados com `WellnessPreOut` e `wellness_pre.yaml`):**
- `readiness`: `type: integer, minimum: 1, maximum: 5` — Hooper Index, opcional
- `mood`: `type: integer, minimum: 1, maximum: 5` — Hooper Index, opcional
- `fatigue`: `type: integer, minimum: 1, maximum: 5` — Hooper Index, opcional
- `muscleSoreness`: `type: integer, minimum: 1, maximum: 5` — Hooper Index, camelCase, opcional
- `notes`: `type: string` — texto livre, opcional

**Nota:** No requestBody, os campos são `type: integer` (não nullable) — diferente do schema de resposta onde são `type: [integer, "null"]`. No requestBody, campo ausente = não enviado; não há semântica de "enviar null para zerar".

**P6-GAP-1:** `openapi_paths.yaml` (PASSO 7) deve ser editado de forma idêntica e na mesma operação — ambos os arquivos têm exatamente o mesmo conteúdo (diff vazio confirmado).

**Critérios de done:**
- [x] POST requestBody contém todos os 7 campos (+ `athleteId`)
- [x] PATCH requestBody contém todos os 7 campos
- [x] `hb artifact` registrado
- [x] `validate_contracts.py` → STATUS: PASS

> **EVIDÊNCIA (2026-04-23):**
> - `contracts/openapi/paths/training.yaml` — POST e PATCH expandidos com `readiness`, `mood`, `fatigue`, `muscleSoreness`, `notes` (campos opcionais, `minimum: 1, maximum: 5`; `notes: type: string`); `additionalProperties: false` preservado.
> - `docs/hbtrack/modulos/training/graph/openapi_paths.yaml` — espelhado de forma idêntica (diff vazio confirmado).
> - Hash novo: `995111183ea91ae3f6fa1c583a58b612b68f8a6c70341448d15f314587dab80f` (antes: `b9ba2e5c...`).
> - `generated/contracts/openapi/paths/training.yaml` copiado e sincronizado.
> - 17 entry-hashes + tree hashes de todos os 30 manifests atualizados com algoritmo `_tree_hash()` correto (seção `source_contracts` separada de `source_inputs`).
> - `hb artifact contracts/openapi/paths/training.yaml` → STATUS: PASS (AXIOM_INTEGRITY_GATE, PATH_CANONICALITY_GATE, JSON_SCHEMA_VALIDATION_GATE: PASS).
> - `validate_contracts.py` → STATUS: PASS (DERIVED_DRIFT_GATE: PASS, HANDOFF_COHERENCE_GATE: PASS).
> - `pytest src/training/tests/ -q` → **406 passed, 19 skipped** (inalterado).

---

### PASSO 7 — Espelhar mudanças em `openapi_paths.yaml` [GAP-5]

**Arquivo-alvo:** `docs/hbtrack/modulos/training/graph/openapi_paths.yaml` — POST e PATCH de wellness-pre

**Correção:** Idêntica ao PASSO 6 — mesmos 5 campos adicionados às mesmas operações.

**Nota:** Executado junto com o PASSO 6 na mesma operação. `openapi_paths.yaml` não é rastreado pelos manifests de traceabilidade (ausente em todos os 30 manifests — confirmado por grep).

**Critérios de done:**
- [x] `openapi_paths.yaml` POST + PATCH espelham `training.yaml` exatamente
- [x] `hb artifact` registrado (via PASSO 6 — arquivo não rastreado nos manifests; `training.yaml` é o artefato canônico)
- [x] `validate_contracts.py` → STATUS: PASS

> **EVIDÊNCIA (2026-04-23):**
> - `diff <(sed -n '1282,1510p' training.yaml) <(sed -n '1289,1517p' openapi_paths.yaml)` → sem saída (idênticos).
> - Hash `openapi_paths.yaml` pós-edição: `b7660d7df3abbe2c04ec2d152af8735d5e2a4322edda76458c43cbc032e5c1ea` (não rastreado nos manifests).
> - `validate_contracts.py` → STATUS: PASS (mesmo resultado que PASSO 6).

---

### PASSO 8 — Expandir testes e remover `_pick()` [GAP-4 + P2-GAP-3]

**Arquivo-alvo:** `src/training/tests/integration/test_training_api.py`

**Correções:**
- `test_get_and_update_wellness_pre`: cobrir round-trip completo dos 7 campos no POST, GET e PATCH
- `test_wellness_pre_required_fields` (novo): 422 para POST sem `sleep_quality` e sem `sleep_hours`
- `test_wellness_pre_patch_null_field` (novo): documentar comportamento atual — PATCH com `null` é ignorado (não zera o campo)
- Remover `_pick()` helper — testes devem verificar apenas camelCase (naming real da API)

**Análise de impacto (pré-implementação):**

| Componente | Impacto | Ação necessária |
|---|---|---|
| `test_get_and_update_wellness_pre` — expansão do POST | Teste envia apenas `sleep_quality`, `sleep_hours`, `readiness` — faltam `mood`, `fatigue`, `muscle_soreness`, `notes`; GET verifica apenas `athleteId`; PATCH verifica apenas `sleepQuality` | Expandir POST com todos os 7 campos; GET com asserção de todos os 7 em camelCase; PATCH com múltiplos campos |
| `test_wellness_pre_required_fields` | Já implementado no PASSO 4 ✅ | Nenhuma — apenas marcar [x] |
| `test_wellness_pre_patch_null_field` | Já implementado no PASSO 4 ✅ | Nenhuma — apenas marcar [x] |
| Remoção de `_pick()` — 15 usos em 9 endpoints distintos | Se qualquer endpoint não retornar camelCase, substituição quebra o teste | Verificar cobertura do CamelRouter em cada endpoint afetado |
| `attendance` POST/GET (`athleteId`, `status`) | CamelRouter aplicado ao sub-roteador `attendance` no PASSO 2 | Substituição segura: `athleteId` e `status` (idêntico) |
| `mesocycle` POST/GET/PATCH (`name`, `createdAt`) | CamelRouter aplicado ao sub-roteador `planning` | `name` → `name` (idêntico, to_camel seguro); `weekNumber`, `plannedSessionsCount` (camelCase) |
| `execution` GET (`id`) | `id` → `id` (sem underscore, to_camel idêntico) | Substituição segura |
| `objectives` GET (`objectiveType`) | CamelRouter em `sessions` sub-roteador | `objectiveType` confirmado via PASSO 2 |
| `feedback` POST/close (`decisionText`) | CamelRouter em `feedback` sub-roteador | Substituição segura |
| `attention-queue` resolve (`resolvedByUserId`) | CamelRouter em `attention` sub-roteador | Substituição segura |
| `recommendations` accept/dismiss (`status`) | CamelRouter em `recommendations` | `status` idêntico, `status` não muda com camelCase |
| `ineligibility` submit/GET (`athleteId`, `reasonFlags`) | CamelRouter em `eligibility` | Substituição segura |
| wellness-post GET/PATCH (`athleteId`, `perceivedExertion`) | CamelRouter em `wellness` | Substituição segura |
| Risco: testes fora de `TestWellnessEndpoints` que dependem de snake_case | Nenhum encontrado — todos os `_pick()` têm camelCase como segundo argumento | Nenhuma ação extra |
| `_pick()` def na linha 33 | Remoção limpa após substituir todos os 15 usos | Deletar definição |

**P8-GAP-1 — campo `notes` no PATCH de `test_get_and_update_wellness_pre`:** O teste atual faz PATCH com `notes: "updated"` mas não verifica o valor no response. A expansão deve verificar `notes` na resposta do PATCH.

**P8-GAP-2 — round-trip de `mood`, `fatigue`, `muscleSoreness` no GET:** O POST atual envia `readiness: 4` mas o GET não verifica. A expansão deve enviar todos os 5 campos opcionais e verificá-los no GET em camelCase.

**Critérios de done:**
- [x] `test_get_and_update_wellness_pre` verifica todos os 7 campos no GET
- [x] `test_wellness_pre_required_fields` confirma 422 sem `sleep_quality` e sem `sleep_hours`
- [x] `test_wellness_pre_patch_null_field` documenta comportamento de PATCH com null
- [x] `_pick()` removido ou substituído por acesso direto camelCase
- [x] `pytest src/training/tests/ -q` → 0 failed

> **EVIDÊNCIA (2026-04-23):**
> - `test_get_and_update_wellness_pre` expandido: POST envia 7 campos opcionais (`sleep_quality`, `sleep_hours`, `readiness`, `mood`, `fatigue`, `muscle_soreness`, `notes`); GET verifica `athleteId`, `trainingSessionId`, `sleepQuality`, `sleepHours`, `readiness`, `mood`, `fatigue`, `muscleSoreness`, `notes`, `createdAt`, `updatedAt`; PATCH verifica `sleepQuality` e `notes`.
> - `_pick()` helper removido da linha 33; 15 chamadas substituídas por acesso direto camelCase em 9 endpoints distintos (attendance, wellness-pre, wellness-post, mesocycles, microcycles, execution-records, objectives, feedback-threads, attention-queue, recommendations, ineligibility).
> - `test_wellness_pre_required_fields`: PASSED (criado PASSO 4, verificado PASSO 8).
> - `test_wellness_pre_patch_null_field`: PASSED (criado PASSO 4, verificado PASSO 8).
> - `pytest src/training/tests/ -q` → **406 passed, 19 skipped, 0 failed**.
> - `timeout 90 validate_contracts.py` → **STATUS: PASS** (todos 22 gates PASS, incluindo DERIVED_DRIFT_GATE e HANDOFF_COHERENCE_GATE).

---

### PASSO 9 — Validar pipeline CDD [P2-GAP-2]

**Descrição:** Após todas as edições de contratos (PASSOs 5–7), os manifests em `generated/` precisam ter seus SHA256 re-computados. `validate_contracts.py` falhará com `DERIVED_DRIFT_GATE` se algum artefato editado não foi re-registrado.

**Como validar:**
```bash
python3 scripts/contracts/validate/validate_contracts.py
```

**Critérios de done:**
- [x] `validate_contracts.py` → `STATUS: PASS`
- [x] `DERIVED_DRIFT_GATE: PASS`
- [x] Zero erros de hash divergente

> **EVIDÊNCIA (2026-04-23):** `timeout 90 validate_contracts.py` → STATUS: PASS. Todos 22 gates PASS: DERIVED_DRIFT_GATE, HANDOFF_COHERENCE_GATE, JSON_SCHEMA_VALIDATION_GATE, OPENAPI_ROOT_STRUCTURE_GATE e demais. Zero hash divergente.

---

### PASSO 10 — Suite completo verde

**Como validar:**
```bash
DJANGO_SETTINGS_MODULE=config.settings .venv/bin/python3 -m pytest src/training/tests/ -q
```

**Critérios de done:**
- [x] 0 failed
- [x] Todos os novos testes passando: `test_wellness_pre_required_fields`, `test_wellness_pre_patch_null_field`, `test_get_and_update_wellness_pre` expandido

> **EVIDÊNCIA (2026-04-23):** `pytest src/training/tests/ -q` → **406 passed, 19 skipped, 0 failed**. `test_wellness_pre_required_fields` PASSED, `test_wellness_pre_patch_null_field` PASSED, `test_get_and_update_wellness_pre` PASSED (com 7 campos verificados).



## 7. Critério de conclusão de REM-1E (atualizado v2)

**Critérios originais (v1):**
- [x] `manage.py migrate` aplicado — coluna `sleep_hours` existe na tabela `training_wellness_pre` ✅
- [x] `wellness_pre.yaml` contém todos os 7 campos canônicos nas properties ✅ PASSO 5
- [x] `training.yaml` POST requestBody contém todos os 7 campos (+ `athleteId`) ✅ PASSO 6
- [x] `training.yaml` PATCH requestBody contém todos os 7 campos ✅ PASSO 6
- [x] `openapi_paths.yaml` POST + PATCH espelhados ✅ PASSO 7
- [x] Manifests re-registrados com `hb artifact` ✅ PASSOs 5–7
- [x] `validate_contracts.py` → STATUS: PASS ✅ PASSO 9
- [x] `pytest src/training/tests/` → 0 failed ✅ PASSO 10
- [x] `test_get_and_update_wellness_pre` verifica round-trip completo dos 7 campos ✅ PASSO 8

**Critérios adicionais (v2 — auditoria profunda):**
- [x] Decisão de naming documentada em canon (Opção A: camelCase no runtime) [GAP-NEW-1] ✅ PASSO 2
- [x] Naming do contrato alinhado com o runtime (runtime agora emite camelCase) [GAP-NEW-1] ✅ PASSO 2
- [x] `_pick()` helper removido dos testes — testes verificam apenas o naming real da API [GAP-NEW-1] ✅ PASSO 8
- [x] `WellnessPre.validate_invariants()` lança `ValueError` para `sleep_hours` fora de [0,24] [GAP-NEW-2] ✅ PASSO 3
- [x] `pytest` confirma 422 para `sleep_hours=25` e `sleep_hours=-1` [GAP-NEW-2] ✅ PASSO 3
- [x] `SubmitWellnessPreIn.sleep_quality` e `sleep_hours` são não-Optional (required) [GAP-NEW-3] (PASSO 4)
- [x] `pytest` confirma 422 para POST sem `sleep_quality` e sem `sleep_hours` [GAP-NEW-3] (PASSO 4)
- [x] Comportamento de PATCH com `null` está documentado e testado [GAP-NEW-4] (PASSO 4)

---

## 8. Separação de módulos (sovereignty check)

O módulo soberano `wellness` (módulo 07 no registry) é **distinto** de `training/wellness-pre`:
- `contracts/openapi/components/schemas/wellness/` — **não tocado** ✅  
- `contracts/openapi/paths/wellness.yaml` — **não tocado** ✅  
- `src/wellness/` — **não existe ainda** (módulo ainda não implementado) ✅  

Todas as alterações ficam estritamente dentro do módulo `training`.

---

## 9. A pergunta que você deveria estar fazendo (e não estava)

> **"A API realmente responde em camelCase como o contrato especifica — ou responde em snake_case?"**

Esta é a pergunta mais crítica e mais omitida. A resposta é: **snake_case puro, sempre**.

Isso significa que o contrato OpenAPI é uma "mentira bem-intencionada" — declara `sleepQuality`, `athleteId`, `trainingSessionId`, `createdAt`, mas a API nunca retornou esses nomes. Qualquer frontend ou SDK construído **a partir do contrato** funciona com nomes errados.

O problema é sistêmico — não é específico de wellness-pre. Afeta **todos** os endpoints do módulo training. E foi completamente invisível porque:

1. Os testes usam `_pick(data, snake, camel)` — aceitam qualquer naming
2. O `validate_contracts.py` não faz diff semântico de campos
3. O Django Ninja não tem configuração de camelCase

Enquanto essa decisão não for tomada e implementada, **nenhum SDK gerado funcionará corretamente com a API real**. Esta é a questão mais urgente antes de qualquer integração frontend.

---

## 10. Auditoria avaliativa pós-implementação (2026-04-24)

> Objetivo: provar (ou refutar) que as propostas dos PASSOs 1-10 estão robustamente implementadas, que as evidências verificam o que afirmam verificar, que os testes não contêm falsos positivos, e que as mudanças foram determinísticas.

### 10.1 Achado positivo — CamelRouter: cobertura real é 100% (não 12/13)

Na sessão anterior, um `grep` apontou "12 instâncias de CamelRouter em 13 arquivos" como gap crítico. Após auditoria direta:

```
0 src/training/api/errors.py    ← sem CamelRouter
2 src/training/api/wellness.py  ← com CamelRouter
2 src/training/api/sessions.py  ← com CamelRouter
... (10 demais arquivos)
```

**`errors.py` é um módulo utilitário** (expõe `@map_exceptions` decorator). Não define nenhum `router`, não registra endpoints. Os 12 arquivos de handler existentes **todos usam `CamelRouter`**. O "gap" era falso — ocorreu porque `errors.py` entrou na contagem de arquivos via `ls *.py` mas não é um handler.

✅ **Critério PASSO 2 confirmado como correto**: "Todos os sub-roteadores usam CamelRouter".

---

### 10.2 Evidência viva — resposta real da API via Django test client

Payload real de um POST `wellness-pre` com todos os 7 campos, fora do pytest, via Django test client direto:

```python
POST /api/training/training-sessions/{id}/wellness-pre  →  201
response keys: ['id', 'trainingSessionId', 'athleteId', 'createdAt', 'updatedAt',
                'readiness', 'sleepQuality', 'sleepHours', 'mood', 'fatigue',
                'muscleSoreness', 'notes']
snake_case keys found: []
camelCase keys found: ['trainingSessionId', 'athleteId', 'createdAt', 'updatedAt',
                       'sleepQuality', 'sleepHours', 'muscleSoreness']
trainingSessionId: <uuid>   sleepQuality: 3   muscleSoreness: 1
```

✅ Zero chaves snake_case. `trainingSessionId` (alias explícito) e `sleepQuality` / `muscleSoreness` (alias_generator) presentes. A API **genuinamente emite camelCase** após os PASSOs 1-2. Não é só o que o teste "vê" — é o payload real.

---

### 10.3 Cadeia de validação — quem rejeita o quê

Verificação ao vivo com 4 cenários de entrada inválida:

| Entrada | Status | Mensagem retornada | Camada |
|---|---|---|---|
| `sleep_hours: 25.0` | 422 | `body.body.sleep_hours: Input should be less than or equal to 24` | Pydantic (PASSO 4) |
| `sleep_hours: -1.0` | 422 | `body.body.sleep_hours: Input should be greater than or equal to 0` | Pydantic (PASSO 4) |
| sem `sleep_quality` | 422 | `body.body.sleepQuality: Field required` | Pydantic (PASSO 4) |
| `sleep_quality: 0` | 422 | `body.body.sleep_quality: Input should be greater than or equal to 1` | Pydantic (PASSO 4) |

Observações:
- **Pydantic rejeita antes do domínio** — `validate_invariants()` do domínio nunca é chamado para inputs inválidos. Isso é correto: Pydantic é a barreira na fronteira HTTP.
- **Domínio também valida** (dupla proteção): `WellnessPre(sleep_hours=25.0).validate_invariants()` lança `ValueError: sleepHours deve estar em [0, 24]` — PASSO 3 implementado. A camada de domínio protege acesso programático direto (fora do HTTP).
- A mensagem de erro do campo obrigatório retorna `sleepQuality` em camelCase — consistente com o alias da schema.

✅ PASSOs 3 e 4 funcionam deterministicamente.

---

### 10.4 Análise crítica do `test_wellness_pre_patch_null_field` — coincidental correctness

**O que o teste afirma testar**: "PATCH com `notes=null` não deve zerar o campo existente (GAP-NEW-4)".

**O que o teste realmente envia**:
```python
# test usa:
data={"notes": None}

# Django test client com content_type='application/json' chama force_bytes(data):
force_bytes({"notes": None})  →  b"{'notes': None}"  # Python repr — NÃO JSON válido!
# JSON correto seria:
json.dumps({"notes": None})   →  b'{"notes": null}'
```

**Mecanismo real de passagem**: O body `b"{'notes': None}"` é inválido como JSON. Ninja/Pydantic ao receber body malformado trata todos os campos de `UpdateWellnessPreIn` como ausentes (todos `None`). O use case então executa:
```python
for field_name in ("readiness", "sleep_quality", ..., "notes"):
    value = getattr(inp, field_name)
    if value is not None:          # ← todos são None → nenhum campo é atualizado
        setattr(wellness, field_name, value)
```
Resultado: `notes` permanece `"nota original"` → teste passa.

**É um falso positivo?** — **Parcialmente sim, mas o comportamento documentado é correto.**

Com JSON null válido (`{"notes": null}`), Pydantic deserializa `notes=None` → use case também ignora (`if value is not None`) → notes também não seria zerado. O comportamento de GAP-NEW-4 **é real** e seria reproduzido mesmo com JSON correto.

Contudo: **o teste não está testando o que afirma**. Está testando "body malformado não afeta o campo" quando deveria estar testando "null JSON não afeta o campo". O resultado final é o mesmo, mas o teste é tecnicamente fraco:
- Não verifica que Ninja aceita o body (poderia estar retornando 422 silenciosamente)
- Não envia JSON válido com null
- A asserção `assert patch_resp.status_code == 200` passa porque body inválido → update sem campos → 200 OK

⚠️ **Diagnóstico**: coincidental correctness. O comportamento de GAP-NEW-4 é real e confirmado via análise do use case. O teste passava pelo motivo errado mas provava o comportamento certo de forma acidental.

**Correção aplicada**: `data={"notes": None}` substituído por `data=json.dumps({"notes": None})` em `test_wellness_pre_patch_null_field`. Após a correção: 6/6 testes de wellness passam, 406/406 suite completo verde.

✅ **GAP-NEW-4 coberto com JSON válido confirmado.**

---

### 10.5 Análise crítica do `test_wellness_pre_required_fields` — suficiente mas mínimo

O teste verifica 4 cenários com apenas `assert resp.status_code == 422`. Não verifica:
- Qual campo foi rejeitado
- Qual mensagem de erro foi retornada
- Se outros campos válidos foram aceitos

**Impacto**: o teste prova que o endpoint rejeita entradas inválidas (comportamento correto). Mas não prova **qual camada rejeita** nem **se a mensagem é informativa**. Para o objetivo de PASSO 4 ("tornar campos obrigatórios"), o teste é suficiente. Para rastrear regressões específicas, seria necessário verificar o campo na mensagem de erro.

✅ Suficiente para o critério de PASSO 4. Melhoria futura: adicionar `assert "sleepQuality" in resp.json()["detail"][0]["loc"]`.

---

### 10.6 Análise do `test_get_and_update_wellness_pre` — genuinamente robusto

Este foi o alvo principal de PASSO 8. Verificação:

- POST com 7 campos: `sleep_quality=3, sleep_hours=7.5, readiness=4, mood=3, fatigue=2, muscle_soreness=1, notes="feeling good"`
- GET verifica: `athleteId`, `trainingSessionId`, `sleepQuality==3`, `sleepHours==7.5`, `readiness==4`, `mood==3`, `fatigue==2`, `muscleSoreness==1`, `notes=="feeling good"`, `"createdAt" in data`, `"updatedAt" in data`
- PATCH verifica: `sleepQuality==5`, `notes=="updated"`
- `_pick()` completamente removido — zero asserções usam atalho de alias

✅ O teste **genuinamente prova** que todos os 7 campos chegam na resposta com camelCase correto. Não há falso positivo aqui — cada asserção verifica um campo específico pelo nome exato.

---

### 10.7 Análise da Seção 3 "Cadeia de impacto" — anotações desatualizadas

A Seção 3 ainda contém anotações do estado **antes** dos PASSOs, como:
- `← sem alias_generator [GAP-NEW-1]` para `WellnessPreOut`
- Referências a gaps já resolvidos

Isso é **deriva de documentação**, não erro funcional. A seção descreve a cadeia causal que levou à decisão (o "antes"), o que tem valor histórico. Mas pode criar confusão para quem ler sem contexto.

⚠️ **Diagnóstico**: documentação desatualizada. Impacto funcional: zero. Recomendação: adicionar nota no topo da seção indicando que descreve o estado pré-implementação.

---

### 10.8 Veredicto final por PASSO

| PASSO | Claim | Verificação | Resultado |
|---|---|---|---|
| PASSO 1 | Migration aplicada, banco com `sleep_hours` | `psql \d training_wellnesspre` → coluna presente | ✅ |
| PASSO 2 | 100% sub-roteadores com CamelRouter | `grep "router = CamelRouter" *.py` → 12/12 handler files | ✅ confirmado (errors.py não é handler) |
| PASSO 2 | API retorna camelCase | Django test client real → 0 snake_case keys | ✅ verificado ao vivo |
| PASSO 3 | `validate_invariants()` valida sleep_hours [0,24] | Direto: `WellnessPre(sleep_hours=25).validate_invariants()` → ValueError | ✅ |
| PASSO 4 | `sleep_quality` e `sleep_hours` required no Pydantic | HTTP 422 + `Field required` / `less than or equal` via test client real | ✅ |
| PASSO 4 | 4 novos testes verdes | `pytest src/training/tests/ -q` → 406 passed | ✅ |
| PASSO 5 | `wellness_pre.yaml` com 14 campos incluindo 5 novos | `yaml.safe_load` + contagem | ✅ |
| PASSO 6 | `training.yaml` POST/PATCH com campos corretos | Leitura direta + `required: [athleteId, sleepQuality, sleepHours]` | ✅ |
| PASSO 7 | `openapi_paths.yaml` espelhado | Leitura + contagem de campos | ✅ |
| PASSO 8 | `_pick()` removido, teste expandido com 7 campos | `grep "_pick" → 0 resultados`, asserções verificadas | ✅ robusto |
| PASSO 9 | `validate_contracts.py` STATUS: PASS | Executado com timeout 120 → STATUS: PASS, exitcode=0 (após sync generated/ + repair_manifests em 2026-04-24) | ✅ |
| PASSO 10 | Suite completo verde | 407 passed, 19 skipped, 0 failed (verificado 2026-04-24) | ✅ |

---

### 10.9 Gaps resolvidos após auditoria avaliativa (2026-04-24)

| ID | Descrição | Solução implementada | Status |
|---|---|---|---|
| GAP-NEW-4 | `test_wellness_pre_patch_null_field` enviava Python repr em vez de JSON null; null não limpava campos | tri-state PATCH via `model_fields_set` + `provided_fields` + contrato OAS 3.1 atualizado | ✅ corrigido |
| R8 | `UniqueConstraint(session_id, athlete_id)` ausente em `WellnessPreModel.Meta` — race condition | UniqueConstraint parcial + migration 0010 + `test_wellness_pre_duplicate_entry` | ✅ corrigido |
| DOC-3 | Seção 3 "Cadeia de impacto" com anotações pré-PASSO desatualizadas | Seção 3 atualizada com estado pós-PASSO e nota de contexto histórico | ✅ corrigido |
| TEST-3 | `test_wellness_pre_required_fields` só verificava status 422, não o campo rejeitado | Asserções de campo adicionadas (`sleepQuality`, `sleepHours`, `sleep_quality`) | ✅ corrigido |
| SCOPE | `SubmitWellnessPostIn` ainda tem campos Optional — wellness-post não corrigido | Fora do escopo de REM-1E — intencional | ℹ️ intencional |
| DRIFT-1 | `generated/contracts/openapi/paths/training.yaml` fora de sincronia com canonical após edição tri-state PATCH — DERIVED_DRIFT_GATE FAIL | `cp canonical → generated/` + `python3 scripts/repair_manifests.py` → 30 manifests atualizados (hash `3bbe4e65...`) | ✅ corrigido |
| DRIFT-2 | `SESSION_HANDOFF.md` campo `resultado: CONCLUIDO_GAPS_RESOLVIDOS` inválido para o schema — HANDOFF_COHERENCE_GATE FAIL | Atualizado para `resultado: DONE` (enum válido em `session_handoff.schema.json`) | ✅ corrigido |

---

### 10.10 Conclusão da auditoria (atualizada 2026-04-24)

**O sistema funciona corretamente no mundo real.** Todas as propriedades centrais foram verificadas com evidências diretas e os gaps identificados foram resolvidos.

**Estado final do suite de testes:**
- **407 passed** (406 anteriores + 1 novo `test_wellness_pre_duplicate_entry`), 19 skipped, 0 failed
- `test_wellness_pre_required_fields`: 4 asserções de status + 4 asserções de campo específico
- `test_wellness_pre_duplicate_entry`: POST duplicado → 409 + INV-TRAIN-009 no detail
- `test_wellness_pre_patch_null_field`: JSON null válido via `json.dumps`

**Invariantes com cobertura completa agora:**
| Invariante | Camada Pydantic | Camada Domínio | Camada DB | Teste |
|---|---|---|---|---|
| INV-TRAIN-009 (unicidade ativa) | ✅ use case check | ✅ use case → 409 | ✅ UniqueConstraint parcial | ✅ `test_wellness_pre_duplicate_entry` |
| INV-TRAIN-033 (sleep_hours [0,24]) | ✅ `Field(ge=0,le=24)` | ✅ `validate_invariants()` | — | ✅ `test_wellness_pre_sleep_hours_range` |
| INV-TRAIN-0XX (sleep_quality required [1-5]) | ✅ `Field(..., ge=1, le=5)` | ✅ `validate_invariants()` | — | ✅ `test_wellness_pre_required_fields` |
| camelCase contract-runtime parity | ✅ `alias_generator` + `CamelRouter` | — | — | ✅ `test_wellness_pre_response_keys_are_camelcase` |

**Não há gaps abertos que afetem funcionalidade em produção.**

**Verificação final (2026-04-24):**
- `pytest src/training/tests/ -q` → `407 passed, 19 skipped, 0 failed` ✅
- `validate_contracts.py` → `STATUS: PASS`, exitcode=0, 30 gates verificados, 0 bloqueantes ✅
- `sha256sum contracts/openapi/paths/training.yaml generated/contracts/openapi/paths/training.yaml` → hashes idênticos (`3bbe4e65...`) ✅
- `SESSION_HANDOFF.md resultado: DONE` ✅
- Pydantic: `sleep_quality required=True [ge=1,le=5]`, `sleep_hours required=True [ge=0,le=24]` ✅
- `WellnessPreOut` keys (by_alias=True): `['id','trainingSessionId','athleteId','createdAt','updatedAt','readiness','sleepQuality','sleepHours','mood','fatigue','muscleSoreness','notes']` ✅
- CamelRouter: 12/12 handler files, 0 snake_case keys na resposta ✅
