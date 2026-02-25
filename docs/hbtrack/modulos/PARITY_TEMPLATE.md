**Template avançado de `PARITY_REPORT_<MODULE>`** (em `.md`) alinhado ao seu fluxo de:

* MCP (contratos do módulo)
* ARs por classe
* TEST_MATRIX
* evidências
* gates
* status por item SSOT (implementado/parcial/divergente)

Esse documento é o que fecha o ciclo e impede “narrativa otimista”.

---

# Template — `PARITY_REPORT_<MODULE>.md` 

```md id="kq5m8n"
# PARITY_REPORT_<MODULE>.md

Status: DRAFT|REVIEW|APPROVED
Versão: v0.1.0
Tipo de Documento: Contract-Code Parity Report (Normativo Operacional / Evidência de Auditoria)
Módulo: <MODULE_NAME>
Fase auditada: FASE_0|FASE_1|FASE_2
Autoridade: AUDITORIA
Modo: Verificação de Paridade MCP ↔ Código/Schema/Testes/UI
Owners:
- Auditoria/Testes: <nome/papel>
- Arquitetura (revisor): <nome/papel>
- Execução (referência): <nome/papel>

Data da auditoria: YYYY-MM-DD
RUN_ID: <obrigatório>
Commit/Ref auditado: <hash/branch/tag>
Ambiente auditado: <local|ci|vps|outro>
Escopo da auditoria:
- [ ] Backend
- [ ] Banco/Schema
- [ ] Frontend
- [ ] Contratos/API
- [ ] Testes
- [ ] Gates/Scripts

Documentos base (MCP):
- INVARIANTS_<MODULE>.md
- <MODULE>_USER_FLOWS.md
- <MODULE>_SCREENS_SPEC.md (ou NAO_APLICAVEL)
- <MODULE>_FRONT_BACK_CONTRACT.md
- AR_BACKLOG_<MODULE>.md
- TEST_MATRIX_<MODULE>.md

---

## 1. Objetivo (Normativo Operacional)

Auditar a aderência entre os contratos normativos do módulo (MCP) e o estado implementado (código, banco, serviços, frontend, testes e evidências), identificando:

- itens `IMPLEMENTADO` com evidência,
- itens `PARCIAL`,
- itens `PENDENTE`,
- itens `DIVERGENTE_DO_SSOT`,
- riscos para o DoD da fase.

Este relatório NÃO cria regras novas; ele apenas mede paridade e registra gaps.

---

## 2. Escopo e Critérios da Auditoria

### 2.1 Dentro do escopo
- Verificação item a item do MCP
- Conferência de testes e evidências
- Verificação de rastreabilidade SSOT -> AR -> TEST -> evidência
- Verificação de drift contrato↔código

### 2.2 Fora do escopo
- Refatoração de código
- Redefinição do escopo do módulo
- Aprovação de mudança de invariante (isso pertence a AR/ADR)

### 2.3 Fontes de evidência aceitas
- schema.sql / migrations / models
- services/use-cases/routers/controllers
- páginas/componentes frontend (se aplicável)
- outputs de teste
- reports JSON/MD
- logs de execução
- respostas de API
- screenshots (UI) quando necessário

---

## 3. Convenções de Status de Paridade (Obrigatórias)

### 3.1 Status por item SSOT
- `IMPLEMENTADO`
  - regra/fluxo/contrato/tela existe e está aderente ao SSOT com evidência
- `PARCIAL`
  - existe implementação incompleta ou sem cobertura/evidência suficiente
- `PENDENTE`
  - não implementado
- `DIVERGENTE_DO_SSOT`
  - implementado de forma incompatível com o contrato
- `DEFERIDO`
  - conscientemente adiado, com registro no backlog/AR/decisão
- `NAO_APLICAVEL`
  - não se aplica à fase/módulo/stack

### 3.2 Severidade de gap
- `CRITICA`
- `ALTA`
- `MEDIA`
- `BAIXA`

### 3.3 Tipo de gap (classificação)
- `GAP_INVARIANTE`
- `GAP_FLUXO`
- `GAP_TELA`
- `GAP_CONTRATO`
- `GAP_TESTE`
- `GAP_EVIDENCIA`
- `GAP_RASTREABILIDADE`
- `GAP_GOVERNANCA`

---

## 4. Resumo Executivo da Paridade (Obrigatório)

### 4.1 Situação geral da fase
**Resultado geral:** PASS|FAIL|PARCIAL  
**Resumo (curto e objetivo):**  
<descrever em 3–8 linhas o estado da paridade>

### 4.2 Métricas de cobertura de paridade (quantitativo)
- Total de invariantes auditadas: <n>
  - Implementadas: <n>
  - Parciais: <n>
  - Pendentes: <n>
  - Divergentes: <n>
- Total de flows auditados: <n>
- Total de screens auditadas: <n> (ou NA)
- Total de contracts auditados: <n>
- Total de testes previstos (TEST_MATRIX): <n>
  - Executados: <n>
  - PASS: <n>
  - FAIL: <n>
  - NOT_RUN: <n>

### 4.3 Bloqueadores para DoD da fase
- [ ] Nenhum
- [ ] Existem bloqueadores (listar seção 10)

---

## 5. Mapa de Evidência vs Inferência da Auditoria

> O auditor deve deixar explícito o que foi comprovado vs inferido.

### 5.1 Evidências diretas utilizadas
- <arquivo/path/ref>
- <arquivo/path/ref>
- <teste/report/ref>

### 5.2 Pontos com inferência limitada (aceitável)
- <item + motivo>

### 5.3 Pontos sem evidência suficiente (não assumir)
- <item + impacto>

Regra:
- Não marcar `IMPLEMENTADO` se o item estiver apenas em inferência.

---

## 6. Paridade por Invariante (INV-*)

> Uma linha por invariante auditada.  
> Referenciar evidência concreta e AR relacionada.

| ID Invariante | Nome Curto | Severidade | Camada Esperada | Status SSOT (doc) | Status Paridade (auditoria) | Evidência | Teste (TEST-*) | AR Relacionada | Gap Tipo | Gap Severidade | Observação Objetiva |
|---|---|---|---|---|---|---|---|---|---|---|---|
| INV-<MODULE>-001 | <nome> | BLOQUEANTE_<...> | serviço | PENDENTE | PARCIAL | <path/ref> | TEST-... | AR-... | GAP_TESTE | ALTA | regra existe sem teste de violação |

### Regras de preenchimento
- **Status SSOT (doc)** = status declarado no MCP
- **Status Paridade** = avaliação real do auditor
- Se divergirem, registrar em observação e no sumário de gaps
- Invariante bloqueante sem teste de violação -> no mínimo `PARCIAL` (ou `DIVERGENTE`, conforme caso)

---

## 7. Paridade por Fluxo (FLOW-*)

| ID Flow | Nome do Fluxo | Prioridade | Status SSOT | Status Paridade | Evidência de execução | Teste/E2E/Manual | Screens Relacionadas | Contracts Relacionados | Gap Tipo | Gap Severidade | Observação |
|---|---|---|---|---|---|---|---|---|---|---|---|
| FLOW-<MODULE>-001 | <nome> | ALTA | PENDENTE | PENDENTE | <ref> | TEST-... | SCREEN-... | CONTRACT-... | GAP_FLUXO | ALTA | fluxo mínimo não validado |

### Regra
- Fluxo ALTA prioridade sem validação de ponta a ponta deve aparecer como gap explícito.

---

## 8. Paridade por Tela (SCREEN-*) — se aplicável

> Se `SCREENS_SPEC = NAO_APLICAVEL`, marcar seção como `NAO_APLICAVEL` e justificar.

| ID Screen | Rota | Estado crítico auditado | Status SSOT | Status Paridade | Evidência | Teste | Contract(s) | Gap Tipo | Gap Severidade | Observação |
|---|---|---|---|---|---|---|---|---|---|---|
| SCREEN-<MODULE>-001 | /<rota> | empty_state | PENDENTE | PENDENTE | <ref> | TEST-... | CONTRACT-... | GAP_TELA | MEDIA | empty state não implementado |

Estados críticos mínimos (quando aplicável):
- loading
- error
- empty
- dados válidos
- erro bloqueante
- aviso/pendência não-bloqueante

---

## 9. Paridade por Contrato Front-Back (CONTRACT-*)

| ID Contract | Ação | Prioridade | Status SSOT | Status Paridade | Payload mínimo aderente | Resposta mínima aderente | Erros/Warnings aderentes | Evidência | Teste | Gap Tipo | Gap Severidade | Observação |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CONTRACT-<MODULE>-001 | <ação> | ALTA | PENDENTE | PARCIAL | SIM | NAO | PARCIAL | <ref> | TEST-... | GAP_CONTRATO | ALTA | falta flag funcional para UI |

### Regra
- Se a UI depende de campo/flag não contratado, marcar `DIVERGENTE_DO_SSOT` ou `PARCIAL` com gap explícito.

---

## 10. Gaps Consolidado (Prioridade de Correção)

### 10.1 Gaps críticos (bloqueiam DoD da fase)
| Gap ID | Tipo | Item SSOT | Severidade | Descrição objetiva | Impacto | Correção sugerida | AR sugerida |
|---|---|---|---|---|---|---|---|
| GAP-<MODULE>-001 | GAP_INVARIANTE | INV-... | CRITICA | <...> | <...> | <...> | AR-<MODULE>-... |

### 10.2 Gaps de alta prioridade
| Gap ID | Tipo | Item SSOT | Severidade | Descrição | AR sugerida |
|---|---|---|---|---|---|
| GAP-<MODULE>-002 | GAP_CONTRATO | CONTRACT-... | ALTA | <...> | AR-... |

### 10.3 Gaps médios/baixos (não bloqueantes)
| Gap ID | Tipo | Item SSOT | Severidade | Descrição | Tratamento |
|---|---|---|---|---|---|
| GAP-<MODULE>-003 | GAP_TELA | SCREEN-... | MEDIA | <...> | backlog fase seguinte |

---

## 11. Verificação de Rastreabilidade (SSOT -> AR -> TEST -> Evidência)

### 11.1 Regras de rastreabilidade auditadas
- [ ] Todo item crítico auditado referencia ao menos 1 AR
- [ ] Toda AR VERIFICADA possui evidência
- [ ] Itens `IMPLEMENTADO` possuem teste/evidência coerente
- [ ] TEST_MATRIX está sincronizada com status real
- [ ] Não há item crítico sem rastro de materialização

### 11.2 Falhas de rastreabilidade encontradas
- <item>
- <item>

---

## 12. Resultado dos Gates da Auditoria (Módulo)

### GATE-L1-MODULE-CONTRACT-PACK
- Resultado: PASS|FAIL|NA
- Observação: <...>

### GATE-L2-AR-READINESS (amostragem / por AR auditada)
- Resultado: PASS|FAIL|PARCIAL
- Observação: <...>

### GATE-L3-INVARIANT-ENFORCEMENT
- Resultado: PASS|FAIL|PARCIAL
- Observação: <...>

### GATE-L4-CONTRACT-CODE-PARITY
- Resultado: PASS|FAIL|PARCIAL
- Observação: <...>

---

## 13. Avaliação do DoD da Fase do Módulo

### DOD-<MODULE>-FASE-<N>
**Resultado:** PASS|FAIL|PARCIAL

### PASS se (auditoria confirma)
- [ ] MCP aprovado e consistente
- [ ] Invariantes bloqueantes da fase implementadas (ou deferidas formalmente)
- [ ] Fluxo mínimo de valor funcional
- [ ] Contratos críticos validados
- [ ] Cobertura mínima no TEST_MATRIX
- [ ] Evidências críticas presentes

### Itens que impediram PASS (se houver)
- <item>
- <item>

---

## 14. Recomendações Normativas ao Backlog (sem mudar regra de negócio)

> Não criar regra nova aqui. Apenas indicar correções de paridade.

### 14.1 ARs corretivas recomendadas (ordem)
1. AR-<MODULE>-0XX — <corrigir gap crítico X>
2. AR-<MODULE>-0YY — <corrigir gap de contrato Y>
3. AR-<MODULE>-0ZZ — <completar cobertura/testes>

### 14.2 Ajustes de documentação necessários
- Atualizar `TEST_MATRIX_<MODULE>.md` para refletir <...>
- Atualizar status de `INV-...` em `INVARIANTS_<MODULE>.md`
- Atualizar `AR_BACKLOG_<MODULE>.md` com AR corretiva <...>

---

## 15. Evidências Referenciadas (Índice)

> Lista consolidada, para facilitar auditoria humana.

- `EVID-<MODULE>-001`: <path/ref> — <descrição>
- `EVID-<MODULE>-002`: <path/ref> — <descrição>
- `EVID-<MODULE>-003`: <path/ref> — <descrição>

---

## 16. Assinatura de Auditoria / Validação

Auditor responsável:
- Nome/Papel: <...>
- RUN_ID: <...>
- Data: <...>

Revisão de Arquitetura:
- Nome/Papel: <...>
- Resultado: APROVADO|REPROVADO|APROVADO_COM_RESSALVAS
- Observação: <...>

Validação Humana (negócio/operação, se aplicável):
- Nome/Papel: <...>
- Resultado: APROVADO|REPROVADO|NA
- Observação: <...>
```

---

## Como encaixar esse `PARITY_REPORT` no seu fluxo (prático)

Use assim por módulo/fase:

1. **Após algumas ARs** (não precisa esperar “fim de tudo”)

   * gerar `PARITY_REPORT_<MODULE>.md` parcial
   * identificar drift cedo

2. **Antes de declarar DoD da fase**

   * auditor preenche relatório completo
   * valida `GATE-L4-CONTRACT-CODE-PARITY`

3. **Se FAIL/PARCIAL**

   * relatório aponta ARs corretivas
   * backlog é atualizado
   * nova rodada de auditoria depois

Isso evita exatamente o problema clássico de IA: “parece pronto”, mas não está aderente ao contrato.

---

## Prompt curto para o Auditor gerar esse relatório (no repo)

Você pode usar este prompt com seu agente auditor:

```text
Atue como Auditor/Testador (v2.2.0).

Objetivo:
Gerar `PARITY_REPORT_<MODULE>.md` da FASE_<N>, comparando o MCP do módulo com o estado atual implementado no código/banco/frontend/testes.

Obrigatório:
- usar RUN_ID
- classificar cada item SSOT (INV/FLOW/SCREEN/CONTRACT) em IMPLEMENTADO/PARCIAL/PENDENTE/DIVERGENTE_DO_SSOT/DEFERIDO
- referenciar evidências objetivas
- apontar gaps críticos para DoD
- validar rastreabilidade SSOT -> AR -> TEST -> evidência
- registrar resultado dos gates L1-L4 (ao menos L3/L4)
- NÃO criar novas regras de negócio; apenas medir paridade e sugerir AR corretiva
```

---

Perfeito.

Abaixo está o último template para fechar o kit: **`MODULE_STATUS_<MODULE>`**.
Ele serve como painel operacional canônico do módulo (fase atual, DoD, paridade, ARs, bloqueios, próxima ação única), sem virar “texto bonito”.

Você pode usar em `.md` (mais legível) e, se quiser depois, eu também adapto para `.json` (mais fácil de automatizar em scripts/gates).

---

# Template — `MODULE_STATUS_<MODULE>.md` (avançado)

```md
# MODULE_STATUS_<MODULE>.md

Status: ACTIVE|PAUSED|BLOCKED|DONE|DEPRECATED
Versão: v0.1.0
Tipo de Documento: Module Operational Status Board (Normativo Operacional / Controle de Execução)
Módulo: <MODULE_NAME>
Fase atual: FASE_0|FASE_1|FASE_2
Autoridade: OPERACIONAL (Arquitetura + Auditoria)
Owners:
- Arquitetura (Arquiteto): <nome/papel>
- Execução (Executor): <nome/papel>
- Auditoria/Testes: <nome/papel>
- Negócio/Operação (se aplicável): <nome/papel>

Última atualização: YYYY-MM-DD
RUN_ID da última atualização: <obrigatório>
Ref/Commit atual: <hash/branch/tag>
Ambiente de referência: <local|ci|vps|outro>

Documentos relacionados:
- INVARIANTS_<MODULE>.md
- <MODULE>_USER_FLOWS.md
- <MODULE>_SCREENS_SPEC.md
- <MODULE>_FRONT_BACK_CONTRACT.md
- AR_BACKLOG_<MODULE>.md
- TEST_MATRIX_<MODULE>.md
- PARITY_REPORT_<MODULE>.md

---

## 1. Objetivo (Normativo Operacional)

Consolidar o estado atual do módulo `<MODULE_NAME>` em um único artefato operacional, com foco em execução determinística:
- fase atual,
- status do DoD,
- paridade contrato↔código,
- ARs em andamento,
- bloqueios,
- próxima ação única.

Este documento NÃO substitui os contratos do módulo (MCP); ele apenas consolida o estado operacional.

---

## 2. Escopo do Status

### 2.1 Dentro do escopo
- Status da fase atual
- Situação dos gates L1-L4
- Resumo de paridade (via PARITY_REPORT)
- Resumo de cobertura (via TEST_MATRIX)
- Situação do backlog de ARs (AR_BACKLOG)
- Bloqueios e riscos ativos
- Próxima ação única (determinística)

### 2.2 Fora do escopo
- Reescrever regras de negócio
- Aprovar mudanças no MCP (isso pertence a AR/ADR)
- Servir como evidência detalhada (ele aponta para evidências, não as substitui)

---

## 3. Snapshot Executivo (Obrigatório)

### 3.1 Estado atual do módulo
**Resultado geral da fase:** PASS|FAIL|PARCIAL|EM_EXECUCAO  
**Status operacional:** ACTIVE|PAUSED|BLOCKED|DONE  
**Resumo (3–6 linhas, objetivo):**  
<descrever o estado real atual do módulo sem narrativa otimista>

### 3.2 Próxima ação única (obrigatória)
> Deve ser executável e inequívoca.

**NEXT_ACTION_ID:** ACT-<MODULE>-<NNN>  
**Descrição:** <ação única, clara, com saída observável>  
**Responsável:** Arquiteto|Executor|Auditor|Humano  
**Pré-condição:** <se houver>  
**Critério de conclusão (PASS):** <condição objetiva>  
**Se falhar:** <ação de fallback / marcar BLOQUEADO e motivo>

### 3.3 Bloqueado?
- [ ] NÃO
- [ ] SIM → ver Seção 9 (Bloqueios)

---

## 4. Estado da Fase e DoD

### 4.1 Fase atual
- Fase: `FASE_<N>`
- Objetivo da fase:
  - <resultado mínimo de valor esperado>

### 4.2 DoD da fase (resumo)
**Fonte:** `AR_BACKLOG_<MODULE>.md` e/ou `PARITY_REPORT_<MODULE>.md`  
**Resultado atual:** PASS|FAIL|PARCIAL

#### Checklist DoD (resumo)
- [ ] MCP aprovado
- [ ] Invariantes bloqueantes da fase implementadas (ou deferidas formalmente)
- [ ] Fluxo mínimo de valor funcional
- [ ] Contratos críticos validados
- [ ] Cobertura mínima em TEST_MATRIX
- [ ] Evidências críticas presentes
- [ ] Paridade contrato↔código aceitável (GATE-L4)

### 4.3 Itens que impedem PASS (se houver)
- <item 1>
- <item 2>

---

## 5. Situação dos Gates (L1-L4)

| Gate | Objetivo | Resultado | Data | RUN_ID | Observação objetiva |
|---|---|---|---|---|---|
| GATE-L1-MODULE-CONTRACT-PACK | MCP mínimo e qualidade documental | PASS|FAIL|PARCIAL|NA | YYYY-MM-DD | <run> | <...> |
| GATE-L2-AR-READINESS | ARs prontas para execução | PASS|FAIL|PARCIAL|NA | YYYY-MM-DD | <run> | <...> |
| GATE-L3-INVARIANT-ENFORCEMENT | Prova de enforcement | PASS|FAIL|PARCIAL|NA | YYYY-MM-DD | <run> | <...> |
| GATE-L4-CONTRACT-CODE-PARITY | Paridade MCP ↔ implementação | PASS|FAIL|PARCIAL|NA | YYYY-MM-DD | <run> | <...> |

### Regra operacional
- Se `GATE-L4 = FAIL`, módulo NÃO pode ser marcado `DONE`.
- Se `GATE-L1 = FAIL`, nenhuma nova AR de código deve iniciar.

---

## 6. Resumo de Paridade (fonte: PARITY_REPORT)

### 6.1 Métricas consolidadas
- Invariantes (total / implementadas / parciais / pendentes / divergentes): `<n>/<n>/<n>/<n>/<n>`
- Flows (total / cobertos / pendentes): `<n>/<n>/<n>`
- Screens (total / cobertas / pendentes / NA): `<n>/<n>/<n>/<n>`
- Contracts (total / aderentes / parciais / divergentes): `<n>/<n>/<n>/<n>`

### 6.2 Principais gaps ativos (máx. 5)
1. `GAP-<MODULE>-...` — <descrição objetiva> — Severidade: CRITICA|ALTA|...
2. `GAP-<MODULE>-...` — <descrição objetiva> — Severidade: ...

### 6.3 Tendência da paridade (opcional, recomendado)
- Melhorando | Estável | Piorando
- Motivo objetivo: <...>

---

## 7. Resumo de Cobertura (fonte: TEST_MATRIX)

### 7.1 Cobertura por criticidade (fase atual)
- Itens críticos cobertos: `<n>/<n>`
- Itens alta prioridade cobertos: `<n>/<n>`
- Fluxo mínimo de valor coberto ponta a ponta: SIM|NAO|PARCIAL

### 7.2 Testes (último ciclo)
- Total previstos: <n>
- Executados: <n>
- PASS: <n>
- FAIL: <n>
- NOT_RUN: <n>

### 7.3 Débito de teste ativo (objetivo)
- <TEST-... pendente + impacto>
- <TEST-... pendente + impacto>

---

## 8. Situação do Backlog de ARs (fonte: AR_BACKLOG)

### 8.1 Resumo por status
- PENDENTE: <n>
- EM_EXECUCAO: <n>
- REVISAO: <n>
- VERIFICADO: <n>
- BLOQUEADO: <n>
- DEFERIDO: <n>
- CANCELADO: <n>

### 8.2 Resumo por classe
- Classe A: <status resumido>
- Classe B: <status resumido>
- Classe C: <status resumido>
- Classe D: <status resumido>
- Classe E: <status resumido>
- Classe T: <status resumido>

### 8.3 ARs críticas da fase (top 5)
| AR ID | Classe | Status | Objetivo | Bloqueio? | Próximo passo |
|---|---|---|---|---|---|
| AR-<MODULE>-001 | A | PENDENTE | <...> | NÃO | <...> |
| AR-<MODULE>-002 | B | BLOQUEADO | <...> | SIM | <...> |

---

## 9. Bloqueios Ativos (se houver)

> Preencher somente se houver bloqueio real.

### BLOCK-<MODULE>-001 — <Nome curto>
**Severidade:** CRITICA|ALTA|MEDIA  
**Tipo:** contrato|dependência|infra|teste|evidência|escopo|decisão_humana  
**Descrição objetiva:** <o que está bloqueado e por quê>  
**AR(s) impactada(s):** AR-..., AR-...  
**Item(ns) SSOT impactado(s):** INV-..., CONTRACT-..., FLOW-...  
**Evidência do bloqueio:** <path/ref/log>  
**Ação para desbloqueio:** <ação única>  
**Responsável pelo desbloqueio:** <papel>  
**Prazo lógico (opcional):** <marco, não estimativa de tempo>

---

## 10. Pendências Não-Bloqueantes (fase atual)

> Pendências aceitas temporariamente sem impedir o valor principal.

| PEND ID | Item SSOT | Tipo | Impacto | Justificativa | Tratamento planejado (fase) |
|---|---|---|---|---|---|
| PEND-<MODULE>-001 | SCREEN-... | UX | BAIXO | <...> | FASE_1 |
| PEND-<MODULE>-002 | INV-... | TESTE/EVIDENCIA | MEDIO | <...> | AR-... |

Regra:
- Pendência não-bloqueante NÃO pode esconder gap crítico.

---

## 11. Decisões e Ressalvas Ativas (operacionais)

### DEC-OPS-<MODULE>-001
**Tipo:** ressalva_operacional|deferimento|exceção_controlada  
**Descrição:** <...>  
**Motivo:** <...>  
**Impacto no módulo:** <...>  
**Validade:** até FASE_<N> ou AR-...  
**Revisão obrigatória em:** <evento/AR/gate>

---

## 12. Mapa de Rastreabilidade Operacional (Resumo)

### 12.1 Caminho de rastreio mínimo validado
- [ ] PRD/RF -> MCP
- [ ] MCP -> AR_BACKLOG
- [ ] AR_BACKLOG -> TEST_MATRIX
- [ ] TEST_MATRIX -> evidências
- [ ] PARITY_REPORT -> MODULE_STATUS

### 12.2 Falhas de rastreabilidade (se houver)
- <item>
- <item>

---

## 13. Próximas Ações (curto prazo)

> Máximo 5. A primeira deve ser igual à NEXT_ACTION_ID da Seção 3.

1. **ACT-<MODULE>-001** — <descrição> — Responsável: <...> — Saída esperada: <...>
2. ACT-<MODULE>-002 — <descrição> — Responsável: <...>
3. ACT-<MODULE>-003 — <descrição> — Responsável: <...>

Regra:
- Não listar ações vagas (“melhorar”, “refinar”, “revisar tudo”).
- Cada ação deve ter saída observável.

---

## 14. Critérios para mudança de status do módulo

### 14.1 `ACTIVE` -> `BLOCKED`
Quando:
- houver bloqueio crítico sem ação de desbloqueio executável imediata
- ou falha em gate crítico impede avanço (ex.: L1/L4 FAIL persistente)

### 14.2 `ACTIVE` -> `DONE`
Somente se:
- DoD da fase = PASS
- GATE-L4 = PASS (ou ressalva formal aprovada e sem impacto crítico)
- sem gaps críticos abertos
- próxima fase explicitamente definida ou módulo encerrado na fase atual

### 14.3 `ACTIVE` -> `PAUSED`
Quando:
- prioridade foi deslocada por decisão explícita
- e backlog/pendências ficaram registradas

---

## 15. Histórico de Atualizações (resumido)

| Data | RUN_ID | Autor/Papel | Mudança resumida |
|---|---|---|---|
| YYYY-MM-DD | <run> | <papel> | criação do status do módulo |
| YYYY-MM-DD | <run> | <papel> | atualização após AR-... / parity report |

---

## 16. Assinaturas Operacionais (opcional, recomendado)

Arquitetura (Arquiteto):
- Nome/Papel: <...>
- Resultado: APROVADO|APROVADO_COM_RESSALVAS|REPROVADO
- Observação: <...>

Auditoria/Testes:
- Nome/Papel: <...>
- Resultado: PASS|FAIL|PARCIAL
- Observação: <...>

Negócio/Operação (se aplicável):
- Nome/Papel: <...>
- Resultado: VALIDADO|NAO_VALIDADO|NA
- Observação: <...>
```

---

## Como usar esse `MODULE_STATUS` no seu fluxo (recomendação prática)

Ordem de atualização por ciclo:

1. Executor termina AR(s)
2. Auditor atualiza `TEST_MATRIX`
3. Auditor gera/atualiza `PARITY_REPORT`
4. Arquiteto atualiza `MODULE_STATUS` (snapshot real + próxima ação única)

Isso evita “status subjetivo”.

---

## Prompt curto para o agente atualizar `MODULE_STATUS_<MODULE>.md`

```text
Atue como Arquiteto Operacional (v2.2.0).

Atualize `MODULE_STATUS_<MODULE>.md` com base em:
- `AR_BACKLOG_<MODULE>.md`
- `TEST_MATRIX_<MODULE>.md`
- `PARITY_REPORT_<MODULE>.md`

Regras:
- usar RUN_ID obrigatório
- refletir estado real (sem narrativa otimista)
- definir NEXT_ACTION única, executável e com critério PASS
- listar bloqueios reais e itens que impedem DoD PASS
- não alterar regras de negócio do MCP
```

---

## O que você não perguntou (mas é a peça final para automatizar)

Agora que você tem o kit completo em `.md`, o próximo passo de maturidade é um espelho em `.json` para automação/gates:

* `module_status.<module>.json`
* `parity_report.<module>.json`
* `test_matrix.<module>.json` (ou exportado)

Isso permite:

* scripts validarem consistência,
* dashboards simples,
* hb_cli listar status por módulo sem parsing frágil de markdown.

Se você quiser, eu posso te entregar na próxima mensagem uma **versão JSON schema mínima** para `MODULE_STATUS` e `PARITY_REPORT` (para o agente nunca quebrar o formato).

