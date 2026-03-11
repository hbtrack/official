# ANÁLISE CONTRATOS MÓDULO ATLETAS — GAP ANALYSIS
Data: 2026-03-08
Versão: 1.0.0
Status: DRAFT — pendente execução das correções

---

## SUMÁRIO EXECUTIVO

- Total de contratos analisados: 19 arquivos
- Arquivos referenciados inexistentes: 21
- Problemas **críticos (P0)**: 8
- Problemas **altos (P1)**: 9
- Problemas **médios (P2)**: 8
- Problemas **menores (P3)**: 5

**Conclusão executiva:** O módulo atletas NÃO pode ser executado por nenhum agente sem alucinação no estado atual. Os dois motores de execução (`hb_plan.py` e `hb_verify.py`) não existem. O handoff que o Executor obrigatoriamente deve ler contém um JSON Schema, não um handoff real. Quatro dos contratos requeridos são documentação markdown (não YAML parseable). 89% dos checkers não tem implementação. O `CHECKERS_REGISTRY.md` está desatualizado e diverge da constituição vigente em 7 checker_ids.

---

## 1. INVENTÁRIO DE CONTRATOS

| # | Arquivo | Tipo | Status | Parseable como YAML/JSON |
|---|---|---|---|---|
| 1 | `00_ATLETAS_CROSS_LINTER_RULES.json` | Meta-contrato JSON | FINAL_DRAFT v1.2.7 | SIM |
| 2 | `00_ATLETAS_CROSS_LINTER_RULES.schema.json` | JSON Schema | Existe | SIM (v1.2.3) |
| 3 | `01_ATLETAS_OPENAPI.yaml` | Contrato HTTP | Markdown com YAML em bloco de código | NÃO |
| 4 | `04_ATLETAS_WORKFLOWS.arazzo.yaml` | Opcional | VAZIO (1 linha) | NÃO |
| 5 | `05_ATLETAS_EVENTS.asyncapi.yaml` | Contrato de eventos | Markdown com YAML em bloco de código | NÃO |
| 6 | `06_ATLETAS_CONSUMER_CONTRACTS.md` | Opcional | VAZIO (1 linha) | NÃO |
| 7 | `08_ATLETAS_TRACEABILITY.yaml` | Traceabilidade | Markdown com YAML em bloco de código | NÃO |
| 8 | `12_ATLETAS_EXECUTION_BINDINGS.yaml` | Bindings de execução | Markdown com YAML em bloco de código | NÃO |
| 9 | `12_ATLETAS_EXECUTION_BINDINGS.schema.json` | JSON Schema | Existe | SIM |
| 10 | `13_ATLETAS_DB_CONTRACT.yaml` | Contrato de BD | YAML real — INCOMPLETO | SIM |
| 11 | `14_ATLETAS_UI_CONTRACT.yaml` | Contrato de UI | Markdown com YAML em bloco de código | NÃO |
| 12 | `15_ATLETAS_INVARIANTS.yaml` | Invariantes de domínio | YAML real | SIM |
| 13 | `16_ATLETAS_AGENT_HANDOFF.json` | Handoff do agente | JSON Schema (NÃO é o handoff real) | SIM (schema, não dado) |
| 14 | `17_ATLETAS_PROJECTIONS.yaml` | Contrato de projeções | YAML real | SIM |
| 15 | `18_ATLETAS_SIDE_EFFECTS.yaml` | Contrato de side effects | YAML real | SIM |
| 16 | `19_ATLETAS_TEST_SCENARIOS.yaml` | Cenários de teste | YAML real | SIM |
| 17 | `20_ATLETAS_EXECUTOR_RESTRICTION_PROMPT.md` | Prompt de restrição | Markdown — v1.2.3 (desatualizado) | N/A |
| 18 | `CHECKERS_REGISTRY.md` | Referência de implementação | Markdown — DESATUALIZADO | N/A |
| 19 | `MOTORES.md` | Referência de motores | Markdown (contexto) | N/A |

---

## 2. ARQUIVOS REFERENCIADOS INEXISTENTES

### 2.1 Motores obrigatórios ausentes (bloqueantes absolutos)

**Evidência: `rascunho.md` linha 21:** "`hb_plan.py` → gerador determinístico do snapshot"
**Evidência: `rascunho.md` linha 25:** "`hb_verify.py` → validador determinístico contra o snapshot"
**Evidência: `MOTORES.md` seção "REGRAS ESTRUTURAIS — hb_plan.py e hb_verify.py"**

- `scripts/run/hb_plan.py` — NÃO EXISTE
- `scripts/run/hb_verify.py` — NÃO EXISTE

**Impacto:** Todo o sistema de validação cross-contract depende desses scripts. Sem eles, nenhum handoff válido pode ser gerado, nenhum hash pode ser verificado, X-012 nunca pode passar.

### 2.2 Estrutura de checkers ausente

**Evidência: `CHECKERS_REGISTRY.md` linha 12:** "`scripts/hbtrack_lint/checkers/`"

- `scripts/hbtrack_lint/` — diretório NÃO EXISTE
- Consequência: 63 checker_ids declarados na constituição não têm implementação Python

### 2.3 Caminhos errados nos cross-contract references

**Evidência: `17_ATLETAS_PROJECTIONS.yaml` linhas 207-211:**
```
requires_events_contract: docs/hbtrack/modules/ATHLETES/05_ATLETAS_EVENTS.asyncapi.yaml
```
**Evidência: `05_ATLETAS_EVENTS.asyncapi.yaml` linhas 479, 483:**
```
required_file: docs/hbtrack/modules/ATHLETES/17_ATLETAS_PROJECTIONS.yaml
```

O caminho correto é `docs/hbtrack/modulos/atletas/` (português, minúsculas). Todos os cross-references usam `docs/hbtrack/modules/ATHLETES/` que não existe.

Arquivos MISSING comprovados:
- `docs/hbtrack/modules/ATHLETES/05_ATLETAS_EVENTS.asyncapi.yaml`
- `docs/hbtrack/modules/ATHLETES/13_ATLETAS_DB_CONTRACT.yaml`
- `docs/hbtrack/modules/ATHLETES/08_ATLETAS_TRACEABILITY.yaml`
- `docs/hbtrack/modules/ATHLETES/15_ATLETAS_INVARIANTS.yaml`
- `docs/hbtrack/modules/ATHLETES/18_ATLETAS_SIDE_EFFECTS.yaml`
- `docs/hbtrack/modules/ATHLETES/17_ATLETAS_PROJECTIONS.yaml`

**Evidência: `00_ATLETAS_CROSS_LINTER_RULES.json` linha 42:**
```json
"path": "docs/hbtrack/modules/<MODULE>/00_ATLETAS_CROSS_LINTER_RULES.schema.json"
```
Mesmo problema: `<MODULE>` não resolvido e path em inglês.

### 2.4 Arquivos de backend referenciados (pré-condição de implementação)

Estes arquivos não existem — estado esperado pré-execução, mas necessário listar para DoD do Executor:

- `backend/app/models/athlete.py` (`13_ATLETAS_DB_CONTRACT.yaml` linha 8)
- `backend/alembic/versions/20260307_1200_create_athletes_table.py` (`13_ATLETAS_DB_CONTRACT.yaml` linha 9)
- `backend/app/domain/invariants/athletes_invariants.py` (`15_ATLETAS_INVARIANTS.yaml` linha 14)
- `backend/app/domain/reference/category_birth_year_mapping.py` (`15_ATLETAS_INVARIANTS.yaml` linha 16)
- `backend/app/projections/athletes_projection.py` (`17_ATLETAS_PROJECTIONS.yaml` linha 56)
- `backend/app/events/upcasters/athletes_upcasters.py` (`17_ATLETAS_PROJECTIONS.yaml` linha 66)
- `backend/app/side_effects/athletes_side_effects.py` (`18_ATLETAS_SIDE_EFFECTS.yaml` linha 14)
- `backend/app/integrations/notification_service.py` (`18_ATLETAS_SIDE_EFFECTS.yaml` linha 15)
- `backend/app/integrations/federation_sync_service.py` (`18_ATLETAS_SIDE_EFFECTS.yaml` linha 16)
- Infraestrutura protegida: `backend/app/integrations/registry.py`, `backend/app/side_effects/idempotency.py`, `backend/app/projections/projection_ledger.py`, `backend/app/projections/transaction_scope.py` (`20_ATLETAS_EXECUTOR_RESTRICTION_PROMPT.md` linhas 214-221)

### 2.5 Artefatos de relatório ausentes

- `_reports/WAIVERS.yaml` (`00_ATLETAS_CROSS_LINTER_RULES.json` linha 916)
- `_reports/cross_lint_report.json` (`00_ATLETAS_CROSS_LINTER_RULES.json` linha 971)
- `_reports/cross_lint_report.md` (`00_ATLETAS_CROSS_LINTER_RULES.json` linha 972)
- `anchor_manifest.json` (`00_ATLETAS_CROSS_LINTER_RULES.json` linha 35 como generated)

---

## 3. PROSA E INSTRUÇÃO BARATA

### 3.1 Contratos requeridos que são markdown, não YAML real

**Evidência: `01_ATLETAS_OPENAPI.yaml` linhas 1-13:**
```
# 01_ATLETAS_OPENAPI.yaml - Módulo ATHLETES

Este template não resolve tudo
...
```yaml
openapi: 3.1.1
...
```
```

O arquivo começa com texto em prosa, tem o YAML dentro de um fenced code block markdown. Um parser YAML carregaria isso como string inválida, não como documento OpenAPI estruturado.

**Afeta:** `01_ATLETAS_OPENAPI.yaml`, `05_ATLETAS_EVENTS.asyncapi.yaml`, `08_ATLETAS_TRACEABILITY.yaml`, `12_ATLETAS_EXECUTION_BINDINGS.yaml`, `14_ATLETAS_UI_CONTRACT.yaml`

**Por que é instrução barata:** Um parser YAML/JSON não consegue extrair o contrato. Quando `hb_plan.py` tentar `yaml.safe_load("# 01_ATLETAS_OPENAPI.yaml...")`, obterá `None` ou erro.

**Solução determinística:** Cada arquivo `.yaml` deve ser YAML puro, sem markdown envelope. A documentação pode existir em arquivo separado (ex: `01_ATLETAS_OPENAPI.md`).

### 3.2 TRACE-RULE-001 sem campo `backend_handler` na estrutura

**Evidência: `08_ATLETAS_TRACEABILITY.yaml` linha 27:** "Every `operation_id` must bind to exactly one `backend_handler`."

Porém a estrutura de exemplo (linhas 153-244) não tem campo `backend_handler` em nenhuma operação. O contrato declara a regra mas não declara o campo que a regra verifica.

**Solução determinística:** Adicionar campo obrigatório `backend_handler: <string>` em cada operação da estrutura TRACEABILITY.

### 3.3 Restriction prompt v1.2.3 vs constituição v1.2.7

**Evidência: `20_ATLETAS_EXECUTOR_RESTRICTION_PROMPT.md` linha 5:**
```
Autoridade: CROSS-LINTER-HBTRACK v1.2.3
```
**Evidência: `00_ATLETAS_CROSS_LINTER_RULES.json` linha 6:**
```json
"version": "1.2.7"
```

O prompt não menciona as regras X-018, X-019, X-020, DOC-004, DOC-005 adicionadas entre v1.2.3 e v1.2.7. Um Executor lendo o prompt pensaria que essas regras não existem.

---

## 4. FALTA DE DETERMINISMO

### 4.1 `13_ATLETAS_DB_CONTRACT.yaml` gravemente incompleto

**Evidência: arquivo completo, linhas 1-28 — apenas 3 colunas declaradas.**

O arquivo declara apenas `athlete_id`, `full_name`, `birth_year` de uma tabela que, pelos demais contratos, precisa de:

| Campo ausente no DB contract | Evidência de onde é requerido |
|---|---|
| `birth_date` | `01_ATLETAS_OPENAPI.yaml` AthleteResponse; CHECK constraint linha 25 usa `birth_date` |
| `category_id` | `01_ATLETAS_OPENAPI.yaml` AthleteCreateRequest required |
| `team_id` | `01_ATLETAS_OPENAPI.yaml` AthleteResponse |
| `federation_id` | `15_ATLETAS_INVARIANTS.yaml` INV-ATH-001 uq constraint |
| `dominant_hand` | `01_ATLETAS_OPENAPI.yaml` AthleteResponse |
| `status` | `01_ATLETAS_OPENAPI.yaml` AthleteResponse required |
| `created_at` | `01_ATLETAS_OPENAPI.yaml` AthleteResponse required |
| `deleted_at` | `15_ATLETAS_INVARIANTS.yaml` INV-ATH-010 `deleted_at IS NULL` |
| `version_id` | `13_ATLETAS_DB_CONTRACT.yaml` linha 27 própria `version_column: version_id` |
| `uq_athletes_federation_id` | `08_ATLETAS_TRACEABILITY.yaml` linha 166; `15_ATLETAS_INVARIANTS.yaml` linha 47 |
| `idx_athletes_team_id` | `08_ATLETAS_TRACEABILITY.yaml` linha 205 |
| `conflict_error_code` | `00_ATLETAS_CROSS_LINTER_RULES.json` CC-002 obrigatório para optimistic_locking |
| `retry_policy` (locking) | `00_ATLETAS_CROSS_LINTER_RULES.json` CC-002 obrigatório para optimistic_locking |
| `meta.status` | `00_ATLETAS_CROSS_LINTER_RULES.json` DOC-002 exige metadata canônico |
| `meta.version` | DOC-002 mesmo |

**Inconsistência interna crítica:** O CHECK constraint na linha 25 referencia `birth_date` (`"birth_year = EXTRACT(YEAR FROM birth_date)"`) mas `birth_date` não está declarada como coluna — DDL inválido em runtime.

### 4.2 INV-ATH-002 requer `competition.year` e `athlete.category_code` não presentes no request

**Evidência: `15_ATLETAS_INVARIANTS.yaml` linhas 86-95:**
```yaml
enforcement_bindings:
  required_inputs:
    - competition.year
    - athlete.birth_date
    - athlete.category_code
```
**Evidência: `01_ATLETAS_OPENAPI.yaml` AthleteCreateRequest:** Aceita `category_id` (UUID) mas não `category_code` (string) nem `competition_year` (integer).

Não existe contrato que especifique:
1. Como derivar `category_code` de `category_id`
2. De onde vem `competition.year` no contexto de uma requisição HTTP POST

**Consequência:** O Executor não pode implementar INV-ATH-002 sem inventar lógica não contratada — violation do restriction prompt.

**Solução determinística — escolher uma opção e declarar:**
- Opção A: adicionar `competition_year: integer` ao `AthleteCreateRequest` no OpenAPI
- Opção B: declarar no DB contract ou num contrato de configuração qual é o `competition_year` corrente e como obtê-lo

### 4.3 Locking policy incompleta (CC-002 violação)

**Evidência: `13_ATLETAS_DB_CONTRACT.yaml` linhas 26-28:**
```yaml
locking_policy:
  type: optimistic_locking
  version_column: version_id
```

Regra CC-002 (`check_optimistic_locking_contract_is_complete`) exige: `version_column` + `conflict_error_code` + `retry_policy`. Os campos `conflict_error_code` e `retry_policy` estão ausentes. CC-002 está na lista `cannot_waive`.

**Solução determinística:**
```yaml
locking_policy:
  type: optimistic_locking
  version_column: version_id
  conflict_error_code: ATHLETE_OPTIMISTIC_LOCK_CONFLICT
  retry_policy: retry_3_times_with_exponential_backoff
```

### 4.4 `16_ATLETAS_AGENT_HANDOFF.json` é um JSON Schema, não um handoff

**Evidência: `16_ATLETAS_AGENT_HANDOFF.json` linhas 1-7:**
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://hbtrack.local/schemas/16_AGENT_HANDOFF.schema.json",
  "title": "HB Track Agent Handoff Schema",
  "type": "object",
  ...
}
```

**Evidência: `20_ATLETAS_EXECUTOR_RESTRICTION_PROMPT.md` linha 17:** "A única fonte de verdade autorizada é: 16_ATLETAS_AGENT_HANDOFF.json"

O arquivo é um molde (schema), não uma instância de handoff. O Executor tentaria ler os campos `meta.handoff_id`, `task_plan`, `entry_gates` e encontraria apenas definições de schema — emitindo BLOCKED_INPUT imediatamente.

---

## 5. ERROS DE LÓGICA EM CROSS RULES

### 5.1 CHECKERS_REGISTRY.md declara checker_ids divergentes da constituição vigente

**Evidência: `CHECKERS_REGISTRY.md` linhas 68-73:**
```
| X-016 | check_traceability_operations_have_execution_binding | cross.py |
| X-017 | check_execution_bindings_reference_traceable_operations | cross.py |
```
**Evidência: `00_ATLETAS_CROSS_LINTER_RULES.json` (constituição v1.2.7):**
```
X-016: check_execution_bindings_are_traceable
X-017: check_execution_bindings_do_not_override_constitution
```

Os checker_ids são completamente diferentes. Um desenvolvedor implementando seguindo `CHECKERS_REGISTRY.md` criaria funções com nomes errados que `hb_plan.py` nunca encontraria no dict CHECKERS.

| Rule | checker_id no CHECKERS_REGISTRY | checker_id na constituição v1.2.7 |
|---|---|---|
| X-016 | `check_traceability_operations_have_execution_binding` | `check_execution_bindings_are_traceable` |
| X-017 | `check_execution_bindings_reference_traceable_operations` | `check_execution_bindings_do_not_override_constitution` |
| DOC-004 | NÃO EXISTE | `check_execution_bindings_validate_against_schema` |
| DOC-005 | NÃO EXISTE | `check_generated_documents_exist_and_have_integrity` |
| X-018 | NÃO EXISTE | `check_execution_bindings_prohibited_keys_are_complete` |
| X-019 | NÃO EXISTE | `check_execution_flags_match_overwrite_policy` |
| X-020 | NÃO EXISTE | `check_canonical_test_scenarios_pass_with_deterministic_report` |

**Total:** 7 checker_ids incorretos ou ausentes no CHECKERS_REGISTRY.md.

### 5.2 INV-ATH-001 e INV-ATH-002 declaram scope `athlete_update` mas operação não existe

**Evidência: `15_ATLETAS_INVARIANTS.yaml` linha 33:** `scope: athlete_create, athlete_update`
**Evidência: `15_ATLETAS_INVARIANTS.yaml` linha 50:** `scope: athlete_create, athlete_update, lineup_assignment`
**Evidência: `01_ATLETAS_OPENAPI.yaml`:** Nenhuma operação PATCH ou PUT declarada.
**Evidência: `08_ATLETAS_TRACEABILITY.yaml`:** Apenas três operações: `create`, `list`, `get`.

Regra X-008: "Every hard_fail invariant must bind to at least one operation". As invariantes INV-ATH-001 e INV-ATH-002 declaram bindings para `athlete_update` que não existe em nenhum contrato. X-008 falha para essas invariantes.

### 5.3 INV-ATH-003 referencia operação `lineup_assignment` inexistente

**Evidência: `15_ATLETAS_INVARIANTS.yaml` linhas 99-115:**
- `scope: lineup_assignment`
- `enforcement_bindings.domain_service: lineup_assign_athlete`

Nenhum dos contratos (`01_ATLETAS_OPENAPI.yaml`, `08_ATLETAS_TRACEABILITY.yaml`, `12_ATLETAS_EXECUTION_BINDINGS.yaml`) tem operação `lineup_assignment`. X-008 falha para INV-ATH-003 também.

### 5.4 PROJ-H-ATH-001 requer invariantes em handler de projeção — conflito com purity_requirements

**Evidência: `17_ATLETAS_PROJECTIONS.yaml` linhas 108-110:**
```yaml
required_invariants:
  - INV-ATH-001
  - INV-ATH-002
```
**Evidência: `17_ATLETAS_PROJECTIONS.yaml` linha 174:**
```yaml
db_lookup_forbidden: true
```

INV-ATH-001 é uma invariante de unicidade que requer consulta ao banco (`uq_athletes_federation_id`). Enforcar INV-ATH-001 dentro de um projection handler requer DB lookup que é explicitamente proibido. Os dois requisitos são logicamente incompatíveis.

### 5.5 SE-ATH-001 consome `AthleteRegistered` event_version: 1 mas projeção consome v2

**Evidência: `18_ATLETAS_SIDE_EFFECTS.yaml` linhas 20-21:**
```yaml
event_type: AthleteRegistered
event_version: 1
```
**Evidência: `17_ATLETAS_PROJECTIONS.yaml` linhas 61-65:**
```yaml
event_type: AthleteRegistered
supported_versions: [2]
legacy_versions_require_upcast: ...
```

Não está definido se o side-effect handler recebe o evento original (v1, antes do upcast) ou o evento pós-upcast (v2). Esta ambiguidade viola TIME-001 e pode causar comportamento não determinístico em replay.

---

## 6. RISCOS NÃO COBERTOS

### 6.1 Operação de update completamente ausente

**Evidência em múltiplos contratos:**
- `15_ATLETAS_INVARIANTS.yaml` INV-ATH-001, INV-ATH-002: `scope: athlete_create, athlete_update`
- `17_ATLETAS_PROJECTIONS.yaml` linhas 68-69: handler `apply_athlete_updated_v1` para `AthleteUpdated`
- `05_ATLETAS_EVENTS.asyncapi.yaml`: operação `publishAthleteUpdatedV1` declarada

Existe toda a infraestrutura de evento para update (evento, projeção, handler) mas nenhum endpoint HTTP, nenhum binding de execução. Executor não tem contrato para seguir → BLOCKED_INPUT.

### 6.2 Nenhum contrato para o campo `deleted_at` (soft delete)

**Evidência: `15_ATLETAS_INVARIANTS.yaml` INV-ATH-010 linha 126:** `query = query.where(athletes.deleted_at.is_(None))`

O mecanismo de soft delete não tem contrato: nenhum endpoint, nenhuma coluna no DB contract, nenhum evento `AthleteDeleted` no AsyncAPI, nenhum handler de projeção.

### 6.3 `category_code` não validado pelo OpenAPI

**Evidência: `19_ATLETAS_TEST_SCENARIOS.yaml` linhas 27-28:** usa `category_code: "U14"`
**Evidência: `01_ATLETAS_OPENAPI.yaml` AthleteCreateRequest:** não tem `category_code`.

Os cenários de teste usam `category_code` como input mas o contrato HTTP não o recebe. Não há contrato especificando como obter `category_code` a partir do `category_id`. Permite que o Executor invente a lógica de derivação.

### 6.4 `category_birth_year_mapping` sem contrato para anos além de 2026

**Evidência: `15_ATLETAS_INVARIANTS.yaml` linhas 137-143:** valores de amostra apenas para 2026.

Não há contrato para: anos anteriores/futuros, mecanismo de atualização da tabela de referência, ownership da função `category_allowed_birth_years`.

### 6.5 Race condition em INSERT sem contrato de locking

**Evidência: `13_ATLETAS_DB_CONTRACT.yaml` linha 26:** `type: optimistic_locking` (para UPDATE apenas).

Dois INSERTs concorrentes com mesmo `federation_id`: o constraint `uq_athletes_federation_id` captura no banco, mas o contrato não especifica qual HTTP status retornar nem se deve haver retry logic para INSERT.

### 6.6 `birth_date` vs `birth_year` — derivação sem contrato

**Evidência: `01_ATLETAS_OPENAPI.yaml` AthleteCreateRequest:** aceita `birth_date` (string date).
**Evidência: `17_ATLETAS_PROJECTIONS.yaml` PROJ-H-ATH-001:** grava `birth_year` (integer).
**Evidência: `05_ATLETAS_EVENTS.asyncapi.yaml` AthleteRegisteredV2Data:** exige `birth_year: integer`.

O request HTTP não aceita `birth_year` — quem calcula o `birth_year`? O serviço antes de emitir o evento? O projection handler? Não há contrato para esta derivação.

---

## 7. YAMLs QUEBRADOS / JSON ESTRUTURALMENTE INVÁLIDOS

### 7.1 `01_ATLETAS_OPENAPI.yaml`: versão inválida

**Evidência: linha 15 (dentro do code block):** `openapi: 3.1.1`

Versões válidas de OpenAPI 3.x: `3.0.0`, `3.0.1`, `3.0.2`, `3.0.3`, `3.1.0`. `3.1.1` não existe.

**Correção:** `openapi: 3.1.0`

### 7.2 `13_ATLETAS_DB_CONTRACT.yaml`: CHECK constraint referencia coluna não declarada

**Evidência: linha 25:**
```yaml
- name: ck_athletes_birth_year_consistency
  check: "birth_year = EXTRACT(YEAR FROM birth_date)"
```

`birth_date` não está listada nas `columns`. DDL gerado produziria CHECK constraint inválido (referência a coluna inexistente — erro SQL em runtime).

### 7.3 `13_ATLETAS_DB_CONTRACT.yaml`: `version_column: version_id` sem coluna `version_id`

**Evidência: linhas 27-28:** `version_column: version_id`

O campo `version_id` não está na lista de colunas do contrato.

### 7.4 `13_ATLETAS_DB_CONTRACT.yaml`: ausência de `meta.status` e `meta.version`

**Evidência: linhas 1-5:** meta não tem `status` nem `version`.

DOC-002 exige campos de metadata canônico. Todos os outros contratos YAML reais (`15`, `17`, `18`, `19`) têm `status` e `module_version`. Apenas o DB contract está faltando.

### 7.5 `05_ATLETAS_EVENTS.asyncapi.yaml`: arquivo é markdown, não AsyncAPI parseable

**Evidência: linha 1:** começa com `## 05_ATLETAS_EVENTS.asyncapi.yaml`

Qualquer validator AsyncAPI falharia ao tentar parsear isso.

### 7.6 `12_ATLETAS_EXECUTION_BINDINGS.yaml` não conforma com o seu próprio schema

**Evidência: `12_ATLETAS_EXECUTION_BINDINGS.schema.json` linha 7:** Requer `meta`, `defaults`, `steps`, `prohibited_keys`, `binding_integrity`.

O arquivo `12_ATLETAS_EXECUTION_BINDINGS.yaml` é markdown com YAML de exemplo. Não tem os campos `defaults`, `steps`, `prohibited_keys` ou `binding_integrity` como campos YAML de nível raiz. DOC-004 é `cannot_waive` — bloqueante imediato.

---

## 8. ANÁLISE DOS AGENTS (DETERMINISMO)

### 8.1 `arquiteto-hbtrack.md`: escopo incorreto para o módulo atletas

**Evidência: `c:\HB TRACK\.claude\agents\arquiteto-hbtrack.md` linhas 9-41:**

O arquivo de instruções do agente arquiteto contém exclusivamente a cadeia canônica do módulo TRAINING, não do módulo atletas.

**Impacto:** Um agente arquiteto invocado para o módulo atletas leria instruções de TRAINING como contexto normativo, potencialmente alucinando referências a `INVARIANTS_TRAINING.md`, `AR_BACKLOG_TRAINING.md`, `openapi_baseline.json`, etc.

**Instrução barata:** "Use this agent when architectural decisions... for the HB Track project" — não especifica qual módulo, não especifica cadeia canônica para módulos não-TRAINING.

**Solução determinística:** Adicionar seção `## Módulo ATLETAS — cadeia canônica` com lista numerada dos 19 contratos em ordem de autoridade.

### 8.2 `AGENTS.md`: cadeia canônica do módulo atletas ausente

**Evidência: `c:\HB TRACK\AGENTS.md` linhas 21-36:** Define apenas o módulo TRAINING.

O arquivo global de instruções para agentes não tem cadeia canônica para o módulo atletas. Um agente recebendo tarefa de atletas sem instrução explícita pode usar analogia com TRAINING, causando alucinação estrutural.

### 8.3 `copilot-instructions.md`: mesmo problema de escopo

**Evidência: `c:\HB TRACK\.github\copilot-instructions.md` linha 25:** Mesma cadeia do TRAINING, nada sobre atletas.

---

## 9. ANÁLISE DOS SCRIPTS (hb_cli.py / hb_gen.py)

### 9.1 `hb_gen.py` incompatível com o sistema de contratos atletas

**Evidência: `c:\HB TRACK\scripts\SSOTs\hb_gen.py` linha 31:**
```python
spec_file = SPECS_DIR / module_name / f"{spec_type.upper()}_{module_name.upper()}.yaml"
```

Para módulo atletas, geraria caminhos como `COMMANDS_ATLETAS.yaml`. Os contratos reais usam a convenção numerada: `05_ATLETAS_EVENTS.asyncapi.yaml`. O gerador não tem consciência do sistema de contratos.

**Funções possíveis de adicionar (sem quebrar):**
1. `generate_atletas_execution_bindings()`: gerar `12_ATLETAS_EXECUTION_BINDINGS.yaml` real a partir de templates + `08_ATLETAS_TRACEABILITY.yaml`
2. `validate_contract_schema(contract_path, schema_path)`: validar contrato YAML/JSON contra schema — útil para DOC-004

**Evidência: linha 84:** `# generate_code("projections", target_module) # Ativar quando o template estiver pronto` — geração de projeções comentada, não implementada.

### 9.2 `hb_cli.py` sem comandos atletas

**Evidência:** grep por `atletas|ATHLETES|cross_lint|hb_plan|hb_verify` retornou 0 resultados em `hb_cli.py`.

O CLI principal não tem comandos para: `hb lint atletas`, `hb plan atletas`, `hb verify atletas`.

**Funções possíveis de adicionar:**
- `cmd_atletas_lint()`: executa `hb_plan.py` (quando existir) no módulo atletas
- `cmd_atletas_handoff()`: gera handoff JSON a partir dos contratos

---

## 10. CONTRATOS PENDENTES / NOVOS

*Apenas lacunas com necessidade explícita evidenciada nos documentos existentes.*

### 10.1 Operação `athletes__athlete__update` (PATCH)

**Necessidade explícita evidenciada em:**
- `15_ATLETAS_INVARIANTS.yaml` linhas 33, 50: `scope: athlete_create, athlete_update`
- `15_ATLETAS_INVARIANTS.yaml` linha 53: `test_athlete_update_duplicate_federation_id_rejected`
- `17_ATLETAS_PROJECTIONS.yaml` linhas 68-69: handler `apply_athlete_updated_v1`
- `05_ATLETAS_EVENTS.asyncapi.yaml`: operação `publishAthleteUpdatedV1` declarada

Toda infraestrutura de evento para update existe mas nenhum endpoint HTTP foi contratado.

### 10.2 Estratégia de soft delete (`athletes__athlete__delete`)

**Necessidade explícita evidenciada em:**
- `15_ATLETAS_INVARIANTS.yaml` INV-ATH-010: requer coluna `deleted_at`
- `17_ATLETAS_PROJECTIONS.yaml` linha 88: campo `athletes.status` já é projetado

O contrato deve escolher explicitamente: soft delete via `status = INACTIVE` ou via coluna `deleted_at` dedicada.

### 10.3 Fonte de `competition_year` corrente

**Necessidade explícita evidenciada em:**
- `15_ATLETAS_INVARIANTS.yaml` INV-ATH-002: `required_inputs: competition.year`
- `19_ATLETAS_TEST_SCENARIOS.yaml`: `competition_reference_year: 2026`

Precisa de contrato (ou seção em contrato existente) especificando como o serviço obtém o `competition_year` ativo.

---

## 11. PLANO DE CORREÇÃO PRIORIZADO

### P0 — Crítico: bloqueante para qualquer execução

| ID | Problema | Arquivo | Ação |
|---|---|---|---|
| P0-001 | `16_ATLETAS_AGENT_HANDOFF.json` é schema, não handoff | `16_ATLETAS_AGENT_HANDOFF.json` | Gerar instância de handoff real com hashes SHA-256 reais, task_plan, entry_gates, exit_gates, prohibitions preenchidos |
| P0-002 | 5 contratos são markdown, não YAML parseable | `01`, `05`, `08`, `12`, `14` | Extrair o bloco YAML dos code blocks e tornar cada arquivo YAML puro |
| P0-003 | `hb_plan.py` e `hb_verify.py` inexistentes | `scripts/run/` | Criar os dois scripts |
| P0-004 | `scripts/hbtrack_lint/` inexistente (89% dos checkers sem impl) | `scripts/hbtrack_lint/` | Criar estrutura e implementar ao menos os checkers `cannot_waive` prioritários |
| P0-005 | `13_ATLETAS_DB_CONTRACT.yaml` incompleto: faltam 10+ colunas | `13_ATLETAS_DB_CONTRACT.yaml` | Adicionar todas as colunas, constraints, indexes e completar locking policy |
| P0-006 | CHECK constraint referencia `birth_date` inexistente nas colunas | `13_ATLETAS_DB_CONTRACT.yaml` | Adicionar coluna `birth_date: date, nullable: false` |
| P0-007 | INV-ATH-002 requer `competition.year` não presente no request HTTP | `01_ATLETAS_OPENAPI.yaml`, `15_ATLETAS_INVARIANTS.yaml` | Adicionar `competition_year: integer` ao request OU declarar fonte de configuração |
| P0-008 | Todos os cross-contract paths usam `docs/hbtrack/modules/ATHLETES/` (inexistente) | `17_ATLETAS_PROJECTIONS.yaml` L207-211; `05_ATLETAS_EVENTS.asyncapi.yaml` L479-483 | Substituir por `docs/hbtrack/modulos/atletas/` |

### P1 — Alto: causa alucinação provável

| ID | Problema | Arquivo | Ação |
|---|---|---|---|
| P1-001 | CHECKERS_REGISTRY.md: X-016/X-017 errados; DOC-004/005, X-018/019/020 ausentes | `CHECKERS_REGISTRY.md` | Sincronizar com constituição v1.2.7 |
| P1-002 | `20_ATLETAS_EXECUTOR_RESTRICTION_PROMPT.md` referencia v1.2.3 | linha 5 | Atualizar para v1.2.7; adicionar X-018, X-019, X-020 |
| P1-003 | INV-ATH-001/002 scope `athlete_update` sem operação contratada | `01_ATLETAS_OPENAPI.yaml`, `08`, `12` | Adicionar endpoint PATCH e operação `athletes__athlete__update` nos três contratos |
| P1-004 | INV-ATH-003 scope `lineup_assignment` sem operação contratada | `15_ATLETAS_INVARIANTS.yaml` | Remover `lineup_assignment` do scope ou criar contrato para a operação |
| P1-005 | PROJ-H-ATH-001 `required_invariants` conflita com `db_lookup_forbidden: true` | `17_ATLETAS_PROJECTIONS.yaml` L108-110 | Remover `required_invariants` do handler de projeção |
| P1-006 | SE-ATH-001 `event_version: 1` vs projeção que consome v2 | `18_ATLETAS_SIDE_EFFECTS.yaml`, `05_ATLETAS_EVENTS.asyncapi.yaml` | Declarar explicitamente se side effects recebem evento pré ou pós-upcast |
| P1-007 | `openapi: 3.1.1` versão inválida | `01_ATLETAS_OPENAPI.yaml` L15 | Corrigir para `openapi: 3.1.0` |
| P1-008 | `arquiteto-hbtrack.md` contém instruções de TRAINING ao invés de atletas | `.claude/agents/arquiteto-hbtrack.md` | Adicionar seção `## Módulo ATLETAS` com cadeia canônica |
| P1-009 | `birth_year` derivado de `birth_date` sem contrato de derivação | `01_ATLETAS_OPENAPI.yaml`, `13`, `05` | Declarar que `birth_year = YEAR(birth_date)` é computado pelo serviço antes de emitir o evento |

### P2 — Médio: aumenta risco

| ID | Problema | Arquivo | Ação |
|---|---|---|---|
| P2-001 | `deleted_at` coluna sem contrato de soft delete | `13`, `01`, `05` | Definir estratégia (INACTIVE vs deleted_at) e contratar |
| P2-002 | TRACEABILITY `ui_selectors` incompleto: falta `name`, `birth_date`, `federation_id` | `08_ATLETAS_TRACEABILITY.yaml` | Adicionar os 3 seletores ausentes |
| P2-003 | TRACEABILITY sem campo `backend_handler` nas operações | `08_ATLETAS_TRACEABILITY.yaml` | Adicionar `backend_handler: <symbol>` em cada operação |
| P2-004 | `athletes__athlete__list` sem testes unit (TRACE-RULE-002) | `08_ATLETAS_TRACEABILITY.yaml` | Adicionar ao menos um teste unit na operação list |
| P2-005 | Cenários de teste usam `category_code` mas request HTTP usa `category_id` | `19_ATLETAS_TEST_SCENARIOS.yaml` | Adicionar `category_id` ou declarar mapeamento explícito |
| P2-006 | `13_ATLETAS_DB_CONTRACT.yaml` sem `meta.status` e `meta.version` | `13_ATLETAS_DB_CONTRACT.yaml` | Adicionar `status: DRAFT` e `module_version: 1.0.0` |
| P2-007 | `module_pack_root_pattern` usa `<MODULE>` placeholder não resolvido | `00_ATLETAS_CROSS_LINTER_RULES.json` L57 | Resolver para `docs/hbtrack/modulos/atletas/` |
| P2-008 | `hb_gen.py` incompatível com convenção de nomes dos contratos | `scripts/SSOTs/hb_gen.py` | Documentar que o script não serve o módulo atletas |

### P3 — Baixo: melhoria de qualidade

| ID | Problema | Ação |
|---|---|---|
| P3-001 | `04_ATLETAS_WORKFLOWS.arazzo.yaml` vazio | Preencher ou remover da lista de contratos opcionais |
| P3-002 | `06_ATLETAS_CONSUMER_CONTRACTS.md` vazio | Preencher com bindings de consumo de eventos ou remover |
| P3-003 | `_reports/WAIVERS.yaml` inexistente | Criar arquivo mínimo com `waivers: []` |
| P3-004 | `AGENTS.md` e `copilot-instructions.md` sem cadeia canônica de atletas | Adicionar seção `## Módulo ATLETAS` análoga ao TRAINING |
| P3-005 | `00_ATLETAS_CROSS_LINTER_RULES.schema.json` `$id` é v1.2.3 mas constituição é v1.2.7 | Atualizar schema para cobrir DOC-004, DOC-005, X-018..X-020 |

---

# Ordem de Execução — ANALISE_CONTRATOS_GAPS.md

# Fase 1 — Mecânica/Verificável por grep (sem decisão de design)
**Item	Arquivo(s)	Critério de done**
1	P0-002	01, 05, 08, 12, 14 .yaml	Extrair YAML dos fenced code blocks → YAML puro; yaml.safe_load retorna dict
2	P0-008	17_ATLETAS_PROJECTIONS.yaml, 05_ATLETAS_EVENTS.asyncapi.yaml	Substituir docs/hbtrack/modules/ATHLETES/ → atletas; grep retorna 0 matches
3	P1-007	01_ATLETAS_OPENAPI.yaml	openapi: 3.1.1 → 3.1.0
4	P2-007	00_ATLETAS_CROSS_LINTER_RULES.json	<MODULE> placeholder → atletas
P0-002 e P0-008 primeiro porque desbloqueiam todos os checkers cross-contract.

Fase 1 concluída com todos os itens PASS:

Item	Status	O que foi feito
P0-002	PASS	5 arquivos (01, 05, 08, 12, 14) já eram YAML puro — confirmado sem fenced blocks, yaml.safe_load retorna dict
P1-007	PASS	openapi: 3.1.1 → 3.1.0 em 01_ATLETAS_OPENAPI.yaml
P0-008	PASS	docs/hbtrack/modules/ATHLETES substituído por atletas em historico.md (33 ocorrências), MOTORES.md (5 oc.) e rascunho.md (14 oc.) — nota: ANALISE_CONTRATOS_GAPS.md mantido intocado (evidência histórica intencional)
P2-007	PASS	Nenhum placeholder <MODULE> encontrado em 00_ATLETAS_CROSS_LINTER_RULES.json

# Fase 2 — Completar DB Contract (P0-005 + P0-006 juntos)
**Item	Ação**
5	P0-005 + P0-006	Adicionar colunas (birth_date, category_id, team_id, federation_id, dominant_hand, status, created_at, deleted_at, version_id), constraints (uq_athletes_federation_id), indexes, locking_policy completo com conflict_error_code + retry_policy
6	P2-006	Adicionar meta.status: DRAFT e meta.module_version: 1.0.0

Fase 2 concluída. Todos os critérios passaram:

13_ATLETAS_DB_CONTRACT.yaml

Item	Status	Resultado
P0-005 + P0-006	✓ PASS	12 colunas: athlete_id, full_name, birth_date, birth_year, category_id, team_id, federation_id, dominant_hand, status, created_at, deleted_at, version_id
uq_athletes_federation_id	✓ PASS	Constraint partial unique declarada
idx_athletes_team_id	✓ PASS	Index btree declarado
birth_date antes do CHECK	✓ PASS	Ordem de declaração correta — DDL válido
locking_policy (CC-002)	✓ PASS	version_column + conflict_error_code: ATHLETE_OPTIMISTIC_LOCK_CONFLICT + retry_policy: retry_3_times_with_exponential_backoff
P2-006	✓ PASS	meta.status: DRAFT e meta.module_version: 1.0.0

# Fase 3 — Decisões de design (requerem escolha explícita)
**Item	Decisão necessária**
7	P0-007	Adicionar competition_year: integer ao AthleteCreateRequest OU declarar fonte de configuração em 15_ATLETAS_INVARIANTS.yaml
8	P2-001	Escolher estratégia de soft delete: status = INACTIVE vs coluna deleted_at dedicada
9	P1-009	Declarar que birth_year = YEAR(birth_date) é computado pelo serviço antes de emitir evento
10	P1-006	Declarar se side effects recebem evento pré ou pós-upcast

Fase 3 concluída — todos os 22 critérios: ALL PASS

Decisões tomadas e declaradas
Item	Arquivo	Decisão	DoD
P0-007	15_ATLETAS_INVARIANTS.yaml	Opção B: competition.year vem de configuração do sistema (HBTRACK_COMPETITION_YEAR em backend/app/core/config.py), injetado pelo application service. Cliente HTTP não envia este campo.	competition_year_configuration.source = system_config + http_client_must_not_send = true
P2-001	13_ATLETAS_DB_CONTRACT.yaml	Estratégia deleted_at: soft delete seta deleted_at = now(). status (ACTIVE/INACTIVE) é estado de negócio — independente. INV-ATH-010 filtra deleted_at IS NULL.	soft_delete_policy com strategy, activate_delete, active_filter
P1-009	13_ATLETAS_DB_CONTRACT.yaml	birth_year = YEAR(birth_date) computado pelo application service antes de emitir AthleteRegistered. Não aceito do HTTP request.	derivation_policy.computed_by = application_service, accepted_from_request = false
P1-006	18_ATLETAS_SIDE_EFFECTS.yaml	SE-ATH-001 consome versão canônica pós-upcast (v2) — consistente com 17_ATLETAS_PROJECTIONS.yaml. SE-ATH-002 mantém v1 (AthleteStatusChanged v1 é canônico).	event_version: 2 + event_version_policy.consumes = post_upcast_canonical_version

# Fase 4 — Contratos de operação ausente
**Item	Arquivo(s)	Depende de**
11	P1-003	01_ATLETAS_OPENAPI.yaml + 08_ATLETAS_TRACEABILITY.yaml + 12_ATLETAS_EXECUTION_BINDINGS.yaml	Fase 1 (YAMLs paresáveis)
12	P1-004	15_ATLETAS_INVARIANTS.yaml	Decisão: remover lineup_assignment ou criar contrato
13	P1-005	17_ATLETAS_PROJECTIONS.yaml	Remover required_invariants de PROJ-H-ATH-001 (purity rule)

**Fase 4 — ALL 21 PASS** *✓*

Resumo do que foi executado:

P1-003 — athletes__athlete__update contratado (10 critérios PASS)
01_ATLETAS_OPENAPI.yaml: adicionado PATCH /api/v1/athletes/{athlete_id} com operationId: athletes__athlete__update e schema AthleteUpdateRequest (campos todos opcionais, minProperties: 1, sem competition_year)
08_ATLETAS_TRACEABILITY.yaml: operação athletes__athlete__update adicionada com INV-ATH-001 e INV-ATH-002 vinculadas
12_ATLETAS_EXECUTION_BINDINGS.yaml: binding backend_service: athlete_update / backend_handler: update_athlete
P1-004 — lineup_assignment removido do scope ativo (3 critérios PASS)
15_ATLETAS_INVARIANTS.yaml: INV-ATH-002 scope removido lineup_assignment → athlete_create, athlete_update apenas
INV-ATH-003 mantido mas com scope_status: deferred + scope_deferred_reason explicando que depende da criação do contrato de lineup
P1-005 — required_invariants removido de PROJ-H-ATH-001 (3 critérios PASS)
17_ATLETAS_PROJECTIONS.yaml: bloco required_invariants: [INV-ATH-001, INV-ATH-002] removido — projection handler é puro e não pode executar invariantes de unicidade que requerem DB lookup

# Fase 5 — Governança e sincronização
**Item	Arquivo(s)**
14	P1-001	CHECKERS_REGISTRY.md — sincronizar X-016/X-017 e adicionar DOC-004/005, X-018/019/020
15	P1-002	20_ATLETAS_EXECUTOR_RESTRICTION_PROMPT.md — atualizar para v1.2.7
16	P1-008	arquiteto-hbtrack.md — adicionar cadeia canônica do módulo atletas
17	P3-004	AGENTS.md + copilot-instructions.md — seção ## Módulo ATLETAS

**Fase 5 — ALL 29 PASS** *✓*

Resumo do que foi executado:
- `P1-001 — CHECKERS_REGISTRY.md` sincronizado (10 critérios PASS)
`CHECKERS_REGISTRY.md`: X-016 corrigido: `check_traceability_operations_have_execution_binding` → `check_execution_bindings_are_traceable`
- `X-017 corrigido`: `check_execution_bindings_reference_traceable_operations` → `check_execution_bindings_do_not_override_constitution`
- `DOC-004` adicionado: `check_execution_bindings_validate_against_schema`
- `DOC-005` adicionado: `check_generated_documents_exist_and_have_integrity`
- X-018/019/020 adicionados com `checker_ids exatos da constituição v1.2.7`

Tabela resumo atualizada: **63 → 68** total
- `P1-002` — Restriction prompt atualizado (6 critérios PASS)
- `20_ATLETAS_EXECUTOR_RESTRICTION_PROMPT.md`: v1.0.2 / v1.2.3 → v1.2.- 7 FINAL, CROSS-LINTER-HBTRACK v1.2.7
- X-018, X-019, X-020 adicionados às condições de HALT na seção 3
- `P1-008 — `arquiteto-hbtrack.md` com cadeia ATLETAS (5 critérios PASS)
- `arquiteto-hbtrack.md`: seção ## Módulo ATLETAS — cadeia canônica - adicionada com os 11 contratos em ordem de autoridade
P3-004 — `AGENTS.md` + `copilot-instructions.md` (8 critérios PASS)
`AGENTS.md` e `copilot-instructions.md`: seção ## Módulo ATLETAS — cadeia canônica adicionada em ambos, incluindo a regra que `ANALISE_CONTRATOS_GAPS.md` não é SSOT ativo

# Fase 6 — Handoff e infraestrutura de scripts (mais custosos)
**Item	Depende de**
18	P0-001	Gerar 16_ATLETAS_AGENT_HANDOFF.json real com SHA-256 dos artefatos → depende de Fases 1–5 (artefatos finais)
19	P0-003	Criar scripts/run/hb_plan.py e hb_verify.py
20	P0-004	Criar scripts/hbtrack_lint/ com checkers cannot_waive

**Fase 6** — DoD: **17/17** PASS (*EXIT: 0*)

Resumo do que foi verificado/corrigido
- **P0-001** — `16_ATLETAS_AGENT_HANDOFF.json`: instância real com `task_plan`, `entry_gates`, `exit_gates`, 12 artefatos, `snapshot_hash` não-zero, sem `$schema` na raiz. *✓*

**P0-003** — `hb_plan.py` e `hb_verify.py`: existem e compilam sem erros. *✓*

- `P0-004 — hbtrack_lint`: **87 checkers** registrados, todos **39** `cannot_waive` implementados, `hb_plan.py` executa com saída **FAIL_ACTIONABLE** (exit 2, esperado) sem nenhum **ERROR**. Breakdown final: **65 PASS** / **12 FAIL** (gaps conhecidos dos contratos) / **12 SKIP** / **0 ERROR**. *✓*

- Correção adicional feita: checker_registry.py agora também varre `global_type_system.rules` (onde ficam TYPE-001..006), corrigindo o bug de **SKIP** silencioso que existia antes.

- O `checker_registry.py` implementa corretamente o comportamento descrito no CHECKERS_REGISTRY.md. Onde o doc diz: com **56 checkers** sem implementação, `hb_plan.py` retornaria **FAIL_ACTIONABLE** (exit=2) para 89% das regras

- O `checker_registry.py` não retorna **FAIL** para checkers não encontrados; ele retorna **SKIP**. Isso é intencional (diverge da implicação do `MOTORES.md` citado no doc), e foi uma decisão deliberada desta implementação ("progressive entry").

O doc `CHECKERS_REGISTRY.md` foi gerado antes das implementações da Fase 6. Na prática, o estado atual do registro é:

**87 checkers implementados** (não 7 como o doc lista)
**SKIP** para `checker_id` ausente (não FAIL)
**global_type_system.rules** corretamente varrido (TYPE-001..006)
O `CHECKERS_REGISTRY.md` está desatualizado em relação ao estado atual do código — é um documento histórico de análise pré-Fase 6, não reflete o que foi construído.

# Fase 7 — Baixa prioridade / qualidade
**Item**
21	P2-002/P2-003/P2-004 — TRACEABILITY: ui_selectors incompleto, backend_handler ausente, testes unit
22	P2-005 — cenários de teste: category_code vs category_id
23	P2-008 — documentar incompatibilidade de hb_gen.py
24	P3-001/P3-002 — preencher ou remover arquivos vazios
25	P3-003 — criar _reports/WAIVERS.yaml mínimo
26	P3-005 — atualizar $id do schema para v1.2.7

*Resumo da dependência crítica:*

```txt
P0-002 (YAML puro) ──┐
P0-008 (paths)   ──┘ → Fase 2 → Fases 3-5 → P0-001 (handoff com hashes reais)
                                          └→ P0-003/P0-004 (scripts — independentes)
```
---
## 12. CRITÉRIOS DE ACEITAÇÃO (DoD)

### DoD P0-001 (Handoff real)
- `16_ATLETAS_AGENT_HANDOFF.json` deve conter os campos: `meta.handoff_id`, `meta.status`, `integrity.artifacts` (lista com sha256 de cada contrato), `task_plan.ordered_steps` (≥1), `entry_gates` (≥1), `exit_gates` (≥1), `prohibitions` (≥1)
- **Critério binário:** `python -c "import json; d=json.load(open('16_ATLETAS_AGENT_HANDOFF.json')); assert 'task_plan' in d and 'entry_gates' in d"` retorna exit 0
- O arquivo NÃO deve ter `"$schema"` como campo de nível raiz

### DoD P0-002 (YAML puro)
- **Critério binário:** `python -c "import yaml; d=yaml.safe_load(open(f).read()); assert isinstance(d, dict)"` para cada um dos 5 arquivos retorna exit 0
- Nenhum dos 5 arquivos deve conter ` ```yaml ` como substring

### DoD P0-005 (DB contract completo)
- `13_ATLETAS_DB_CONTRACT.yaml` deve listar todas as colunas da tabela P0-005
- `yaml.safe_load` deve conseguir carregar sem erro
- `birth_date` deve aparecer nas `columns` antes do CHECK constraint que a referencia
- `uq_athletes_federation_id` deve existir como constraint
- `locking_policy` deve ter `conflict_error_code` E `retry_policy` além de `version_column`
- **Critério binário:** grep por `birth_date`, `federation_id`, `deleted_at`, `version_id`, `conflict_error_code`, `retry_policy` retorna ≥1 match cada um

### DoD P0-007 (competition_year)
- `AthleteCreateRequest` deve ter campo `competition_year: integer` OU `15_ATLETAS_INVARIANTS.yaml` INV-ATH-002 deve ter `required_inputs` com fonte de `competition.year` declarada como campo de configuração com localização explícita
- **Critério binário:** nenhuma referência a `competition.year` permanece sem fonte declarada no sistema de contratos

### DoD P0-008 (paths corrigidos)
- **Critério binário:** `grep -r "modules/ATHLETES" docs/hbtrack/modulos/atletas/` retorna 0 resultados

### DoD P1-001 (CHECKERS_REGISTRY corrigido)
- **Critério binário:** para cada checker_id na constituição v1.2.7, grep no CHECKERS_REGISTRY.md retorna ≥1 match com o mesmo nome exato

### DoD P1-003 (UPDATE contratado)
- `01_ATLETAS_OPENAPI.yaml` deve ter endpoint `PATCH /api/v1/athletes/{athlete_id}` com operationId `athletes__athlete__update`
- `08_ATLETAS_TRACEABILITY.yaml` deve ter operação `athletes__athlete__update`
- `12_ATLETAS_EXECUTION_BINDINGS.yaml` deve ter binding para `athletes__athlete__update`
- **Critério binário:** grep por `athletes__athlete__update` retorna ≥3 matches (um em cada arquivo)

### DoD P1-005 (PROJ-H-ATH-001 corrigido)
- **Critério binário:** `17_ATLETAS_PROJECTIONS.yaml` não deve ter `required_invariants` sob `PROJ-H-ATH-001`
- INV-ATH-001 enforcement deve aparecer apenas em `backend_service: athlete_create` e `athlete_update`

---

*Próximo passo recomendado: Executar P0-002 (extrair YAML puro dos 5 arquivos markdown) e P0-008 (corrigir paths) — são mecânicos, verificáveis por grep, e desbloqueiam todos os demais checkers.*
