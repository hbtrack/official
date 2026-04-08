---
doc_type: canon
version: "1.0.0"
last_reviewed: "2026-03-18"
status: active
artifact: "SCOPE_BOUNDARY_POLICY"
scope: "global"
---

# Política de Boundary entre Módulos — HB Track

## Objetivo

Definir as regras explícitas de cross-module references permitidas no HB Track, mitigando vulnerabilidades de scope overflow (falhas de isolamento entre domínios) detectadas na auditoria red team (ADR-034).

Este documento é o **SSOT (Single Source of Truth)** para validação de referências cross-module em tempo de pre-contrato (Fase 1 do orchestrador).

---

## 1. Princípios de Boundary

### 1.1 Isolamento por Domínio Funcional

O HB Track é um monólito modular com 17 módulos lógicos. Cada módulo é autoridade em seu macrodomínio:

- **users**: identidade pessoal, perfil funcional, vínculo com times/temporadas
- **identity_access**: autenticação, autorização, credenciais, sessão, MFA, JWT, RBAC
- **training**: planejamento de sessões de treino, execução, feedback, carga
- **wellness**: métricas pós-treino, fadiga, recuperação
- **medical**: histórico clínico, lesões, elegibilidade médica
- **analytics**: agregações de dados, KPIs, relatórios
- **audit**: rastreamento de mudanças, compliance, auditoria
- ...

### 1.2 Regra Crítica: Nenhuma Referência sem Justificativa

Uma referência de módulo A para recurso de módulo B é válida **somente se**:

1. Consta em `allowed_references` do módulo A nesta policy, **OU**
2. Existe ADR aprovada que autoriza a exceção (link em `exceptions`)

Se nenhuma das duas condições for verdadeira → **BLOCKED_SCOPE_OVERFLOW**

### 1.3 Cross-Cutting vs. Funcional

- **Cross-cutting módulos** (`identity_access`, `audit`, `notifications`) podem ser referenciados por módulos funcionais em casos justificados.
- **Módulos funcionais** devem evitar referenciar outros módulos funcionais, salvo quando há dependência de dados unidirecional explícita.

---

## 2. Matriz de Boundaries por Módulo

### users
**Função**: Gestão de identidade pessoal, profile funcional, vínculo com times e temporadas  
**Owner**: platform-core

```yaml
allowed_references:
  - module: seasons
    reason: "Link atleta → temporada (via time)"
    examples: ["/users/{userId}/seasons", "user.seasons"]
    
  - module: teams
    reason: "Link atleta → time (relação um-para-muitos por temporada)"
    examples: ["/users/{userId}/teams", "user.team_memberships"]
    
  - module: training
    reason: "Referência para contexto de sessão (quem participou)"
    examples: ["session.participants[*].user_id"]
    
  - module: wellness
    reason: "Dados de wellness referem identificação do atleta"
    examples: ["wellness_entry.user_id"]
    
  - module: medical
    reason: "Dados clínicos referem identificação do atleta"
    examples: ["medical_record.user_id"]
    
  - module: analytics
    reason: "Agregações referem usuários por ID"
    examples: ["analytics.aggregations[*].user_ids"]
    
  - module: reports
    reason: "Relatórios incluem identificação"
    examples: ["report.individual_data[*].user_id"]
    
  - module: scout
    reason: "Scout data includes atleta identification"
    examples: ["scout_entry.athlete_user_id"]

forbidden_references:
  - module: identity_access
    reason: "Nenhum dado de users pode definir/modificar credenciais, authn ou authz"
    
  - module: audit
    reason: "users não deve chamar audit diretamente; audit observa via integração"
    
  - module: notifications
    reason: "notifications é outbound; users não pode deflagrar eventos de notificação"
    
  - module: competitions
  - module: matches
  - module: exercises
  - module: ai_ingestion

exceptions: []
```

---

### seasons
**Função**: Ciclo de temporada, períodos, fases competitivas (conforme IHF)  
**Owner**: handball-ops

```yaml
allowed_references:
  - module: teams
    reason: "Uma temporada vincula múltiplos times"
    examples: ["/seasons/{seasonId}/teams", "season.teams"]
    
  - module: competitions
    reason: "Uma temporada contém competições reguladas"
    examples: ["/seasons/{seasonId}/competitions"]
    
  - module: users
    reason: "Metadados de temporada referem criador/modificador"
    examples: ["season.created_by_user_id"]
    
  - module: analytics
    reason: "Agregações de temporada"
    examples: ["analytics.season_leaderboards[*].season_id"]

forbidden_references:
  - module: identity_access
  - module: audit
  - module: notifications
  - module: training
  - module: wellness
  - module: medical
  - module: matches
  - module: scout
  - module: exercises
  - module: reports
  - module: ai_ingestion

exceptions: []
```

---

### teams
**Função**: Composição de elenco, categoria, configuração, staff  
**Owner**: handball-ops

```yaml
allowed_references:
  - module: seasons
    reason: "Time é defindo por temporada"
    examples: ["/teams/{teamId}/seasons/{seasonId}"]
    
  - module: users
    reason: "Elenco e staff vinculados a usuários"
    examples: ["/teams/{teamId}/roster", "team.coaching_staff[*].user_id"]
    
  - module: competitions
    reason: "Time participa de competições em uma temporada"
    examples: ["/teams/{teamId}/competitions"]
    
  - module: training
    reason: "Contextualizar treinos por time"
    examples: ["training_session.team_id"]
    
  - module: matches
    reason: "Contexto de partidas"
    examples: ["match.home_team_id", "match.away_team_id"]
    
  - module: analytics
    reason: "Agregações de performance por time"
    examples: ["analytics.team_stats[*].team_id"]
    
  - module: scout
    reason: "Scout data scoped by team"
    examples: ["scout_entry.team_id"]

forbidden_references:
  - module: identity_access
  - module: audit
  - module: notifications
  - module: wellness
  - module: medical
  - module: exercises
  - module: reports
  - module: ai_ingestion

exceptions: []
```

---

### training
**Função**: Planejamento de sessões, execução, carga, feedback, periodização  
**Owner**: performance-tech

```yaml
allowed_references:
  - module: users
    reason: "Atletas e staff em session"
    examples: ["/training/sessions/{sessionId}/participants", "session.coach_user_id"]
    
  - module: teams
    reason: "Sessão associada a um time"
    examples: ["/training/sessions/{sessionId}", "session.team_id"]
    
  - module: seasons
    reason: "Contexto de temporada para periodização"
    examples: ["/training/sessions/{sessionId}", "session.season_id"]
    
  - module: exercises
    reason: "Exercícios dentro de sessões"
    examples: ["/training/sessions/{sessionId}/exercises", "session.exercises[*].exercise_id"]
    
  - module: wellness
    reason: "Integração pós-treino: carga e wellness"
    examples: ["training_session.wellness_checkpoint"]
    
  - module: medical
    reason: "Elegibilidade médica para treino (ex: restrições)"
    examples: ["session.medical_clearance_required"]
    
  - module: analytics
    reason: "Agregações de carga, aderência, sessões"
    examples: ["analytics.session_load_data[*].session_id"]
    
  - module: ai_ingestion
    reason: "Processamento IA de sessões (ex: análise de vídeo)"
    examples: ["training_session.ai_insights"]
    
  - module: reports
    reason: "Relatórios de treino"
    examples: ["/reports/training_summary/{sessionId}"]

forbidden_references:
  - module: identity_access
  - module: audit
  - module: notifications
  - module: competitions
  - module: matches
  - module: scout

exceptions: []
```

---

### wellness
**Função**: Métricas de bem-estar, fadiga, recuperação pós-treino  
**Owner**: performance-tech

```yaml
allowed_references:
  - module: users
    reason: "Wellness links a atleta"
    examples: ["/wellness/{userId}", "wellness_entry.user_id"]
    
  - module: training
    reason: "Wellness completa contextualização de treino"
    examples: ["wellness_entry.training_session_id"]
    
  - module: teams
    reason: "Agregações de wellness por time"
    examples: ["wellness_summary.team_id"]
    
  - module: seasons
    reason: "Contextualizar wellness em temporada"
    examples: ["wellness_entry.season_id"]
    
  - module: medical
    reason: "Integração com histórico médico (contraincações, restrições)"
    examples: ["wellness_entry.medical_clearance"]
    
  - module: analytics
    reason: "Agregações de wellness"
    examples: ["analytics.wellness_trends[*].user_id"]

forbidden_references:
  - module: identity_access
  - module: audit
  - module: notifications
  - module: competitions
  - module: matches
  - module: scout
  - module: exercises
  - module: reports
  - module: ai_ingestion

exceptions: []
```

---

### medical
**Função**: Histórico clínico, lesões, elegibilidade, return-to-play  
**Owner**: performance-tech

```yaml
allowed_references:
  - module: users
    reason: "Registro clínico linked to atleta"
    examples: ["/medical/{userId}", "medical_record.user_id"]
    
  - module: training
    reason: "Restrições médicas impactam treino"
    examples: ["training_session.medical_restrictions[*].restriction_id"]
    
  - module: wellness
    reason: "Historico médico contexto para wellness"
    examples: ["wellness_entry.medical_status"]
    
  - module: teams
    reason: "Elegibilidade clínica agregada por time"
    examples: ["team.medical_summary"]
    
  - module: seasons
    reason: "Contexto de temporada para medical planning"
    examples: ["medical_record.season_id"]
    
  - module: analytics
    reason: "Agregações de lesões, disponibilidade"
    examples: ["analytics.injury_statistics[*].user_id"]

forbidden_references:
  - module: identity_access
  - module: audit
  - module: notifications
  - module: competitions
  - module: matches
  - module: scout
  - module: exercises
  - module: reports
  - module: ai_ingestion

exceptions: []
```

---

### competitions
**Função**: Fases competitivas, tabelas, chaveamentos, pontuação (conforme IHF)  
**Owner**: handball-ops

```yaml
allowed_references:
  - module: seasons
    reason: "Competição é definda dentro de temporada"
    examples: ["/competitions/{competitionId}", "competition.season_id"]
    
  - module: teams
    reason: "Times participam de competições"
    examples: ["/competitions/{competitionId}/teams", "competition.participating_teams"]
    
  - module: matches
    reason: "Matches são executados em uma competição"
    examples: ["/competitions/{competitionId}/matches"]
    
  - module: analytics
    reason: "Scoreboard, rankings by competition"
    examples: ["analytics.competition_standings[*].competition_id"]

forbidden_references:
  - module: identity_access
  - module: audit
  - module: notifications
  - module: users
  - module: training
  - module: wellness
  - module: medical
  - module: scout
  - module: exercises
  - module: reports
  - module: ai_ingestion

exceptions: []
```

---

### matches
**Função**: Registro de partidas, súmula, timeline de eventos, resultado  
**Owner**: handball-ops

```yaml
allowed_references:
  - module: competitions
    reason: "Match acontece em uma competição"
    examples: ["/matches/{matchId}", "match.competition_id"]
    
  - module: teams
    reason: "Times particiam: home e away"
    examples: ["match.home_team_id", "match.away_team_id"]
    
  - module: seasons
    reason: "Contexto de temporada"
    examples: ["match.season_id"]
    
  - module: scout
    reason: "Scout data coletada durante/após match"
    examples: ["match.scout_entries"]
    
  - module: analytics
    reason: "Estatísticas de match"
    examples: ["analytics.match_stats[*].match_id"]

forbidden_references:
  - module: identity_access
  - module: audit
  - module: notifications
  - module: users
  - module: training
  - module: wellness
  - module: medical
  - module: exercises
  - module: reports
  - module: ai_ingestion

exceptions: []
```

---

### scout
**Função**: Coleta e análise de performance durante treinos/partidas  
**Owner**: handball-ops

```yaml
allowed_references:
  - module: users
    reason: "Scout observer ou atleta sendo analisado"
    examples: ["scout_entry.observer_user_id", "scout_entry.athlete_user_id"]
    
  - module: teams
    reason: "Scout data scoped by team"
    examples: ["scout_entry.team_id"]
    
  - module: matches
    reason: "Scout durante partida"
    examples: ["scout_entry.match_id"]
    
  - module: training
    reason: "Scout durante treino"
    examples: ["scout_entry.training_session_id"]
    
  - module: analytics
    reason: "Agregações de scout"
    examples: ["analytics.scout_metrics[*].scout_entry_id"]
    
  - module: ai_ingestion
    reason: "IA processing de scout video/data"
    examples: ["scout_entry.ai_insights"]

forbidden_references:
  - module: identity_access
  - module: audit
  - module: notifications
  - module: seasons
  - module: competitions
  - module: wellness
  - module: medical
  - module: exercises
  - module: reports

exceptions: []
```

---

### exercises
**Função**: Catálogo de exercícios, progressões, métricas de execução  
**Owner**: performance-tech

```yaml
allowed_references:
  - module: training
    reason: "Exercícios executados em sessões"
    examples: ["training_session.exercises[*].exercise_id"]
    
  - module: analytics
    reason: "Agregações de execução de exercício"
    examples: ["analytics.exercise_performance[*].exercise_id"]

forbidden_references:
  - module: identity_access
  - module: audit
  - module: notifications
  - module: users
  - module: teams
  - module: seasons
  - module: competitions
  - module: matches
  - module: wellness
  - module: medical
  - module: scout
  - module: reports
  - module: ai_ingestion

exceptions: []
```

---

### analytics
**Função**: Agregações de dados, KPIs, dashboards, exportações  
**Owner**: performance-tech

```yaml
allowed_references:
  - module: users
    reason: "Individualização de analytics"
    examples: ["analytics.individual_stats[*].user_id"]
    
  - module: teams
    reason: "Agregações por time"
    examples: ["analytics.team_performance[*].team_id"]
    
  - module: seasons
    reason: "Analytics scoped by season"
    examples: ["analytics.seasonal_trends[*].season_id"]
    
  - module: training
    reason: "Carga, aderência, tendências"
    examples: ["analytics.training_load[*].session_id"]
    
  - module: wellness
    reason: "Wellness trends, correlações com carga"
    examples: ["analytics.wellness_correlation[*].wellness_id"]
    
  - module: medical
    reason: "Injury frequency, availability"
    examples: ["analytics.injury_trends[*].injury_id"]
    
  - module: competitions
    reason: "Scoreboards, standings"
    examples: ["analytics.standings[*].competition_id"]
    
  - module: matches
    reason: "Match statistics"
    examples: ["analytics.match_stats[*].match_id"]
    
  - module: scout
    reason: "Scout analysis aggregation"
    examples: ["analytics.scout_trends[*].scout_id"]
    
  - module: exercises
    reason: "Exercise performance metrics"
    examples: ["analytics.exercise_stats[*].exercise_id"]

forbidden_references:
  - module: identity_access
  - module: audit
  - module: notifications
  - module: reports
  - module: ai_ingestion

exceptions: []
```

---

### reports
**Função**: Relatórios gerados, exportações PDF/CSV, insights  
**Owner**: performance-tech

```yaml
allowed_references:
  - module: analytics
    reason: "Reports consomem aggregated analytics"
    examples: ["report.analytics_source"]
    
  - module: users
    reason: "Report recipient/owner"
    examples: ["report.recipient_user_id"]
    
  - module: teams
    reason: "Team context in report"
    examples: ["report.team_id"]
    
  - module: seasons
    reason: "Seasonal report context"
    examples: ["report.season_id"]
    
  - module: training
    reason: "Training summary in report"
    examples: ["report.training_data"]
    
  - module: wellness
    reason: "Wellness data in report"
    examples: ["report.wellness_summary"]
    
  - module: medical
    reason: "Medical status in report"
    examples: ["report.medical_clearance_status"]
    
  - module: ai_ingestion
    reason: "IA insights embedded in report"
    examples: ["report.ai_insights"]

forbidden_references:
  - module: identity_access
  - module: audit
  - module: notifications
  - module: competitions
  - module: matches
  - module: scout
  - module: exercises

exceptions: []
```

---

### ai_ingestion
**Função**: Ingestão de dados, processamento IA, insights, análise  
**Owner**: platform-core

```yaml
allowed_references:
  - module: training
    reason: "IA processes training sessions: video, metrics"
    examples: ["training_session.ai_insights"]
    
  - module: wellness
    reason: "IA correlates wellness with training"
    examples: ["wellness_entry.ai_analysis"]
    
  - module: scout
    reason: "IA analyzes scout video, performance patterns"
    examples: ["scout_entry.ai_processed"]
    
  - module: reports
    reason: "IA generated insights for reports"
    examples: ["report.ai_insights"]
    
  - module: analytics
    reason: "IA enriches analytics with predictions"
    examples: ["analytics.ai_predictions"]

forbidden_references:
  - module: identity_access
  - module: audit
  - module: notifications
  - module: users
  - module: teams
  - module: seasons
  - module: competitions
  - module: matches
  - module: medical
  - module: exercises

exceptions: []
```

---

### video
**Função**: Gestão e distribuição de vídeo esportivo (streaming, upload, mídia de partida e treino)  
**Owner**: platform-core

```yaml
allowed_references:
  - module: identity_access
    reason: "DR-VID-009: toda distribuição é auditada — publishedByUserId rastreia quem disparou a publicação (audit trail, não ownership)"
    examples: ["distribution_profile.publishedByUserId"]
    note: "video não modela identidade; referencia userId como FK de auditoria de distribuição apenas"

forbidden_references:
  - module: users
  - module: seasons
  - module: teams
  - module: training
  - module: wellness
  - module: medical
  - module: competitions
  - module: matches
  - module: scout
  - module: exercises
  - module: analytics
  - module: reports
  - module: ai_ingestion
  - module: audit
  - module: notifications

exceptions: []
```

---

### identity_access (Cross-Cutting)
**Função**: Autenticação, autorização, credenciais, sessão, MFA, JWT, RBAC  
**Owner**: platform-core

```yaml
allowed_references:
  - module: users
    reason: "identity_access validates/bridges user identity for authz purposes only"
    examples: ["/identity/users/{userId}/permissions", "identity.resolve_user_rbac"]
    note: "identity_access reads user identity to enforce permissions; never modifies user profile data"
    
  - module: audit
    reason: "identity_access registers authz decisions for audit trail"
    examples: ["audit_entry.authorization_decision"]

forbidden_references:
  - module: teams
  - module: seasons
  - module: training
  - module: wellness
  - module: medical
  - module: competitions
  - module: matches
  - module: scout
  - module: exercises
  - module: analytics
  - module: reports
  - module: ai_ingestion
  - module: notifications

exceptions: []
note: "identity_access is cross-cutting and should never depend on functional domain logic."
```

---

### audit (Cross-Cutting)
**Função**: Rastreamento de mudanças, compliance, auditoria  
**Owner**: platform-core

```yaml
allowed_references:
  - module: users
    reason: "Audit logs track user-initiated changes"
    examples: ["audit_entry.initiated_by_user_id"]
    
  - module: teams
    reason: "Audit logs track team mutations"
    examples: ["audit_entry.team_id"]
    
  - module: seasons
    reason: "Audit logs track season changes"
    examples: ["audit_entry.season_id"]
    
  - module: training
    reason: "Audit logs track session mutations"
    examples: ["audit_entry.training_session_id"]
    
  - module: wellness
    reason: "Audit logs track wellness changes"
    examples: ["audit_entry.wellness_id"]
    
  - module: medical
    reason: "Audit logs track medical record mutations (compliance critical)"
    examples: ["audit_entry.medical_record_id"]
    
  - module: competitions
    reason: "Audit logs track competition mutations"
    examples: ["audit_entry.competition_id"]
    
  - module: matches
    reason: "Audit logs track match mutations"
    examples: ["audit_entry.match_id"]
    
  - module: scout
    reason: "Audit logs track scout data mutations"
    examples: ["audit_entry.scout_entry_id"]
    
  - module: exercises
    reason: "Audit logs track exercise catalog mutations"
    examples: ["audit_entry.exercise_id"]
    
  - module: identity_access
    reason: "Audit logs track authz decisions"
    examples: ["audit_entry.authorization_event"]

forbidden_references:
  - module: analytics
  - module: reports
  - module: ai_ingestion
  - module: notifications

exceptions: []
note: "audit is observer-only; never initiates business logic or operational changes."
```

---

### notifications (Cross-Cutting)
**Função**: Notificações internas, alertas de sistema  
**Owner**: platform-core

```yaml
allowed_references:
  - module: users
    reason: "Notifications target users"
    examples: ["notification.recipient_user_id"]

forbidden_references:
  - module: teams
  - module: seasons
  - module: training
  - module: wellness
  - module: medical
  - module: competitions
  - module: matches
  - module: scout
  - module: exercises
  - module: analytics
  - module: reports
  - module: ai_ingestion
  - module: identity_access
  - module: audit

exceptions: []
note: "notifications is outbound-only and never participates in domain logic."
```

---

## 3. Transitividades e Context Bridges

Algumas referências não são diretas, mas transitivas. Exemplo:

**Caso**: `training` module document references a entity that includes user data indirectly.

```
training_session
  ├── team_id (reference to teams)
  └── teams.users (transitively includes user data via team roster)
```

**Regra**: 
- Se a transitividade é documentada e intencional → OK
- Se a transitividade é implícita ou resultado de join semântico não explícito → revisar

---

## 4. Como Validar Referências Nesta Policy

### 4.1 Por Contrato (OpenAPI, Schema, Arazzo)

Ao criar ou revisar um contrato:

1. **Identifique o módulo de origem**: Qual módulo está definindo este contrato? (ex: `users`)
2. **Estraia todas as referências**:
   - `$ref` em JSON Schema
   - `operationId` em OpenAPI que cruza módulos
   - `$servers` ou `base_path` que aponta para outro módulo
   - Nomes de eventos in AsyncAPI que implicam acoplamento
3. **Consulte a tabela do módulo A** na seção 2
4. **Procure o módulo B na lista `allowed_references`**:
   - Se sim → PASS ✓
   - Se não → Procure em `exceptions` por uma ADR relevante
   - Se ainda não → BLOCKED_SCOPE_OVERFLOW ✗

### 4.2 Validator Script Behavior

O script `scripts/gates/check_scope_boundary.py` implementa este algoritmo:

```python
artifact = load(contract_path)
module_origin = extract_module_from_path(contract_path)  # ex: users
policy = load_policy()  # esta seção 2

for reference in extract_references(artifact):
    module_target = parse_module_from_reference(reference)
    
    if module_target == module_origin:
        continue  # intra-module OK
    
    if module_target in policy[module_origin]['allowed_references']:
        continue  # explicitly allowed
    
    if module_target in policy[module_origin]['forbidden_references']:
        return (False, "BLOCKED_SCOPE_OVERFLOW")
    
    # Edge case: not explicitly in allowed ou forbidden
    # Favor deny (fail safe)
    return (False, "BLOCKED_SCOPE_OVERFLOW")

return (True, None)
```

---

## 5. Exceções via ADR

### 5.1 Quando Criar uma ADR de Exceção

Se uma referência legítima de negócio não está em `allowed_references`, você pode propor uma exceção via ADR.

**Pré-requisitos**:
1. Você já tentou refatorar para evitar a referência?
2. Há justificativa forte de negócio?
3. A referência é **unidirecional** ou **de leitura apenas**?

**Processo**:
1. Crie uma ADR (ex: ADR-032: "Allow training → competitions reference")
2. Descreva:
   - Por que training precisa referenciar competitions
   - Por que não é possível encapsular esta dependência
   - Que proteções serão implementadas para evitar acoplamento excessivo
3. Atualize `exceptions` desta policy com o link à ADR
4. Execute `hb verify` para validar

### 5.2 Exemplo de Exceção

```yaml
# Na seção exercises (hipotético)
exceptions:
  - adr_id: ADR-032
    reason: "Allow exercises → competitions reference (exercise eligiblity by competition category)"
    link: "docs/_canon/decisions/ADR-032-exercise-competition-eligibility.md"
    status: "accepted"
    validation_rule: "exercises can READ competition.category for filtering; never modify"
```

---

## 6. Rastreabilidade e Evolução

### 6.1 Mudanças Requerem Aprovação

Estrutura de governança para modificações a esta policy:

| Mudança | Gate | Aprovação |
|---------|------|-----------|
| Adicionar `allowed_reference` | SCOPE_BOUNDARY_GATE | Tech lead + module owner |
| Remover `allowed_reference` | SCOPE_BOUNDARY_GATE + breaking change check | Tech lead + product |
| Adicionar exceção via ADR | ADR review + SCOPE_BOUNDARY_GATE | ADR deciders |
| Novo módulo | MODULE_REGISTRY.yaml | Tech lead |

### 6.2 Auditoria

Esta policy é auditada automaticamente:
- Toda nova contract com cross-module reference executa `check_scope_boundary.py` em Fase 1
- Red team audits reavalidam esta policy semestralmente
- Violations (BLOCKED_SCOPE_OVERFLOW) são reportadas em pipeline health dashboard

---

## 7. Referências e Links

- **ADR-034**: "Scope Boundary Validation — Detectar Referências Cross-Module" → Define gate de validação (orchestrator F1.5)
- **MODULE_REGISTRY.yaml**: Status operacional de cada módulo
- **MODULE_SOURCE_AUTHORITY_MATRIX.yaml**: Fonte de autoridade por módulo (IHF, ACSM, etc.)
- **SYSTEM_SCOPE.md**: Escopo geral do sistema, macrodomínios, fora-de-escopo
- **CONTRACT_SYSTEM_RULES.md §2C**: Taxonomia canônica de módulos
- **Relatório Red Team A8**: `_reports/AUDIT_RED_TEAM_PIPELINE_20260317.md`

---

**Status**: ✅ Active (2026-03-18)

**Próxima Revisão**: 2026-06-18 (trimestral)

**Casos de Uso**:
- Validação de novos contratos em pre-contract Fase 1
- Detecção de scope overflow em auditorias
- Documentação de dependências cross-module
- Justificativa de ADRs de exceção
