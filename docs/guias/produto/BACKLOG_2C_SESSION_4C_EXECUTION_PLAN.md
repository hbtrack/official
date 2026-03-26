# Sessão 4C — Plano de Execução

**Status:** ✅ PRONTO PARA EXECUÇÃO  
**Data de Aprovação:** 2026-03-20  
**Responsabilidade:** Auditar 132 campos Bucket 1-remanescente

---

## Ordem de Execução Fixa

### PASSO 1: Extrair & Auditar (Raw Output)

```bash
# Extrair lista dos 132 Bucket 1-remanescente do latest.json
# Para cada campo:
#   - decision (BUCKET_1 | BUCKET_4)
#   - reason_code (taxonomia controlada)
#   - confidence (HIGH | MEDIUM para B1, N/A para B4)
#   - reason_detail (esclarecedor)
#   - locations (1-3 exemplos de arquivo:line)

# Salvar em: BACKLOG_2C_SESSION_4C_RAW_AUDIT.json
```

**Formato:**
```json
{
  "field": "createdAt",
  "decision": "BUCKET_1",
  "reason_code": "CANONICAL_TIMESTAMP_SUFFIX",
  "confidence": "HIGH",
  "reason_detail": "...",
  "locations": ["path:line"]
}
```

### PASSO 2: Agregar Imediatamente

```bash
# Ler BACKLOG_2C_SESSION_4C_RAW_AUDIT.json
# Agregar:
#   - Por decision (BUCKET_1, BUCKET_4)
#   - Por reason_code (contar frequencies)
#   - Por confidence dentro de BUCKET_1 (HIGH, MEDIUM)
#   - Gerar listas por destino

# Salvar em: BACKLOG_2C_SESSION_4C_AGGREGATED.json
```

**Output:**
```json
{
  "bucket1_staying": {
    "total": X,
    "by_confidence": { "HIGH": X, "MEDIUM": X },
    "by_reason_code": { "CANONICAL_TIMESTAMP_SUFFIX": X, ... }
  },
  "bucket4_reclassified": {
    "total": Y,
    "by_reason_code": { ... }
  },
  "v6_candidates": {
    "high_confidence": X,
    "medium_confidence_review": Y,
    "total": Z
  },
  "zero_undecided": true
}
```

### PASSO 3: Revisar Distribuição (Quality Gate)

⚠️ **CRÍTICO — Este passo detecta distorções de taxonomia**

Verificar:

1. **Confidence distribution é balanceada?**
   - ✅ 85–95% HIGH, 5–15% MEDIUM → Heurística v5 boa
   - ⚠️ 60–70% HIGH, 30–40% MEDIUM → Casos limítrofes reais
   - ❌ <50% HIGH → Revisar se audit foi muito severa
   - ❌ >95% HIGH → Revisar se audit foi muito leniente

2. **Reason codes excessivamente concentrados?**
   - ✅ Espalhado por 5–8 categorias → Padrão saudável
   - ⚠️ 70%+ em 1 categoria → Pode indicar missed pattern
   - ❌ 20+ categorias únicas → Possível oversegmentação

3. **Nenhum campo ficou em "undecided"?**
   - ✅ 132/132 tem decision
   - ❌ Qualquer campo sem → BLOQUEIO, revisar

Se alguma métrica acende ⚠️ ou ❌:
- Não descarta 4C, mas **marca para investigação pós-4C**
- Continua com output atual
- Registra na decisão operacional

### PASSO 4: Declarar 4C Concluída

**Saída Obrigatória:**

1. **BACKLOG_2C_SESSION_4C_RAW_AUDIT.json** — Os 132 casos auditados
2. **BACKLOG_2C_SESSION_4C_AGGREGATED.json** — Resumo agregado
3. **Resumo textual curto:**
   ```
   4C CONCLUÍDO
   - 132/132 auditados
   - HIGH: X (v6 imediata)
   - MEDIUM: Y (v6 com review)
   - Bucket 4: Z (reclassificado)
   - Decisão v6: [PROSSEGUIR COM HIGH | REVISAR MEDIUM ANTES | DESCARTA V6]
   ```

4. **git commit:**
   ```bash
   git add BACKLOG_2C_SESSION_4C_RAW_AUDIT.json \
           BACKLOG_2C_SESSION_4C_AGGREGATED.json \
           SESSION_HANDOFF.md
   git commit -m "audit(2C-4C): 132 Bucket 1-restante auditados, taxonomia registrada, v6 strategy decidida"
   ```

---

## Critério de Aceite Final (Go/No-Go)

### ✅ Condição de Aceite (4C PASSA)

- [ ] 132/132 campos auditados com decision + reason_code + confidence
- [ ] Zero campos em "undecided" ou "revisar depois"
- [ ] Distribuição agregada revisada e considerada **plausível** (nem todas métricas perfeitas, mas nenhuma bandeira vermelha crítica)
- [ ] JSON artifacts validados (sintaxe correta, estrutura consistente)
- [ ] Commit registrado com rastreabilidade histórica

### ❌ Condição de Bloqueio (4C FALHA)

- [ ] Qualquer campo sem decision
- [ ] Distribuição com <50% HIGH ou >95% HIGH sem explicação
- [ ] Reason codes incompreensível ou não taxonomizado
- [ ] Output não rastreável ou agregação inválida

---

## Próximos Gates (após 4C PASSAR)

### Imediato (Sessão 4C.1-2)

- **Se HIGH >= 60:** v6 pode começar com esses (implementação segura)
- **Se MEDIUM >= 15:** Revisar MEDIUM casos antes de incluir em v6
- **Se Bucket 4 >= 50:** Preparar decision-tree para 4D

### Desacoplado (Sessão 4D+)

- 4D: Decision-tree para os ~57 Bucket 4 ambíguos
- 5A: 147 enums (2D), trilha paralela

---

## Checklist de Execução

- [ ] Ler este documento antes de começar
- [ ] Executar PASSO 1 (extrair & auditar 132)
- [ ] Executar PASSO 2 (agregar)
- [ ] PARAR e revisar PASSO 3 (qualidade)
- [ ] Registrar observações de PASSO 3
- [ ] Executar PASSO 4 (declarar concluída)
- [ ] Commitar com rastreabilidade
- [ ] Reportar status em SESSION_HANDOFF.md

**Nota:** Não itere o design. Não redesenhe a taxonomia durante execução. Não mude o formato JSON. Execute como definido.

