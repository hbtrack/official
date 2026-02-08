# UAT Plan — Módulo TRAINING

## 1. Controle do documento

* **Status**: DRAFT
* **Versão**: v1.0
* **Data**: 2026-02-07
* **Escopo**: User Acceptance Testing para módulo Training V1.0
* **Referências**:
  * PRD: `docs/Hb Track/PRD_HB_TRACK.md` (§6 RF-001 a RF-009, §7 User Stories)
  * TRD: `docs/02-modulos/training/TRD_TRAINING.md` (contratos API, regras)
  * PRD Baseline: `docs/02-modulos/training/PRD_BASELINE_ASIS_TRAINING.md`

---

## 2. Objetivo

Validar que o módulo Training atende aos critérios de aceitação definidos no PRD antes do lançamento para Early Adopters (Q1/2026).

**Critério de Sucesso Global**: Todos cenários CT-* passam sem bugs bloqueantes em 2 sprints consecutivos.

---

## 3. Cenários de Teste por Persona

### 3.1 Treinador Solo (Carlos — PRD §3.1 Persona 1)

| ID | Cenário | PRD-FR | Critério de Aceitação |
|----|---------|--------|----------------------|
| CT-001 | Criar sessão de treino com 5 áreas de foco (soma = 100%) | RF-001 | Sessão criada com status `draft`, focus sum validado |
| CT-002 | Publicar sessão (draft → scheduled) | RF-001 | Status muda para `scheduled`, lista de presença gerada automaticamente |
| CT-003 | Registrar presença (Present/Absent/Justified) | RF-001 | Attendance registrado, cache invalidado |
| CT-004 | Visualizar dashboard de wellness pré-treino antes da sessão | RF-002 | Dashboard exibe dados de wellness da equipe em < 3s |
| CT-005 | Fechar sessão (in_progress → pending_review → readonly) | RF-001 | Lifecycle completo, sessão readonly não editável |
| CT-006 | Duplicar sessão existente para nova data | RF-001 | Nova sessão criada com mesmos templates/exercises |

### 3.2 Atleta (Beatriz — PRD §3.1 Persona 3)

| ID | Cenário | PRD-FR | Critério de Aceitação |
|----|---------|--------|----------------------|
| CT-007 | Submeter wellness pré-treino (5 escalas) | RF-002 | Submissão aceita em < 30s, validação das escalas 1-5 |
| CT-008 | Verificar deadline de wellness pré (session_at - 2h) | RF-002 | Rejeição após deadline com erro 423 Locked |
| CT-009 | Submeter wellness pós-treino (RPE + minutes_effective) | RF-003 | `internal_load` calculado automaticamente pelo trigger |
| CT-010 | Verificar duplicidade de submission | RF-002/003 | Erro 409 ao tentar submeter 2x para mesma sessão |
| CT-011 | Visualizar badges conquistados (wellness champion, streak) | RF-006 | Lista de badges visível com mês de referência |

### 3.3 Coordenador (Mariana — PRD §3.1 Persona 2)

| ID | Cenário | PRD-FR | Critério de Aceitação |
|----|---------|--------|----------------------|
| CT-012 | Visualizar analytics dashboard (17 métricas) | RF-008 | Dashboard carrega em < 3s com dados de cache |
| CT-013 | Comparar carga semanal entre equipes | RF-005 | Métricas exibidas por microciclo e mensalmente |
| CT-014 | Verificar alertas de sobrecarga (threshold 1.5x) | RF-005 | Atleta com carga > threshold exibe alerta |
| CT-015 | Visualizar Top 5 performers wellness | RF-006 | Ranking correto baseado em response_rate |
| CT-016 | Criar e gerenciar ciclos (macro/meso) | RF-007 | Ciclo criado com validação de datas |

### 3.4 Dirigente (Roberto — PRD §3.1 Persona 4)

| ID | Cenário | PRD-FR | Critério de Aceitação |
|----|---------|--------|----------------------|
| CT-017 | Exportar dados de atleta (LGPD self-service) | RF-009 | Export gerado via Celery, rate limit 5/dia |
| CT-018 | Auditar logs de ações sensíveis | RF-010 | Audit logs visíveis, append-only, filtráveis |
| CT-019 | Verificar controle de acesso (atleta não vê wellness de outro) | RF-002 | Erro 403 ao acessar dados de outro atleta |
| CT-020 | Verificar retenção e anonymização após 3 anos | RF-009 | Dados de wellness anonimizados (athlete_id = NULL) |

---

## 4. Cenários Negativos e Edge Cases

| ID | Cenário | Resultado Esperado |
|----|---------|-------------------|
| CT-N01 | Criar sessão sem equipe ativa | Erro 422 com mensagem clara |
| CT-N02 | Publicar sessão sem focus areas | Erro de validação |
| CT-N03 | Tentar editar sessão em status readonly | Erro 409/403 |
| CT-N04 | Wellness pré com escala fora do range (0 ou 6) | Erro 422 |
| CT-N05 | Export com rate limit excedido (6a exportação no dia) | Erro 429 |

---

## 5. Critérios de Aceitação Global

| Critério | Meta | Método de Medição |
|----------|------|-------------------|
| Completion rate (sem ajuda) | ≥ 95% | Observação direta durante UAT |
| Bugs bloqueantes | 0 em 2 sprints | Bug tracker (Issues GitHub) |
| Tempo operações críticas | < 30s (wellness submit) | Cronômetro durante UAT |
| Dashboard load time | < 3s | Observação + browser DevTools |
| Erros de validação claros | 100% mensagens compreensíveis | Feedback qualitativo dos testers |

---

## 6. Ambiente de Teste

* **Ambiente**: Staging (Render) com dados de demonstração
* **Database**: PostgreSQL (Neon) — clone de produção com dados anonimizados
* **Usuários de teste**: 3 clubes piloto com dados reais anonimizados
* **Browsers suportados**: Chrome 120+, Safari 17+, Firefox 120+
* **Dispositivos**: Desktop (Windows/Mac) + Mobile (Android/iOS)

---

## 7. Calendário

| Semana | Atividade | Responsável |
|--------|-----------|-------------|
| Semana 1 | Setup ambiente staging + criação de dados demo + briefing usuários | Tech Lead |
| Semana 2-3 | Execução dos cenários CT-001 a CT-020 + CT-N01 a CT-N05 | QA + Usuários piloto |
| Semana 4 | Compilação de resultados + triagem de bugs + ajustes | Equipe dev |
| Semana 5 | Re-teste de bugs corrigidos + sign-off | Product Owner |

---

## 8. Rastreabilidade

| PRD-FR | Cenários UAT | Coverage |
|--------|-------------|----------|
| RF-001 | CT-001, CT-002, CT-003, CT-005, CT-006, CT-N02, CT-N03 | ✅ 7 cenários |
| RF-002 | CT-004, CT-007, CT-008, CT-010, CT-019, CT-N04 | ✅ 6 cenários |
| RF-003 | CT-009, CT-010 | ✅ 2 cenários |
| RF-005 | CT-012, CT-013, CT-014 | ✅ 3 cenários |
| RF-006 | CT-011, CT-015 | ✅ 2 cenários |
| RF-007 | CT-016 | ✅ 1 cenário |
| RF-008 | CT-012 | ✅ 1 cenário |
| RF-009 | CT-017, CT-020, CT-N05 | ✅ 3 cenários |
| RF-010 | CT-018 | ✅ 1 cenário |

**Total**: 25 cenários (20 positivos + 5 negativos) cobrindo 9 PRD-FRs
