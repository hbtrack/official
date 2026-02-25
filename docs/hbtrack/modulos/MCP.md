# MODULE_MATERIALIZATION_MASTER_PLAN.md

Status: APPROVED
Versão: v1.0.0
Tipo de Documento: Master Materialization Plan (Normativo Operacional / SSOT)
Sistema: HB Track
Autoridade: NORMATIVO_OPERACIONAL
Modo: IA + ARs + Contratos Determinísticos
Owners:
- Arquitetura (Arquiteto): <Agente Arquiteto do Repositório>
- Operação/Negócio: <Agente Executor do Repositório>
- Auditoria/Testes: <Agente Auditor do Repositório>

Última revisão: YYYY-MM-DD
Próxima revisão recomendada: YYYY-MM-DD

Documentos relacionados:
- PRD Hb Track (fonte de módulos e RFs)
- docs/_canon/contratos/Dev Flow.md
- docs/_canon/contratos/ar_contract.schema.json
- docs/_canon/specs/GATES_REGISTRY.yaml
- docs/hbtrack/modulos/<module>/INVARIANTS_<MODULE>.md
- docs/hbtrack/modulos/<module>/<MODULE>_USER_FLOWS.md
- docs/hbtrack/modulos/<module>/<MODULE>_SCREENS_SPEC.md
- docs/hbtrack/modulos/<module>/<MODULE>_FRONT_BACK_CONTRACT.md
- docs/hbtrack/modulos/<module>/AR_BACKLOG_<MODULE>.md
- docs/hbtrack/modulos/<module>/TEST_MATRIX_<MODULE>.md

---

## 1. Objetivo (Normativo)

Definir o processo padrão e determinístico para materializar módulos do HB Track a partir do `PRD Hb Track.md`, usando agentes de IA do repositório, por meio de contratos normativos de módulo + ARs pequenas + validação por evidências.

Este plano existe para:
- reduzir alucinação de agentes
- evitar retrabalho por escopo implícito
- alinhar frontend/backend/UX ao PRD
- garantir rastreabilidade PRD -> Contratos -> ARs -> Testes -> Evidências

---

## 2. Escopo

### 2.1 Dentro do escopo
- Geração e aprovação de pacotes contratuais por módulo (MCP)
- Decomposição em ARs por classe (A/B/C/D/E/T)
- Implementação incremental por AR
- Gates de pré-governança, materialização e paridade
- Critérios PASS/FAIL por módulo

### 2.2 Fora do escopo
- Implementação direta de módulo inteiro sem contratos
- Refatorações amplas não motivadas por AR
- Mudanças de PRD sem registro em decisão/AR
- “Atalhos” que pulem etapa de auditoria e contrato normativo

---

## 3. Definições Canônicas

- **MCP (Module Contract Pack):** pacote de contratos determinísticos do módulo.
- **AS-IS:** descrição do estado atual evidenciado no código/banco/telas.
- **TO-BE / SSOT:** contrato normativo aprovado (o que deve ser implementado).
- **AR:** unidade de materialização auditável, com escopo, AC, validação e evidências.
- **Classe de AR:** categoria da AR por camada (A/B/C/D/E/T).
- **Invariante bloqueante:** regra cuja violação impede entrega do objetivo funcional da fase.
- **Aviso/Pendência não-bloqueante:** inconsistência permitida sem impedir entrega do valor principal.
- **Paridade contrato↔código:** aderência entre SSOT do módulo e estado implementado.

---

## 4. Princípios Normativos do Processo

### MP-PRINC-001 — Contrato antes de código
Nenhum módulo PODE iniciar implementação por AR de código sem MCP mínimo aprovado (ou em REVIEW autorizado).

### MP-PRINC-002 — Descoberta controlada
O agente DEVE auditar o sistema real (AS-IS) antes de escrever contratos TO-BE.

### MP-PRINC-003 — Separação entre descrição e norma
Documentação AS-IS NÃO substitui documento normativo SSOT.

### MP-PRINC-004 — Fatiamento por camada
ARs DEVEM ser fatiadas preferencialmente por classe (A/B/C/D/E/T), evitando AR híbrida multi-camada.

### MP-PRINC-005 — Evidência antes de “implementado”
Nenhum item de contrato pode ser marcado como IMPLEMENTADO sem evidência objetiva no código/schema/testes.

### MP-PRINC-006 — Testar violação de invariantes
Toda invariante bloqueante materializada DEVE ter validação com tentativa explícita de violação.

---

## 5. Classificação Padrão de ARs (Obrigatória)

- **Classe A — Banco/Persistência**
  - migrations, constraints, FKs, índices, soft delete, modelos
- **Classe B — Regras de Domínio/Services**
  - validações de negócio, políticas, resolução canônica
- **Classe C — Cálculo/Derivados/Determinismo**
  - standings, agregações, recálculo, consistência determinística
- **Classe D — Frontend/UX**
  - telas, fluxos de interação, estados UI, CTAs
- **Classe E — Contrato Front-Back**
  - payloads, respostas, flags funcionais, códigos de erro/aviso
- **Classe T — Testes/Gates/Paridade**
  - testes unit/integration/e2e, gates, checagens de paridade

### Regra de fatiamento
1. Preferir 1 AR = 1 classe.
2. Se misturar classes, justificar explicitamente no plano da AR.
3. AR híbrida A+B+D é proibida salvo exceção aprovada.

---

## 6. Pacote Contratual Mínimo por Módulo (MCP-MIN)

Para um módulo iniciar materialização, DEVEM existir:

1. `INVARIANTS_<MODULE>.md`
2. `<MODULE>_USER_FLOWS.md`
3. `<MODULE>_SCREENS_SPEC.md` (ou `NAO_APLICAVEL` justificado)
4. `<MODULE>_FRONT_BACK_CONTRACT.md`
5. `AR_BACKLOG_<MODULE>.md`
6. `TEST_MATRIX_<MODULE>.md`

### Requisitos mínimos de qualidade (por documento)
- Status / Versão / Tipo / Módulo / Fase / Autoridade
- Escopo / Fora de escopo
- IDs estáveis e rastreáveis
- Regras observáveis/testáveis
- Bloqueante vs não-bloqueante (quando aplicável)
- Relações cruzadas com demais documentos do MCP

---

## 7. Gates Normativos (Processo por Módulo)

## 7.1 GATE-L1-MODULE-CONTRACT-PACK (Pré-governança)

**Objetivo:** impedir implementação sem contrato mínimo.

### PASS se (todos)
- [ ] MCP-MIN completo (6 documentos)
- [ ] Cada doc tem metadados mínimos (Status, Versão, Tipo, Módulo, Fase, Autoridade)
- [ ] Invariantes com IDs `INV-*`
- [ ] Flows com IDs `FLOW-*`
- [ ] Screens com IDs `SCREEN-*` (ou NAO_APLICAVEL)
- [ ] Contratos com IDs `CONTRACT-*`
- [ ] AR Backlog com IDs `AR-*` e classes A/B/C/D/E/T
- [ ] Test Matrix com IDs `TEST-*`
- [ ] Matriz de rastreabilidade entre docs (mínimo: tela -> contrato -> invariantes)

### FAIL se (qualquer um)
- [ ] Falta qualquer doc do MCP-MIN
- [ ] Mistura AS-IS e TO-BE sem marcação
- [ ] Inventa funcionalidades fora do PRD como se fossem normativas
- [ ] Não separa bloqueante vs não-bloqueante onde necessário

---

## 7.2 GATE-L2-AR-READINESS (Pronto para materializar uma AR)

**Objetivo:** impedir AR ambígua ou fora do SSOT.

### PASS se (todos)
- [ ] AR referencia IDs do SSOT (INV/FLOW/SCREEN/CONTRACT)
- [ ] Classe da AR declarada (A/B/C/D/E/T)
- [ ] Escopo de leitura/escrita definido
- [ ] Fora do escopo/proibido explícito
- [ ] AC binário definido
- [ ] validation_command definido (ou estratégia de validação equivalente)
- [ ] Dependências de ARs anteriores declaradas

### FAIL se (qualquer um)
- [ ] “Implementar módulo X” sem fatiamento
- [ ] AR sem alvos SSOT
- [ ] AR sem AC binário
- [ ] AR sem critério de validação

---

## 7.3 GATE-L3-INVARIANT-ENFORCEMENT (Validação da materialização)

**Objetivo:** provar que a regra foi de fato aplicada.

### PASS se (todos)
- [ ] Teste/validação tenta violar a invariante
- [ ] Sistema bloqueia (ou marca pendência, se regra não-bloqueante)
- [ ] Evidência coletada e referenciada
- [ ] Status da invariante atualizado (`IMPLEMENTADA`, `PARCIAL`, etc.)
- [ ] TEST_MATRIX atualizado com cobertura correspondente

### FAIL se (qualquer um)
- [ ] Apenas teste de “caminho feliz”
- [ ] Sem prova de bloqueio/controle
- [ ] Sem evidência objetiva

---

## 7.4 GATE-L4-CONTRACT-CODE-PARITY (Paridade módulo)

**Objetivo:** detectar drift entre SSOT e implementação.

### PASS se (todos)
- [ ] Mudanças de código relevantes atualizaram docs impactados
- [ ] Mudanças de contrato atualizaram testes/AR backlog
- [ ] Front-back contract compatível com telas/flows atuais
- [ ] Itens `DIVERGENTE_DO_SSOT` listados explicitamente (se existirem)
- [ ] Sem “implementado” sem evidência

### FAIL se (qualquer um)
- [ ] Código alterado sem atualização de contrato relacionado
- [ ] Contrato mudou sem impacto mapeado em teste
- [ ] Frontend depende de flag/erro não contratados

---

## 8. Pipeline Padrão por Módulo (Etapas Numeradas)

### ETAPA-MP-001 — Seleção do módulo-alvo
**Entrada:** PRD + priorização do produto/arquitetura  
**Saída:** módulo e fase definidos (ex.: `COMPETITIONS`, FASE_0)

**PASS:** módulo, RF e objetivo da fase explícitos  
**FAIL:** “vamos implementar tudo do PRD”

---

### ETAPA-MP-002 — Auditoria AS-IS (descritiva)
O agente DEVE:
1. Ler schema/modelos/migrations
2. Ler services/use-cases/routers
3. Ler frontend (pages/components) se houver
4. Comparar com o PRD
5. Marcar `EVIDENCIADO` vs `HIPOTESE`
6. Listar gaps

**Saída obrigatória:**
- Resumo AS-IS
- Mapa de evidência vs hipótese
- Lista de gaps

**PASS:** evidência separada de inferência  
**FAIL:** contrato normativo escrito sem auditoria

---

### ETAPA-MP-003 — Geração do MCP (TO-BE normativo)
O agente DEVE gerar:
1. Invariantes
2. User Flows
3. Screens Spec
4. Front-Back Contract
5. AR Backlog
6. Test Matrix

**PASS:** GATE-L1 aprovado  
**FAIL:** qualquer lacuna no MCP-MIN

---

### ETAPA-MP-004 — Validação humana do MCP
Humanos responsáveis DEVEM:
- validar semântica de negócio
- cortar escopo excessivo
- aprovar jornada mínima de valor
- aprovar bloqueios vs avisos

**Saída:** versão do MCP marcada `APPROVED` (ou `REVIEW` autorizado)

**PASS:** owners aprovam e registram pendências remanescentes  
**FAIL:** seguir para código sem aprovação semântica

---

### ETAPA-MP-005 — Materialização por ARs (execução)
Executar ARs conforme ordem do `AR_BACKLOG_<MODULE>.md`.

Regra:
- Implementar por lotes pequenos
- Coletar evidências por AR
- Atualizar status de invariantes/contratos/testes

**PASS:** GATE-L2 + GATE-L3 por AR  
**FAIL:** execução fora do backlog / sem validação

---

### ETAPA-MP-006 — Paridade e fechamento da fase do módulo
Ao fim da fase:
- rodar checagem de paridade contrato↔código
- atualizar `TEST_MATRIX`
- declarar status do módulo (FASE_x)

**PASS:** GATE-L4 aprovado + DoD do módulo atendido  
**FAIL:** drift não mapeado ou cobertura insuficiente

---

## 9. DoD de Módulo (Template Normativo)

Cada módulo DEVE declarar seu DoD de fase em documento próprio (`AR_BACKLOG` ou doc de módulo), no formato:

### DOD-<MODULE>-FASE-<N>
**PASS se (todos):**
- [ ] MCP aprovado
- [ ] Invariantes bloqueantes da fase implementadas ou explicitamente deferidas
- [ ] Fluxo mínimo de valor funcional
- [ ] Contratos front-back mínimos testados
- [ ] Testes de violação de invariantes bloqueantes executados
- [ ] Evidências anexadas/referenciadas
- [ ] Itens pendentes remanescentes classificados (bloqueante/não-bloqueante)

**FAIL se (qualquer um):**
- [ ] Valor principal ainda depende de fluxo manual não previsto
- [ ] Front/backend divergentes no contrato
- [ ] Tabela/derivado/cálculo muda sem determinismo (quando aplicável)
- [ ] Invariantes bloqueantes sem prova de enforcement

---

## 10. Política Anti-Alucinação para Agentes (Obrigatória)

### MP-AA-001 — Não inventar fora do PRD
Feature fora do PRD só pode aparecer em seção:
`Proposta fora do PRD (não normativa)`.

### MP-AA-002 — Não confundir detalhe técnico com regra de domínio
Ex.: JSONB, framework, componente UI não substituem regra normativa.

### MP-AA-003 — Não marcar implementado sem evidência
Todo status `IMPLEMENTADA` exige referência objetiva a código/teste/schema/evidência.

### MP-AA-004 — Não expandir escopo por “melhores práticas”
Melhoria opcional pode ser registrada, não materializada sem aprovação.

### MP-AA-005 — Não bloquear fluxo principal por enriquecimento
Dados de enriquecimento (quando assim definido no MCP) NÃO devem bloquear entrega do valor principal.

---

## 11. Ordem Mestra Recomendada de Módulos (Adaptável ao PRD)

> Ajustar com base na priorização do PRD e dependências reais.

### MP-MOD-001 — Competitions (fundação)
Objetivo de fase inicial:
- competição + fase + adversários + partidas mínimas + tabela/classificação

### MP-MOD-002 — Matches Basic
Objetivo de fase inicial:
- partida mínima operável e vinculada à competição/fase

### MP-MOD-003 — Roster / Participantes (enriquecimento)
Objetivo de fase inicial:
- participantes com pendência de vínculo sem bloquear tabela

### MP-MOD-004 — Scout (modelo próprio, fase separada)
Objetivo de fase inicial:
- base de eventos de scout conforme taxonomia definida

### MP-MOD-005 — Exports / Jobs Async
Objetivo de fase inicial:
- fila, status, idempotência, polling/download

### MP-MOD-006 — Notifications
Objetivo de fase inicial:
- leitura/ack/listagem + estados visuais mínimos

### MP-MOD-007 — AI Parser / Ingestion (transversal)
Objetivo de fase inicial:
- extração estruturada + pendências + validação humana

---

## 12. Template de Prompt Mestre (para o agente do repo, por módulo)

```text
Atue como Arquiteto (v2.2.0).

OBJETIVO
Materializar o Module Contract Pack (MCP) do módulo <MODULO>, com base no PRD Hb Track e no estado atual do repositório, para implementação por IA via ARs.

MODO
Descoberta controlada + SSOT normativo.
NÃO implementar código nesta etapa.

ETAPA 1 — AUDITORIA AS-IS
- Ler schema/modelos/migrations/services/routers/frontend (se houver)
- Comparar com RF/PRD do módulo
- Marcar EVIDENCIADO vs HIPOTESE
- Listar gaps

ETAPA 2 — GERAR MCP (TO-BE NORMATIVO)
Gerar nesta ordem:
1. INVARIANTS_<MODULO>.md
2. <MODULO>_USER_FLOWS.md
3. <MODULO>_SCREENS_SPEC.md (ou NAO_APLICAVEL justificado)
4. <MODULO>_FRONT_BACK_CONTRACT.md
5. AR_BACKLOG_<MODULO>.md
6. TEST_MATRIX_<MODULO>.md

REGRAS
- Escopo / fora de escopo obrigatórios
- IDs estáveis (INV/FLOW/SCREEN/CONTRACT/AR/TEST)
- Separar bloqueante vs não-bloqueante
- Mapear camada de enforcement
- Criar matriz de rastreabilidade entre docs
- Não inventar features fora do PRD (usar seção “Proposta fora do PRD — não normativa”)

ETAPA 3 — PLANO DE MATERIALIZAÇÃO
No AR_BACKLOG:
- fatiar por classes A/B/C/D/E/T
- declarar dependências
- AC binário por AR
- estratégia de validação com tentativa de violação das invariantes bloqueantes

SAÍDA
- Resumo de auditoria
- Mapa evidência vs hipótese
- Conteúdo dos 6 documentos
- Decisões pendentes para validação humana
````

---

## 13. Checklist Operacional do Arquiteto (por módulo)

### Antes do MCP

* [ ] Módulo e RF definidos
* [ ] Fase e objetivo da fase definidos
* [ ] Dependências conhecidas listadas

### Após MCP gerado

* [ ] GATE-L1 aprovado
* [ ] Semântica validada por humano
* [ ] Escopo cortado para MVP real
* [ ] AR_BACKLOG ordenado

### Durante ARs

* [ ] GATE-L2 por AR
* [ ] GATE-L3 por AR
* [ ] Evidências anexadas
* [ ] TEST_MATRIX atualizado

### Fechamento da fase

* [ ] GATE-L4 aprovado
* [ ] DoD do módulo atingido
* [ ] Pendências classificadas
* [ ] Próxima fase definida

---

## 14. Critérios de Falha Sistêmica (Red Flags)

Se qualquer item abaixo ocorrer, o processo deve ser interrompido e corrigido:

1. Agente implementa código antes de MCP mínimo
2. AR sem alvo SSOT (INV/FLOW/SCREEN/CONTRACT)
3. “Implementado” sem evidência
4. Frontend inventado sem `SCREENS_SPEC`/`FRONT_BACK_CONTRACT`
5. Invariante bloqueante sem teste de violação
6. Mistura AS-IS e TO-BE sem marcação
7. Escopo expandido por “boas práticas” sem aprovação

---

## 15. Política de Evolução deste Plano (Governança)

Mudanças neste documento DEVEM:

1. Referenciar AR/ADR de governança
2. Explicar impacto no fluxo de módulos
3. Atualizar gates/checklists se aplicável
4. Ser aprovadas pelos owners definidos no cabeçalho

---

## 16. Status Inicial Recomendado (Execução)

### Módulo piloto recomendado

* `COMPETITIONS` (FASE_0)

### Próxima ação objetiva

* Rodar o Template de Prompt Mestre (Seção 12) para `COMPETITIONS`
* Gerar MCP completo
* Submeter à validação humana
* Iniciar ARs Classe A/B/C do núcleo bloqueante


