Abaixo estão os **2 templates complementares avançados** que faltam para fechar o MCP com foco no seu fluxo (ARs + determinismo + validação por evidência):

1. `TEST_MATRIX_<MODULE>.md` (avançado)
2. `AR_BACKLOG_<MODULE>.md` (avançado, compatível com AR/validation_command/evidências)

---

# 1) Template — `TEST_MATRIX_<MODULE>.md` (avançado)

```md
# TEST_MATRIX_<MODULE>.md

Status: DRAFT|REVIEW|APPROVED|DEPRECATED
Versão: v0.1.0
Tipo de Documento: Verification & Traceability Matrix (Normativo Operacional / SSOT)
Módulo: <MODULE_NAME>
Fase: FASE_0|FASE_1|FASE_2
Autoridade: NORMATIVO_OPERACIONAL
Owners:
- Arquitetura: <nome/papel>
- Auditoria/Testes: <nome/papel>
- Backend/Frontend (se aplicável): <nome/papel>

Última revisão: YYYY-MM-DD
Próxima revisão recomendada: YYYY-MM-DD

Dependências:
- INVARIANTS_<MODULE>.md
- <MODULE>_USER_FLOWS.md
- <MODULE>_SCREENS_SPEC.md
- <MODULE>_FRONT_BACK_CONTRACT.md
- AR_BACKLOG_<MODULE>.md

---

## 1. Objetivo (Normativo)

Garantir rastreabilidade e cobertura verificável entre:
- contratos do módulo (INV/FLOW/SCREEN/CONTRACT),
- ARs de materialização,
- testes automatizados/manuais,
- evidências de execução.

Este documento define **o que deve ser testado**, **como provar**, e **qual status de cobertura** cada item possui.

---

## 2. Escopo

### 2.1 Dentro do escopo
- Mapeamento de cobertura por item do MCP
- Testes de violação de invariantes
- Testes de fluxo (happy path e exceções principais)
- Testes de contrato front-back
- Evidências mínimas exigidas por item crítico

### 2.2 Fora do escopo
- Implementação detalhada dos testes (código)
- Testes de performance/carga (salvo se explicitamente incluído)
- QA visual/pixel-perfect (salvo se explicitamente incluído)

---

## 3. Convenções de Classificação

### 3.1 Tipos de teste
- UNIT
- INTEGRATION
- CONTRACT
- E2E
- MANUAL_GUIADO
- GATE_CHECK
- REGRESSION

### 3.2 Criticidade de cobertura
- CRITICA
- ALTA
- MEDIA
- BAIXA

### 3.3 Status de cobertura
- COBERTO
- PARCIAL
- PENDENTE
- BLOQUEADO
- NAO_APLICAVEL

### 3.4 Resultado da última execução
- PASS
- FAIL
- NOT_RUN
- FLAKY (somente se formalmente aceito; evitar)

### 3.5 Tipo de prova esperada
- log
- screenshot
- report_json
- test_output
- db_state_before_after
- api_response
- e2e_video (opcional)
- manual_checklist

---

## 4. Regras Normativas de Verificação

1. Toda **invariante bloqueante** DEVE ter pelo menos 1 teste de violação (tentativa de quebrar a regra).
2. Todo **fluxo principal (happy path)** DEVE ter cobertura E2E ou MANUAL_GUIADO equivalente.
3. Todo **CONTRACT-*** de alta prioridade DEVE ter teste de integração/contrato.
4. Teste de “caminho feliz” não substitui teste de violação de invariante.
5. Item marcado `COBERTO` DEVE ter referência de evidência.
6. Item `IMPLEMENTADO` no MCP sem cobertura correspondente deve ser marcado `PARCIAL` ou `PENDENTE` aqui (nunca “COBERTO” por inferência).

---

## 5. Matriz de Cobertura por Invariantes

> Uma linha por teste relevante. Se uma invariante precisar de múltiplos testes, repetir o `INV-*`.

| ID Item | Nome Curto | Severidade | Camada | ID Teste | Tipo | Objetivo do Teste | Tentativa de Violação | Criticidade | Status Cobertura | Últ. Execução | Evidência | AR Relacionada |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| INV-<MODULE>-001 | <nome> | BLOQUEANTE_<...> | serviço | TEST-<MODULE>-INV-001-INT | INTEGRATION | <...> | SIM | CRITICA | PENDENTE | NOT_RUN | <path/ref> | AR-<MODULE>-001 |

### Notas de preenchimento (obrigatórias)
- **Tentativa de Violação = SIM** para invariantes bloqueantes.
- **Evidência** deve apontar para saída verificável (arquivo/path/report/log).
- **AR Relacionada** deve mapear a AR que materializou (ou ajustou) a regra.

---

## 6. Matriz de Cobertura por Fluxos

| ID Flow | Nome do Fluxo | Prioridade | ID Teste | Tipo | Cenário | Happy Path / Exceção | Status Cobertura | Últ. Execução | Evidência | Screens Relacionadas | Contratos Relacionados |
|---|---|---|---|---|---|---|---|---|---|---|---|
| FLOW-<MODULE>-001 | <nome> | ALTA | TEST-<MODULE>-FLOW-001-E2E | E2E | <...> | Happy | PENDENTE | NOT_RUN | <path/ref> | SCREEN-... | CONTRACT-... |

### Regras
- Fluxos ALTA prioridade DEVEM estar cobertos ao final da fase.
- Exceções críticas DEVEM ter ao menos 1 cenário validado.

---

## 7. Matriz de Cobertura por Telas (UI funcional)

| ID Screen | Rota | Estado de UI | ID Teste | Tipo | Cenário | Criticidade | Status Cobertura | Últ. Execução | Evidência |
|---|---|---|---|---|---|---|---|---|---|
| SCREEN-<MODULE>-001 | /<rota> | empty_state | TEST-<MODULE>-SCREEN-001-EMPTY | E2E|MANUAL_GUIADO | <...> | ALTA | PENDENTE | NOT_RUN | <path/ref> |

Estados mínimos a mapear (se aplicável):
- loading
- error
- empty
- dados disponíveis
- bloqueio de validação
- aviso não-bloqueante

---

## 8. Matriz de Cobertura por Contratos Front-Back

| ID Contract | Ação | Prioridade | ID Teste | Tipo | Payload Mínimo | Resposta Mínima | Erro Bloqueante | Aviso/Pendência | Status Cobertura | Últ. Execução | Evidência |
|---|---|---|---|---|---|---|---|---|---|---|---|
| CONTRACT-<MODULE>-001 | <ação> | ALTA | TEST-<MODULE>-CONTRACT-001 | CONTRACT|INTEGRATION | Validado | Validada | Validado | Validado | PENDENTE | NOT_RUN | <path/ref> |

---

## 9. Mapa AR -> Cobertura -> Evidência

> Útil para auditoria de materialização por AR.

| AR ID | Classe | Itens SSOT Alvo | Testes previstos | Testes executados | Evidências mínimas esperadas | Status |
|---|---|---|---|---|---|---|
| AR-<MODULE>-001 | B | INV-..., CONTRACT-... | TEST-..., TEST-... | <preencher> | report_json + test_output | PENDENTE |

---

## 10. Critérios de PASS/FAIL da Fase (Matriz)

### PASS (fase do módulo) se:
- [ ] Todas as invariantes bloqueantes da fase = `COBERTO` ou `PARCIAL` com justificativa aprovada
- [ ] Todos os flows ALTA prioridade = `COBERTO`
- [ ] Contratos ALTA prioridade = `COBERTO`
- [ ] Evidências referenciadas para itens críticos
- [ ] Sem itens críticos `FAIL` sem plano de correção

### FAIL (fase do módulo) se:
- [ ] Invariante bloqueante sem teste de violação
- [ ] Fluxo mínimo de valor sem cobertura
- [ ] Contrato front-back crítico sem validação
- [ ] Itens marcados COBERTO sem evidência
- [ ] Divergência contrato↔código sem registro

---

## 11. Protocolo de Atualização

Toda mudança em:
- Invariantes -> atualizar seção 5
- Flows -> atualizar seção 6
- Screens -> atualizar seção 7
- Contratos -> atualizar seção 8
- AR backlog -> atualizar seção 9

Regra:
- atualização da matriz é obrigatória no mesmo ciclo da AR (ou marcar explicitamente `BLOQUEADO` com motivo).

---

## 12. Checklist do Auditor (rápido)

- [ ] Cada `INV` bloqueante tem teste de violação
- [ ] Há evidência real (não narrativa)
- [ ] `COBERTO` não foi usado por inferência
- [ ] Fluxo mínimo de valor está coberto de ponta a ponta
- [ ] Contratos de alta prioridade têm teste de integração/contrato
- [ ] ARs materializadas aparecem no mapa AR -> cobertura
```

---

# 2) Template — `AR_BACKLOG_<MODULE>.md` (avançado, compatível com seu fluxo)

````md
# AR_BACKLOG_<MODULE>.md

Status: DRAFT|REVIEW|APPROVED
Versão: v0.1.0
Tipo de Documento: AR Materialization Backlog (Normativo Operacional / SSOT)
Módulo: <MODULE_NAME>
Fase: FASE_0|FASE_1|FASE_2
Autoridade: NORMATIVO_OPERACIONAL
Owners:
- Arquitetura (Arquiteto): <nome/papel>
- Execução (Executor): <nome/papel>
- Auditoria/Testes: <nome/papel>

Última revisão: YYYY-MM-DD
Próxima revisão recomendada: YYYY-MM-DD

Dependências:
- INVARIANTS_<MODULE>.md
- <MODULE>_USER_FLOWS.md
- <MODULE>_SCREENS_SPEC.md
- <MODULE>_FRONT_BACK_CONTRACT.md
- TEST_MATRIX_<MODULE>.md

---

## 1. Objetivo (Normativo)

Decompor a implementação do módulo `<MODULE_NAME>` em ARs pequenas, rastreáveis, testáveis e auditáveis, alinhadas ao MCP do módulo, com ordem de execução e critérios binários de aceite.

---

## 2. Escopo e Regras de Fatiamento

### 2.1 Escopo
- Materialização dos itens do MCP da fase atual
- Correções de divergência contrato↔código do módulo
- Testes e evidências mínimas para fechamento da fase

### 2.2 Fora do escopo
- Refatorações amplas sem vínculo com itens do MCP
- Features novas fora do PRD/MCP
- Mudanças em outros módulos (salvo dependência explícita)

### 2.3 Regras obrigatórias de fatiamento
1. Preferir 1 AR = 1 classe (A/B/C/D/E/T).
2. Cada AR DEVE referenciar IDs SSOT alvo (`INV`, `FLOW`, `SCREEN`, `CONTRACT`).
3. Cada AR DEVE ter AC binário (PASS/FAIL observável).
4. Cada AR DEVE ter estratégia de validação (incluindo tentativa de violação para invariantes bloqueantes).
5. Se a AR alterar contrato/resposta, atualizar `TEST_MATRIX_<MODULE>.md`.
6. AR híbrida A+B+D é proibida salvo justificativa aprovada.

---

## 3. Classes de AR (Padrão)

- **A** — Banco/Persistência (migrations, constraints, models)
- **B** — Regras de Domínio/Services
- **C** — Cálculo/Derivados/Determinismo
- **D** — Frontend/UX
- **E** — Contrato Front-Back / integração
- **T** — Testes/Gates/Paridade

---

## 4. Ordem Sugerida de Materialização (Lotes)

### Lote 1 — Núcleo bloqueante (A/B/C)
- AR-<MODULE>-001 (Classe A)
- AR-<MODULE>-002 (Classe B)
- AR-<MODULE>-003 (Classe C)

### Lote 2 — Contratos e UI mínima (E/D)
- AR-<MODULE>-004 (Classe E)
- AR-<MODULE>-005 (Classe D)

### Lote 3 — Cobertura e paridade (T)
- AR-<MODULE>-006 (Classe T)

> Ajustar por módulo/fase, mantendo a lógica: regra -> cálculo -> contrato -> UI -> testes/paridade.

---

## 5. Tabela Resumo do Backlog de ARs

| AR ID | Classe | Prioridade | Objetivo | Alvos SSOT | Dependências | Status |
|---|---|---|---|---|---|---|
| AR-<MODULE>-001 | A | ALTA | <...> | INV-..., CONTRACT-... | - | PENDENTE |
| AR-<MODULE>-002 | B | ALTA | <...> | INV-..., FLOW-... | AR-<MODULE>-001 | PENDENTE |

### Status permitidos
- PENDENTE
- EM_EXECUCAO
- REVISAO
- VERIFICADO
- BLOQUEADO
- CANCELADO
- DEFERIDO

---

## 6. Template Completo por AR (Obrigatório)

> Repetir este bloco para cada AR do backlog.

### AR-<MODULE>-001 — <Nome Curto>

**Status:** PENDENTE|EM_EXECUCAO|REVISAO|VERIFICADO|BLOQUEADO|CANCELADO|DEFERIDO  
**Classe:** A|B|C|D|E|T  
**Prioridade:** ALTA|MEDIA|BAIXA  
**Fase:** FASE_0|FASE_1|FASE_2  
**Objetivo da AR (1 frase):**  
<descrever o resultado observável da AR>

#### 6.1 Alvos SSOT (obrigatório)
**Invariantes:**
- INV-<MODULE>-...
- INV-<MODULE>-...

**Flows (se aplicável):**
- FLOW-<MODULE>-...

**Screens (se aplicável):**
- SCREEN-<MODULE>-...

**Contracts (se aplicável):**
- CONTRACT-<MODULE>-...

#### 6.2 Tipo de mudança esperada
- [ ] Banco / Migration
- [ ] Model
- [ ] Service / Regra de domínio
- [ ] Cálculo / Derivado
- [ ] API / Contrato
- [ ] Frontend / UX
- [ ] Testes
- [ ] Gate / Script de validação
- [ ] Documentação MCP (ajuste)

#### 6.3 Dependências
**ARs predecessoras obrigatórias:**
- <AR IDs> (ou `-`)

**Pré-condições técnicas:**
- <ex.: tabela X existe>
- <ex.: endpoint Y disponível>

#### 6.4 Escopo de leitura (READ)
- <paths exatos permitidos>
- <docs SSOT obrigatórios a ler>

#### 6.5 Escopo de escrita (WRITE)
- <paths exatos permitidos>
- <arquivos esperados a alterar/criar>

#### 6.6 Fora do escopo / Proibido (MUST NOT)
- <paths e tipos de mudança proibidos>
- <não alterar outros módulos>
- <não reescrever contratos sem AR/ADR>

#### 6.7 Acceptance Criteria (AC) binário (obrigatório)

##### AC-001
**Descrição:** <...>  
**PASS:** <condição observável>  
**FAIL:** <condição observável>

##### AC-002
**Descrição:** <...>  
**PASS:** <condição observável>  
**FAIL:** <condição observável>

> Regra: ACs devem ser testáveis. Evitar “código limpo”, “melhorado”, “organizado”.

#### 6.8 Estratégia de validação (obrigatória)
**validation_command (preferencial):**
```bash
<command>
````

**Se não houver command único, descrever steps de validação:**

1. <step>
2. <step>
3. <step>

**Tentativa de violação de invariantes bloqueantes (obrigatória quando aplicável):**

* Invariante alvo: INV-<MODULE>-...
* Como tentar violar: <cenário>
* Resultado esperado: bloqueio / warning / pendência

#### 6.9 Evidências esperadas (objetivas)

* [ ] test_output
* [ ] report_json
* [ ] diff de migration (Classe A)
* [ ] api_response sample (Classe E)
* [ ] screenshot/registro de tela (Classe D)
* [ ] before/after de cálculo (Classe C)
* [ ] atualização da TEST_MATRIX_<MODULE>.md
* [ ] atualização de status dos itens SSOT impactados

**Paths de evidência (preencher):**

* <path 1>
* <path 2>

#### 6.10 Riscos e armadilhas (anti-alucinação)

* Risco 1: <...>

* Mitigação: <...>

* Risco 2: <...>

* Mitigação: <...>

#### 6.11 Critério de bloqueio da AR (quando marcar BLOQUEADO)

Marcar `BLOQUEADO` se:

* dependência não concluída
* gap de contrato SSOT impede implementação
* evidência contradiz regra normativa e requer decisão humana
* escopo real extrapola a AR

Registrar:

* motivo objetivo
* item SSOT impactado
* ação de desbloqueio proposta

#### 6.12 Critério de encerramento da AR

**VERIFICADO somente se (todos):**

* [ ] ACs PASS
* [ ] Validação executada
* [ ] Evidências anexadas/referenciadas
* [ ] TEST_MATRIX atualizada (quando aplicável)
* [ ] Itens SSOT impactados com status revisado
* [ ] Nenhuma mudança fora do WRITE scope

---

## 7. Mapa de Dependências entre ARs (Resumo)

* AR-<MODULE>-001 -> AR-<MODULE>-002 -> AR-<MODULE>-003
* AR-<MODULE>-004 depende de AR-<MODULE>-002 e AR-<MODULE>-003
* AR-<MODULE>-005 depende de AR-<MODULE>-004
* AR-<MODULE>-006 valida cobertura/paridade dos anteriores

---

## 8. Critérios de PASS/FAIL do Backlog da Fase (Módulo)

### PASS se:

* [ ] ARs críticas (prioridade ALTA) = VERIFICADO ou DEFERIDO com aprovação
* [ ] Invariantes bloqueantes da fase com materialização e teste de violação
* [ ] Fluxo mínimo de valor implementado
* [ ] Contratos front-back mínimos validados
* [ ] TEST_MATRIX atualizada e coerente
* [ ] Sem AR crítica BLOQUEADA sem plano de desbloqueio

### FAIL se:

* [ ] ARs executadas sem alvos SSOT
* [ ] AR VERIFICADO sem evidência
* [ ] Quebra de escopo recorrente
* [ ] Drift contrato↔código sem registro
* [ ] Invariante bloqueante da fase sem enforcement comprovado

---

## 9. Protocolo de Mudança do Backlog

Alterações neste backlog DEVEM:

1. Referenciar motivo (mudança de escopo, dependência, bug, decisão)
2. Manter histórico de IDs (não reutilizar AR ID)
3. Atualizar dependências e ordem dos lotes
4. Atualizar impactos na TEST_MATRIX e nos docs SSOT, se aplicável

### Regras de ID

* IDs cancelados não devem ser reutilizados
* IDs decompostos devem manter referência ao pai (ex.: AR-...-005A / 005B ou novos IDs com nota de decomposição)

---

## 10. Checklist do Arquiteto (antes de liberar para Executor)

* [ ] Cada AR tem classe definida
* [ ] Cada AR tem alvos SSOT explícitos
* [ ] ACs são binários e observáveis
* [ ] validation_command/estratégia existe
* [ ] Tentativa de violação prevista (quando aplicável)
* [ ] READ/WRITE/FORA DO ESCOPO definidos
* [ ] Dependências coerentes
* [ ] Ordem dos lotes faz sentido para o valor da fase

```



