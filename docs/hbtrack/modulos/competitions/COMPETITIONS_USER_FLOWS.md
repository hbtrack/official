# COMPETITIONS_USER_FLOWS.md

Status: DRAFT
Versão: v0.1.0
Tipo de Documento: User Flows (Normativo Operacional / SSOT)
Módulo: COMPETITIONS
Fase: FASE_0
Autoridade: NORMATIVO_OPERACIONAL
Owners:
- Arquitetura (Arquiteto): Agente Arquiteto
- Produto: Agente Executor
- Auditoria: Agente Testador

Última revisão: 2026-02-25
Próxima revisão recomendada: 2026-03-15

Dependências:
- INVARIANTS_COMPETITIONS.md
- COMPETITIONS_SCREENS_SPEC.md
- COMPETITIONS_FRONT_BACK_CONTRACT.md
- AR_BACKLOG_COMPETITIONS.md
- TEST_MATRIX_COMPETITIONS.md

---

## 1. Objetivo (Normativo)

Definir os fluxos de interação do usuário com o módulo Competitions, ancorando cada passo em telas (SCREEN-COMP-*) e contratos front-back (CONTRACT-COMP-*). Estes fluxos são o contrato de jornada mínima de valor para a fase.

---

## 2. Escopo

### 2.1 Dentro do escopo
- Fluxos de criação e gestão de competições (manual e via IA/PDF)
- Fluxos de gestão de fases, equipes adversárias e partidas
- Visualização de tabela de classificação (standings)
- Resolução de pendências de ingestão IA

### 2.2 Fora do escopo
- Fluxos de scout (módulo separado)
- Configurações de organização/usuário
- Exportação de relatórios (módulo separado)
- Notificações (módulo separado)

---

## 3. Convenções

- **Ator principal**: Treinador / Coordenador autenticado na organização
- **Pré-condição global**: usuário autenticado com organização selecionada
- **Estados de partida**: draft → scheduled → in_progress → finished | cancelled
- **Estado “pendência”**: dado incompleto que NÃO bloqueia o fluxo principal (INV-COMP-010, INV-COMP-011)

---

## 4. Fluxos

---

### FLOW-COMP-001 — Criar Competição (Manual)

**Prioridade**: ALTA  
**Fase**: FASE_0  
**Alvos SSOT**: INV-COMP-001, INV-COMP-002, INV-COMP-007, INV-COMP-009  
**Telas**: SCREEN-COMP-001, SCREEN-COMP-002  
**Contratos**: CONTRACT-COMP-001, CONTRACT-COMP-002

#### Passos

| # | Ator | Ação | Sistema | Tela/Contrato |
|---|------|------|---------|---------------|
| 1 | Usuário | Acessa módulo Competitions | Exibe lista de competições | SCREEN-COMP-001 |
| 2 | Usuário | Clica "Nova Competição" | Abre formulário de criação | SCREEN-COMP-002 |
| 3 | Usuário | Preenche nome, temporada, modalidade, pontuação | Valida campos obrigatórios | SCREEN-COMP-002 |
| 4 | Usuário | Submete formulário | POST /api/v1/competitions/v2 | CONTRACT-COMP-002 |
| 5 | Sistema | Valida unicidade (org+nome+temporada) | Retorna 409 se duplicado | INV-COMP-009 |
| 6 | Sistema | Persiste competição com status=draft | Redireciona para detalhe | SCREEN-COMP-003 |

#### Exceções

| Código | Condição | Comportamento |
|--------|----------|---------------|
| E-001 | Nome+temporada já existe na org | Erro 409, campo destacado |
| E-002 | Modalidade fora do domínio | Erro 422 de validação |
| E-003 | points_per_win ausente | Erro 422 (NOT NULL, INV-COMP-007) |

---

### FLOW-COMP-002 — Criar Competição via PDF/IA

**Prioridade**: ALTA  
**Fase**: FASE_0  
**Alvos SSOT**: INV-COMP-023, INV-COMP-029, INV-COMP-014  
**Telas**: SCREEN-COMP-008  
**Contratos**: CONTRACT-COMP-009

#### Passos

| # | Ator | Ação | Sistema | Tela/Contrato |
|---|------|------|---------|---------------|
| 1 | Usuário | Clica "Importar PDF" | Abre modal de upload | SCREEN-COMP-008 |
| 2 | Usuário | Faz upload do PDF da súmula/tabela | POST /api/v1/competitions/v2/parse-pdf | CONTRACT-COMP-009 |
| 3 | Sistema | IA extrai: competição, fases, adversários, partidas | Retorna estrutura com flags de confiança | CONTRACT-COMP-009 |
| 4 | Usuário | Revisa e confirma extração | Visualiza pendências marcadas | SCREEN-COMP-008 |
| 5 | Usuário | Confirma importação | POST /api/v1/competitions/v2/{id}/import-from-ai | CONTRACT-COMP-009 |
| 6 | Sistema | Cria entidades; adversários ambíguos = PENDÊNCIA (não bloqueante) | Retorna sumário de criação + pendências | INV-COMP-023 |

#### Exceções

| Código | Condição | Comportamento |
|--------|----------|---------------|
| E-001 | PDF ilegível / sem dados | Erro 422, usuário tenta upload manual |
| E-002 | Competição já existe (external_ref duplicado) | Sistema identifica e não duplica (INV-COMP-014) |
| E-003 | Adversário ambíguo — múltiplos matches | Cria PENDÊNCIA para resolução manual (INV-COMP-011) |

---

### FLOW-COMP-003 — Gerir Fases de Competição

**Prioridade**: ALTA  
**Fase**: FASE_0  
**Alvos SSOT**: INV-COMP-019  
**Telas**: SCREEN-COMP-004  
**Contratos**: CONTRACT-COMP-004

#### Passos

| # | Ator | Ação | Sistema | Tela/Contrato |
|---|------|------|---------|---------------|
| 1 | Usuário | Acessa detalhe da competição | Exibe abas: Fases / Equipes / Partidas / Classificação | SCREEN-COMP-003 |
| 2 | Usuário | Vai em aba "Fases", clica "Nova Fase" | Abre formulário de fase | SCREEN-COMP-004 |
| 3 | Usuário | Preenche nome, datas inicio/fim | Valida datas | SCREEN-COMP-004 |
| 4 | Usuário | Submete | POST /api/v1/competitions/{id}/phases | CONTRACT-COMP-004 |
| 5 | Sistema | Cria fase, associa à competição | Exibe fase na lista | SCREEN-COMP-004 |

#### Notas
- Fase com deleted_at IS NOT NULL requer deleted_reason (INV-COMP-003)
- Soft delete via PATCH (não DELETE) mantém rastreabilidade

---

### FLOW-COMP-004 — Gerir Equipes Adversárias

**Prioridade**: ALTA  
**Fase**: FASE_0  
**Alvos SSOT**: INV-COMP-011, INV-COMP-027  
**Telas**: SCREEN-COMP-005  
**Contratos**: CONTRACT-COMP-005

#### Passos

| # | Ator | Ação | Sistema | Tela/Contrato |
|---|------|------|---------|---------------|
| 1 | Usuário | Vai em aba "Equipes" na competição | Lista equipes adversárias | SCREEN-COMP-005 |
| 2 | Usuário | Clica "Adicionar Equipe" | Abre modal com campo de nome | SCREEN-COMP-005 |
| 3 | Usuário | Digita nome da equipe | Sistema sugere equipes similares (canonical) | INV-COMP-011 |
| 4 | Usuário | Confirma nova equipe ou seleciona existente | POST /api/v1/competitions/{id}/opponent-teams | CONTRACT-COMP-005 |
| 5 | Sistema | Valida unicidade canônica (normalize+UNIQUE) | Retorna 409 se alias já mapeado | INV-COMP-011 |

#### Exceções

| Código | Condição | Comportamento |
|--------|----------|---------------|
| E-001 | Nome normalizado já existe | Erro 409 com sugestão de equipe canônica |
| E-002 | Bulk create com duplicatas parciais | Retorna criados + ignorados com motivo |

---

### FLOW-COMP-005 — Registrar Partida (Manual)

**Prioridade**: ALTA  
**Fase**: FASE_0  
**Alvos SSOT**: INV-COMP-012, INV-COMP-016, INV-COMP-018, INV-COMP-019, INV-COMP-021  
**Telas**: SCREEN-COMP-006  
**Contratos**: CONTRACT-COMP-006, CONTRACT-COMP-007

#### Passos

| # | Ator | Ação | Sistema | Tela/Contrato |
|---|------|------|---------|---------------|
| 1 | Usuário | Vai em aba "Partidas", clica "Nova Partida" | Abre formulário | SCREEN-COMP-006 |
| 2 | Usuário | Seleciona: fase, data, equipe mandante, equipe visitante | Valida equipes distintas | INV-COMP-018 |
| 3 | Usuário | Submete partida | POST /api/v1/competitions/{id}/matches | CONTRACT-COMP-006 |
| 4 | Sistema | Cria partida com status=draft (sem placar) | Exibe na lista com status draft | SCREEN-COMP-006 |
| 5 | Usuário | Edita partida para inserir placar | PATCH /api/v1/competitions/{id}/matches/{match_id}/result | CONTRACT-COMP-007 |
| 6 | Sistema | Valida placar >= 0, persiste, recalcula standings | Exibe placar atualizado | INV-COMP-016 |

#### Exceções

| Código | Condição | Comportamento |
|--------|----------|---------------|
| E-001 | home_team_id == away_team_id | Erro 422 (INV-COMP-018) |
| E-002 | Placar negativo | Erro 422 (INV-COMP-016) |
| E-003 | Partida status=draft não conta nos standings | Comportamento esperado (INV-COMP-012) |

---

### FLOW-COMP-006 — Visualizar Tabela de Classificação

**Prioridade**: ALTA  
**Fase**: FASE_0  
**Alvos SSOT**: INV-COMP-008, INV-COMP-012, INV-COMP-015, INV-COMP-017, INV-COMP-019, INV-COMP-021, INV-COMP-024  
**Telas**: SCREEN-COMP-007  
**Contratos**: CONTRACT-COMP-008

#### Passos

| # | Ator | Ação | Sistema | Tela/Contrato |
|---|------|------|---------|---------------|
| 1 | Usuário | Vai em aba "Classificação" | Tela exibe tabela com loading | SCREEN-COMP-007 |
| 2 | Sistema | GET /api/v1/competitions/{id}/standings | Filtra apenas partidas concluídas com equipes resolvidas | CONTRACT-COMP-008 |
| 3 | Sistema | Calcula pontos usando ppw/ppd/ppl da competição | Sem valores hardcoded (INV-COMP-008) | INV-COMP-024 |
| 4 | Sistema | Retorna rankings ordenados por pontos → saldo de gols → gols marcados | Exibe tabela completa | SCREEN-COMP-007 |
| 5 | Usuário | Filtra por fase (opcional) | GET com ?phase_id=X | INV-COMP-019 |

#### Notas
- Nossa equipe (linked_team_id) destacada na tabela (PRD §8.3)
- Recálculo é idempotente (INV-COMP-015, INV-COMP-017)
- Partidas draft excluídas (INV-COMP-012)

---

### FLOW-COMP-007 — Resolver Pendências de Ingestão IA

**Prioridade**: MÉDIA  
**Fase**: FASE_1  
**Alvos SSOT**: INV-COMP-010, INV-COMP-011, INV-COMP-023, INV-COMP-029  
**Telas**: SCREEN-COMP-008  
**Contratos**: CONTRACT-COMP-009

#### Passos

| # | Ator | Ação | Sistema | Tela/Contrato |
|---|------|------|---------|---------------|
| 1 | Sistema | Após importação, lista pendências | Badge de pendências na competição | SCREEN-COMP-003 |
| 2 | Usuário | Clica "Resolver Pendências" | Lista adversários/atletas não resolvidos | SCREEN-COMP-008 |
| 3 | Usuário | Para cada pendência: confirma match sugerido ou cria novo | PATCH opponent-team ou match | CONTRACT-COMP-005 |
| 4 | Sistema | Remove pendência, associa entidade canônica | Atualiza lista de pendências | SCREEN-COMP-008 |

---

## 5. Matriz de Rastreabilidade (Flows → SSOT)

| FLOW ID | Fase | Prioridade | Invariantes Alvo | Telas | Contratos |
|---------|------|------------|------------------|-------|-----------|
| FLOW-COMP-001 | FASE_0 | ALTA | INV-001, 002, 007, 009 | SCREEN-001, 002, 003 | CONTRACT-001, 002 |
| FLOW-COMP-002 | FASE_0 | ALTA | INV-014, 023, 029 | SCREEN-008 | CONTRACT-009 |
| FLOW-COMP-003 | FASE_0 | ALTA | INV-003, 019 | SCREEN-003, 004 | CONTRACT-004 |
| FLOW-COMP-004 | FASE_0 | ALTA | INV-011, 027 | SCREEN-005 | CONTRACT-005 |
| FLOW-COMP-005 | FASE_0 | ALTA | INV-012, 016, 018, 019, 021 | SCREEN-006 | CONTRACT-006, 007 |
| FLOW-COMP-006 | FASE_0 | ALTA | INV-008, 012, 015, 017, 019, 021, 024 | SCREEN-007 | CONTRACT-008 |
| FLOW-COMP-007 | FASE_1 | MÉDIA | INV-010, 011, 023, 029 | SCREEN-008 | CONTRACT-005, 009 |

---

## 6. Decisões Pendentes para Validação Humana

| # | Decisão | Impacto | Status |
|---|---------|---------|--------|
| D-001 | Recálculo de standings: automático no insert/update de partida ou sob demanda? | Performance vs UX | PENDENTE |
| D-002 | Critérios de desempate configuráveis por competição (JSONB) ou fixed 3 critérios? | INV-COMP-013 | PENDENTE |
| D-003 | Nossa equipe sempre aparece na tabela mesmo sem partidas? | UX vs integridade | PENDENTE |
| D-004 | Fluxo de cancelamento de competição ativa: confirmação obrigatória? | UX guard | PENDENTE |
