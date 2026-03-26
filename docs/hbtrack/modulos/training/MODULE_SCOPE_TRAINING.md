---
module: "training"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: true
contract_path_ref: "../../../../contracts/openapi/paths/training.yaml"
schemas_ref: "../../../../contracts/schemas/training/"
type: "module-scope"
---

# MODULE_SCOPE_TRAINING.md

## Objetivo
Definir claramente o que o módulo `training` faz e o que não faz.

## Missão do módulo
O módulo `training` existe para suportar o ciclo completo de planejamento, execução, registro e análise de sessões de treinamento de handebol, respeitando a periodização, categorias, posições e fases do jogo da modalidade.

## Responsabilidades
- Planejamento de sessões de treino com exercícios, objetivos, carga e foco
- Registro de execução de treinos (horário real, duração, presença de atletas)
- Coleta de dados de wellness pré-treino (disposição, sono, dor muscular)
- Coleta de dados de wellness pós-treino (RPE, fadiga, sensação pós-treino)
- Vínculo de sessões a equipes, temporadas e categorias
- Suporte a periodização em 4 níveis: macrociclo (temporada) → mesociclo → microciclo (semana) → sessão
- Classificação de exercícios por posição-alvo (conforme HBR-014) e fase do jogo
- Fornecimento de dados de carga interna/externa para o módulo `analytics`

## Atores
- **Treinador**: planeja e executa sessões, registra detalhes e wellness
- **Coordenador**: aprova planos, revisa sessões executadas, ajusta periodização
- **Atleta**: visualiza próprio histórico de treinos e wellness
- **Dirigente**: acessa relatórios executivos derivados de treinos

## Entidades principais
- `TrainingSession` — sessão de treino planejada ou executada
- `Exercise` — exercício individual dentro de uma sessão
- `WellnessPre` — dados de wellness pré-treino
- `WellnessPost` — dados de wellness pós-treino (RPE, fadiga)
- `Periodization` — estrutura de macrociclo, mesociclo, microciclo

## Entradas
- Requests HTTP definidos em `contracts/openapi/paths/training.yaml`
- Dados de equipes e atletas (upstream: módulo `teams`)
- Dados de temporadas (upstream: módulo `seasons`)
- Dados de exercícios catalogados (upstream: módulo `exercises`)

## Saídas
- Responses HTTP (sessões criadas, atualizadas, listadas)
- Mudanças de estado de sessões (ADR-017 FSM: DRAFT → SCHEDULED/PUBLISHED → IN_PROGRESS → COMPLETED → ARCHIVED; cancelável de qualquer estado pré-terminal)
- Dados de carga e volume consumidos por `analytics`
- Histórico de wellness para análise de sobrecarga

## Dentro do escopo
- Planejamento de sessões de treino
- Registro de execução e presença
- Coleta de wellness (pré e pós)
- Periodização de treinos
- Classificação de exercícios por posição e fase do jogo (conforme HBR-014)
- Histórico de treinos para analytics

## Fora do escopo
- Registro de partidas oficiais ou amistosos (módulo `matches`)
- Scout de eventos de jogo (módulo `scout`)
- Gestão de lesões, consultas e tratamentos médicos (módulo `medical`)
- Cálculo de métricas, KPIs e dashboards (módulo `analytics`)
- Cadastro de exercícios no catálogo global (módulo `exercises`)
- Notificações push/email sobre treinos (módulo `notifications`)

## Dependências
- Módulos upstream: `teams`, `seasons`, `exercises`
- Módulos downstream: `analytics`, `wellness`
- Artefatos globais:
  - `SYSTEM_SCOPE.md`
  - `HANDBALL_RULES_DOMAIN.md` (HBR-014: Treino Orientado à Modalidade)

## Regras de fronteira
1. O módulo não deve assumir responsabilidades de outro módulo sem decisão explícita.
2. O módulo não deve expor comportamento fora do seu contrato.
3. Toda exceção de escopo deve ser registrada formalmente.

---

## Identidade de módulo (TRAIN-DEC-001, TRAIN-DEC-002)

> **Materializado em 2026-03-16 a partir de ARCH_DECISIONS_TRAINING.md (DSS).**

### Unidade soberana

A unidade soberana do módulo **não** é `TrainingSession`. É `training_intervention_cycle`.

A `training_session` é um artefato interno do ciclo de intervenção.

### Backbone operacional

```
Need → Objective → Prescription → Session → Execution → Response → Review → Adjustment
```

Toda sessão **deve** nascer de uma `need_detected`, `goal_gap` ou `competitive_focus`. O sistema pergunta "qual necessidade isso resolve?" antes de "qual é a duração?". Sessão sem objetivo operacional explícito é inválida.

### Orientação a decisão (não a cadastro)

O módulo é orientado à **decisão do treinador**, não ao preenchimento de formulários. Analytics e IA produzem `recommendations` e `signals` — nunca decisões de prescrição. A materialização de `training_session` a partir de recomendação exige ato explícito de treinador autorizado.

## Entidades do domínio (atualizado 2026-03-16)

### Fase 1 — Núcleo obrigatório
- `TrainingSession` — sessão planejada ou executada (FSM: DRAFT→SCHEDULED/PUBLISHED→IN_PROGRESS→COMPLETED→ARCHIVED)
- `SessionBlock` — DSL operacional da sessão; define phase, order, duration, intensity (TRAIN-DEC-049, INV-TRAIN-083)
- `SessionObjective` — objetivo operacional obrigatório; exige `origin` rastreável (TRAIN-DEC-004, TRAIN-DEC-005)
- `ExecutionRecord` — fato de execução append-only; preserva `planned vs actual` imutavelmente (TRAIN-DEC-007, TRAIN-DEC-008)
- `FeedbackThread` — conversa técnica contextual com `conversationOutcome` obrigatório (TRAIN-DEC-010, TRAIN-DEC-015)
- `AttentionQueueItem` — item de atenção finita com `severity`, `reasonCode` e `targetEntity` obrigatórios (TRAIN-DEC-027)
- `WellnessPre` — dados de wellness pré-treino
- `WellnessPost` — dados de wellness pós-treino (RPE, fadiga, carga interna)
- `Periodization` — macrociclo → mesociclo → microciclo → sessão

### Fase 2 (planejado)
- `AdherenceRecord` — aderência de primeira classe: miss_reason, partial_completion, consistency_streak (TRAIN-DEC-019)
- `DropoutRiskSignal` — derivado soberano de `analytics`; training consome read-only (TRAIN-DEC-046)

## Fronteiras de módulo (atualizado 2026-03-16)

| Boundary | Regra | Decisão |
|---|---|---|
| `notifications` | `training` emite `notification_intent`; não entrega diretamente | TRAIN-DEC-022 |
| `audit` | `training` emite `audit_event`; não mantém trilha interna | TRAIN-DEC-023 |
| `medical` | `training` consome `restriction_profile` e `return_to_play_guard` como somente leitura | TRAIN-DEC-024 |
| `identity_access` | `identity_access` é fonte soberana de policy; `training` apenas aplica | TRAIN-DEC-025 |
| `analytics` | `analytics` é soberano de `derived_signal`; `training` consome read-only | TRAIN-DEC-046 |
| `exercises` | `exercises` é módulo soberano; `training` referencia `exercise_id + exercise_version_id` | TRAIN-DEC-047 |

## Fases de implementação (TRAIN-DEC-028)

**Fase 1 — Núcleo operacional:**
- Detectar necessidade → Definir objetivo → Criar sessão → Montar blocos → Publicar
- Confirmar presença → Registrar execução → Feedback contextual → Ajuste de ciclo

**Fase 2 — Precisão e contexto expandido:**
- Vídeo/playbook contextual, variantes por atleta, `attention_queue` completa
- Guards de retorno progressivo avançados, `planned vs actual` avançado

**Fase 3 — IA e analytics integrados:**
- `dropout_risk_signal`, recomendações de periodização, análise de aderência avançada
