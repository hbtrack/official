# TRAINING_BATCH_PLAN_v1.md — Plano de Batches do Módulo TRAINING

Data: 2026-03-03
Versão: v1.3.0
Sync (pós-patch SSOT): `AR-TRAIN-010A/010B` + `AR-TRAIN-015`→`FLOW-TRAIN-008`.
Sync: Batch-6 adicionado — AR-TRAIN-010B desbloqueada (deps 001..009 VERIFICADAS 2026-03-01)
Sync: Batch-7 adicionado — AR-TRAIN-022 (Governança: sync INVARIANTS_TRAINING.md — deps 011..021 VERIFICADAS 2026-03-01)
Sync: Batch-8 adicionado — AR-TRAIN-023 (Governança: sync TEST_MATRIX §9 pós-Batch 7 — deps 001/002/010A/022 VERIFICADAS 2026-03-02)
Sync: Batches 9-11 adicionados — AR-TRAIN-024..031 (Fix FAILs críticos + Flow/Contract P0 evidence + Done Gate — planejado 2026-03-02)
Sync v1.1.0: Batches 12-16 adicionados — AR-TRAIN-032..043 (Cobertura §10 formal — decisão humana 2026-03-03)
Sync v1.2.0: Batch 17 adicionado — AR-TRAIN-044..047 (Fix FAILs test-layer Batch 13 — decisão humana Opção A 2026-03-03)
Sync v1.3.0: Batch 19 adicionado — AR-TRAIN-048 (Sincronização em Lote app layer — decisão humana 2026-03-03; GOVERNED_ROOTS.yaml UNLOCKED_FOR_SYNC_BATCH_19)

## SSOTs lidos (bindings)
- `docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md`
- `docs/hbtrack/modulos/treinos/TRAINING_FRONT_BACK_CONTRACT.md`
- `docs/hbtrack/modulos/treinos/TRAINING_USER_FLOWS.md`
- `docs/hbtrack/modulos/treinos/TRAINING_SCREENS_SPEC.md`
- `docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md`
- `docs/hbtrack/modulos/treinos/AR_BACKLOG_TRAINING.md`
- `docs/hbtrack/modulos/treinos/REPORT_TRAINING_DOCS_ASIS_TOBE.md` (input auxiliar; validado contra SSOTs acima)

## Definição de Done (módulo Treinos) — binding externo (humano)
Done do MÓDULO TREINOS = 100% INV/CONTRACT/FLOW/SCREEN sem GAP (ou seja: nenhum item com status GAP/PARCIAL/BLOQUEADO/DIVERGENTE/DEPRECATED; todos devem estar EVIDENCIADO/IMPLEMENTADO ou equivalente canônico).

---

## 1) Correções de rastreabilidade

### Correção de rastreabilidade: FLOW-TRAIN-016

#### 1.1 Re-localização (SSOT) + referências explícitas

**SSOT:** `docs/hbtrack/modulos/treinos/TRAINING_USER_FLOWS.md`

**(a) Screens referenciadas por FLOW-TRAIN-016**
- `SCREEN-TRAIN-022`

Evidência (trecho do SSOT):
```text
telas:
  - SCREEN-TRAIN-022 # /athlete/training/[sessionId]
```

**(b) Contracts referenciados por FLOW-TRAIN-016**
- `CONTRACT-TRAIN-096`
- `CONTRACT-TRAIN-105`

Evidência (trecho do SSOT):
```text
contratos:
  - CONTRACT-TRAIN-096 # GET /athlete/training-sessions/{session_id}/preview
  - CONTRACT-TRAIN-105 # GET /athlete/wellness-content-gate/{session_id}
```

**(c) Invariantes-chave referenciadas por FLOW-TRAIN-016**
- `INV-TRAIN-068`
- `INV-TRAIN-069`
- `INV-TRAIN-071`
- `INV-TRAIN-076`

Evidência (trecho do SSOT):
```text
invariantes_chave:
  - INV-TRAIN-068 # atleta vê treino antes
  - INV-TRAIN-069 # mídia acessível ao atleta
```

Evidência (trecho do SSOT):
```text
  - INV-TRAIN-071 # wellness missing bloqueia conteúdo completo
  - INV-TRAIN-076 # wellness obrigatório
evidencias: []
```

#### 1.2 Verificação de vínculo oficial FLOW-TRAIN-016 ↔ INV-TRAIN-054..056

**(b) Vínculo direto no SSOT do FLOW (TRAINING_USER_FLOWS.md):** não há referência a `INV-TRAIN-054..056` no bloco `invariantes_chave` do `FLOW-TRAIN-016` (apenas `INV-TRAIN-068/069/071/076`).

**Vínculo no SSOT do backlog (AR_BACKLOG_TRAINING.md):** existe associação explícita via `AR-TRAIN-015` apontando `INV-TRAIN-054..056` junto de `FLOW-TRAIN-008`.

Evidência (trecho do SSOT):
```text
| AR-TRAIN-015 | A/B | ALTA | Schema + Service ciclos hierarchy (macro→meso→micro) | INV-TRAIN-054..056, FLOW-TRAIN-008 | - | PENDENTE |
```

**CONTRADIÇÃO SSOT (rastreabilidade):** (pré-patch) `FLOW-TRAIN-016` não referenciava `INV-TRAIN-054..056` no SSOT de fluxos, mas o SSOT de backlog conectava esses itens via `AR-TRAIN-015`.  
**Ação (pós-patch):** DEC-TRAIN-FLOW-001 + patch em `AR_BACKLOG_TRAINING.md` (AR-TRAIN-015 agora referencia `FLOW-TRAIN-008`).

---

## 2) Batch Plan v1 (batches 0..5)

> Nota de método: este plano organiza o trabalho por batches usando **apenas** IDs e dependências já presentes nos SSOTs (principalmente `AR_BACKLOG_TRAINING.md` + `TEST_MATRIX_TRAINING.md`).  
> Onde houver dependência/associação ambígua entre SSOTs, o item aparece como risco/pendência de DEC/ADR.

### Batch 0 — P0 blockers (Step18 IDs + Wellness FE + Presenças UI) + início de desbloqueio de testes

**Objetivo:** atacar gaps P0 de paridade FE↔BE e iniciar remoção de bloqueios de teste por SSOT (`docs/_generated/*`).

**AR-TRAIN incluídas (SSOT):**
- `AR-TRAIN-001`
- `AR-TRAIN-003`
- `AR-TRAIN-005`
- `AR-TRAIN-010A`

**GAP-TRAIN cobertos (SSOT):**
- `GAP-TRAIN-001`
- `GAP-TRAIN-002`
- `GAP-TRAIN-004`
- `GAP-TRAIN-007`

**Itens alvo (IDs SSOT):**
- **INV:** `INV-TRAIN-014`, `INV-TRAIN-040`, `INV-TRAIN-041`
- **CONTRACT:** `CONTRACT-TRAIN-077..085`, `CONTRACT-TRAIN-029..039`, `CONTRACT-TRAIN-025..028`
- **FLOW:** `FLOW-TRAIN-005/006`, `FLOW-TRAIN-004`
- **SCREEN:** `SCREEN-TRAIN-018/019`, `SCREEN-TRAIN-020`

**DoD objetivo do batch (alinhado ao Done do módulo):**
- Todos os itens alvo acima deixam de estar em `GAP|PARCIAL|BLOQUEADO|DIVERGENTE|DEPRECATED` e passam a `EVIDENCIADO/IMPLEMENTADO` (ou equivalente canônico) nos SSOTs aplicáveis.
- `TEST_MATRIX_TRAINING.md` deixa de marcar como `BLOQUEADO` por `_generated` os itens em escopo (`INV-TRAIN-040/041`) e passa a ter evidência prevista/registrável.

**Non-scope (o que NÃO mexer):**
- Qualquer `AR-TRAIN-*` fora do escopo deste batch.
- Qualquer alteração de texto normativo em `INV-TRAIN-*` (apenas execução técnica/implementação fora desta etapa de planejamento).

**Riscos/Dependências (somente SSOT; senão “SEM EVIDÊNCIA NO SSOT”):**
- Dependência declarada (SSOT backlog): `AR-TRAIN-010B` depende de `AR-TRAIN-001..009`; `AR-TRAIN-010A` não declara dependências (ver evidência abaixo).

**Evidências (trechos SSOT):**
- `docs/hbtrack/modulos/treinos/AR_BACKLOG_TRAINING.md`
```text
| AR-TRAIN-001 | E | ALTA | Tipar IDs Step18 como UUID e alinhar contrato | CONTRACT-TRAIN-077..085, INV-TRAIN-014 | - | PENDENTE |
| AR-TRAIN-003 | D | ALTA | Corrigir Wellness FE (paths + payload schema + self-only sem athlete_id) | FLOW-TRAIN-005/006, SCREEN-TRAIN-018/019, CONTRACT-TRAIN-029..039 | - | PENDENTE |
| AR-TRAIN-005 | D | ALTA | Materializar UI de presenças (justified + batch) | FLOW-TRAIN-004, SCREEN-TRAIN-020, CONTRACT-TRAIN-025..028 | - | PENDENTE |
```

- `docs/hbtrack/modulos/treinos/AR_BACKLOG_TRAINING.md`
```text
| AR-TRAIN-010A | T | ALTA | Testes/Gates: migrar refs `_generated` → `docs/ssot` | INV-TRAIN-008/020/021/030/031/040/041, TEST_MATRIX_TRAINING | - | PENDENTE |
| AR-TRAIN-010B | T | ALTA | Testes de contrato/cobertura (workstream) | INV-TRAIN-013/024, CONTRACT-TRAIN-073..075, CONTRACT-TRAIN-077..085, TEST_MATRIX_TRAINING | AR-TRAIN-001..009 | PENDENTE |
```

- `docs/hbtrack/modulos/treinos/AR_BACKLOG_TRAINING.md`
```text
- **GAP-TRAIN-001:** IDs `int` em Step18 (`team_id`, `alert_id`, `suggestion_id`) divergem do DB `uuid` e impedem UI confiável.
  Alvos: `CONTRACT-TRAIN-077..085`, `INV-TRAIN-014`.
```

- `docs/hbtrack/modulos/treinos/AR_BACKLOG_TRAINING.md`
```text
- **GAP-TRAIN-002:** Wellness FE chama endpoints errados e formulário pré não está alinhado ao schema (sem `sleep_hours`, campos divergentes).
  Alvos: `SCREEN-TRAIN-018`, `CONTRACT-TRAIN-029..034`, `INV-TRAIN-002`.
```

- `docs/hbtrack/modulos/treinos/AR_BACKLOG_TRAINING.md`
```text
- **GAP-TRAIN-004:** UI de presenças não materializada; falta suporte a `justified` e semântica de `reason_absence` (DB).
  Alvos: `SCREEN-TRAIN-020`, `CONTRACT-TRAIN-025..028`, `INV-TRAIN-030`.
```

- `docs/hbtrack/modulos/treinos/AR_BACKLOG_TRAINING.md`
```text
- **GAP-TRAIN-007:** Testes invariants referenciam `docs/_generated/*` ao invés do SSOT atual `docs/ssot/*`.
  Alvos: `INV-TRAIN-040/041`, gates T.
```

---

### Batch 1 — Completar wellness self-only + tornar Step18 funcional (pós-IDs)

**Objetivo:** completar correções BE/contrato de wellness self-only e concluir materialização funcional do Step18.

**AR-TRAIN incluídas (SSOT):**
- `AR-TRAIN-002`
- `AR-TRAIN-004`

**GAP-TRAIN cobertos (SSOT):**
- `GAP-TRAIN-003`

**Itens alvo (IDs SSOT):**
- **INV:** `INV-TRAIN-014`, `INV-TRAIN-023`, `INV-TRAIN-002`, `INV-TRAIN-003`, `INV-TRAIN-026`
- **CONTRACT:** `CONTRACT-TRAIN-029..039`
- **FLOW:** `FLOW-TRAIN-005/006`

**DoD objetivo do batch (alinhado ao Done do módulo):**
- Todos os itens alvo acima deixam de estar em `GAP|PARCIAL|BLOQUEADO|DIVERGENTE|DEPRECATED` e passam a `EVIDENCIADO/IMPLEMENTADO` (ou equivalente canônico) nos SSOTs aplicáveis.

**Non-scope (o que NÃO mexer):**
- Qualquer `AR-TRAIN-*` fora do escopo deste batch.

**Riscos/Dependências (somente SSOT; senão “SEM EVIDÊNCIA NO SSOT”):**
- Dependência declarada: `AR-TRAIN-002` depende de `AR-TRAIN-001`.
- Dependência declarada: `AR-TRAIN-004` depende de `AR-TRAIN-003`.

**Evidências (trechos SSOT):**
- `docs/hbtrack/modulos/treinos/AR_BACKLOG_TRAINING.md`
```text
| AR-TRAIN-002 | B | ALTA | Tornar Step18 funcional com schema SSOT | INV-TRAIN-014, INV-TRAIN-023 | AR-TRAIN-001 | PENDENTE |
| AR-TRAIN-004 | B/E | ALTA | Corrigir wellness self-only (athlete_id inferido do token) e payload mínimo + mapeamento FE→payload | INV-TRAIN-002/003/026, CONTRACT-TRAIN-029..039 | AR-TRAIN-003 | PENDENTE |
```

- `docs/hbtrack/modulos/treinos/AR_BACKLOG_TRAINING.md`
```text
- **GAP-TRAIN-003:** Serviços wellness para atleta dependem de resolução de `athlete_id` (há evidência de query por coluna inexistente em `Athlete`).
  Alvos: `INV-TRAIN-026`, `FLOW-TRAIN-005/006`.
```

---

### Batch 2 — Rankings + Exports (contratos e UI)

**Objetivo:** fechar gaps de rankings e export (contrato + BE + FE) conforme backlog SSOT.

**AR-TRAIN incluídas (SSOT):**
- `AR-TRAIN-006`
- `AR-TRAIN-007`
- `AR-TRAIN-008`
- `AR-TRAIN-009`

**GAP-TRAIN cobertos (SSOT):**
- `GAP-TRAIN-005`
- `GAP-TRAIN-006`

**Itens alvo (IDs SSOT):**
- **INV:** `INV-TRAIN-036`, `INV-TRAIN-027`, `INV-TRAIN-012`, `INV-TRAIN-025`
- **CONTRACT:** `CONTRACT-TRAIN-073..076`, `CONTRACT-TRAIN-086..090`
- **FLOW:** `FLOW-TRAIN-012`
- **SCREEN:** `SCREEN-TRAIN-014/015`, `SCREEN-TRAIN-013`

**DoD objetivo do batch (alinhado ao Done do módulo):**
- Todos os itens alvo acima deixam de estar em `GAP|PARCIAL|BLOQUEADO|DIVERGENTE|DEPRECATED` e passam a `EVIDENCIADO/IMPLEMENTADO` (ou equivalente canônico) nos SSOTs aplicáveis.

**Non-scope (o que NÃO mexer):**
- Qualquer `AR-TRAIN-*` fora do escopo deste batch.

**Riscos/Dependências (somente SSOT; senão “SEM EVIDÊNCIA NO SSOT”):**
- Dependências declaradas: `AR-TRAIN-006` depende de `AR-TRAIN-004`; `AR-TRAIN-007` depende de `AR-TRAIN-006`; `AR-TRAIN-009` depende de `AR-TRAIN-008`.
- Risco/estado SSOT: `FLOW-TRAIN-012` está `BLOQUEADO` por routers desabilitados no agregador.

**Evidências (trechos SSOT):**
- `docs/hbtrack/modulos/treinos/AR_BACKLOG_TRAINING.md`
```text
| AR-TRAIN-006 | B/C/E | MEDIA | Corrigir rankings wellness (cálculo + response_model) | CONTRACT-TRAIN-073..075, INV-TRAIN-036/027 | AR-TRAIN-004 | PENDENTE |
| AR-TRAIN-007 | D | MEDIA | Corrigir Rankings/TopPerformers FE (UUID + endpoint canônico CONTRACT-TRAIN-076) | SCREEN-TRAIN-014/015, CONTRACT-TRAIN-073..076 | AR-TRAIN-006 | PENDENTE |
| AR-TRAIN-008 | E | MEDIA | Reabilitar exports + atualizar OpenAPI SSOT + estado degradado sem worker | CONTRACT-TRAIN-086..090, INV-TRAIN-012/025 | - | PENDENTE |
```

- `docs/hbtrack/modulos/treinos/AR_BACKLOG_TRAINING.md`
```text
| AR-TRAIN-009 | D | MEDIA | Conectar ExportPDFModal (polling + history + rate limit + estado degradado) | FLOW-TRAIN-012, SCREEN-TRAIN-013, CONTRACT-TRAIN-086..089 | AR-TRAIN-008 | PENDENTE |
```

- `docs/hbtrack/modulos/treinos/TRAINING_USER_FLOWS.md`
```text
- `FLOW-TRAIN-012` está `BLOQUEADO`: routers de export existem, mas estão **desabilitados** no agregador atual (ver `Hb Track - Backend/app/api/v1/api.py`).
```

- `docs/hbtrack/modulos/treinos/AR_BACKLOG_TRAINING.md`
```text
- **GAP-TRAIN-005:** Rankings FE usa `team_id:number` e `parseInt`, mas SSOT é UUID; endpoints de drilldown têm response_model ausente.
  Alvos: `SCREEN-TRAIN-014/015`, `CONTRACT-TRAIN-073..076`, `INV-TRAIN-036`.
```

- `docs/hbtrack/modulos/treinos/AR_BACKLOG_TRAINING.md`
```text
- **GAP-TRAIN-006:** Exports/LGPD export routers existem mas estão desabilitados no agregador v1, bloqueando US-003 “Export PDF”.
  Alvos: `CONTRACT-TRAIN-086..090`, `INV-TRAIN-012`, `INV-TRAIN-025`.
```

---

### Batch 3 — Banco de exercícios (schema/svc/contrato) + UI (scope/ACL/mídia)

**Objetivo:** materializar decisões EXB (scope, visibility, ACL, mídia) via ARs do backlog SSOT.

**AR-TRAIN incluídas (SSOT):**
- `AR-TRAIN-011`
- `AR-TRAIN-012`
- `AR-TRAIN-013`
- `AR-TRAIN-014`

**GAP-TRAIN cobertos (SSOT):**
- `GAP-TRAIN-EXB-001`
- `GAP-TRAIN-EXB-002`
- `GAP-TRAIN-EXB-003`

**Itens alvo (IDs SSOT):**
- **INV:** `INV-TRAIN-047..053`, `INV-TRAIN-EXB-ACL-001..007`, `INV-TRAIN-048`, `INV-TRAIN-051`, `INV-TRAIN-052`
- **CONTRACT:** `CONTRACT-TRAIN-091..095`, `CONTRACT-TRAIN-053..056`
- **FLOW:** `FLOW-TRAIN-009`
- **SCREEN:** `SCREEN-TRAIN-010/011`

**DoD objetivo do batch (alinhado ao Done do módulo):**
- Todos os itens alvo acima deixam de estar em `GAP|PARCIAL|BLOQUEADO|DIVERGENTE|DEPRECATED` e passam a `EVIDENCIADO/IMPLEMENTADO` (ou equivalente canônico) nos SSOTs aplicáveis.

**Non-scope (o que NÃO mexer):**
- Qualquer `AR-TRAIN-*` fora do escopo deste batch.

**Riscos/Dependências (somente SSOT; senão “SEM EVIDÊNCIA NO SSOT”):**
- Dependências declaradas: `AR-TRAIN-012` depende de `AR-TRAIN-011`; `AR-TRAIN-013` depende de `AR-TRAIN-012`; `AR-TRAIN-014` depende de `AR-TRAIN-013`.

**Evidências (trechos SSOT):**
- `docs/hbtrack/modulos/treinos/AR_BACKLOG_TRAINING.md`
```text
| AR-TRAIN-011 | A | ALTA | Materializar schema exercises (scope, visibility_mode) + exercise_acl + exercise_media | INV-TRAIN-047..053, INV-TRAIN-EXB-ACL-001/006 | - | PENDENTE |
| AR-TRAIN-012 | B/E | ALTA | Guards de escopo SYSTEM/ORG + RBAC "Treinador" + service ACL + visibilidade | INV-TRAIN-048/051, INV-TRAIN-EXB-ACL-002..005/007 | AR-TRAIN-011 | PENDENTE |
| AR-TRAIN-013 | B/E | MEDIA | Endpoints ACL + copy SYSTEM→ORG + toggle visibilidade | CONTRACT-TRAIN-091..095, INV-TRAIN-EXB-ACL-001..007 | AR-TRAIN-012 | PENDENTE |
```

- `docs/hbtrack/modulos/treinos/AR_BACKLOG_TRAINING.md`
```text
| AR-TRAIN-014 | D | MEDIA | UI scope/visibility/ACL/mídia no exercise-bank FE | SCREEN-TRAIN-010/011, FLOW-TRAIN-009 | AR-TRAIN-013 | PENDENTE |
```

- `docs/hbtrack/modulos/treinos/AR_BACKLOG_TRAINING.md`
```text
- **GAP-TRAIN-EXB-001:** Schema/model de `exercises` não possui campo `scope` (SYSTEM|ORG) nem `visibility_mode` (org_wide|restricted). Decisões DEC-TRAIN-EXB-001/001B aprovadas mas não materializadas.
  Alvos: `INV-TRAIN-047`, `INV-TRAIN-EXB-ACL-001`, `CONTRACT-TRAIN-053..056`.
```

- `docs/hbtrack/modulos/treinos/AR_BACKLOG_TRAINING.md`
```text
- **GAP-TRAIN-EXB-002:** Tabela `exercise_acl` e tabela `exercise_media` não evidenciadas no schema atual. Necessárias para suportar ACL por usuário e mídias ricas.
  Alvos: `INV-TRAIN-EXB-ACL-002..006`, `INV-TRAIN-052`.
```

- `docs/hbtrack/modulos/treinos/AR_BACKLOG_TRAINING.md`
```text
- **GAP-TRAIN-EXB-003:** Service de exercícios não possui guards de escopo (`SYSTEM` imutável), visibilidade (`restricted` + ACL), nem RBAC explícito "Treinador".
  Alvos: `INV-TRAIN-048`, `INV-TRAIN-051`, `INV-TRAIN-EXB-ACL-004`.
```

---

### Batch 4 — FASE_3 (presença oficial + pending queue + visão atleta pré-sessão)

**Objetivo:** materializar FASE_3 para presença oficial, pendências e visão pré-treino do atleta conforme AR backlog SSOT.

**AR-TRAIN incluídas (SSOT):**
- `AR-TRAIN-017`
- `AR-TRAIN-018`
- `AR-TRAIN-019`

**GAP-TRAIN cobertos (SSOT):**
- SEM EVIDÊNCIA NO SSOT de `GAP-TRAIN-###` específico para estes itens (há menção a “GAPs implícitos” em changelog do backlog; ver evidência).

**Itens alvo (IDs SSOT):**
- **INV:** `INV-TRAIN-063..066`, `INV-TRAIN-066/067`, `INV-TRAIN-068/069/071/076/078`
- **CONTRACT:** `CONTRACT-TRAIN-097/098`, `CONTRACT-TRAIN-099/100`, `CONTRACT-TRAIN-096/105`
- **FLOW:** `FLOW-TRAIN-017`, `FLOW-TRAIN-018`, `FLOW-TRAIN-016/021`
- **SCREEN:** `SCREEN-TRAIN-023`, `SCREEN-TRAIN-022`

**DoD objetivo do batch (alinhado ao Done do módulo):**
- Todos os itens alvo acima deixam de estar em `GAP|PARCIAL|BLOQUEADO|DIVERGENTE|DEPRECATED` e passam a `EVIDENCIADO/IMPLEMENTADO` (ou equivalente canônico) nos SSOTs aplicáveis.

**Non-scope (o que NÃO mexer):**
- Qualquer `AR-TRAIN-*` fora do escopo deste batch.

**Riscos/Dependências (somente SSOT; senão “SEM EVIDÊNCIA NO SSOT”):**
- Dependências declaradas: `AR-TRAIN-018` depende de `AR-TRAIN-017`; `AR-TRAIN-019` depende de `AR-TRAIN-017`.

**Evidências (trechos SSOT):**
- `docs/hbtrack/modulos/treinos/AR_BACKLOG_TRAINING.md`
```text
| AR-TRAIN-017 | B/E | ALTA | Presença oficial (pre-confirm + closure + pending) | INV-TRAIN-063..066, FLOW-TRAIN-017, SCREEN-TRAIN-023, CONTRACT-TRAIN-097/098 | - | PENDENTE |
| AR-TRAIN-018 | D/E | ALTA | UI fila de pendências (pending queue treinador) | INV-TRAIN-066/067, FLOW-TRAIN-018, SCREEN-TRAIN-023, CONTRACT-TRAIN-099/100 | AR-TRAIN-017 | PENDENTE |
| AR-TRAIN-019 | D/E | ALTA | Visão pré-treino atleta + wellness content gate | INV-TRAIN-068/069/071/076/078, FLOW-TRAIN-016/021, SCREEN-TRAIN-022, CONTRACT-TRAIN-096/105 | AR-TRAIN-017 | PENDENTE |
```

- `docs/hbtrack/modulos/treinos/AR_BACKLOG_TRAINING.md`
```text
> - Novos GAPs implícitos: ciclos hierarchy, presença oficial, IA coach (a detalhar em §2 se necessário)
```

---

### Batch 5 — FASE_3 (ciclos hierarchy + sessão standalone + pós-treino + IA coach)

**Objetivo:** completar itens FASE_3 restantes do backlog SSOT (ciclos hierarchy, sessão standalone, pós-treino e IA coach).

**AR-TRAIN incluídas (SSOT):**
- `AR-TRAIN-015`
- `AR-TRAIN-016`
- `AR-TRAIN-020`
- `AR-TRAIN-021`

**GAP-TRAIN cobertos (SSOT):**
- SEM EVIDÊNCIA NO SSOT de `GAP-TRAIN-###` específico para estes itens (há menção a “GAPs implícitos” em changelog do backlog).

**Itens alvo (IDs SSOT):**
- **INV:** `INV-TRAIN-054..056`, `INV-TRAIN-057..059`, `INV-TRAIN-070/077`, `INV-TRAIN-072..075/079..081`
- **CONTRACT:** `CONTRACT-TRAIN-101..104`
- **FLOW:** `FLOW-TRAIN-019/020`, `FLOW-TRAIN-008` (via `AR-TRAIN-015`)
- **SCREEN:** `SCREEN-TRAIN-024/025`

**DoD objetivo do batch (alinhado ao Done do módulo):**
- Todos os itens alvo acima deixam de estar em `GAP|PARCIAL|BLOQUEADO|DIVERGENTE|DEPRECATED` e passam a `EVIDENCIADO/IMPLEMENTADO` (ou equivalente canônico) nos SSOTs aplicáveis.

**Non-scope (o que NÃO mexer):**
- Qualquer `AR-TRAIN-*` fora do escopo deste batch.

**Riscos/Dependências (somente SSOT; senão “SEM EVIDÊNCIA NO SSOT”):**
- Dependência declarada: `AR-TRAIN-020` depende de `AR-TRAIN-019`.
- Dependência declarada: `AR-TRAIN-021` depende de `AR-TRAIN-020`.
- Riscos adicionais: SEM EVIDÊNCIA NO SSOT.

**Evidências (trechos SSOT):**
- `docs/hbtrack/modulos/treinos/AR_BACKLOG_TRAINING.md`
```text
| AR-TRAIN-015 | A/B | ALTA | Schema + Service ciclos hierarchy (macro→meso→micro) | INV-TRAIN-054..056, FLOW-TRAIN-008 | - | PENDENTE |
| AR-TRAIN-016 | B/E | ALTA | Sessão standalone + mutabilidade + order_index exercícios | INV-TRAIN-057..059 | - | PENDENTE |
| AR-TRAIN-020 | B/E | MEDIA | Pós-treino conversacional + feedback imediato | INV-TRAIN-070/077 | AR-TRAIN-019 | PENDENTE |
```

- `docs/hbtrack/modulos/treinos/AR_BACKLOG_TRAINING.md`
```text
| AR-TRAIN-021 | B/E | MEDIA | IA coach (drafts, chat, justificativas, privacidade) | INV-TRAIN-072..075/079..081, FLOW-TRAIN-019/020, SCREEN-TRAIN-024/025, CONTRACT-TRAIN-101..104 | AR-TRAIN-020 | PENDENTE |
```

---

### Batch 6 — Testes de contrato/cobertura (workstream)

**Objetivo:** cobrir contratos críticos sem schema no OpenAPI e consolidar cobertura do `TEST_MATRIX_TRAINING` para itens PARCIAL restantes.

**AR-TRAIN incluídas (SSOT):**
- `AR-TRAIN-010B`

**GAP-TRAIN cobertos (SSOT):**
- SEM EVIDÊNCIA NO SSOT de `GAP-TRAIN-###` específico (AR de workstream de testes).

**Itens alvo (IDs SSOT):**
- **INV:** `INV-TRAIN-013`, `INV-TRAIN-024`
- **CONTRACT:** `CONTRACT-TRAIN-073..075`, `CONTRACT-TRAIN-077..085`
- **TEST_MATRIX:** sync de status para itens em escopo

**DoD objetivo do batch (alinhado ao Done do módulo):**
- Todos os itens alvo acima passam a ter cobertura `COBERTO` ou `PARCIAL justificada` no `TEST_MATRIX_TRAINING.md`.
- `TEST_MATRIX_TRAINING.md` referencia `AR-TRAIN-010B` para `INV-TRAIN-013/024` (AC-001 do backlog SSOT).

**Non-scope (o que NÃO mexer):**
- Qualquer `AR-TRAIN-*` fora do escopo deste batch.
- Invariantes com status `BLOQUEADO` por dependências não resolvidas neste batch.

**Riscos/Dependências (somente SSOT; senão "SEM EVIDÊNCIA NO SSOT"):**
- Dependência declarada (SSOT backlog): `AR-TRAIN-010B` depende de `AR-TRAIN-001..009` — todas VERIFICADAS em 2026-03-01.

**Evidências (trechos SSOT):**
- `docs/hbtrack/modulos/treinos/AR_BACKLOG_TRAINING.md`
```text
| AR-TRAIN-010B | T | ALTA | Testes de contrato/cobertura (workstream) | INV-TRAIN-013/024, CONTRACT-TRAIN-073..075, CONTRACT-TRAIN-077..085, TEST_MATRIX_TRAINING | AR-TRAIN-001..009 | PENDENTE |
```

---

## 3) Test strategy per batch

### 3.1 Regras normativas de teste (SSOT)

SSOT: `docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md`

Evidência (trecho do SSOT):
```text
1. Toda invariante `BLOQUEANTE_VALIDACAO` deve ter pelo menos 1 **teste de violação** (tentar quebrar a regra).
2. Todo `FLOW-TRAIN-*` `P0` deve ter cobertura `E2E` ou `MANUAL_GUIADO` equivalente até o fechamento da fase.
3. Todo contrato `CONTRACT-TRAIN-*` `P0` deve ter pelo menos 1 teste `CONTRACT` cobrindo:
```

Evidência (trecho do SSOT):
```text
4. Item marcado `COBERTO` deve ter caminho de teste e caminho de evidência esperado.
5. Se o item estiver `BLOQUEADO`, deve apontar a AR que remove o bloqueio.
```

### 3.2 Estratégia incremental por batch (sem bloquear batches anteriores)

**Problema (pré-patch; binding humano):** “A AR de testes não pode depender de 001..009 como bloqueio total”.

**Evidência do bloqueio (SSOT TEST_MATRIX):**
```text
2. Parte dos testes existentes referencia `Hb Track - Backend/docs/_generated/*` (inexistente no repo atual) ⇒ itens ficam `BLOQUEADO` até `AR-TRAIN-010A`.
```

**Evidência de itens bloqueados por `_generated` (SSOT TEST_MATRIX):**
```text
- `INV-TRAIN-008`, `INV-TRAIN-020`, `INV-TRAIN-021`, `INV-TRAIN-030`, `INV-TRAIN-031`, `INV-TRAIN-040`, `INV-TRAIN-041`: `BLOQUEADO` por dependência de `Hb Track - Backend/docs/_generated/*` (migrar para `docs/ssot/*` via `AR-TRAIN-010A`).
```

**Evidência da dependência declarada (SSOT BACKLOG):**
```text
| AR-TRAIN-010A | T | ALTA | Testes/Gates: migrar refs `_generated` → `docs/ssot` | INV-TRAIN-008/020/021/030/031/040/041, TEST_MATRIX_TRAINING | - | PENDENTE |
| AR-TRAIN-010B | T | ALTA | Testes de contrato/cobertura (workstream) | INV-TRAIN-013/024, CONTRACT-TRAIN-073..075, CONTRACT-TRAIN-077..085, TEST_MATRIX_TRAINING | AR-TRAIN-001..009 | PENDENTE |
```

**Plano (por batch):**
- Para cada batch **0..5**, executar a parte de testes correspondente aos itens alvo do batch (INV/CONTRACT/FLOW/SCREEN) conforme a matriz:
  - atualizar o status de cobertura para refletir o estado (`COBERTO|PARCIAL|PENDENTE|BLOQUEADO`) e apontar evidência prevista;
  - produzir evidência de execução quando aplicável (o SSOT explicita que “COBERTO” não implica execução imediata).

Evidência (semântica de “COBERTO” no SSOT TEST_MATRIX):
```text
3. “COBERTO” neste documento significa **teste implementado e apontado**. Resultado de execução permanece `NOT_RUN` até a produção de evidência (`_reports/*`).
```

**Ação (pós-patch; governança SSOT):** DEC-TRAIN-TESTS-001 + patch em `AR_BACKLOG_TRAINING.md` (split `AR-TRAIN-010A/010B`) + patch em `TEST_MATRIX_TRAINING.md` (gate `_generated` aponta para `AR-TRAIN-010A`).

### 3.3 Tratamento explícito de GAP-TRAIN-007 (docs/_generated vs docs/ssot)

**Evidência do GAP (SSOT BACKLOG):**
```text
- **GAP-TRAIN-007:** Testes invariants referenciam `docs/_generated/*` ao invés do SSOT atual `docs/ssot/*`.
  Alvos: `INV-TRAIN-040/041`, gates T.
```

**Evidência do bloqueio por `_generated` (SSOT TEST_MATRIX):**
```text
- `INV-TRAIN-008`, `INV-TRAIN-020`, `INV-TRAIN-021`, `INV-TRAIN-030`, `INV-TRAIN-031`, `INV-TRAIN-040`, `INV-TRAIN-041`: `BLOQUEADO` por dependência de `Hb Track - Backend/docs/_generated/*` (migrar para `docs/ssot/*` via `AR-TRAIN-010A`).
```

---

## 4) Pendências de documentação (apenas “NÃO ENCONTRADO NO SSOT” ou “CONTRADIÇÃO SSOT”)

### 4.1 CONTRADIÇÃO SSOT — FLOW-TRAIN-016 ↔ INV-TRAIN-054..056 via AR-TRAIN-015
- Ver seção 1.2: `FLOW-TRAIN-016` não referencia `INV-TRAIN-054..056` no SSOT de flows, mas `AR-TRAIN-015` conecta esses itens no SSOT de backlog.  
- **Ação (pós-patch):** DEC-TRAIN-FLOW-001 + patch em `AR_BACKLOG_TRAINING.md` (AR-TRAIN-015 agora referencia `FLOW-TRAIN-008`).

### 4.2 CONTRADIÇÃO SSOT — Defaults de `visibility_mode` (exercise ORG)

SSOT: `docs/hbtrack/modulos/treinos/TRAINING_FRONT_BACK_CONTRACT.md`

Evidência (trecho do SSOT — default `restricted`):
```text
| `visibility_mode` (exercício ORG) | `restricted` | DEC-TRAIN-EXB-001, INV-TRAIN-060 (AMENDADO v1.3.0: era org_wide) |
```

Evidência (trecho do SSOT — regra dizendo default `restricted`):
```text
- Se `visibility_mode` não for informado em `ExerciseCreate`, o backend DEVE usar `restricted`.
```

Evidência adicional (trecho do SSOT — default `restricted` em CONTRACT-TRAIN-095 copy SYSTEM→ORG):
```text
- `visibility_mode` padrão = `restricted` (pode ser overridden no request).
```

**Ação (pós-patch):** DEC-TRAIN-EXB-003 + patch em `TRAINING_FRONT_BACK_CONTRACT.md` (alinhamento do default normativo `restricted`).

---

### Batch 7 — Governança: Sync INVARIANTS_TRAINING.md (pós-Batch 3..5)

**Objetivo:** promover 31 invariantes de `GAP/PARCIAL/DIVERGENTE_DO_SSOT` → `IMPLEMENTADO` em `INVARIANTS_TRAINING.md`, bumpando versão para v1.5.0, com notas de rastreabilidade para as ARs de origem já verificadas.

**AR-TRAIN incluídas (SSOT):**
- `AR-TRAIN-022`

**GAP-TRAIN cobertos (SSOT):**
- Todos os 31 itens restantes com status não-IMPLEMENTADO em `INVARIANTS_TRAINING.md` (ver §8 AR-TRAIN-022 no backlog).

**Itens alvo (IDs SSOT):**
- **INV:** `INV-TRAIN-013/014/023/024/025/047..053/EXB-ACL-001..007/054..062/079..081` (31 invariantes)

**DoD objetivo do batch (alinhado ao Done do módulo):**
- `INVARIANTS_TRAINING.md` não contém `status: GAP`, `status: PARCIAL`, nem `status: DIVERGENTE_DO_SSOT` em nenhum bloco yaml de invariante.
- Versão atualizada para v1.5.0 com changelog.
- Cada invariante promovido tem `note:` com rastreabilidade da AR de origem.

**Non-scope (o que NÃO mexer):**
- `Hb Track - Backend/` e `Hb Track - Frontend/` (zero toque de código).
- `docs/ssot/` (somente leitura para evidência).
- Qualquer `AR-TRAIN-*` fora deste scope.

**Riscos/Dependências (somente SSOT; senão "SEM EVIDÊNCIA NO SSOT"):**
- Dependências declaradas: `AR-TRAIN-011..021` — todas VERIFICADO em 2026-03-01 (Kanban).

**Evidências (trechos SSOT):**
- `docs/hbtrack/modulos/treinos/AR_BACKLOG_TRAINING.md`
```text
| AR-TRAIN-022 | G | ALTA | Sync INVARIANTS_TRAINING.md: promover 31 itens GAP/PARCIAL/DIVERGENTE_DO_SSOT → IMPLEMENTADO | INV-TRAIN-013/014/023/024/025/047..053/EXB-ACL-001..007/054..062/079..081 | AR-TRAIN-011..021 | PENDENTE |
```

---

### Batch 8 — Governança: Sync TEST_MATRIX_TRAINING.md §9 (pós-Batch 3..7)

**Objetivo:** Atualizar `TEST_MATRIX_TRAINING.md` para refletir o estado real das ARs verificadas nos Batches 3..7. Promover §9 de PENDENTE para VERIFICADO para AR-TRAIN-001/002/003/004/005/010A/010B/022. Desbloquear 7 invariantes (INV-TRAIN-008/020/021/030/031/040/041) e 9 contratos (CONTRACT-TRAIN-077..085) cujas dependências foram verificadas.

**AR-TRAIN incluídas (SSOT):**
- `AR-TRAIN-023`

**GAP-TRAIN cobertos (SSOT):**
- §9 stale: 8 entradas com status PENDENTE apesar de ARs VERIFICADAS no Kanban.
- §5 BLOQUEADO: 7 invariantes aguardando AR-TRAIN-010A (já VERIFICADO).
- §8 BLOQUEADO: 9 contratos aguardando AR-TRAIN-001/002 (já VERIFICADOS).

**DoD objetivo do batch:**
- `TEST_MATRIX_TRAINING.md` não contém nenhuma linha com BLOQUEADO em §5 (INV) ou §8 (CONTRACT) para as dependências já verificadas.
- §9 reflete corretamente o status VERIFICADO de AR-TRAIN-001..005/010A/010B/022.
- Versão v1.5.1 → v1.6.0 com changelog.

**Non-scope (o que NÃO mexer):**
- `Hb Track - Backend/` e `Hb Track - Frontend/` (zero toque de código).
- Nenhum outro arquivo SSOT além de `TEST_MATRIX_TRAINING.md`.
- **NÃO executar pytest** — execução de testes é escopo de AR futura.

**Riscos/Dependências:**
- AR-TRAIN-001/002/010A/022 = VERIFICADO (pré-condição confirmada pelo Arquiteto via Kanban).
- §0 summary: recalcular contadores — BLOQUEADO → 0 (INV e CONTRACT); COBERTO +16.

**Evidências confirmadas pelo Arquiteto:**

| AR-TRAIN | ARs de evidência | Batch |
|---|---|---|
| AR-TRAIN-001 | AR_126, AR_127, AR_128, AR_129 | Batch 3 |
| AR-TRAIN-002 | AR_175 | Batch 3 |
| AR-TRAIN-003 | AR_169, AR_170 | Batch 3 |
| AR-TRAIN-004 | AR_176 | Batch 3 |
| AR-TRAIN-005 | AR_171, AR_172 | Batch 3 |
| AR-TRAIN-010A | AR_173, AR_174 | Batch 4/5 |
| AR-TRAIN-010B | AR_195 | Batch 6 |
| AR-TRAIN-022 | AR_197 | Batch 7 |

**Tabela de conteúdo:**

```text
| AR-TRAIN-023 | G | ALTA | Sync TEST_MATRIX_TRAINING.md §9: AR-TRAIN-001..022 PENDENTE→VERIFICADO + desbloquear 7 INV e 9 CONTRACT | TEST_MATRIX_TRAINING.md §9/§5/§8 | AR-TRAIN-001/002/010A/022 | PENDENTE |
```

---

### Batch 9 — Fix FAILs críticos (test-layer only)

**Objetivo:** Eliminar 5 FAILs que bloqueiam o Done Gate do módulo TRAINING. Todos os fixes são exclusivamente no diretório `tests/training/` — zero mudança de produto backend/frontend.

**AR-TRAIN incluídas (SSOT):**
- `AR-TRAIN-024` — Fix INV-001: expected constraint name errado em test_invalid_case_2
- `AR-TRAIN-025` — Fix INV-008: schema_path com 3 .parent (deve ser 4)
- `AR-TRAIN-026` — Fix INV-030: schema_path com 3 .parent (mesma causa INV-008)
- `AR-TRAIN-027` — Fix INV-032: 6 async fixtures @pytest.fixture → @pytest_asyncio.fixture
- `AR-TRAIN-028` — Fix CONTRACT-077-085: ROUTER_PATH com 3 .parent (deve ser 4)

**Itens alvo (IDs SSOT):**
- **INV:** `INV-TRAIN-001`, `INV-TRAIN-008`, `INV-TRAIN-030`, `INV-TRAIN-032`
- **CONTRACT:** `CONTRACT-TRAIN-077..085` (evidência renovada)

**DoD objetivo do batch:**
- 0 FAILs, 0 ERRORs nos 5 arquivos de teste corrigidos.
- Evidências atualizadas em `_reports/training/`.

**Non-scope:**
- `Hb Track - Backend/app/` — zero toque em código de produto
- `Hb Track - Frontend/`
- `TEST_MATRIX_TRAINING.md` — sync será feito na AR-TRAIN-031 (Batch 11)

**Riscos/Dependências:**
- Nenhuma dependência de AR anterior (fixes independentes entre si).
- INV-032: pytest-asyncio >= 0.21 necessário (verificar requirements.txt).
- INV-008/030: schema.sql existe em `Hb Track - Backend/docs/ssot/schema.sql` (confirmado).

---

### Batch 10 — Evidências P0: Flows + Contracts

**Objetivo:** Cobrir os itens P0 restantes do §6 (Flows) e §8 (Contracts) da TEST_MATRIX. Após este batch, todos os flows P0 (001-006, 017, 018) terão evidência MANUAL_GUIADO e os contracts P0 (097-100) terão teste automatizado passando.

**AR-TRAIN incluídas (SSOT):**
- `AR-TRAIN-029` — Flow P0 evidence: FLOW-TRAIN-001..006 + 017 + 018 (MANUAL_GUIADO)
- `AR-TRAIN-030` — Contract P0 tests: CONTRACT-TRAIN-097..100 (pre-confirm, close, pending-items)

**Itens alvo (IDs SSOT):**
- **FLOW:** `FLOW-TRAIN-001/002/003/004/005/006/017/018`
- **CONTRACT:** `CONTRACT-TRAIN-097/098/099/100`

**DoD objetivo do batch:**
- 8 arquivos de evidência FLOW criados em `_reports/training/TEST-TRAIN-FLOW-*.md`.
- 1 arquivo de teste `tests/training/contracts/test_contract_train_097_100_presence_pending.py` com 0 FAILs.
- `TEST_MATRIX_TRAINING.md` §6 e §8 atualizados para os itens em escopo.

**Non-scope:**
- Demais contracts P1/P2 (fora de escopo deste batch).
- Demais flows além dos 8 listados.

**Riscos/Dependências:**
- **Dep obrigatória:** Batch 9 (AR-TRAIN-024..028) VERIFICADO.
- CONTRACT-097/098 dependem de endpoints implementados por AR-TRAIN-017 (VERIFICADO: AR_185).
- CONTRACT-099/100 dependem de endpoints implementados por AR-TRAIN-018 (VERIFICADO: AR_186).

---

### Batch 11 — Done Gate: Sync TEST_MATRIX v1.8.0 + Declaração DONE

**Objetivo:** Sincronização final da TEST_MATRIX_TRAINING.md e declaração do Done Gate do módulo TRAINING. Não cria testes — apenas governa e valida o estado final.

**AR-TRAIN incluídas (SSOT):**
- `AR-TRAIN-031` — Done Gate: sync TEST_MATRIX v1.8.0 + validar §10

**Itens alvo (IDs SSOT):**
- `TEST_MATRIX_TRAINING.md` — §9 (sync AR-TRAIN-024..030), §5/§6/§8 (status finais), §0 (contadores), versão v1.7.0 → v1.8.0
- `_reports/training/DONE_GATE_TRAINING.md` — declaração Done Gate

**DoD objetivo do batch:**
- `TEST_MATRIX_TRAINING.md` versão v1.8.0 com §9 incluindo AR-TRAIN-024..031.
- §5: INV-001/008/030/032 com status COBERTO e Últ.Execução atualizada.
- §8: CONTRACT-077..085 evidência renovada; CONTRACT-097..100 status COBERTO.
- §6: FLOW-TRAIN-001..006/017/018 status COBERTO.
- `_reports/training/DONE_GATE_TRAINING.md` com critérios §10 satisfeitos.
- Smoke pytest (5 testes corrigidos no Batch 9) = 0 FAILs.

**Non-scope:**
- `Hb Track - Backend/app/` e `Hb Track - Frontend/` — zero toque.
- Testes P1/P2 restantes — fora do escopo Done Gate.

**Riscos/Dependências:**
- **Dep obrigatória:** Batches 9 e 10 (AR-TRAIN-024..030) todos VERIFICADO.
- A declaração Done Gate não é a selagem final — o humano executa `hb seal` por conta própria.

---

### Batch 12 — Sync Matrix §10 + 6 Testes Ausentes

**Objetivo:** Resolver a dessincronia crítica entre TEST_MATRIX_TRAINING.md e o estado real do filesystem: ~40 invariantes marcadas PENDENTE mas com testes criados pelas ARs 144-167. Criar os 6 arquivos de teste que genuinamente não existem.

**AR-TRAIN incluídas:**
- `AR-TRAIN-032` — Sync §5 TEST_MATRIX: ~40 INV PENDENTE → COBERTO
- `AR-TRAIN-033` — Criar 6 testes ausentes: INV-053/060/061/062/EXB-ACL-005/007

**Itens alvo (IDs SSOT):**
- **TEST_MATRIX §5:** todas as INV PENDENTE onde arquivo de teste já existe no filesystem
- **INV:** INV-TRAIN-053, 060, 061, 062, EXB-ACL-005, EXB-ACL-007

**DoD objetivo do batch:**
- TEST_MATRIX §5: zero linhas PENDENTE para INV com arquivo de teste presente.
- 6 novos arquivos de teste criados e passando (0 FAILs).
- §0 contadores atualizados.

**Non-scope:**
- `Hb Track - Backend/app/` e `Hb Track - Frontend/` — zero toque.

**Riscos/Dependências:**
- **Dep obrigatória:** Batch 11 (AR-TRAIN-031) VERIFICADO.
- Dessincronia confirmada: ~40 INV marcadas PENDENTE na Matrix apesar de testes existentes criados nos Batches 3-8 (ARs 144-167). Causa: AR-TRAIN-031 (Done Gate v1.8.0) não retroagiu nos status da Matrix.

---

### Batch 13 — Execução NOT_RUN + Evidências Formais

**Objetivo:** Executar os ~32 testes marcados NOT_RUN no §5 da TEST_MATRIX e gerar evidências formais de passagem.

**AR-TRAIN incluídas:**
- `AR-TRAIN-034` — Executar todos NOT_RUN + evidências formais

**Itens alvo:**
- **TEST_MATRIX §5:** todas as linhas NOT_RUN

**DoD objetivo do batch:**
- TEST_MATRIX §5: zero linhas NOT_RUN.
- `_reports/training/evidence_run_batch13.txt` com output pytest = 0 FAILs.

**Non-scope:**
- `Hb Track - Backend/app/` — zero toque.

**Riscos/Dependências:**
- **Dep obrigatória:** Batch 12 (AR-TRAIN-032/033) VERIFICADO.
- Alguns NOT_RUN podem revelar FAILs reais — se houver, criar AR de fix antes de prosseguir (Executor deve reportar).

---

### Batch 14 — Contratos P0 Automatizados por Domínio

**Objetivo:** Criar testes automatizados de contrato para os ~88 contratos P0 ainda sem cobertura, organizados por domínio em 5 ARs paralelas.

**AR-TRAIN incluídas:**
- `AR-TRAIN-035` — Contract tests: Sessions CRUD (CONTRACT-001..012)
- `AR-TRAIN-036` — Contract tests: Teams + Attendance (CONTRACT-013..028)
- `AR-TRAIN-037` — Contract tests: Wellness pre/post (CONTRACT-029..039)
- `AR-TRAIN-038` — Contract tests: Ciclos/Exercises/Analytics/Export (CONTRACT-040..095)
- `AR-TRAIN-039` — Contract tests: IA Coach + Athlete view (CONTRACT-096/101..105)

**Itens alvo:**
- **CONTRACT:** CONTRACT-TRAIN-001..072, 076, 086..096, 101..105
- **Já cobertos (não tocar):** CONTRACT-073..075, 077..085, 097..100 (testes existentes)

**DoD objetivo do batch:**
- 5+ novos arquivos de contract tests criados, todos: 0 FAILs.
- TEST_MATRIX §8: todos os contratos P0 em escopo = COBERTO.

**Non-scope:**
- `Hb Track - Backend/app/` — zero toque.

**Riscos/Dependências:**
- **Dep obrigatória:** Batch 13 (AR-TRAIN-034) VERIFICADO.
- Testes de contrato devem usar aproximação estática (import + schema inspection) quando DB não disponível em CI.

---

### Batch 15 — DEC Tests + Flows P1 + Screens

**Objetivo:** Cobrir os 11 DECs do módulo com testes automatizados, os 13 flows P1 com evidências MANUAL_GUIADO, e as 25 telas com smoke tests.

**AR-TRAIN incluídas:**
- `AR-TRAIN-040` — DEC tests automatizados (DEC-TRAIN-001..004 + EXB-* + RBAC-*)
- `AR-TRAIN-041` — Flows P1 evidência MANUAL_GUIADO (FLOW-007..016/019..021)
- `AR-TRAIN-042` — Screens smoke tests MANUAL_GUIADO (SCREEN-001..025)

**Itens alvo:**
- **TEST_MATRIX §5b:** 11 DEC tests
- **TEST_MATRIX §6:** FLOW-TRAIN-007..016/019..021 (13 flows P1)
- **TEST_MATRIX §7:** SCREEN-TRAIN-001..025 (25 telas)

**DoD objetivo do batch:**
- TEST_MATRIX §5b: todos DECs = COBERTO.
- TEST_MATRIX §6: todos flows P1 = COBERTO.
- TEST_MATRIX §7: todas telas = COBERTO ou NOT_APPLICABLE com nota.

**Non-scope:**
- `Hb Track - Backend/app/` — zero toque.

**Riscos/Dependências:**
- **Dep obrigatória:** Batch 12 (AR-TRAIN-033) VERIFICADO para AR-TRAIN-040.
- **Dep obrigatória:** Batch 13 (AR-TRAIN-034) VERIFICADO para AR-TRAIN-041/042.
- AR-TRAIN-040 pode ser executada em paralelo com AR-TRAIN-041/042 (independentes).

---

### Batch 16 — Done Gate §10 Final

**Objetivo:** Sync final do TEST_MATRIX_TRAINING.md para v2.0.0, verificação de que todos os critérios §10 estão formalmente satisfeitos, e emissão da declaração Done Gate §10.

**AR-TRAIN incluídas:**
- `AR-TRAIN-043` — Done Gate §10 final: sync TEST_MATRIX v2.0.0 + full suite verde

**Itens alvo:**
- `TEST_MATRIX_TRAINING.md` — versão v1.8.0 → v2.0.0, §10 todos ✅, §9 AR-TRAIN-024..043
- `_reports/training/DONE_GATE_TRAINING_v2.md` — declaração formal

**DoD objetivo do batch:**
- TEST_MATRIX v2.0.0 com §10 todos PASS marcados.
- `pytest tests/training/ -q` = 0 FAILs (full suite).
- DONE_GATE_TRAINING_v2.md emitido com assinatura do Arquiteto.

**Non-scope:**
- `Hb Track - Backend/app/` e `Hb Track - Frontend/` — zero toque.

**Riscos/Dependências:**
- **Dep obrigatória:** Batches 12-15 (AR-TRAIN-032..042) todos VERIFICADO.
- A declaração Done Gate não substitui `hb seal` — o humano executa por conta própria.

---

### Batch 18 — Fix FAILs de test-layer pré-existentes (Batch 13)

**Objetivo:** Zerar os 109 FAILs + 31 ERRORs residuais na suite `tests/training/` provenientes do Batch 13, agrupados em 4 tipos: async fixtures, DB fixture setup, import stubs ausentes, e residuais mistos.

**AR-TRAIN incluídas:**
- `AR-TRAIN-044` — Fix async fixtures: `@pytest.fixture` → `@pytest_asyncio.fixture` (~23+ tests, 7 arquivos)
- `AR-TRAIN-045` — Fix DB fixture setup: `category_id` NOT NULL + FK `team_registrations` (~57+ ERROs)
- `AR-TRAIN-046` — Fix import stubs ausentes em `ai_coach_service` (3 ERRORs coleta: INV-079/080/081)
- `AR-TRAIN-047` — Fix residuais mistos + validação done gate (0 FAILs suite completa)

**Itens alvo:**
- **TypeError globals:** `test_inv_train_024`, `_031`, `_034`, `_035`, `_036`, `_037`, `_070`
- **category_id NOT NULL:** `test_inv_train_011`, `_013`, `_020`, `_021`, `_028`, `_029`, `_050`, `_052`, `_058`, `_059`, `_063`, `_064`, `_076`, `_148`, `exb_acl_006`
- **ImportError ai_coach_service:** `test_inv_train_079`, `_080`, `_081`
- **Residuais:** `test_inv_train_010`, `_018`, `_019`, `_054`, `_057`, `_065`, `_066`, `_067`

**DoD objetivo do batch:**
- `pytest tests/training/ -q --tb=no` = 0 FAILs, 0 ERRORs.
- AR-TRAIN-044/045/046 podem rodar em paralelo (arquivos disjuntos).
- AR-TRAIN-047 depende das 3 anteriores.

**Non-scope:**
- `Hb Track - Backend/app/` — zero toque.
- Não criar novos testes de produto — apenas corrigir fixtures/imports existentes.

**Riscos/Dependências:**
- **Dep obrigatória:** AR-TRAIN-034 VERIFICADO.
- AR-TRAIN-047 só pode rodar após AR-TRAIN-044 + 045 + 046 VERIFICADO.
- Residuais em AR-TRAIN-047 podem revelar FAILs adicionais — se ocorrer, Executor reporta e Arquiteto cria AR-TRAIN-048 antes de prosseguir para AR_222.
- AR_222 (Done Gate §10) só pode ser re-executada após AR-TRAIN-047 VERIFICADO e suite verde.


---

### Batch 19 — Sincronização em Lote: Transposição SSOT → App Layer

**Objetivo:** Eliminar o desalinhamento entre `app/` e o contrato v1.3.0 + Invariantes v1.5.0, aplicando correções determinísticas em modelos, serviços e stubs de IA Coach. Esta é a única AR do batch — toda a sincronização é concentrada para execução única.

**AR-TRAIN incluida:**
- `AR-TRAIN-048` (A/E) — Sync app/models/ (UniqueConstraint/FK: INV-010/035/036/054) + app/services/ (assinaturas contrato v1.3.0) + stubs IA Coach (`RecognitionApproved`, `CoachSuggestionDraft`, `JustifiedSuggestion`)

**Zonas de impacto:**
- **Zona 1 — Modelos:** `athlete.py` (campos Glossário), `exercise.py` (visibility_mode default restricted INV-060), `training_session.py`, `attendance.py`, `training_cycle.py`
- **Zona 2 — Serviços:** `exercise_service.py` (assinatura update_exercise), `attendance_service.py` (GAP-CONTRACT-7 stubs)
- **Zona 3 — Stubs IA:** `ai_coach_service.py` (3 dataclasses mínimas importáveis)
- **Zona 4 — OpenAPI:** `docs/ssot/openapi.json` (atualizar se necessário após mudanças de assinatura)

**DoD objetivo do batch:**
- AC-001: `app/models/athlete.py` alinhado ao Glossário (athlete_name, birth_date)
- AC-002: `app/models/exercise.py` com `visibility_mode` server_default=`restricted`
- AC-003: `exercise_service.update_exercise` aceita `(exercise_id, data: dict, organization_id)`
- AC-004: `ai_coach_service.py` exporta `RecognitionApproved`, `CoachSuggestionDraft`, `JustifiedSuggestion`
- AC-005: `pytest tests/training/invariants/test_inv_train_079*.py 080*.py 081*.py` = 0 ERRORs coleta

**Non-scope:**
- `Hb Track - Backend/tests/` — zero toque nesta AR (testes são alvo do Batch 18)
- `Hb Track - Frontend/` — zero toque
- Qualquer `app/` não listado no write_scope de AR-TRAIN-048

**Riscos/Dependências:**
- **Dep obrigatória:** AR-TRAIN-044..047 (Batch 18) todos VERIFICADO. Suite tests/ deve estar verde antes desta AR.
- Modificações em `app/models/` podem exigir `alembic revision --autogenerate` se houver novas Column/Constraint. Executor DEVE verificar antes do `hb report`.
- Se durante a execução surgir necessidade de alterar `app/` além dos 9 arquivos do write_scope → Executor para, documenta no `executor_main.log` e reporta BLOCKED para o Arquiteto.
- **ALERTA PÓS-EXECUÇÃO:** AR_229 revelou status server_default `'''draft'''` com triple-quote BUG em `training_session.py`. Executor deve corrigir (sa.text("'draft'::character varying")) dentro do write_scope de AR_229 antes de re-run do `hb report 229`.

---

### Batch 20 — Fix residuais test-layer pós-Batch 18/19

**Objetivo:** Eliminar 6 FAILs + 10 ERRORs remanescentes em `tests/training/invariants/` que emergiram durante execução de AR_229 (Batch 19). Todos são bugs exclusivamente de test-layer (nenhuma mudança de produto). Esta é a AR capturadora final antes do verde completo da suite.

**AR-TRAIN incluída:**
- `AR-TRAIN-049` (T) — Fix 6 FAILs + 10 ERRORs residuais em 8 arquivos de teste

**Zonas de impacto (apenas tests/):**
- `test_018_route.py` — add birth_date em Person()
- `test_035_runtime.py` — renomear kwarg organization_id → org_id em SessionTemplate()
- `test_058.py` / `test_059.py` — add category fixture + category_id em Team() local
- `test_063.py` / `test_064.py` — substituir athlete.person_id → athlete.id em team_registrations
- `test_076.py` — substituir status='concluída' → 'pending_review'
- `test_exb_acl_006.py` — corrigir uuid4.__class__(exercise_id) → UUID(exercise_id)

**DoD objetivo do batch:**
- AC-001..005: cada file-pair passando 0 FAILs, 0 ERRORs
- AC-006: `pytest tests/training/ -q --tb=no` = `0 failed, 0 errors` (suite training/ verde completa)
- Após AC-006 ✅: re-executar `hb report 228` e `hb report 229` para verificação final + AR_222 (Done Gate §10)

**Non-scope:**
- `app/` — zero toque (bugs são exclusivamente test-layer)
- `Hb Track - Frontend/` — zero toque
- `tests/training/invariants/conftest.py` — zero toque
- Qualquer arquivo de teste não listado no write_scope

**Riscos/Dependências:**
- **Dep obrigatória:** AR-TRAIN-048 executado (com amendment de status server_default).
- test_058/059: usar `ON CONFLICT DO NOTHING` na criação de fixture `category` para evitar colisão com id=9999 de outros testes.
- test_076: verificar coerência semântica ao substituir 'concluída' → 'pending_review' na lógica do teste.
- Após AR-TRAIN-049 VERIFICADO: re-executar `hb report 228` + `hb report 229` para fechar os dois ciclos em aberto.