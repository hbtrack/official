# BACKLOG_ITEM_2 — Decisão de Escopo (2026-03-20)

## Resumo Executivo

O gate `CROSS_SPEC_ALIGNMENT_GATE` reporta **542 violações** que foram separadas em duas **trilhas de trabalho independentes**:

| Item | Tipo | Contagem | Descrição | Próxima Ação |
|------|------|----------|-----------|--------------|
| **2C** | Pattern/Format | 383 | Campos sem padrão canônico (uuid_v4, timestamp_utc, date_only, trace_id, request_id) | Sessão 4B: Aplicar x-domain-pattern-ref |
| **2D** | Enum Semantics | 155 | Enums sem referência explícita a axiomas de domínio | Sessão 5A: Normalização + geração |

---

## Decisão: Por Que Separar?

### Razão 1: Estratégias Diferentes
- **2C (Pattern):** Automático + determinístico (`x-domain-pattern-ref`)
- **2D (Enum):** Semântico + decisão arquitetural (modelo de domínio)

### Razão 2: Riscos Diferentes
- **2C:** Baixo risco, reversível, regra simples
- **2D:** Alto risco, afeta contrato semântico, requer consenso

### Razão 3: Verificação Diferente
- **2C:** Validação: padrão correspondência
- **2D:** Validação: conformidade axiomática + enums gerados

---

## ITEM 2C — Pattern/Format Violations (383)

### Distribuição

```
uuid_v4         206 (53.8%)  ← campo Id / id genérico
timestamp_utc   105 (27.4%)  ← campos sufixo At  
trace_id         27 (7.0%)   ← traceId
request_id       27 (7.0%)   ← requestId
date_only        18 (4.7%)   ← campos sufixo Date
```

### 4-Bucket Classificação

| Bucket | Descrição | Ação | Contagem Estimada |
|--------|-----------|------|-------------------|
| **1** | Canônico óbvio (IA pode arrumar) | Patch automático | ~280 |
| **2** | Padrão específico de domínio | Revisão + padrão customizado | ~40 |
| **3** | Gate cego a nomes válidos | Ajuste detector | ~35 |
| **4** | Ambíguo (i.e., `id` genérico) | Revisão manual | ~28 |

### Execução Recomendada (Sessão 4B)

1. **Pré-fixing:** Rodar classificação completa em JSON
2. **Automático (Bucket 1):** Adicionar `x-domain-pattern-ref` em 280 campos
3. **Teste:** Rerodar validador, medir queda
4. **Manual (Buckets 2-4):** Decisão caso-a-caso
5. **Commit:** Registrar `Bucket 1 PASS` + `Buckets 2-4 RDR`

---

## ITEM 2D — Enum Alignment (155)

### Violação

```
"Enum encontrado sem `x-domain-enum-ref` (proibido por contrato)"
```

### Root Cause

Enums em schemas não fazem referência a valores canônicos em `DOMAIN_AXIOMS.json`. Contrato exige:
```yaml
# Errado ❌
enum: [PENDING, ACTIVE, CLOSED]

# Certo ✓
x-domain-enum-ref: training_session_statuses
```

### Execução Recomendada (Sessão 5A)

1. **Mapeamento:** Encontrar todos enums únicos
2. **Axioma:** Decidir quais vão para DOMAIN_AXIOMS vs manutenção inline
3. **Geração:** Atualizar axiomas
4. **Refs:** Adicionar x-domain-enum-ref em 155 campos
5. **Teste:** CROSS_SPEC_ALIGNMENT_GATE PASS

---

## Critério de Pronto para Sessão 4B

✅ **Item 2C Executado se:**
- [ ] Bucket 1 (280/383 estimado) remediado
- [ ] Validador rerrodado
- [ ] Contagem final: `patterns_remaining` + `buckets_2-4` explicitado
- [ ] Commit: `feat(2C): bucket 1 automatizado — X violações corrigidas`

⏳ **Item 2D Bloqueado Até:**
- [ ] 2C Bucket 1 completo (ou decision taken to parallelize)

---

## Arquivos

- SESSION_HANDOFF.md — Descrição curta do estado
- BACKLOG_ITEM_2C_BASELINE.json — 383 patterns + 155 enums contagem
- (próximo session) 2C_REMEDIATION_REPORT.json — Detalhes da execução
- (próximo session) 2D_ENUM_MAPPING.json — Axiomas vs inline decision

---

## Notas Técnicas

### Por que não `pattern: <regex>` literal?

Aos primeiros tentar adicionar o regex literal do DOMAIN_AXIOMS:
```yaml
createdAt:
  type: string
  pattern: ^\d{4}-...$
```

O validador **ainda reportava violação** porque procura por:
1. `x-domain-pattern-ref: timestamp_utc` (referência canônica), ou
2. Conformidade verificável a partir do axioma

**Solução:** Usar `x-domain-pattern-ref` + deixar o validador resolver o regex via axioma.

### Impacto esperado

- **Antes (atual):** 382 patern FAIL + 155 enum FAIL = 542 total
- **Após 2C Bucket 1:** ~100 patterns FAIL + 155 enum FAIL = ~255 total (-47%)
- **Após 2D completo:** ~0 FAIL no CROSS_SPEC_ALIGNMENT_GATE (ou deliberado waiver)

---

**Tempo de conclusão estimado:**
- **2C Bucket 1:** 45 min (automático)
- **2C Buckets 2–4:** 2–3 horas (revisão)
- **2D mapping:** 1–2 horas (geração axioma)
- **2D refs:** 45 min (automático)

**Total:** 4–7 horas de engenharia distribuído em 2 sessões.
