---
module: "training"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: true
contract_path_ref: "../../../../contracts/openapi/paths/training.yaml"
schemas_ref: "../../../../contracts/schemas/training/"
type: "arch-decisions"
promoted_from: ".dev/arquitetura/ARCH-DEC-TRAIN.md"
promoted_at: "2026-03-15"
promoted_by: "DSS-TRAINING-003"
---

# ARCH-DEC-TRAIN — Registro de Decisões Arquiteturais: Módulo Training

- Status: Accepted
- Data: 2026-03-15
- Módulo: `training`
- Autor: Arquiteto HB Track
- Fonte: `.dev/arquitetura/Arquitetura Treinos.md`
- Tags: training, architecture, domain-decisions, invariants, boundary

---

## Sumário

| ID | Decisão | Tipo | Status |
|---|---|---|---|
| [TRAIN-DEC-001](#train-dec-001) | `training_session` não é a unidade central | Identidade de módulo | Accepted |
| [TRAIN-DEC-002](#train-dec-002) | Módulo orientado a decisão, não a cadastro | Identidade de módulo | Accepted |
| [TRAIN-DEC-003](#train-dec-003) | Analytics e IA só recomendam; treinador decide | Autoridade de domínio | Accepted |
| [TRAIN-DEC-004](#train-dec-004) | Sessão exige objetivo operacional | Prescrição | Accepted |
| [TRAIN-DEC-005](#train-dec-005) | Objetivo exige origem rastreável | Prescrição | Accepted |
| [TRAIN-DEC-006](#train-dec-006) | Sessão publicada exige conteúdo mínimo | Publicação | Accepted |
| [TRAIN-DEC-007](#train-dec-007) | `execution_record` exige contexto de prescrição | Execução | Accepted |
| [TRAIN-DEC-008](#train-dec-008) | `planned vs actual` é obrigatório | Execução | Accepted |
| [TRAIN-DEC-009](#train-dec-009) | Ajuste ao vivo exige motivo estruturado | Execução | Accepted |
| [TRAIN-DEC-010](#train-dec-010) | Feedback é contextual, nunca solto | Feedback | Accepted |
| [TRAIN-DEC-011](#train-dec-011) | Revisão exige evidência de execução | Revisão | Accepted |
| [TRAIN-DEC-012](#train-dec-012) | Restrição crítica bloqueia ou exige override auditado | Elegibilidade | Accepted |
| [TRAIN-DEC-013](#train-dec-013) | Sessão `COMPLETED` é imutável por edição destrutiva | Imutabilidade | Accepted |
| [TRAIN-DEC-014](#train-dec-014) | Estados derivados não substituem dados-fonte | Integridade | Accepted |
| [TRAIN-DEC-015](#train-dec-015) | Conversa técnica precisa gerar consequência operacional | Interação | Accepted |
| [TRAIN-DEC-016](#train-dec-016) | Dois loops explícitos: coletivo e individual | Estrutura | Accepted |
| [TRAIN-DEC-017](#train-dec-017) | Vídeo e playbook são objetos operacionais, não anexos | Conteúdo | Accepted |
| [TRAIN-DEC-018](#train-dec-018) | Fricção adaptativa é princípio sistêmico | Experiência | Accepted |
| [TRAIN-DEC-019](#train-dec-019) | Aderência é entidade de primeira classe | Domínio | Accepted |
| [TRAIN-DEC-020](#train-dec-020) | Edição viva de sessão deve ser suportada | Execução | Accepted |
| [TRAIN-DEC-021](#train-dec-021) | Continuidade interstaff é responsabilidade do módulo | Memória técnica | Accepted |
| [TRAIN-DEC-022](#train-dec-022) | `training` não entrega notificação diretamente | Boundary | Accepted |
| [TRAIN-DEC-023](#train-dec-023) | Auditoria via módulo `audit`, não interna | Boundary | Accepted |
| [TRAIN-DEC-024](#train-dec-024) | Restrições médicas são somente leitura operacional | Boundary | Accepted |
| [TRAIN-DEC-025](#train-dec-025) | `identity_access` governa permissão; `training` aplica | Boundary | Accepted |
| [TRAIN-DEC-026](#train-dec-026) | Status de sessão tem máquina de estados fechada | Governança | Accepted |
| [TRAIN-DEC-027](#train-dec-027) | Atenção do treinador deve ser finita e priorizada | Alerta | Accepted |
| [TRAIN-DEC-028](#train-dec-028) | Fases de implementação: 1, 2, 3 | Escopo | Accepted |
| [TRAIN-DEC-029](#train-dec-029) | Módulo `training` = HYBRID persistence | Persistência | Accepted |
| [TRAIN-DEC-030](#train-dec-030) | Eventos append-only não eliminam o agregado CRUD | Persistência | Accepted |
| [TRAIN-DEC-031](#train-dec-031) | `session_templates` e `planning_periodization` são CRUD puros | Persistência | Accepted |
| [TRAIN-DEC-032](#train-dec-032) | Separação estrita: Domínio ≠ DTO ≠ ViewModel ≠ Props | Arquitetura de camadas | Accepted |
| [TRAIN-DEC-033](#train-dec-033) | Modelo de domínio não é moldado por UI nem por provedores | Arquitetura de camadas | Accepted |
| [TRAIN-DEC-034](#train-dec-034) | DTO de API não vaza internos de persistência | Arquitetura de camadas | Accepted |
| [TRAIN-DEC-035](#train-dec-035) | ViewModel não oculta distinções canônicas de status | Arquitetura de camadas | Accepted |
| [TRAIN-DEC-036](#train-dec-036) | Dados externos passam pela camada de ingestão | Ingestão | Accepted |
| [TRAIN-DEC-037](#train-dec-037) | `observed_at` e `ingested_at` são distintos | Ingestão | Accepted |
| [TRAIN-DEC-038](#train-dec-038) | Idempotência obrigatória para fatos ingeridos | Ingestão | Accepted |
| [TRAIN-DEC-039](#train-dec-039) | Dados de wellness consumidos por training são domínio sensível | Governança sensível | Accepted |
| [TRAIN-DEC-040](#train-dec-040) | Training não expõe detalhes sensíveis em endpoints genéricos | Governança sensível | Accepted |
| [TRAIN-DEC-041](#train-dec-041) | Inferências de IA sobre estado do atleta são consultivas | Governança sensível | Accepted |
| [TRAIN-DEC-042](#train-dec-042) | `dropout_risk_signal` é derivado — nunca fonte primária | Governança sensível | Accepted |
| [TRAIN-DEC-043](#train-dec-043) | Registros sensíveis sem armazenamento ad hoc em training | Governança sensível | Accepted |
| [TRAIN-DEC-044](#train-dec-044) | Sessão híbrida: escopo coletivo + variantes individuais embedded | Estrutura de domínio | Accepted |
| [TRAIN-DEC-045](#train-dec-045) | `planned vs actual` é dualidade embedded; comparação é query derivada | Execução | Accepted |
| [TRAIN-DEC-046](#train-dec-046) | `analytics` é soberano de `derived_signal`; `training` consome read-only | Boundary | Accepted |

---

## Decisões

---

### TRAIN-DEC-001

**`training_session` não é a unidade central do módulo**

- **Tipo:** Identidade de módulo
- **Status:** Accepted

#### Contexto

Sistemas esportivos imaturos modelam `Training` como CRUD de sessões. O benchmark de mercado (XPS Network, Smartabase, Teamworks AMS) mostra consistentemente que o valor real está no ciclo completo de intervenção, não na sessão isolada.

#### Decisão

A unidade soberana do módulo é `training_intervention_cycle`. A `training_session` é apenas um artefato interno desse ciclo.

O backbone operacional é:

```
Need → Objective → Prescription → Session → Execution → Response → Review → Adjustment
```

#### Rationale

- Nenhum sistema maduro trata `training_session` como entidade central isolada.
- Modelar por ciclo preserva a lógica causal entre necessidade e intervenção.
- Evita que o módulo degrade para agenda de compromissos.

#### Consequências

- **Positivo:** Contrato nasce orientado à decisão do treinador, não ao formulário.
- **Positivo:** Analytics e wellness se encaixam naturalmente como fontes de `need_detected`.
- **Negativo:** Maior custo de modelagem inicial em relação a CRUD simples.

#### Invariantes vinculadas

`INV-TRAIN-001`, `INV-TRAIN-002`, `INV-TRAIN-003`

---

### TRAIN-DEC-002

**Módulo orientado a decisão, não a cadastro**

- **Tipo:** Identidade de módulo
- **Status:** Accepted

#### Contexto

Sistemas abandonados foram-no quando viraram "lugar para preencher coisa". Sistemas com alta retenção (Bridge, XPS, Teamworks) funcionam como sistema operacional diário do treinador.

#### Decisão

Toda sessão deve nascer de uma `need_detected`, `goal_gap` ou `competitive_focus`. O sistema pergunta "qual necessidade isso resolve?" antes de "qual é a duração?".

#### Rationale

- Conecta analytics ao treino sem automatizar o treinador.
- Reduz abandono por burocracia.
- Distingue HB Track de plataformas de agendamento simples.

#### Consequências

- **Positivo:** Cada sessão tem propósito explícito e rastreável.
- **Negativo:** Fluxo de criação de sessão é mais longo que um formulário básico.

#### Invariantes vinculadas

`INV-TRAIN-001`, `INV-TRAIN-002`

---

### TRAIN-DEC-003

**Analytics e IA só recomendam; treinador decide**

- **Tipo:** Autoridade de domínio
- **Status:** Accepted

#### Contexto

Em sistemas maduros existe tensão entre automação e autoridade técnica do treinador. A automação opaca é um dos fatores de abandono e perda de confiança.

#### Decisão

Qualquer saída de `analytics`, `ai_ingestion` ou regras automáticas entra no módulo como `recommendation` ou `signal`. Jamais como decisão final de prescrição.

A materialização de `training_session` a partir de `need_detected` ou `recommendation` exige ato explícito de treinador autorizado.

#### Rationale

- Preserva autoridade técnica do coach — ponto central da proposta de valor.
- Evita prescrições automáticas que não consideram contexto humano do treinador.
- Alinhado com padrão de mercado: Teamworks, Smartabase e Bridge nunca automatizam a decisão de treino.

#### Consequências

- **Positivo:** Treinador mantém controle total sobre prescrições.
- **Positivo:** Recomendações ficam visíveis e auditáveis como objetos do domínio.
- **Negativo:** Não há automação total de prescrição, mesmo quando analytics é claro.

#### Boundary

- `analytics` → produz `recommendation` → `training` consome como input
- `ai_ingestion` → produz `signal` → `training` consome como input
- `training` → autoridade soberana sobre `session`, `prescription`, `execution`

#### Invariantes vinculadas

`INV-TRAIN-003`, `INV-TRAIN-004`, `INV-TRAIN-015`

---

### TRAIN-DEC-004

**Toda sessão exige objetivo operacional**

- **Tipo:** Prescrição
- **Status:** Accepted

#### Decisão

Toda `training_session` deve possuir pelo menos um `session_objective` válido e explícito. Sessão "vazia" ou "apenas calendário" é inválida.

#### Rationale

- Sem objetivo, a sessão não tem propósito operacional verificável.
- Impede que o módulo vire agendamento passivo.

#### Invariantes vinculadas

`INV-TRAIN-001`

---

### TRAIN-DEC-005

**Todo objetivo exige origem rastreável**

- **Tipo:** Prescrição
- **Status:** Accepted

#### Decisão

Todo `session_objective` deve referenciar uma das seguintes origens:
- `need_detected`
- `competitive_focus`
- `development_goal`
- `manual_coach_rationale`

Objetivo sem origem é tratado como dado incompleto.

#### Rationale

- Garante que qualquer decisão de plano pode ser explicada e auditada.
- Conecta objetivos ao ciclo causal do domínio.

#### Invariantes vinculadas

`INV-TRAIN-002`

---

### TRAIN-DEC-006

**Sessão publicada exige conteúdo mínimo treinável**

- **Tipo:** Publicação
- **Status:** Accepted

#### Decisão

Uma sessão só pode transitar para `PUBLISHED` ou `SCHEDULED` se possuir:
- `team_scope` e/ou `athlete_scope`
- pelo menos um `session_objective`
- horário/data
- pelo menos um bloco ou prescrição mínima
- responsável técnico (`coach_assignment`)

Sem esses campos, o status máximo permitido é `DRAFT`.

#### Invariantes vinculadas

`INV-TRAIN-005`, `INV-TRAIN-018`

---

### TRAIN-DEC-007

**`execution_record` exige contexto de prescrição**

- **Tipo:** Execução
- **Status:** Accepted

#### Decisão

`execution_record` não pode existir como objeto solto. Deve apontar para:
- `training_session`, e/ou
- `session_block`, e/ou
- `prescription_line`

Se for improviso documentado, deve carregar `coach_rationale` de ajuste ao vivo.

#### Invariantes vinculadas

`INV-TRAIN-006`

---

### TRAIN-DEC-008

**`planned vs actual` é obrigatório**

- **Tipo:** Execução
- **Status:** Accepted

#### Contexto

Bridge, TeamBuildr e outros sistemas maduros diferenciam explicitamente o que foi prescrito do que foi realizado. Sobrescrever o planejado com o realizado destrói o histórico decisório.

#### Decisão

Toda sessão concluída deve preservar separadamente e de forma imutável:
1. O que foi **planejado**
2. O que foi **executado**
3. O que foi **alterado**
4. **Por que** foi alterado

O campo `planned` nunca é sobrescrito pelo `actual`.

#### Consequências

- **Positivo:** Histórico de decisões preservado para análise retrospectiva.
- **Positivo:** Suporta análise de aderência ao plano.
- **Negativo:** Requer estrutura de dados que suporte dualidade planejado/realizado.

#### Invariantes vinculadas

`INV-TRAIN-007`

---

### TRAIN-DEC-009

**Ajuste ao vivo exige motivo estruturado**

- **Tipo:** Execução
- **Status:** Accepted

#### Decisão

Toda `live_session_adjustment`, `constraint_override`, `alternate_exercise` ou `load_recalculation` deve registrar motivo em campo estruturado (não texto livre irrestrito).

#### Rationale

- Sem motivo, ajustes ao vivo são ruído sem valor retrospectivo.
- Suporta continuidade interstaff e avaliação posterior.

#### Invariantes vinculadas

`INV-TRAIN-008`

---

### TRAIN-DEC-010

**Feedback é contextual, nunca solto**

- **Tipo:** Feedback
- **Status:** Accepted

#### Decisão

Todo `feedback_thread` ou feedback técnico deve referenciar pelo menos um dos seguintes:
- sessão
- bloco
- objetivo
- evidência
- atleta/grupo específico

Feedback sem contexto vinculado não tem valor operacional e não deve ser aceito pelo módulo.

#### Invariantes vinculadas

`INV-TRAIN-010`

---

### TRAIN-DEC-011

**Revisão exige evidência de execução**

- **Tipo:** Revisão
- **Status:** Accepted

#### Decisão

Não pode haver `review_outcome` sem pelo menos um dos seguintes:
- `execution_record`
- `post_session_report`
- evento equivalente de evidência

Revisão sem evidência é inválida.

Da mesma forma, ajuste futuro de plano deve derivar de:
- revisão documentada, ou
- decisão manual justificada do coach

#### Invariantes vinculadas

`INV-TRAIN-011`, `INV-TRAIN-012`

---

### TRAIN-DEC-012

**Restrição crítica bloqueia ou exige override auditado**

- **Tipo:** Elegibilidade
- **Status:** Accepted

#### Contexto

Em sistemas de alta performance (Catapult, Teamworks AMS), restrições médicas e de return-to-play são fronteiras hard que protegem o atleta.

#### Decisão

Atleta com bloqueio por:
- restrição médica ativa
- indisponibilidade severa
- guarda de retorno progressivo (`return_to_play_guard`)

não pode receber prescrição executável sem `override` explícito, autorizado e auditado.

#### Consequências

- **Positivo:** Protege atleta de prescrições inadequadas.
- **Positivo:** Cria trilha de auditoria para decisões de risco.
- **Negativo:** Requer mecanismo de override com permissão específica.

#### Boundary

`training` consome restrição de `medical` (somente leitura). Override é registrado via `audit`.

#### Invariantes vinculadas

`INV-TRAIN-021`, `INV-TRAIN-014`

---

### TRAIN-DEC-013

**Sessão `COMPLETED` é imutável por edição destrutiva**

- **Tipo:** Imutabilidade
- **Status:** Accepted

#### Decisão

Após transição para `COMPLETED`, o conteúdo histórico da sessão é imutável por edição direta. Alterações no registro histórico devem ocorrer apenas por:
- correção auditada (versionada)
- não por edição destrutiva

Sessões em `IN_PROGRESS` não podem ser excluídas fisicamente — apenas cancelamento lógico com trilha é permitido.

#### Invariantes vinculadas

`INV-TRAIN-019`, `INV-TRAIN-020`

---

### TRAIN-DEC-014

**Estados derivados não substituem dados-fonte**

- **Tipo:** Integridade
- **Status:** Accepted

#### Decisão

Campos como `readiness_score`, `dropout_risk_signal` e `engagement_signal` são **derivados**. Eles nunca substituem as respostas brutas ou fatos originais que os originaram.

A fonte primária de verdade é sempre o dado coletado; o derivado é uma projeção calculada.

#### Invariantes vinculadas

`INV-TRAIN-036`

---

### TRAIN-DEC-015

**Conversa técnica precisa gerar consequência operacional**

- **Tipo:** Interação
- **Status:** Accepted

#### Contexto

O módulo não é um chatbot genérico. Feedback conversacional só tem valor operacional quando vinculado a treino, objetivo ou atleta, e quando produz resultado concreto.

#### Decisão

Toda conversa técnica relevante deve produzir pelo menos um dos seguintes:
- `reflexão` documentada
- `compromisso` do atleta
- `pendência` de follow-up
- `follow_up_check` agendado
- `decisão` registrada

Conversa sem consequência operacional não pertence ao núcleo do módulo.

#### Entidades

`feedback_thread`, `coach_prompt`, `athlete_reflection`, `action_commitment`, `followup_check`, `conversation_outcome`

#### Invariantes vinculadas

`INV-TRAIN-028`

---

### TRAIN-DEC-016

**Dois loops explícitos: coletivo e individual**

- **Tipo:** Estrutura de domínio
- **Status:** Accepted

#### Contexto

Teamworks e Smartabase mostram claramente IDPs (Individual Development Plans); XPS e Sportlyzer mostram o lado coletivo de calendário, RSVPs e organização. Sistemas que não formalizam os dois loops deixam o comportamento ambíguo.

#### Decisão

O módulo opera dois ciclos explícitos e separados:

1. **Loop coletivo:** `team_training_cycle` — calendário, presença, disponibilidade, plano semanal, comunicação de equipe.
2. **Loop individual:** `individual_development_cycle` — carga, readiness, progressão, restrição, metas de desenvolvimento, evidência de resposta individual.

#### Consequências

- **Positivo:** Clareza sobre qual entidade é afetada em cada operação.
- **Positivo:** Permite que sessão híbrida seja modelada explicitamente.
- **Negativo:** Aumenta complexidade relacional do modelo de dados.

#### Invariantes vinculadas

`INV-TRAIN-035`

---

### TRAIN-DEC-017

**Vídeo e playbook são objetos operacionais, não anexos**

- **Tipo:** Conteúdo
- **Status:** Accepted

#### Contexto

XPS posiciona playbook, diagramas e animações como parte do fluxo técnico, não como biblioteca passiva. TeamBuildr mostra vídeo coaching integrado ao fluxo de treino.

#### Decisão

`video_clip`, `diagram`, `playbook_pattern` e `coaching_cue` são vinculáveis a:
- `session_objective`
- `session_block`
- `exercise_variant`
- `error_pattern`
- `feedback_thread`

Mídia solta (não vinculada a prescrição, bloco, objetivo ou evento de avaliação) não resolve o problema central do módulo.

#### Consequências

- **Positivo:** Vídeo e playbook ganham contexto operacional e são rastreáveis.
- **Negativo:** Requer modelo de dados que suporte vinculação polimórfica de mídia.

---

### TRAIN-DEC-018

**Fricção adaptativa é princípio sistêmico**

- **Tipo:** Experiência
- **Status:** Accepted

#### Contexto

Teamworks Forms mostra lógica condicional para reduzir campos e melhorar completion. Tratar todo dia como auditoria completa é causa de abandono.

#### Decisão

O fluxo de check-in e interações do atleta devem ser adaptativos:
- Estado normal → fluxo mínimo
- Risco / restrição / dor / anomalia detectada → sistema expande perguntas e validações

Toda interação pedida ao atleta deve ter propósito downstream claro. Questionário ou check-in sem uso explícito não é permitido.

#### Invariantes vinculadas

`INV-TRAIN-025`, `INV-TRAIN-026`

---

### TRAIN-DEC-019

**Aderência é entidade de primeira classe**

- **Tipo:** Domínio
- **Status:** Accepted

#### Contexto

TeamBuildr flerta com streaks e engagement; Sportlyzer mostra attendance e histórico. HB Track deve conectar aderência a intervenção real antes que o atleta "desapareça".

#### Decisão

Aderência não é apenas `attendance`. O domínio inclui:
- `adherence_status`
- `miss_reason`
- `partial_completion`
- `reschedule_window`
- `consistency_streak`
- `engagement_signal`
- `dropout_risk_signal`

Esses objetos devem ser modelados como entidades do domínio, não como campos avulsos.

---

### TRAIN-DEC-020

**Edição viva de sessão deve ser suportada**

- **Tipo:** Execução
- **Status:** Accepted

#### Contexto

Bridge é explícito em suportar edição por readiness, dor, lotação, material, viagem ou clima. Sistemas que não suportam ajuste ao vivo são abandonados no primeiro choque com a realidade operacional.

#### Decisão

O módulo deve suportar explicitamente:
- `live_session_adjustment`
- `alternate_exercise`
- `constraint_override`
- `load_recalculation`
- `coach_rationale` (motivo do ajuste)

Todos esses objetos devem gerar trilha auditável.

#### Invariantes vinculadas

`INV-TRAIN-008`, `INV-TRAIN-009`

---

### TRAIN-DEC-021

**Continuidade interstaff é responsabilidade do módulo**

- **Tipo:** Memória técnica
- **Status:** Accepted

#### Contexto

Case público da University of Oregon (Smartabase) demonstra problema real de turnover de staff. HB Track pode ter vantagem competitiva se o raciocínio técnico ficar rastreável, não só os números.

#### Decisão

O módulo deve suportar:
- `decision_rationale` — justificativa técnica preservada
- `coach_annotation` — observações qualitativas do treinador
- `staff_handoff` — pacote de contexto para transição de staff
- `continuity_snapshot` — estado operacional em um ponto no tempo
- `observation_log` — registro cronológico de observações

Esses elementos não são descartáveis. Devem sobreviver à troca de staff.

#### Invariantes vinculadas

`INV-TRAIN-030`

---

### TRAIN-DEC-022

**`training` não entrega notificação diretamente**

- **Tipo:** Boundary
- **Status:** Accepted

#### Decisão

O módulo `training` emite **intents de notificação** para o módulo `notifications`. Não entrega notificações diretamente ao atleta ou treinador.

#### Boundary

```
training → emit notification_intent → notifications → entrega ao destinatário
```

#### Invariantes vinculadas

`INV-TRAIN-039`

---

### TRAIN-DEC-023

**Auditoria via módulo `audit`, não interna**

- **Tipo:** Boundary
- **Status:** Accepted

#### Decisão

`training` registra fatos auditáveis enviando eventos ao módulo `audit`. Não mantém trilha de auditoria informal interna.

#### Boundary

```
training → emit audit_event → audit → auditoria soberana
```

#### Invariantes vinculadas

`INV-TRAIN-040`

---

### TRAIN-DEC-024

**Restrições e dados médicos são somente leitura operacional**

- **Tipo:** Boundary
- **Status:** Accepted

#### Decisão

`training` pode consumir `restriction_profile`, `return_to_play_guard` e status de aptidão do módulo `medical`. Não pode criar, editar ou soberanizar verdade clínica.

#### Boundary

```
medical → fonte soberana de restrição → training consome como read-only
```

#### Invariantes vinculadas

`INV-TRAIN-014`, `INV-TRAIN-037`

---

### TRAIN-DEC-025

**`identity_access` governa permissão; `training` apenas aplica**

- **Tipo:** Boundary
- **Status:** Accepted

#### Decisão

O módulo `identity_access` é a fonte soberana de autorização. `training` consome a policy decidida e a aplica em suas operações. Não redefine permissões.

#### Boundary

```
identity_access → source de policy → training aplica policy em guards e transições
```

#### Invariantes vinculadas

`INV-TRAIN-041`, `INV-TRAIN-022`

---

### TRAIN-DEC-026

**Status de sessão tem máquina de estados fechada**

- **Tipo:** Governança
- **Status:** Accepted

#### Decisão

O status de `training_session` segue transições explícitas e fechadas:

```
DRAFT → SCHEDULED/PUBLISHED → IN_PROGRESS → COMPLETED
              ↓                     ↓
          CANCELLED             CANCELLED
                                    ↓
                                 ARCHIVED
```

Transições arbitrárias são proibidas. Exemplos:
- `DRAFT → COMPLETED` → **inválido**
- `COMPLETED → IN_PROGRESS` → **inválido**

Se uma sessão publicada perder campos mínimos, o sistema deve bloquear a alteração ou rebaixar para `DRAFT`.

#### Invariantes vinculadas

`INV-TRAIN-017`, `INV-TRAIN-018`, `INV-TRAIN-019`

---

### TRAIN-DEC-027

**Atenção do treinador deve ser finita e priorizada**

- **Tipo:** Alerta / UX
- **Status:** Accepted

#### Decisão

O módulo não pode gerar filas, alertas ou notificações sem:
- `severity` explícita
- `reason` estruturado
- `target_entity` identificado

Tudo que entra em `attention_queue` precisa ter racional explícito. Alertas sem essas propriedades são recusados.

#### Invariantes vinculadas

`INV-TRAIN-027`

---

### TRAIN-DEC-028

**Fases de implementação: 1, 2 e 3**

- **Tipo:** Escopo de entrega
- **Status:** Accepted

#### Decisão

O escopo de implementação é dividido em três fases para evitar supermodelagem:

**Fase 1 — Núcleo operacional obrigatório:**
- Detectar necessidade
- Definir objetivo
- Criar sessão
- Montar blocos
- Publicar sessão
- Confirmar presença
- Orquestração de contexto com `wellness`
- Registrar execução
- Feedback contextual
- Ajuste de ciclo

**Fase 2 — Precisão e contexto expandido:**
- Vídeo/playbook contextual
- Variantes por atleta
- `attention_queue` completa
- Guards de retorno progressivo avançados
- `planned vs actual` avançado

**Fase 3 — Inteligência e continuidade:**
- Feedback conversacional estruturado
- Risco de abandono
- Recomendações automáticas assistidas
- Continuidade interstaff avançada

#### Rationale

Se todas as capacidades forem contratadas simultaneamente, o agente vai supermodelar antes de o núcleo estar funcional.

---

## Mapa de Boundaries Formais

| Módulo externo | Direção | O que `training` consome | O que `training` emite | Soberania |
|---|---|---|---|---|
| `wellness` | Consome | `readiness_snapshot`, `wellness_check` | — | `wellness` é soberano; `training` consome read-only |
| `medical` | Consome | `restriction_profile`, `return_to_play_guard` | — | `medical` é soberano; `training` consome read-only |
| `analytics` | Consome | `signal`, `need_detected`, `recommendation` | — | `analytics` sugere; `training` decide |
| `scout` | Consome | `signal`, `competitive_focus` | — | `scout` sugere; `training` decide |
| `notifications` | Emite | — | `notification_intent` | `notifications` entrega |
| `audit` | Emite | — | `audit_event` | `audit` é repositório soberano |
| `identity_access` | Consome | `permission_policy` | — | `identity_access` governa; `training` aplica |
| `exercises` | Consome | `exercise`, `exercise_library`, `drill` | — | `exercises` fornece conteúdo; `training` governa uso contextual |
| `matches` | Consome | `competitive_context`, `match_result` | — | `matches` é soberano |
| `reports` | Emite | — | `reportable_facts` | `reports` agrega |

---

## Invariantes por Camada

Classificação das 41 invariantes segundo o tipo de enforcement:

### Negócio (regra semântica do domínio)
`INV-TRAIN-001`, `INV-TRAIN-002`, `INV-TRAIN-003`, `INV-TRAIN-004`, `INV-TRAIN-006`, `INV-TRAIN-007`, `INV-TRAIN-010`, `INV-TRAIN-011`, `INV-TRAIN-012`, `INV-TRAIN-025`, `INV-TRAIN-026`, `INV-TRAIN-027`, `INV-TRAIN-028`

### Contrato de API (campos/estados/transições obrigatórias)
`INV-TRAIN-005`, `INV-TRAIN-017`, `INV-TRAIN-018`, `INV-TRAIN-032`, `INV-TRAIN-033`, `INV-TRAIN-034`, `INV-TRAIN-035`

### Persistência (uniqueness, FK, status, soft delete, versioning)
`INV-TRAIN-019`, `INV-TRAIN-020`, `INV-TRAIN-023`, `INV-TRAIN-032`, `INV-TRAIN-036`

### Aplicação (guards, autorização contextual, transições)
`INV-TRAIN-008`, `INV-TRAIN-009`, `INV-TRAIN-013`, `INV-TRAIN-014`, `INV-TRAIN-015`, `INV-TRAIN-016`, `INV-TRAIN-021`, `INV-TRAIN-022`, `INV-TRAIN-024`

### Boundary (acoplamentos entre módulos)
`INV-TRAIN-037`, `INV-TRAIN-038`, `INV-TRAIN-039`, `INV-TRAIN-040`, `INV-TRAIN-041`

### Auditoria / Gate (verificações automatizadas de conformidade)
`INV-TRAIN-029`, `INV-TRAIN-030`, `INV-TRAIN-031`

---

## Decisões Abertas

| # | Questão | Impacto | Superfície afetada | Bloqueia? |
|---|---|---|---|---|
| OPEN-001 | Sessão híbrida (coletiva + individual simultânea): modelo explícito ainda não formalizado | Alto | `training_session`, schema, OpenAPI | **Resolved** — ver TRAIN-DEC-044 |
| OPEN-002 | Granularidade de `planned vs actual` na Fase 1: campo resumido ou estrutura dualista completa? | Médio | Schema, contrato API | **Resolved** — ver TRAIN-DEC-045 |
| OPEN-003 | `dropout_risk_signal`: calculado internamente ou consumido de `analytics`? | Médio | Boundary, schema | **Resolved** — ver TRAIN-DEC-046 |
| OPEN-004 | `staff_handoff`: entidade própria ou campo de `continuity_snapshot`? | Baixo | Schema | Não |
| OPEN-005 | Política de tolerância para duração de blocos vs duração total da sessão | Médio | `INV-TRAIN-034`, schema | Sim |

---

## Decisão Arquitetural Mãe

> **O módulo `training` não é uma agenda de sessões. É um motor de decisão operacional do treinador que transforma contexto competitivo e dados do elenco em intervenção treinável, coordenada e executável.**
>
> A unidade de valor é o ciclo completo:
> `Need → Objective → Prescription → Session → Execution → Response → Review → Adjustment`
>
> Toda decisão de contrato, schema, boundary e implementação deve ser avaliada contra essa definição. Se uma decisão reduz o módulo a CRUD de sessão, ela está errada.

---

---

## Decisões de Persistência

---

### TRAIN-DEC-029

**Módulo `training` adota arquitetura HYBRID de persistência**

- **Tipo:** Persistência
- **Status:** Accepted
- **Fonte:** `HB_TRACK_ARCHITECTURE_DECISION.md` + `HB_TRACK_PERSISTENCE_POLICY.md`

#### Contexto

O módulo precisa gerenciar estado operacional de sessões (ciclo de vida DRAFT → SCHEDULED → COMPLETED) e ao mesmo tempo preservar fatos históricos de execução que não devem ser sobrescritos.

#### Decisão

`training` é classificado como **HYBRID**:

- **Parte CRUD:** agregado de `training_session` e estrutura de agenda (estado operacional atual)
- **Parte append-only:** fatos de sessão com valor histórico

#### Fatos de treino que DEVEM ser append-only

| Fato | Descrição |
|---|---|
| `presence_registered` | Marcação de presença de atleta |
| `session_started` | Início efetivo da sessão |
| `session_finished` | Conclusão da sessão |
| `drill_completed` | Conclusão de exercício por atleta |
| `load_recorded` | Registro de carga realizada |
| `coach_observation_added` | Observação qualitativa do treinador |

#### Rationale

- Sessões têm estado operacional com transitions (DRAFT, SCHEDULED, IN_PROGRESS, COMPLETED) — adequado para CRUD.
- Ocorrências de presença, execução e observação são fatos históricos — adequados para append-only.
- HYBRID é o padrão de mercado: Teamworks AMS, Bridge, XPS mantêm distinção clara entre planejamento (mutável) e fatos realizados (imutável).

#### Consequências

- **Positivo:** Histórico de fatos preservado e auditável.
- **Positivo:** Estado operacional simples de consultar e atualizar.
- **Negativo:** Fluxo híbrido mais complexo do que CRUD puro; exige consumidor claro para cada fluxo de eventos.

#### Pré-condição para o fluxo append-only

O fluxo de eventos append-only só é válido se satisfizer todos os critérios canônicos:
1. Valor de negócio do histórico é explícito.
2. Escrita é naturalmente factual (evento ocorrido em tempo T).
3. Pelo menos um caso de replay/projeção é real, não especulativo.
4. Idempotência está definida.
5. Versionamento de eventos está definido.
6. Política de reprocessamento está definida.
7. Observabilidade para falhas de projeção existe.
8. Retenção e custo são aceitáveis.
9. Equipe consegue depurar o fluxo com segurança.
10. CRUD com tabela de auditoria não resolve o mesmo problema de forma mais simples.

---

### TRAIN-DEC-030

**Evento append-only não elimina o agregado CRUD**

- **Tipo:** Persistência
- **Status:** Accepted
- **Fonte:** `HB_TRACK_PERSISTENCE_POLICY.md`

#### Decisão

O agregado `training_session` e a estrutura de agenda planejada (ciclo de vida, blocos, objetivos, responsáveis) **permanecem CRUD**.

Eventos de sessão com valor histórico são **adicionais** ao CRUD — não o substituem.

#### Proibido

- Modelar o estado operacional de sessão via event sourcing apenas por entusiasmo.
- Usar event-first quando CRUD com tabela de auditoria resolve o problema de forma mais simples.

---

### TRAIN-DEC-031

**`session_templates` e `planning_periodization` são CRUD puros**

- **Tipo:** Persistência
- **Status:** Accepted
- **Fonte:** `HB_TRACK_PERSISTENCE_POLICY.md`

#### Decisão

Templates de sessão e estruturas de periodização são artefatos de configuração em tempo de design. Não geram fatos históricos relevantes para replay. São classificados como **CRUD**.

---

## Decisões de Separação de Camadas

---

### TRAIN-DEC-032

**Separação estrita entre Domínio, DTO de API, ViewModel e Props de UI**

- **Tipo:** Arquitetura de camadas
- **Status:** Accepted
- **Fonte:** `DTO_VIEWMODEL_BOUNDARY_RULES.md`

#### Contexto

Sem separação explícita de camadas, o frontend se acopla a internos do backend, DTOs ficam inflados para satisfazer telas e o modelo de domínio fica moldado por necessidades de renderização.

#### Decisão

O HB Track mantém separação estrita e não intercambiável entre:

| Camada | Responsabilidade | Proibido |
|---|---|---|
| **Modelo de Domínio** | Invariantes, ciclo de vida, regras de negócio | Adaptar-se a conveniências de renderização ou payload de provedores |
| **DTO de API** | Contrato de transporte versionável entre backend e frontend | Expor entidade de BD, artefato de UI ou payload bruto de provedor |
| **ViewModel** | Composição e formatação específica de tela | Tornar-se contrato canônico de backend ou fonte de verdade |
| **Props de Componente UI** | Limite mínimo de renderização do componente | Carregar bagagem de transporte/domínio não relacionada |

#### Fluxo canônico obrigatório

```
Provedor/Entrada
→ Contrato de Ingestão
→ Lógica de Domínio
→ DTO de API
→ ViewModel
→ Props de Componente de UI
→ UI Renderizada
```

Simplificação só é permitida quando a camada ignorada realmente não existe como preocupação separada — e deve ser justificada explicitamente.

#### Consequências

- **Positivo:** Refatorações de domínio não quebram contratos de API.
- **Positivo:** Telas evoluem sem alterar contratos de backend.
- **Negativo:** Custo inicial de modelagem mais alto.

---

### TRAIN-DEC-033

**Modelo de domínio de `training` não é moldado por UI nem por provedores**

- **Tipo:** Arquitetura de camadas
- **Status:** Accepted
- **Fonte:** `DTO_VIEWMODEL_BOUNDARY_RULES.md`

#### Decisão

O modelo de domínio do módulo `training` (agregados `TrainingSession`, `SessionBlock`, `ExecutionRecord`, etc.) não deve ser:
- moldado por necessidades de renderização de tela
- moldado por particularidades de payload de provedores externos

Ele pode ser mais rico do que contratos de API e conter invariantes internas não expostas ao cliente.

---

### TRAIN-DEC-034

**DTO de API de `training` não vaza internos de persistência**

- **Tipo:** Arquitetura de camadas
- **Status:** Accepted
- **Fonte:** `DTO_VIEWMODEL_BOUNDARY_RULES.md`

#### Decisão

DTOs de API do módulo `training` (ex.: `TrainingSessionResponseDto`, `SessionBlockDto`) não devem expor:
- estrutura de tabelas de junção internas
- nomenclatura de chave estrangeira interna
- colunas de soft-delete
- formato bruto de armazenamento do event store

DTOs devem carregar **valores semânticos**, não strings de apresentação:
- Correto: `scheduled_start_at: datetime`, `planned_duration_min: integer`
- Errado: `start_label: "Amanhã às 08:00"`, `duration_label: "1h 30min"`

Strings de apresentação pertencem ao ViewModel ou à camada de formatação.

---

### TRAIN-DEC-035

**ViewModel de `training` não oculta distinções canônicas de status**

- **Tipo:** Arquitetura de camadas
- **Status:** Accepted
- **Fonte:** `DTO_VIEWMODEL_BOUNDARY_RULES.md`

#### Decisão

ViewModels de telas de treino não devem colapsar distinções de status do domínio em um único campo genérico de exibição quando a UI ainda precisa dessas distinções.

As distinções canônicas (`DRAFT`, `SCHEDULED`, `PUBLISHED`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED`, `ARCHIVED`) devem ser preservadas upstream e derivadas conscientemente para badges ou labels de exibição — nunca substituídas por `"active"` genérico.

---

## Decisões de Ingestão

---

### TRAIN-DEC-036

**Dados externos para `training` passam obrigatoriamente pela camada de ingestão**

- **Tipo:** Ingestão
- **Status:** Accepted
- **Fonte:** `INGESTION_PROVIDER_CONTRACT.md`

#### Contexto

O módulo `training` pode receber dados de fontes externas: importações CSV de presença, feeds de competição, entradas manuais de treinadores via ferramentas externas, integrações com dispositivos de carga.

#### Decisão

Todo dado que entra no módulo `training` a partir de qualquer fonte que **não seja o modelo de domínio canônico do HB Track** deve passar pela camada canônica de ingestão.

Nenhum módulo downstream (incluindo `training`) pode depender diretamente de nomes de campos nativos de provedores ou estruturas de payload externo.

#### Campos obrigatórios em todo registro ingerido que afete `training`

- `source_type` (enum canônico)
- `source_system`
- `source_record_id`
- `ingested_at`
- `observed_at`
- `confidence_level` (quando extração é probabilística)
- `normalization_version`
- `sensitivity_class` + `access_classification`

#### Valores canônicos de `source_type` relevantes para `training`

- `manual_coach_entry`
- `manual_staff_entry`
- `manual_athlete_entry`
- `spreadsheet_import`
- `csv_import`
- `sensor_device`
- `partner_webhook`

---

### TRAIN-DEC-037

**Tempo observado e tempo de ingestão são distintos**

- **Tipo:** Ingestão
- **Status:** Accepted
- **Fonte:** `INGESTION_PROVIDER_CONTRACT.md`

#### Decisão

Em registros ingeridos que afetam `training`, `observed_at` (quando o fato ocorreu) e `ingested_at` (quando o HB Track recebeu) não devem ser inferidos como o mesmo valor a menos que as regras de mapeamento explicitamente assim estabeleçam.

Exemplo relevante para `training`: um registro de presença importado via CSV de uma sessão que ocorreu ontem deve ter `observed_at` = horário da sessão, `ingested_at` = horário da importação.

---

### TRAIN-DEC-038

**Idempotência é obrigatória para fatos ingeridos de `training`**

- **Tipo:** Ingestão
- **Status:** Accepted
- **Fonte:** `INGESTION_PROVIDER_CONTRACT.md`

#### Decisão

Chegadas duplicadas do mesmo fato externo para `training` (ex.: registro de presença duplicado numa importação reprocessada) devem ser detectáveis ou governáveis via `dedupe_key` ou `idempotency_key`.

---

## Decisões de Governança de Dados Sensíveis

---

### TRAIN-DEC-039

**Sinais de wellness e readiness consumidos por `training` são domínio sensível**

- **Tipo:** Governança de dados sensíveis
- **Status:** Accepted
- **Fonte:** `SENSITIVE_DOMAIN_GOVERNANCE.md`

#### Contexto

O módulo `training` consome dados de `wellness` (readiness_snapshot, estado emocional, fadiga, qualidade de sono) para decisões de prescrição adaptativa. Esses dados são individualmente identificáveis e de alto risco de uso indevido.

#### Decisão

Dados de `wellness` e sinais de prontidão consumidos por `training` são classificados como **domínio sensível** e sujeitos à política `SENSITIVE_DOMAIN_GOVERNANCE`.

Não devem ser:
- tratados como telemetria esportiva ordinária
- mesclados em dashboards genéricos de performance
- expostos em DTOs genéricos como `TrainingSessionDto`

#### Classes sensíveis canônicas aplicáveis

- `sensitive_health_adjacent` — readiness física, fadiga, indicadores de carga
- `sensitive_psychological` — estado emocional, motivação, estresse relatado

#### Acesso

Acesso a esses dados dentro do contexto de `training` requer:
- `need-to-know` operacional explícito
- escopo contextual (equipe/atleta atribuído ao role)
- `access_classification`: mínimo `restricted_coaching`

---

### TRAIN-DEC-040

**`training` não pode expor detalhes sensíveis de wellness em endpoints genéricos**

- **Tipo:** Governança de dados sensíveis
- **Status:** Accepted
- **Fonte:** `SENSITIVE_DOMAIN_GOVERNANCE.md`

#### Decisão

Endpoints genéricos do módulo `training` (ex.: listagem de sessões, dashboard de equipe) **não devem** incluir campos sensíveis de wellness por conveniência.

Resumos sensíveis (ex.: `readiness_flag: LOW`) só podem aparecer em endpoints explicitamente projetados para aquele nível de exposição, com política de acesso documentada.

---

### TRAIN-DEC-041

**Inferências derivadas de IA sobre estado do atleta são consultivas até revisão humana**

- **Tipo:** Governança de dados sensíveis
- **Status:** Accepted
- **Fonte:** `SENSITIVE_DOMAIN_GOVERNANCE.md`

#### Contexto

O módulo `training` pode consumir sinais derivados de IA sobre estado do atleta (fadiga estimada, risco de burnout, prontidão projetada). Esses sinais são inferências probabilísticas, não verdades autoritativas.

#### Decisão

Toda inferência derivada de IA que afete `training` tem autoridade **apenas consultiva** até revisão humana explícita. O sistema deve:
1. Marcá-la com `review_status: pending_human_review` por padrão.
2. Não operacionalizá-la em prescrições sem decisão explícita do coach.
3. Preservar `model_name`, `model_version`, `confidence_level` e `confidence_label` na proveniência.

#### Hierarquia de autoridade para dados sobre o atleta

| Tipo | Autoridade |
|---|---|
| Fato observado (check-in respondido, presença confirmada) | Factual — não autoriza conclusão interpretiva por si só |
| Interpretação autorada por humano (nota do coach, observação do staff) | Interpretativa e atribuível |
| Inferência candidata por IA | Apenas consultiva — nunca autoritativa por padrão |
| Conclusão operacional revisada | Autoritativa conforme política de workflow e papel |

---

### TRAIN-DEC-042

**`dropout_risk_signal` e `engagement_signal` são derivados — nunca fonte primária**

- **Tipo:** Governança de dados sensíveis + Integridade
- **Status:** Accepted
- **Fonte:** `SENSITIVE_DOMAIN_GOVERNANCE.md` + `Arquitetura Treinos.md`

#### Decisão

`dropout_risk_signal`, `engagement_signal` e similares são **derivados computados** de dados-fonte (respostas brutas de check-in, padrões de presença, RPE). Eles:
- nunca substituem ou deletam os dados-fonte
- são recalculáveis se a fórmula mudar
- não podem ser exportados como fatos de risco individualizados sem revisão humana

---

### TRAIN-DEC-043

**Registros sensíveis não têm armazenamento ad hoc em `training`**

- **Tipo:** Governança de dados sensíveis
- **Status:** Accepted
- **Fonte:** `SENSITIVE_DOMAIN_GOVERNANCE.md`

#### Decisão

O módulo `training` não deve criar compartimentos de armazenamento ad hoc para dados sensíveis arbitrários. Dados sensíveis dentro do fluxo de `training` devem ser persistidos como tipos explicitamente modelados ou referenciados via `wellness` como módulo soberano.

Tipos de registro sensível permitidos no contexto de `training`:
- `wellbeing_checkin_response` — soberano do módulo `wellness`; training consome referência
- `health_adjacent_flag` — soberano do módulo `medical`; training consome read-only

---

## Decisões de Escopo e Boundary Formalizadas

---

### TRAIN-DEC-044

**Sessão híbrida usa escopo coletivo com variantes individuais embedded**

- **Tipo:** Estrutura de domínio
- **Status:** Accepted
- **Resolve:** OPEN-001

#### Contexto

Sessões de treino precisam suportar prescrição coletiva (toda a equipe), individual (atleta específico em reabilitação) e híbrida (coletiva com adaptações por atleta). Não existe um modelo explícito para esse continuum.

#### Decisão

`training_session` é uma entidade única com campo `individualization_mode`:

| Modo | Semântica |
|---|---|
| `COLLECTIVE_UNIFORM` | Todos os atletas seguem os mesmos blocos e cargas |
| `COLLECTIVE_WITH_VARIANTS` | Mesmos blocos; variações de carga/exercício por atleta via `block_athlete_variant` |
| `INDIVIDUAL_ONLY` | Sessão criada para atleta(s) específico(s) — ex.: reabilitação, return-to-play |

**Não existem duas entidades-tipo** (`team_session` e `individual_session`). A sessão é sempre uma — o nível de individualização é um atributo, não um tipo.

`session_scope.team_ref` define o coletivo base. `session_scope.athlete_refs` lista atletas explícitos quando o modo for `INDIVIDUAL_ONLY`. `block_athlete_variant` carrega sobrescritas por atleta no modo `COLLECTIVE_WITH_VARIANTS`.

#### Consequências

- **Positivo:** Modelo unificado — consultas, relatórios e permissões operam sobre um único tipo de entidade.
- **Positivo:** `INV-TRAIN-035` pode ser especificado com precisão.
- **Negativo:** `block_athlete_variant` adiciona complexidade relacional ao bloco.

#### Invariantes vinculadas

`INV-TRAIN-035` (atualizado para refletir `individualization_mode`)

---

### TRAIN-DEC-045

**`planned vs actual` é estrutura dualista embedded; comparação é sempre query derivada**

- **Tipo:** Execução
- **Status:** Accepted
- **Resolve:** OPEN-002, OD-TRAIN-003

#### Decisão

A dualidade planejado/realizado é **obrigatória e embedded** — não uma entidade separada:

- `planned_content_snapshot` — capturado no momento da publicação da sessão; imutável após publicação.
- `execution_records` — fatos append-only acumulados durante e após a sessão.
- Comparação planned vs actual é sempre uma **query derivada** — não é armazenada como campo.

**Granularidade por fase:**

| Fase | Granularidade obrigatória |
|---|---|
| Fase 1 | Nível de sessão: `planned_duration_min` vs `actual_duration_min`; `planned_load_target` vs `actual_load_recorded` |
| Fase 2 | Nível de bloco e drill por atleta |

#### Consequências

- **Positivo:** `planned_content_snapshot` nunca é sobrescrito — decisão histórica preservada.
- **Positivo:** Granularidade de Fase 1 é contratável sem esperar Fase 2.
- **Negativo:** Query de comparação é derivada; caching pode ser necessário em listas grandes.

#### Invariantes vinculadas

`INV-TRAIN-007` (atualizado para especificar granularidade por fase)

---

### TRAIN-DEC-046

**`analytics` é soberano de `derived_signal`; `training` consome como read-only**

- **Tipo:** Boundary
- **Status:** Accepted
- **Resolve:** OPEN-003, OD-TRAIN-007

#### Decisão

O módulo `analytics` é o único produtor e soberano de sinais derivados sobre atletas:
- `readiness_score`
- `dropout_risk_signal`
- `engagement_signal`
- Outros sinais computados

`training` **não implementa** cálculo de sinal derivado internamente. Consome os sinais como referências somente leitura com metadados de proveniência (`model_name`, `model_version`, `confidence_level`, `computed_at`).

**Fluxo de trigger (Fase 2):**

```
training → emite trigger_event (ex.: session_completed, checkin_received)
→ analytics processa e recalcula sinais relevantes
→ training consome sinal atualizado via subscription ou pull
```

Até a Fase 2 estar implementada, sinais são consumidos via pull no momento da consulta.

#### Consequências

- **Positivo:** Lógica de cálculo centralizada em `analytics` — sem duplicação.
- **Positivo:** `training` não acumula dependência de modelos de ML.
- **Negativo:** Latência entre evento em `training` e sinal atualizado em `analytics` (aceitável para sinais não-críticos).

#### Invariantes vinculadas

`INV-TRAIN-036` (atualizado para especificar boundary analytics)

---

## Decisões Abertas Formais (OD-TRAIN)

As decisões abaixo são registros formais do `MODULE_DECISION_IR.json`. Decisões com `status: resolved` já foram incorporadas ao contrato.

| ID | Título | Status | Bloqueia? | Resolução / Recomendação |
|---|---|---|---|---|
| OD-TRAIN-001 | exercises/playbook como submódulo de Training ou módulo separado | Open | Não | Módulo separado — Training apenas referencia, evitando acoplamento e supermódulo |
| OD-TRAIN-002 | Escopo de `feedback_thread` — conversação async ou reflexão estruturada | Open | Não | Fase 1: reflexão estruturada com outcome obrigatório; Fase 3: multi-turno |
| OD-TRAIN-003 | `planned_vs_actual` como entidade separada ou embedded em `execution_record` | **Resolved** | Não | Embedded — dualidade por fase; comparação é query derivada — ver TRAIN-DEC-045 |
| OD-TRAIN-004 | MVP scope: capacidades obrigatórias de Fase 2 e 3 no MVP | Resolved | Não | Core MVP: UC-TRAIN-001 a UC-TRAIN-010 (Fase 1); Fase 2 e 3 são iterações seguintes |
| OD-TRAIN-005 | `athlete_checkin` pertence a Training ou Wellness | Resolved | Não | `athlete_checkin` é soberano do módulo `wellness`; Training orquestra e consome `readiness_snapshot_ref` |
| OD-TRAIN-006 | Escopo final de `athlete_feedback` — reflexão única ou multi-turno | Open | Não | Fase 1: resposta única estruturada; Fase 3: conversação multi-turno |
| OD-TRAIN-007 | Política de `derived_signal` — fase 2 scope e triggers de cálculo | **Resolved** | Não | `analytics` é soberano; `training` consome read-only; Fase 2: trigger via evento — ver TRAIN-DEC-046 |

### Resolução formal: OD-TRAIN-005

> **DECISÃO (2026-03-15):** `athlete_checkin` é soberano do módulo `Wellness`. Training orquestra o momento operacional (dispara fluxo de check-in) e consome `readiness_snapshot_ref`. Training não persiste, não cria e não é dono de `athlete_checkin`.
>
> Impacto: `INV-TRAIN-025`, `INV-TRAIN-026`, `INV-TRAIN-037` atualizados para refletir o boundary. `UC-TRAIN-014` atualizado para GET readiness-snapshot.

### Resolução formal: OPEN-001 / TRAIN-DEC-044

> **DECISÃO (2026-03-15):** `training_session` é uma entidade única com campo `individualization_mode` (`COLLECTIVE_UNIFORM`, `COLLECTIVE_WITH_VARIANTS`, `INDIVIDUAL_ONLY`). Não existem dois tipos-entidade para sessão coletiva vs individual. Variações por atleta são expressas via `block_athlete_variant`. `INV-TRAIN-035` atualizado para especificar o modelo.

### Resolução formal: OD-TRAIN-003 / TRAIN-DEC-045

> **DECISÃO (2026-03-15):** `planned vs actual` é dualidade embedded: `planned_content_snapshot` imutável na publicação; `execution_records` append-only acumulam o realizado. Comparação é query derivada — nunca campo armazenado. Fase 1: granularidade de sessão obrigatória. Fase 2: granularidade de bloco/drill/atleta.
>
> Impacto: `INV-TRAIN-007` atualizado para especificar granularidade mínima de Fase 1.

### Resolução formal: OD-TRAIN-007 / TRAIN-DEC-046

> **DECISÃO (2026-03-15):** `analytics` é o módulo soberano de computação de sinais derivados (`readiness_score`, `dropout_risk_signal`, `engagement_signal`). `training` consome esses sinais como read-only com proveniência completa. `training` não implementa cálculo de sinal internamente. Fase 2: `training` emite trigger_event → `analytics` recalcula → `training` consome resultado atualizado.
>
> Impacto: `INV-TRAIN-036` atualizado para especificar boundary analytics. OPEN-003 e OD-TRAIN-007 encerrados.

---

## Inferências Globalmente Proibidas

As seguintes inferências estão explicitamente proibidas no módulo `training`, conforme `MODULE_DECISION_IR.json → forbidden_inference_global`. Qualquer agente, gerador ou implementação que inferir esses comportamentos deve bloquear com erro explícito.

| # | Inferência Proibida |
|---|---|
| FI-001 | `training` criar ou atualizar registros médicos (`restriction_profile`, `return_to_play_guard`) |
| FI-002 | `analytics` ou IA criar, atualizar ou deletar `training_session`, `session_block` ou `prescription_line` diretamente |
| FI-003 | `training` ser dono soberano de `athlete`, `team`, `season` ou `competition` — apenas referência |
| FI-004 | `training` entregar notificações diretamente — apenas emitir `notification_intent` |
| FI-005 | `training` manter log de auditoria próprio — apenas emitir eventos estruturados para módulo `audit` |
| FI-006 | `training` definir regras de permissão — apenas aplicar decisões de `identity_access` |
| FI-007 | `training_session` com status `COMPLETED` ser mutada diretamente — correções apenas via `audit_correction` versionada |
| FI-008 | `recommendation` de analytics auto-materializar como sessão sem ação explícita do coach |
| FI-009 | `derived_signal` (readiness_score, dropout_risk_signal) substituir ou deletar dados-fonte brutos |
| FI-010 | `need_detected` criar automaticamente `training_session` sem ação explícita do coach |
| FI-011 | `feedback_thread` ser fechada sem `conversation_outcome` |
| FI-012 | `session_objective` existir sem origem (`need_ref`, `competitive_focus_ref`, `development_goal_ref` ou `manual_coach_rationale`) |
| FI-013 | `attention_queue_item` ser criada sem `severity_level` + `reason_code` + `target_entity_ref` |
| FI-014 | Atleta com restrição ativa receber prescrição executável sem `restriction_override` autorizado + `audit_event` |
| FI-015 | `training` ser dono da verdade de check-in do atleta — `athlete_checkin` é soberano do módulo `wellness`; training consome apenas `readiness_snapshot_ref` |
| FI-016 | `identity_access` ser tratado como dono de identidade humana — identidade humana e roster de staff são soberanos do módulo `users/staff_directory` |
| FI-017 | `training_recommendation` contornar revisão explícita do coach — nenhuma auto-materialização como sessão, objetivo ou prescrição |
| FI-018 | Revisão existir sem entidade formal `review_outcome` — revisões implícitas ou não documentadas são inválidas |
| FI-019 | Restrição ser quebrada sem entidade formal `restriction_override` com `authorization_level` + trilha de auditoria |

---

## Políticas Globais Aplicadas a `training`

Resumo das políticas da plataforma que incidem sobre o módulo `training`:

| Política | Documento | Impacto em `training` |
|---|---|---|
| CRUD por padrão | `HB_TRACK_ARCHITECTURE_DECISION.md` | Agregado de sessão permanece CRUD |
| HYBRID para `training` | `HB_TRACK_PERSISTENCE_POLICY.md` | Fatos de execução e presença são append-only |
| Separação de camadas | `DTO_VIEWMODEL_BOUNDARY_RULES.md` | Domínio ≠ DTO ≠ ViewModel ≠ Props |
| Camada de ingestão | `INGESTION_PROVIDER_CONTRACT.md` | Dados externos passam por normalização canônica |
| Governança sensível | `SENSITIVE_DOMAIN_GOVERNANCE.md` | Dados de wellness consumidos por training são domínio sensível |
| Contract-Driven Development | `ADR-001` | Contratos precedem implementação; agente não infere comportamento sem artefato normativo |

---

*Gerado em: 2026-03-15 | Fontes: `.dev/arquitetura/Arquitetura Treinos.md`, `HB_TRACK_ARCHITECTURE_DECISION.md`, `HB_TRACK_PERSISTENCE_POLICY.md`, `INGESTION_PROVIDER_CONTRACT.md`, `DTO_VIEWMODEL_BOUNDARY_RULES.md`, `SENSITIVE_DOMAIN_GOVERNANCE.md`, `MODULE_DECISION_IR.json`*
