# Bucket 1 Remanescente — Critério de Auditoria

**Sessão:** 4C (próxima)  
**Objetivo:** Reclassificar 132 campos Bucket 1-restante  
**Decisão:** Fica em Bucket 1 (automático) ou migra para Bucket 4 (ambíguo)?

---

## Critério Binário

### ✅ Permanece em Bucket 1 (Candidato a Automático v6)

Um campo **permanece** no Bucket 1 inequívoco se **TODOS** os critérios abaixo são verdadeiros:

| Critério | Definição | Exemplo |
|----------|-----------|---------|
| **Inequívoco semântico** | Nome indica exatamente uma pattern correta, sem ambiguidade | `createdAt` → sempre `timestamp_utc` |
| **Pattern única no domínio** | Não existe contexto onde o campo teria pattern diferente | `organizationId` → sempre `uuid_v4` |
| **Convenção estabelecida** | Segue padrão de nomenclatura HB Track (sufixo `At`, `Id`, `Date`) | `startDate` → sempre `date_only` |
| **Sem variante semântica** | Campo não representa conceitos múltiplos conforme contexto | ✅ `updatedAt` (sempre timestamp) |

### ❌ Migra para Bucket 4 (Ambíguo/Manual)

Um campo **sai** do automático e vai para Bucket 4 se **QUALQUER** critério abaixo é verdadeiro:

| Critério | Definição | Exemplo |
|----------|-----------|---------|
| **Nome genérico** | Campo `id` sem qualificador, ou sufixo não-padrão | `id` (pode ser uuid ou opaque string) |
| **Polissêmico** | Mesmo nome poderia ter patterns diferentes em contextos diferentes | `expiresAt` (pode ser timestamp OU date conforme domínio) |
| **Contexto-dependente** | Pattern depende de onde o campo aparece | `jobId` (em jobs é uuid, em reports pode ser opaque) |
| **Sufixo não-canônico** | Não segue convenção HB (ex: `recordedAt`, `sessionAt`, `entryId`) | `recordedAt` (não é `createdAt/updatedAt/...`) |
| **Fora do dicionário Bucket 1** | Campo não está na lista pré-aprovada de 28 inequívocos | Qualquer campo novo não previamente catalogado |

---

## Dicionário Bucket 1 Aprovado

Campos que **garantidamente** permanecem em Bucket 1:

### Timestamps (15)
```
adjustedAt, captureStartedAt, completedAt, computedAt, correctionAt,
createdAt, decidedAt, declaredAt, endedAt, failedAt, nextRetryAt,
occurredAt, publishedAt, startedAt, updatedAt
```
**Pattern:** `timestamp_utc`  
**Razão:** Todos indicam execução/mudança de estado inequívoca no tempo

### UUIDs (12)
```
athleteId, coachId, conversationId, createdByUserId, decidedByCoachId,
generatedSessionId, generatedTrainingSessionId, matchId, organizationId,
sessionId, teamId, trainingId
```
**Pattern:** `uuid_v4`  
**Razão:** Todos identificadores de entidades específicas do domínio

### Datas (2)
```
endDate, startDate
```
**Pattern:** `date_only`  
**Razão:** Convenção clara de limites temporais (sem time)

### Especiais (2)
```
traceId → trace_id
requestId → request_id
```
**Pattern:** Pattern nomeada  
**Razão:** Nomeclatura canônica no sistema tracing

**Total garantido:** 31 campos (alguns já foram no v4/v5, outros ainda estão nos 132 remanescentes)

---

## Taxonomia de Motivos — Obrigatória para cada decisão

Cada um dos 132 campos **deve ter** um motivo classificado em uma destas categorias:

### Motivos para Permanecer em Bucket 1

| Código | Descrição | Exemplo |
|--------|-----------|---------|
| `CANONICAL_TIMESTAMP_SUFFIX` | Sufixo `At` com heurística clara (timestamp_utc) | `createdAt`, `updatedAt` |
| `CANONICAL_UUID_SUFFIX` | Sufixo `Id` com heurística clara (uuid_v4) | `athleteId`, `organizationId` |
| `CANONICAL_DATE_SUFFIX` | Sufixo `Date` com heurística clara (date_only) | `startDate`, `endDate` |
| `CANONICAL_SPECIAL_NAME` | Nome específico e inequívoco (traceId, requestId) | `traceId` → `trace_id` |
| `MISS_HEURISTIC_INDENTATION` | **Nome canônico mas v5 perdeu por indentação exótica** | `createdAt` em nested YAML com 6 espaços |
| `MISS_HEURISTIC_ALIAS` | **Campo é alias/renamed de um aprovado** | `created_timestamp` (variante de `createdAt`) |
| `MISS_HEURISTIC_SUFFIX_VARIANT` | **Sufixo similar mas não exato** (ex: `Created`, `Created_at`) | `Created` (maiúscula), `Created_at` |

### Motivos para Migrar para Bucket 4

| Código | Descrição | Exemplo |
|--------|-----------|---------|
| `AMBIGUOUS_GENERIC_ID` | Nome `id` sem qualificador — múltiplas interpretações | Campo nomeado simplesmente `id` |
| `AMBIGUOUS_TIME_FIELD` | Sufixo `At` mas polissêmico (timestamp vs date contexto) | `expiresAt` (sessão expira TS vs permissão expira D) |
| `AMBIGUOUS_NAMESCOPE` | Sufixo canônico mas nome do escopo ambíguo | `sessionAt` (qual session? qual timestamp?) |
| `OUTSIDE_APPROVED_DICTIONARY` | Nome não está na lista de 31 inequívocos aprovados | `recordedAt` (não é na lista original) |
| `POLYSEMIC_CONTEXT_DEPENDENT` | Mesmo campo teria pattern diferente em contextos diferentes | `jobId` (em Jobs table: uuid, em async message: opaque) |
| `GENERIC_QUALIFICATION` | Qualificador genérico inadequado | `data_id`, `info_id` (não semântico) |

---

## Output Obrigatório da Sessão 4C

### Formato por campo

```json
{
  "field_name": "createdAt",
  "current_pattern_violation": "timestamp_utc",
  "expected_pattern": "timestamp_utc",
  "decision": "BUCKET_1",
  "reason_code": "MISS_HEURISTIC_INDENTATION",
  "confidence": "HIGH",
  "reason_detail": "Campo está em nested YAML com 6 espaços de indent; regex v5 esperava 4. Semântica invariável: sempre timestamp_utc.",
  "location_examples": [
    "contracts/asyncapi/components/schemas/training_session_started_payload.yaml:L42"
  ]
}
```

### Campo `confidence` — Regra Prática

| Decisão | Confidence | Significado | Ação |
|---------|-----------|-----------|------|
| `BUCKET_1` | `HIGH` | Inequívoco, padrão canônico, v6-candidate de primeira escolha | ✅ Incluir na v6 |
| `BUCKET_1` | `MEDIUM` | Provável Bucket 1, mas casos limítrofes ou heurística fraca | ⚠️ Revisar antes de v6 |
| `BUCKET_4` | — | Fora do escopo automático por definição | ❌ Não incluir em v6 |

**Regra:** Se a confiança é `MEDIUM`, o item vai para Bucket 1, mas sinalizado para revisão manual antes de inclusão na v6.



### Agregação por tipo

```json
{
  "bucket1_staying": {
    "total": 75,
    "by_confidence": {
      "HIGH": 63,
      "MEDIUM": 12
    },
    "by_reason": {
      "CANONICAL_TIMESTAMP_SUFFIX": 35,
      "CANONICAL_UUID_SUFFIX": 28,
      "MISS_HEURISTIC_INDENTATION": 8,
      "MISS_HEURISTIC_ALIAS": 4
    },
    "fields": [...]
  },
  
  "bucket4_reclassified": {
    "total": 57,
    "by_reason": {
      "AMBIGUOUS_GENERIC_ID": 13,
      "AMBIGUOUS_TIME_FIELD": 22,
      "OUTSIDE_APPROVED_DICTIONARY": 18,
      "POLYSEMIC_CONTEXT_DEPENDENT": 4
    },
    "fields": [...]
  },
  
  "v6_candidates": {
    "high_confidence": 63,
    "medium_confidence_review_required": 12,
    "total_v6_candidates": 75
  },
  
  "summary": {
    "bucket1_total": 75,
    "bucket1_high_confidence": 63,
    "bucket1_medium_confidence": 12,
    "bucket4_total": 57,
    "total_audited": 132,
    "zero_undecided": true
  }
}
```



## Exemplos de Aplicação (com confidence)

### Campo: `createdAt`
```json
{
  "field": "createdAt",
  "decision": "BUCKET_1",
  "reason_code": "CANONICAL_TIMESTAMP_SUFFIX",
  "confidence": "HIGH",
  "detail": "Sufixo At canônico HB, semântica invariável (criação), sempre timestamp_utc"
}
```
→ **v6-candidate imediata**

### Campo: `receivedAt`
```json
{
  "field": "receivedAt",
  "decision": "BUCKET_1",
  "reason_code": "MISS_HEURISTIC_INDENTATION",
  "confidence": "MEDIUM",
  "detail": "Sufixo At sugere timestamp, mas nome menos convencional (não na lista de 31). Verificar contexto."
}
```
→ **v6-candidate com revisão obrigatória antes de incluir**

### Campo: `expiresAt`
```json
{
  "field": "expiresAt",
  "decision": "BUCKET_4",
  "reason_code": "AMBIGUOUS_TIME_FIELD",
  "confidence": "N/A (Bucket 4)",
  "detail": "Polissêmico: sessão expira em timestamp, permissão expira em date. Contexto-dependente."
}
```
→ **Fora do automático, requer 4D decision-tree**

### Campo: `jobId`
```json
{
  "field": "jobId",
  "decision": "BUCKET_1",
  "reason_code": "CANONICAL_UUID_SUFFIX",
  "confidence": "HIGH",
  "detail": "Sufixo Id padrão HB, identifica agregado Job, sempre uuid_v4"
}
```
→ **v6-candidate imediata**

### Campo: `id`
```json
{
  "field": "id",
  "decision": "BUCKET_4",
  "reason_code": "AMBIGUOUS_GENERIC_ID",
  "confidence": "N/A (Bucket 4)",
  "detail": "Campo id genérico sem qualificador, pode ser uuid, opaque, ou numeric conforme contexto"
}
```
→ **Fora de qualquer automático**



---

## Sessão 4C — Critério de Sucesso

### ✅ 4C é bem-sucedida QUANDO:

1. **132/132 campos auditados** — Zero campos em limbo
2. **Cada campo:**
   - Tem decisão binária clara (`BUCKET_1` ou `BUCKET_4`)
   - Tem motivo classificado (um dos códigos de taxonomia)
   - Tem confidence atribuída (`HIGH` ou `MEDIUM` para Bucket 1, `N/A` para Bucket 4)
   - Tem detalhamento (por que não é o outro bucket?)
3. **Baseline atualizada** com estrutura JSON agregada (veja secção anterior "Output Obrigatório")
4. **Listas limpas:**
   - Lista de v6-candidates `HIGH` (automáticas)
   - Lista de v6-candidates `MEDIUM` (requer review)
   - Lista de reclassificados para Bucket 4
   - Nenhuma "quando tiver tempo depois"
5. **Distribuição de confidence é razoável** — Não 100% MEDIUM (indicaria heurística ruim) nem 100% HIGH (indicaria oversimplificação)

### ❌ 4C FRACASSOU se:

- Há campos ainda com "ambíguo, precisa revisar"
- Motivo não é esclarecedor ou está vago
- Output não é rastreável por campo
- Decisões variam arbitrariamente entre campos similares
- Confidence está vago ou ausente (todos HIGH = problema, todos MEDIUM = problema)

### 🎯 Métrica de Qualidade

A **distribuição de confidence** é diagnóstico da qualidade da auditoria:

- **85–95% HIGH, 5–15% MEDIUM:** Heurística v5 era boa, audit confirmou maioria
- **50–50 ou mais MEDIUM:** Casos são genuinamente limítrofes; v6 conservadora recomendada
- **Quase 100% de qualquer um:** Revisar — pode indicar padrão muito rigidez ou muito frouxidão

**Tanto um resultado quanto o outro prova que a auditoria foi estruturada.**

---

## Exemplo: Executar 4C

### Passo 1: Extrair lista dos 132

```bash
# Pseudocódigo: ler latest.json, extrair campos Bucket 1-restante
# Resultado: CSV ou JSON com 132 linhas
```

### Passo 2: Para cada campo, preencher:

| Campo | Pattern | Decision | Reason | Detail |
|-------|---------|----------|--------|--------|
| `createdAt` | `timestamp_utc` | BUCKET_1 | MISS_HEURISTIC_INDENTATION | "6 espaços de indent, v5 regex usava `(?:.*\n)*?` com 4 espaços" |
| `id` | `uuid_v4` | BUCKET_4 | AMBIGUOUS_GENERIC_ID | "Genérico absoluto, pode ser uuid ou opaque conforme contexto" |
| `receivedAt` | `timestamp_utc` | BUCKET_1 | CANONICAL_TIMESTAMP_SUFFIX | "Sufixo At clara, inequívoco, candidato v6" |

### Passo 3: Gerar output estruturado

```json
{
  "session": "4C",
  "date": "2026-03-XX",
  "audit_result": {
    "bucket1_staying": 75,
    "bucket4_reclassified": 57,
    "by_reason_code": {
      "CANONICAL_TIMESTAMP_SUFFIX": 35,
      "CANONICAL_UUID_SUFFIX": 28,
      ...
    }
  },
  "fields": [
    {
      "field": "createdAt",
      "decision": "BUCKET_1",
      "reason_code": "MISS_HEURISTIC_INDENTATION",
      ...
    },
    ...
  ]
}
```

### Passo 4: Commit

```bash
git add BACKLOG_2C_BUCKET1_AUDIT_RESULTS.json SESSION_HANDOFF.md
git commit -m "audit(2C-4C): 132 Bucket 1-remanescente reclassificados, taxonomia de motivos registrada"
```

---

## Saídas Esperadas vs Aceitas

| Cenário | Distribuição Confidence | Decisão v6 | Status |
|---------|------------------------|-----------|--------|
| 75 Bucket 1 + 57 Bucket 4, 90% HIGH | Maioria HIGH, poucos MEDIUM | v6 pode ser agressiva | ✅ Go |
| 75 Bucket 1 + 57 Bucket 4, 60% HIGH / 40% MEDIUM | Significativo MEDIUM | v6 conservadora (include HIGH only) | ✅ Go |
| 100 Bucket 1 + 32 Bucket 4, 95% HIGH | Muito uniforme | v6 pode cobrir mais | ✅ Go |
| 40 Bucket 1 + 92 Bucket 4, 80% HIGH | Menos candidates mas claros | v6 pequena, foco Bucket 4 | ✅ Go |
| 50 Bucket 1 com motivos diversos + 82 Bucket 4 | Padrão heterogêneo | Inspect antes de v6 | ✅ Go |
| "Não consigo decidir, MEDIUM pra quase tudo" | 80%+ MEDIUM | ❌ Não vai passar em review | ❌ FAIL |
| "Tudo é HIGH, muito fácil" | 100% HIGH | ❌ Verificar se audit foi superficial | ❌ FAIL |

A meta é **encerrar a incerteza com rastreabilidade**, não ser perfeito. A confidence é ferramenta para priorizar v6, não julgamento de qualidade.



