# 4C.2.v2 — Estratégia de Remedição Estrutural

**Execução:** 2026-03-20  
**Fase:** Diagnóstico Structural (4C.2.v2 COMPLETE)  
**Status:** ✅ PRONTO PARA DECISÃO

---

## 📊 Achados Diagnósticos

### Overview
- **Total violations (por ocorrência):** 200
- **Campos únicos:** 90
- **Fixáveis:** 37 campos (41%)
- **Bloqueados:** 53 campos (58%)

### Categorias Detalhadas

#### 🟢 **FIXÁVEIS (37 campos)**

| Tipo | Count | Ação | Esforço |
|------|-------|------|---------|
| **Type Array** | 6 | Mudar `['string', 'null']` para `'string'` apenas | LOW |
| **Pattern Missing** | 19 | Adicionar padrão esperado | LOW |
| **Pattern Wrong** | 12 | Substituir padrão errado por correto | MEDIUM |

**Exemplo - Pattern Missing:**
```yaml
# Antes
athleteUserId:
  type: string

# Depois
athleteUserId:
  type: string
  pattern: ^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$
```

**Exemplo - Type Array:**
```yaml
# Antes
correlationId:
  type: ['string', 'null']

# Depois
correlationId:
  type: string
```

#### 🔴 **BLOQUEADOS (53 campos)**

| Tipo | Count | Razão | Ação Requerida |
|------|-------|-------|-----------------|
| **Not in Schema** | 42 | Campo não existe em nenhum arquivo de schema | Definir campo antes de aplicar pattern |
| **Type Wrong** | 0 | – | – |
| **Falso Positivo** | 11 | Campo tem pattern correto mas gate falha | Investigar gate logic |

**Campos Not in Schema (amostra):**
- `decidedByCoachId`, `suggestedAt`, `generatedTrainingSessionId`, `transcodeCompletedAt`, `createdAt` (+37 more)

---

## 🎯 Opções Estratégicas

### **OPÇÃO A (Recomendada): 4C.2.v2.a — Quick Win**

**Escopo:** Executar fases 1-3 apenas (campos fixáveis)

**Ações:**
1. Fase 1: Fix 6 campos type array → change `['string', 'null']` to `'string'`
2. Fase 2: Add pattern a 19 campos missing
3. Fase 3: Fix pattern em 12 campos wrong
4. Gate revalidation

**Resultado Esperado:**
- 200 violations → ~40-60 violations (se ~70% sucesso em aplicação)
- Redução: ~140-160 violations
- Métricas: Prova de conceito que remediation é possível

**Tempo Estimado:** 30 min (automation + validation)

**Risco:** Médio (alguns campos podem ter padrões mais complexos)

---

### **OPÇÃO B: 4C.2.v2.b — Full Structural Fix**

**Escopo:** Opção A + fases 4 (NOT_IN_SCHEMA)

**Ações Adicionais:**
1. Analisar 42 campos não em schema
2. Decidir quais devem ser criados vs. ignorados
3. Criar definições missing nas schemas apropriadas
4. Aplicar patterns

**Resultado Esperado:**
- 200 violations → potencialmente ~0-20 (se todos 42 campos resolvidos)
- Mais alinhado com gate expectations

**Tempo Estimado:** 2-3 horas (requer decisão manual por campo)

**Risco:** Alto (requer conhecimento de quais campos devem existir em quais schemas)

---

### **OPÇÃO C: Skip 4C.2, Jump to 4D.2**

**Escopo:** Defer pattern automation, atacar CONTEXT_DEPENDENT manually

**Racional:** Se 42/90 campos bloqueados não tem schema, maybe pattern-first approach isn't viable. Pivot to domain-expert review.

**Tempo:** ~4-5 horas (domain decision-making)

**Risco:** Alto (necessita expertise de quem sabe quais campos são semanticamente válidos)

---

## 📋 Recomendação

**→ Execute OPÇÃO A (4C.2.v2.a) AGORA**

**Motivos:**
1. ✅ 37 campos são remediáveis COM SEGURANÇA
2. ✅ 6+19 campos têm remediation trivial (type fix + add pattern)
3. ✅ 12 campos need pattern update (medium effort)
4. ✅ Vai reduzir violations significativamente (~70% success)
5. ✅ Se sucesso, prova que estratégia é viável
6. ✅ Se falha, teremos mais dados para decidir Opção B vs C

**Próximo Passo:** User approves OPÇÃO A → Execute 4C.2.v2.a (FASE 1-3)

---

## 📝 Campos por Categoria

### Type Array (6)
`correlationId`, `targetResourceId`, `organizationId`, `seniorCoachId`, `videoAnalysisId`, `transcodingJobId`

### Pattern Missing (19)
`actorUserId`, `athleteUserId`, `awayTeamId`, `clipId`, `competitionId`, `deliveryId`, `entryId`, `eventId`, `grantedByUserId`, `homeTeamId`, `jobId`, `matchId`, `needId`, `originId`, `questionnaireId`, `recipientUserId`, `relatedId`, `requestId`, `roomId`

### Pattern Wrong (12)
`completionEvidenceId`, `lastAttemptAt`, `deliveredAt`, `requestedAt`, `needId`, `videoAssetId`, `teamId`, `leaderboardId`, `participantId`, `documentId`, `feedbackId`, `evaluationId`

### Not in Schema (42)
`decidedByCoachId`, `suggestedAt`, `generatedTrainingSessionId`, `transcodeCompletedAt`, `createdAt`, ... (+37)

---

## 📊 Metriquês CDD

| Métrica | Baseline | Esperado 4C.2.v2.a |
|---------|----------|-------------------|
| Total Violations | 408 | ~250-280 |
| Pattern Violations | 249 | ~80-120 |
| Reduction % | — | 48-52% |
| Fields Fixed | 0 | 37 |
| Automation %ile | 0 | 41% |

---

## ⏭️ Próximos Passos (Dependendo Aprovação)

**Se Opção A → 4C.2.v2.a:**
1. Create `remediate_4c2_v2a_phases123.py`
2. Implement type array fixes (6)
3. Implement pattern additions (19)
4. Implement pattern updates (12)
5. Run gate validation
6. Commit + update SESSION_HANDOFF.md

**Se Opção B → 4C.2.v2.b:**
1. Manual analysis of 42 NOT_IN_SCHEMA fields
2. Create field definitions where needed
3. Run remediation
4. Gate validation

**Se Opção C → 4D.2:**
1. Jump to CONTEXT_DEPENDENT manual review
2. Defer pattern concerns temporarily

---

**Decision awaited → Ready when you are** ✨
