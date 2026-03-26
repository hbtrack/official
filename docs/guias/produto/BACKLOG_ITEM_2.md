# BACKLOG ITEM 2 — CROSS_SPEC_ALIGNMENT_GATE Validação Real
> Documento de apoio humano, não canônico e não soberano. Serve para investigação histórica e registro de execução; não substitui o canon nem os gates ativos.

## Status: INVESTIGAÇÃO COMPLETA — PIVOT PARA ITEM 2C

**Data:** 2026-03-20  
**Epic:** Teste real de revalidação cross-module com dependência quebrada  
**Prioridade:** Alta  
**Scope:** 3 sub-itens independentes (4 + 158 + 374 → 542 violações de padrão/formato)

**MUDANÇA IMPORTANTE:** Item 2A investigado e concluído como "não reproduzido". O trabalho real concentra-se em Item 2C (542 violações de padrão canonical uuid_v4, timestamp_utc, etc.)

---

## Contexto

CROSS_SPEC_ALIGNMENT_GATE valida:
- **Arazzo operationId** → deve existir em OpenAPI root ✅ **(Item 2A: Feito — 0 violações)**
- **Enums** → devem ser consistentes entre OpenAPI, AsyncAPI, JSON Schema, axiomas **(Item 2B)**
- **Formats** → padrões regex compartilhados entre superfícies **(Item 2C: PRÓXIMO ATIVO — 542 violações)**

**Mapeamento atual:** 542 violações consolidadas (Item 2A não contribui; focos reais em patterns + enums).

**Objetivo:** Resolver Item 2C (patterns) e Item 2B (enums) com estratégia clara (automática ou manual).

---

## Item 2A: Arazzo Links — ENCERRADO (Não Reproduzido / Já Resolvido)

**Status:** ✅ CONCLUÍDO — Item foi superado pelos fatos durante desenvolvimento anterior

### Hipótese Original

Arazzo workflows referenciam operationId que não existem (ou existem em formato diferente) no OpenAPI root. 

- **Severidade estimada:** Alta (quebra automação de fluxo)  
- **Escopo estimado:** 4 workflows Arazzo com links inválidos

### Investigação Executada (2026-03-20)

**Técnica:** Validação isolada de operationIds em Arazzo vs OpenAPI root + paths/

1. Carregamento de todos os operationIds disponíveis:
   - OpenAPI root (contracts/openapi/openapi.yaml): 0 em paths diretos
   - OpenAPI paths/ (contracts/openapi/paths/*.yaml): 153 operationIds
   - **Total disponível:** 153 operationIds

2. Varredura de todos os Arazzo files (24 arquivos):
   - Procura por `operationId:` em diretos (excluindo `PLACEHOLDER`)
   - Validação contra os 153 operationIds disponíveis
   - **Resultado:** 0 operationIds faltando

### Achado

| Verificação | Resultado |
|---|---|
| operationIds ausentes em OpenAPI | **0** |
| Arazzo com links quebrados | **0** |
| Violações atribuíveis a operationId | **0** |

### Conclusão

**Item 2A não é mais trabalho pendente.** As operationId usadas por Arazzo workflows existem todas no OpenAPI. A hipótese original de 4 links quebrados não foi reproduzida — foi por superado durante desenvolvimento anterior.

**Causa provável:** Sincronização com renomeações de operationIds em OpenAPI root ou preenchimento de workflows após definição de operationIds no OpenAPI.

### Ação Tomada

- ✅ Configuração gate CROSS_SPEC_ALIGNMENT_GATE em _precommit_ids
- ✅ Validação confirma: gate EXECUTA, mas falha por OTHER reasons (patterns/enums), não por operationIds
- ✅ Reclassificação: foco da iniciativa pivota para **Item 2C** (542 violações de formato/padrão)

---

## 🎯 PRÓXIMO ATIVO: Item 2C — Pattern/Format Violations

**Status:** PREPARADO PARA EXECUÇÃO

**Scope:** 542 violações de formatação em campos UUID e timestamp

**Violações reportadas:**
- `uuid_v4` pattern: 122+ campos (jobId, deliveryId, exerciseId, entryId, eventId, etc.)
- `timestamp_utc` pattern: 180+ campos (deliveredAt, distributedAt, endedAt, failedAt, etc.)
- `date_only` pattern: 5+ campos (endDate, startDate, etc.)
- Outras patterns: custom fields

**Artefatos afetados:**
- contracts/openapi/components/schemas/ (13+ violações)
- contracts/openapi/paths/ (18+ violações)
- contracts/asyncapi/components/schemas/ (160+ violações)
- contracts/schemas/ (JSON Schema, ~20+ violações)

**Abordagem recomendada:**
1. Identificar campos que devem ser UUID mas estão sem pattern (ou pattern genérico)
2. Identificar timestamps sem pattern canônico
3. Aplicar pattern correto conforme axiomas (DOMAIN_AXIOMS.json define canonical patterns)
4. Validar gate: 542 → 0

**Próxima ação:** Iniciar investigação de Item 2C quando aprovado pelo usuário.

---

## Item 2B: Enum Violations (158 violações)

### Causa Raiz

Enums declarados em um lugar (OpenAPI, AsyncAPI, axiomas) diferem de outro. Exemplo:

```
OpenAPI: enum: [ACTIVE, INACTIVE, SUSPENDED]
AsyncAPI: enum: [ACTIVE, INACTIVE, BLOCKED]  ← mismatch
Axioms:  VALID_STATES: [ACTIVE, INACTIVE]    ← diferente de ambos
```

**Severidade:** Alta (quebra validação de estado)  
**Escopo:** 158 divergências em campos de estado, status, role, etc.

### Estratégia

1. **Diagnóstico:** Agrupar por tipo de enum (status, role, state, etc.)
2. **Classificação:** Verdadeira divergência vs typo vs deprecação intencional
3. **Resolução:**
   - **Opção A (Automático):** Consolidar em axiomas → gerar OpenAPI/AsyncAPI via template
   - **Opção B (Manual):** Revisar cada grupo, decidir enum canônico, aplicar em todos
4. **Gate:** CROSS_SPEC_ALIGNMENT_GATE FAIL crisp: enum mismatch → blocking_code

### Critério de Pronto (Binário)

✅ **PRONTO** quando:
- Todos enums em OpenAPI, AsyncAPI, axiomas são idênticos
- Gate executa: PASS (zero enum violations)
- Fonte de verdade declarada (axiomas ou OpenAPI como SSOT)

❌ **NÃO PRONTO** quando:
- Qualquer enum ainda divergente

### Decisão: Automático vs Manual

**Decisão:** AUTOMÁTICO (com revisão spot-check)

**Por quê:** Enums são dados, padrão é consolidar em axiomas + gerar. Menos risco que renomear operationIds.

**Abordagem:**
1. Screamng heuristicamente por tipo (extrair enums de OpenAPI + axiomas)
2. Gerar conflitos óbvios + decidir winner (exemplo: axiomas é SSOT)
3. Aplicar template generator para sincronizar
4. Teste gate de validação
5. Spot-check manual de 10 enums críticos (autenticação, acesso, estado)

---

## Item 2C: Format Patterns (374 violações)

### Causa Raiz

Padrões regex/formatos compartilhados entre módulos não são sincronizados. Exemplo:

```
OpenAPI:  pattern: '^[a-z0-9_-]{3,50}$'   (team name)
AsyncAPI: pattern: '^[A-Z0-9]{3,50}$'     ← diferente, rejeita lowercase
Axioms:   TEAM_NAME_PATTERN: '...'        ← terceira versão
```

**Severidade:** Média-Alta (quebra validação de dados em produção)  
**Escopo:** 374 divergências (maior categoria)

### Estratégia

1. **Diagnóstico:** Mapear quais tipos de campos têm padrões (uuid, email, domain, IDs, nomes, etc.)
2. **Consolidação:** Centralizar em axiomas/config (uma fonte de verdade)
3. **Geração:** Template que lê axiomas → injeta padrões em OpenAPI/AsyncAPI/JSON Schema
4. **Validação:** Gate executa com zero format pattern violations
5. **Automação:** Script CI que valida sincronização automaticamente

### Critério de Pronto (Binário)

✅ **PRONTO** quando:
- Padrão canônico (source) declarado em axiomas para cada tipo de campo
- OpenAPI, AsyncAPI, JSON Schema têm o mesmo padrão para cada campo
- Gate executa: PASS (zero format pattern violations)
- CI roda verificação automática de sincronização

❌ **NÃO PRONTO** quando:
- Qualquer padrão divergente ainda existe

### Decisão: Automático vs Manual

**Decisão:** AUTOMÁTICO + CI ENFORCEMENT

**Por quê:** 374 violações = impossível revisar manualmente. Padrão é transformação sistemática.

**Abordagem:**
1. Scrit que lê axiomas → valida OpenAPI/AsyncAPI/JSON Schema
2. Gera diffs claros (padrão esperado vs real)
3. Script generator que aplica automaticamente
4. Teste gate após aplicação
5. CI job que bloqueia PRs com padrões desatualizados

---

## Sequência de Execução Proposta

```
2A (Arazzo Links)
    ↓ Diagnóstico + manual fix
    ↓ Gate PASS
    ↓
2B (Enum Violations)
    ↓ Diagnóstico + automático consolidate
    ↓ Spot-check 10 críticos
    ↓ Gate PASS
    ↓
2C (Format Patterns)
    ↓ Diagnóstico + automático generate
    ↓ CI enforcement setup
    ↓ Gate PASS
```

**Estimativa:** 2A (1-2h manual), 2B (2-3h automático + review), 2C (3-4h automático + CI)

---

## Teste de Validação Final

Após os 3 sub-itens:

1. **Breaker Test:** Alterar intencionalmente um enum/pattern → gate FAIL ✅
2. **Cross-module Test:** Mudar contrato em módulo base → gate detecta impacto em dependentes ✅
3. **CI Test:** PR que tenta padrão desatualizado → bloqueado automaticamente ✅

---

## Pronto para começar?

Confirme a ordem e estratégia (especialmente: Automático vs Manual para cada sub-item).
