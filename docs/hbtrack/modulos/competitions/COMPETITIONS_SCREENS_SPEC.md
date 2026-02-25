# COMPETITIONS_SCREENS_SPEC.md

Status: DRAFT
Versão: v0.1.0
Tipo de Documento: Screens Specification (Normativo Operacional / SSOT)
Módulo: COMPETITIONS
Fase: FASE_0
Autoridade: NORMATIVO_OPERACIONAL
Owners:
- Arquitetura (Arquiteto): Agente Arquiteto
- Frontend: Agente Executor
- Auditoria: Agente Testador

Última revisão: 2026-02-25
Próxima revisão recomendada: 2026-03-15

Dependências:
- INVARIANTS_COMPETITIONS.md
- COMPETITIONS_USER_FLOWS.md
- COMPETITIONS_FRONT_BACK_CONTRACT.md
- AR_BACKLOG_COMPETITIONS.md

---

## 1. Objetivo (Normativo)

Especificar os estados funcionais mínimos de cada tela do módulo Competitions. Este documento é a fonte de verdade para implementação de frontend e testes de UI.

---

## 2. Escopo

### 2.1 Dentro do escopo
- Estados funcionais de cada tela (loading, error, empty, data, validação)
- CTAs (Call-to-Action) obrigatórios por tela
- Dados mínimos exibidos e campos obrigatórios
- Comportamento de erros e avisos por estado

### 2.2 Fora do escopo
- Pixel-perfect design / paleta de cores
- Responsividade avançada
- Animações e microinterações
- Telas de outros módulos

---

## 3. Convenções de Estado

| Estado | Símbolo | Descrição |
|--------|---------|-----------|
| loading | ⏳ | Requisição em andamento |
| error | 🔴 | Erro de API ou validação |
| empty | ⬜ | Lista/dado vazio, sem erro |
| data | ✅ | Dados carregados com sucesso |
| pending | ⚠️ | Dado com pendência não-bloqueante |
| blocked | ❌ | Ação bloqueada por invariante |

---

## 4. Telas

---

### SCREEN-COMP-001 — Lista de Competições

**Rota**: `/competitions`
**Fase**: FASE_0
**Prioridade**: ALTA
**Flows**: FLOW-COMP-001
**Contratos**: CONTRACT-COMP-001

#### Estados da tela

| Estado | Conteúdo mínimo | CTA disponível |
|--------|-----------------|----------------|
| ⏳ loading | Skeleton/spinner | — |
| 🔴 error | Mensagem de erro + retry | Retry |
| ⬜ empty | "Nenhuma competição" + call-to-action | "Nova Competição" |
| ✅ data | Lista: nome, temporada, modalidade, status, total partidas | "Nova Competição", "Ver Detalhe" |

#### Filtros mínimos
- Por status: draft / active / finished / cancelled
- Por temporada (season)
- Busca por nome

#### Dados mínimos por item
- nome, temporada, modalidade, status (badge), contagem partidas, data criação

#### Invariantes aplicadas
- INV-COMP-001: status exibido deve ser do domínio válido

---

### SCREEN-COMP-002 — Formulário Criar/Editar Competição

**Rota**: `/competitions/new` | `/competitions/{id}/edit`
**Fase**: FASE_0
**Prioridade**: ALTA
**Flows**: FLOW-COMP-001
**Contratos**: CONTRACT-COMP-002

#### Campos obrigatórios

| Campo | Tipo | Validação | Invariante |
|-------|------|-----------|------------|
| nome | text | required, max 255 | INV-COMP-009 |
| temporada | text | required | INV-COMP-009 |
| modalidade | select | required, enum | INV-COMP-002 |
| points_per_win | number | required, integer >= 1 | INV-COMP-007 |
| points_per_draw | number | optional, integer >= 0 | INV-COMP-007 |
| points_per_loss | number | optional, integer >= 0 | INV-COMP-007 |

#### Estados de submissão

| Estado | Comportamento |
|--------|---------------|
| ⏳ submitting | Botão desabilitado + spinner |
| 🔴 error 409 | Campo nome+temporada destacado: "Já existe" |
| 🔴 error 422 | Campos inválidos destacados |
| ✅ success | Redirect para SCREEN-COMP-003 |

---

### SCREEN-COMP-003 — Detalhe de Competição

**Rota**: `/competitions/{id}`
**Fase**: FASE_0
**Prioridade**: ALTA
**Flows**: FLOW-COMP-001..006
**Contratos**: CONTRACT-COMP-003

#### Layout com abas

| Aba | Tela Destino |
|-----|------|
| Visão Geral | Resumo + metadados |
| Fases | SCREEN-COMP-004 |
| Equipes | SCREEN-COMP-005 |
| Partidas | SCREEN-COMP-006 |
| Classificação | SCREEN-COMP-007 |

#### Cabeçalho
- nome, temporada, modalidade, status
- pontuação configurada (ppw/ppd/ppl)
- badge de pendências (INV-COMP-010, 011)
- CTAs: "Editar", "Importar PDF", "Resolver Pendências" (se badge > 0)

#### Badge de pendências

| Condição | Exibição |
|----------|----------|
| Sem pendências | Sem badge |
| 1+ adversários ambíguos | ⚠️ badge laranja com contagem |
| 1+ atletas sem vínculo | ⚠️ badge laranja com contagem |

---

### SCREEN-COMP-004 — Gestão de Fases

**Rota**: `/competitions/{id}/phases`
**Fase**: FASE_0
**Prioridade**: ALTA
**Flows**: FLOW-COMP-003
**Contratos**: CONTRACT-COMP-004

#### Estados

| Estado | Conteúdo |
|--------|----------|
| ⬜ empty | "Nenhuma fase cadastrada" + CTA "Nova Fase" |
| ✅ data | Lista de fases: nome, data início/fim, status |

#### Campos do formulário de fase

| Campo | Tipo | Obrigatório |
|-------|------|-------------|
| nome | text | sim |
| data_inicio | date | sim |
| data_fim | date | sim |
| tipo | select | não |

#### Ações por fase
- Editar (PATCH)
- Excluir (soft delete — requer deleted_reason, INV-COMP-003)

---

### SCREEN-COMP-005 — Gestão de Equipes Adversárias

**Rota**: `/competitions/{id}/teams`
**Fase**: FASE_0
**Prioridade**: ALTA
**Flows**: FLOW-COMP-004
**Contratos**: CONTRACT-COMP-005

#### Estados

| Estado | Conteúdo |
|--------|----------|
| ⬜ empty | "Nenhuma equipe" + CTA "Adicionar Equipe" |
| ✅ data | Lista: nome, canonical_name, linked_team, pendências |
| ⚠️ pending | Equipe com aliases ambíguos |

#### Formulário de adição

| Campo | Tipo | Comportamento |
|-------|------|---------------|
| nome | text | Sugestão de equipes similares ao digitar |
| linked_team | select (opcional) | Para vincular como "nossa equipe" |

---

### SCREEN-COMP-006 — Lista e Registro de Partidas

**Rota**: `/competitions/{id}/matches`
**Fase**: FASE_0
**Prioridade**: ALTA
**Flows**: FLOW-COMP-005
**Contratos**: CONTRACT-COMP-006, CONTRACT-COMP-007

#### Estados da lista

| Estado | Conteúdo |
|--------|----------|
| ⬜ empty | "Nenhuma partida" + CTA "Nova Partida" |
| ✅ data | Tabela: data, mandante, placar, visitante, fase, status |
| ⏳ draft | Partidas sem placar: badge "Rascunho" |

#### Formulário nova partida

| Campo | Tipo | Validação | Invariante |
|-------|------|-----------|------------|
| fase_id | select | required | INV-COMP-019 |
| data | datetime | required | — |
| equipe_mandante | select | required | INV-COMP-018 |
| equipe_visitante | select | required, ≠ mandante | INV-COMP-018 |
| external_ref | text | unique por competição (opcional) | INV-COMP-014 |

#### Formulário de placar

| Campo | Tipo | Validação | Invariante |
|-------|------|-----------|------------|
| home_score | number | >= 0 | INV-COMP-016 |
| away_score | number | >= 0 | INV-COMP-016 |
| status | select (finished/cancelled) | required | INV-COMP-012 |

#### Nota
- Partidas draft: NÃO contam na classificação (INV-COMP-012) — indicador visual claro

---

### SCREEN-COMP-007 — Tabela de Classificação (Standings)

**Rota**: `/competitions/{id}/standings`
**Fase**: FASE_0
**Prioridade**: ALTA
**Flows**: FLOW-COMP-006
**Contratos**: CONTRACT-COMP-008

#### Estados

| Estado | Conteúdo |
|--------|----------|
| ⏳ loading | Skeleton da tabela |
| ⬜ empty | "Nenhuma partida finalizada para calcular classificação" |
| ✅ data | Tabela completa |
| ⚠️ pending | "X partidas pendentes não contabilizadas" |

#### Colunas mínimas

| # | Coluna | Origem |
|---|--------|--------|
| 1 | Posição | Calculada |
| 2 | Equipe | opponent_team.name |
| 3 | PJ | wins + draws + losses |
| 4 | PTS | ppw×wins + ppd×draws + ppl×losses |
| 5 | V | wins |
| 6 | E | draws |
| 7 | D | losses |
| 8 | GP | goals_for |
| 9 | GC | goals_against |
| 10 | SG | goals_for - goals_against |

#### Destaques
- Nossa equipe (linked_team_id) com linha destacada
- Filtro por fase
- Badge aviso se sem regras de desempate (INV-COMP-013)

---

### SCREEN-COMP-008 — Importação via IA / Resolver Pendências

**Rota**: `/competitions/{id}/import` | `/competitions/{id}/pending`
**Fase**: FASE_0
**Prioridade**: ALTA
**Flows**: FLOW-COMP-002, FLOW-COMP-007
**Contratos**: CONTRACT-COMP-009

#### Sub-tela: Upload PDF

| Estado | Conteúdo |
|--------|----------|
| inicial | Dropzone + botão upload |
| ⏳ processing | "IA processando PDF..." |
| 🔴 error | Mensagem + retry |
| ✅ preview | Estrutura extraída com confidence scores |

#### Sub-tela: Revisão antes de importar

| Item | Exibição | Ação |
|------|----------|------|
| Competição | Nome + temporada + modalidade extraídos | Editar |
| Fases | Lista extraída | Aceitar/Editar/Remover |
| Equipes | CONFIRMADO / PENDENTE (ambíguo) | Selecionar match manual |
| Partidas | Lista com placares | Editar se necessário |

#### Sub-tela: Pendências após importação

| Item | Exibição |
|------|----------|
| Adversários ambíguos | Lista com sugestões de merge |
| Atletas sem vínculo | Lista com ação: vincular ao time correto |
| Partidas com equipe TBD | Lista com ação: resolver equipe |

---

## 5. Matriz de Rastreabilidade (Telas → Flows → Contratos)

| SCREEN ID | Rota | Flows | Contratos | Fase | Prioridade |
|-----------|------|-------|-----------|------|------------|
| SCREEN-COMP-001 | /competitions | FLOW-001 | CONTRACT-001 | FASE_0 | ALTA |
| SCREEN-COMP-002 | /competitions/new | FLOW-001 | CONTRACT-002 | FASE_0 | ALTA |
| SCREEN-COMP-003 | /competitions/{id} | FLOW-001..006 | CONTRACT-003 | FASE_0 | ALTA |
| SCREEN-COMP-004 | /competitions/{id}/phases | FLOW-003 | CONTRACT-004 | FASE_0 | ALTA |
| SCREEN-COMP-005 | /competitions/{id}/teams | FLOW-004 | CONTRACT-005 | FASE_0 | ALTA |
| SCREEN-COMP-006 | /competitions/{id}/matches | FLOW-005 | CONTRACT-006, 007 | FASE_0 | ALTA |
| SCREEN-COMP-007 | /competitions/{id}/standings | FLOW-006 | CONTRACT-008 | FASE_0 | ALTA |
| SCREEN-COMP-008 | /competitions/{id}/import | FLOW-002, 007 | CONTRACT-009 | FASE_0 | ALTA |

---

## 6. Decisões de UX Pendentes

| # | Decisão | Impacto | Status |
|---|---------|---------|--------|
| D-001 | Classificação recalculada em tempo real ou com botão? | UX vs performance | PENDENTE |
| D-002 | Modal ou página separada para nova partida? | UX | PENDENTE |
| D-003 | Import PDF: wizard multi-step ou página única? | UX | PENDENTE |
| D-004 | Nossa equipe destacada em cor específica? | UX/branding | PENDENTE |
