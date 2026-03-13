# CONTRACT_TRAINING.md
## Contrato Canônico do Módulo TRAINING — HB Track

---

**Artefato:** `CONTRACT_TRAINING`
**Módulo:** `TRAINING`
**Versão:** `1.1.0`
**Status:** `APROVADO — decisões incorporadas em 2026-03-13`
**Data de emissão:** `2026-03-13`
**Responsável pela aprovação:** Product Owner / Principal Architect
**Fontes normativas:**
- `.contract_driven/DOMAIN_AXIOMS.json` v1.0.0
- `docs/_canon/GLOBAL_INVARIANTS.md`
- `docs/hbtrack/modulos/training/INVARIANTS_TRAINING.md`

---

> **Semântica normativa:** As palavras DEVE, DEVEM (obrigação), NÃO DEVE, NÃO DEVEM (proibição) e PODE, PODEM (permissão) têm significado operacional verificável neste contrato. Toda afirmação normativa é auditável por teste, lint ou revisão formal.

---

## Sumário

1. [Objetivo do Módulo](#1-objetivo-do-módulo)
2. [Responsabilidades Permitidas](#2-responsabilidades-permitidas)
3. [Responsabilidades Proibidas](#3-responsabilidades-proibidas)
4. [Entidades do Domínio](#4-entidades-do-domínio)
5. [Casos de Uso](#5-casos-de-uso)
6. [Regras de Negócio Obrigatórias](#6-regras-de-negócio-obrigatórias)
7. [Invariantes do Módulo](#7-invariantes-do-módulo)
8. [Limites de Boundary com Outros Módulos](#8-limites-de-boundary-com-outros-módulos)
9. [Eventos de Entrada e Saída](#9-eventos-de-entrada-e-saída)
10. [Dependências Permitidas](#10-dependências-permitidas)
11. [Dados Sensíveis e Regras de Proteção](#11-dados-sensíveis-e-regras-de-proteção)
12. [Requisitos de Auditoria](#12-requisitos-de-auditoria)
13. [Erros de Contrato e Violações](#13-erros-de-contrato-e-violações)
14. [Critérios de Aceite Verificáveis](#14-critérios-de-aceite-verificáveis)
15. [Artefatos Obrigatórios Derivados](#15-artefatos-obrigatórios-derivados)
16. [Lacunas que Exigem Decisão Humana](#16-lacunas-que-exigem-decisão-humana)

---

## 1. Objetivo do Módulo

O módulo TRAINING é o domínio responsável pela **gestão completa do ciclo de vida de sessões de treino de handebol**, desde o planejamento periódico até a análise de carga e saúde do atleta.

Suas finalidades operacionais são:

1. **Planejamento de periodização:** gerenciar a hierarquia Macrociclo → Mesociclo → Microciclo → Sessão, permitindo ao treinador estruturar temporadas completas com rastreabilidade de progresso.
2. **Execução de sessões:** controlar o ciclo de vida de cada `training_session` (criação, agendamento, execução, revisão e encerramento definitivo), incluindo a biblioteca de exercícios usados.
3. **Coleta de wellness:** capturar dados subjetivos de pré-treino (disponibilidade, sono, dor) e pós-treino (RPE, carga percebida, dificuldade, feedback) de cada atleta.
4. **Presença:** registrar, validar e consolidar presença oficial de atletas ao encerramento da sessão, com suporte a correções auditáveis.
5. **Analytics de carga interna:** calcular e expor métricas de carga (internal_load = minutes_effective × session_rpe), sobrecarga semanal, rankings e evolução de periodização.
6. **Biblioteca de exercícios:** manter catálogo de exercícios em dois escopos — SYSTEM (plataforma) e ORG (organização) — com controle de visibilidade, ACL e mídia.
7. **IA copiloto:** expor funcionalidades de sugestão assistida por IA para treinadores e atletas, sempre como rascunho submetido a aprovação humana, nunca com publicação automática.
8. **Compliance e auditoria:** registrar todos os acessos a dados sensíveis, operações de mutação de sessões e exports, conforme legislação LGPD e políticas internas.

O módulo TRAINING **não** gerencia identidade, autenticação, autorizações de sistema, dados de competição ou comunicação direta com canais externos (e-mail, SMS).

---

## 2. Responsabilidades Permitidas

O módulo TRAINING PODE e DEVE implementar as seguintes responsabilidades:

### 2.1 Gestão de Sessões de Treino
- Criar, editar, publicar, encerrar e cancelar `training_sessions`.
- Transicionar o status da sessão conforme máquina de estados canônica (§6.1).
- Controlar janelas de edição por papel (treinador/coordenador/dirigente) e por status da sessão.
- Bloquear edição de sessões com `session_at` anterior a 60 dias.
- Suportar sessões avulsas (`standalone`) desvinculadas de microciclo, com flag explícita.

### 2.2 Gestão de Exercícios
- Manter catálogo de exercícios de escopo `SYSTEM` (instalados pela plataforma) e `ORG` (criados por usuários da organização).
- Controlar visibilidade de exercícios ORG via `visibility_mode` (`org_wide` | `restricted`) e ACL por usuário.
- Permitir ao treinador criar cópia ORG de exercício SYSTEM para adaptação local (operação `copy-to-org`).
- Gerir favoritos de exercícios por usuário.
- Gerir mídias (image, video, youtube_link, external_link) vinculadas a exercícios.
- Expor ao atleta mídias/instruções de exercícios presentes em sua sessão, independentemente do escopo do exercício.

### 2.3 Periodização
- Criar e gerir `macrocycles`, `mesocycles` e `microcycles` com hierarquia obrigatória Macro → Meso → Micro.
- Permitir sobreposição de datas entre mesociclos da mesma equipe/macrociclo.
- Vincular sessões a microciclos ou marcá-las como avulsas.
- Validar que datas de microciclos estejam 100% contidas no intervalo do mesociclo pai.

### 2.4 Wellness
- Registrar `wellness_pre` (até 2h antes da sessão) e `wellness_post` (até 24h após criação).
- Calcular `internal_load` automaticamente ao submeter `wellness_post` (minutes_effective × session_rpe).
- Emitir verificação de sobrecarga semanal após submissão de `wellness_post`.
- Atualizar `wellness_reminders.responded_at` quando houver reminder pendente para o atleta.
- Emitir badges de wellness por taxa de resposta e consistência mensal.

### 2.5 Presença
- Receber pré-confirmação de atletas (`preconfirmed`) como dado provisório.
- Consolidar presença oficial (presente / ausente / justificado) apenas no encerramento da sessão pelo treinador.
- Registrar correções de presença com campos obrigatórios `correction_by_user_id` e `correction_at`.
- Criar pendências para atletas com dados não resolvidos no encerramento, sem bloquear o fluxo de encerramento.

### 2.6 Analytics e Exports
- Expor endpoints de `summary`, `weekly-load`, `deviation-analysis` e `prevention-effectiveness`.
- Calcular `threshold_critical = threshold_base × teams.alert_threshold_multiplier` por equipe.
- Gerar exports LGPD e relatórios PDF de forma assíncrona via Celery, com rastreabilidade de job.
- Aplicar rate limiting por usuário: máximo 5 exports PDF de analytics/dia e 3 exports de atleta/dia.
- Invalidar `training_analytics_cache` ao inserir, alterar ou remover sessões ou wellness_post.

### 2.7 IA Copiloto
- Sugerir exercícios, rascunhos de sessão e planejamento de microciclo para o treinador, sempre como `DRAFT`.
- Enviar mensagens automáticas ao atleta com tom de sugestão/apoio (não-imperativo).
- Gerar rascunho de "treino extra" a pedido do atleta, roteado ao treinador para aprovação.
- Gerar feedback pós-treino para o atleta (1 reconhecimento + 1 orientação prática) após conclusão do pós-treino conversacional.
- Explicar regras do jogo e conteúdo educativo tático ao atleta (sem alterar treino/agendamento).
- Incluir justificativa rastreável em toda sugestão ao treinador.

### 2.8 Notificações e Alertas
- Emitir alertas de sobrecarga crítica via `NotificationService` + broadcast WebSocket para usuários-alvo.
- Emitir badges de wellness relevantes via `NotificationService`.

---

## 3. Responsabilidades Proibidas

O módulo TRAINING NÃO DEVE assumir as seguintes responsabilidades:

### 3.1 Identidade e Acesso
- NÃO DEVE gerenciar criação, autenticação, recuperação ou revogação de contas de usuário.
- NÃO DEVE emitir tokens de autenticação, sessões HTTP ou credenciais de acesso ao sistema.
- NÃO DEVE misturar tabelas de `identity_access` com tabelas de `users` de domínio de treinamento.
- NÃO DEVE fazer decisões de RBAC fora do escopo do módulo (ex.: decidir se usuário pode acessar módulo de competições).

### 3.2 Publicação Automática via IA
- NÃO DEVE publicar, agendar ou tornar oficial qualquer treino gerado por IA sem ação explícita do treinador humano.
- NÃO DEVE criar registros de `training_session` com status diferente de `DRAFT` como resultado direto de geração por IA.

### 3.3 Integridade do Catálogo Global
- NÃO DEVE permitir edição ou exclusão de exercícios de escopo `SYSTEM` por usuários de organização.
- NÃO DEVE criar exercícios `ORG` sem `organization_id` válido e FK ativa.

### 3.4 Competições e Partidas
- NÃO DEVE gerenciar entidades de competições, partidas, escalações ou resultados de jogo.
- NÃO DEVE referenciar eventos de `match_state` ou `match_phase` em lógica de sessão de treino.

### 3.5 Histórico Imutável
- NÃO DEVE alterar a estrutura de exercícios de sessões encerradas (`status = readonly`).
- NÃO DEVE hard-deletar exercícios referenciados por sessões históricas sem mecanismo de tombstone ou fallback.
- NÃO DEVE transformar pendências de encerramento em dados oficiais da sessão encerrada.

### 3.6 Privacidade de Conversas com IA
- NÃO DEVE expor conteúdo íntimo de conversas do atleta com a IA ao treinador ou a terceiros.
- NÃO DEVE usar conteúdo de conversa para geração de reconhecimento público; apenas métricas agregadas são permitidas.

### 3.7 Comunicação Direta com Canais Externos
- NÃO DEVE enviar e-mails, SMS ou notificações push diretamente; DEVE delegar ao serviço de notificações.
- NÃO DEVE armazenar credenciais de canais externos (SMTP, FCM, APNs).

### 3.8 Timestamps Não-UTC
- NÃO DEVE usar timezone local em comparações de datetime em jobs Celery ou em qualquer lógica de janela temporal.

---

## 4. Entidades do Domínio

Todas as entidades listadas abaixo são de propriedade exclusiva do módulo TRAINING. Identificadores públicos DEVEM seguir formato `uuid_v4` (`^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$`).

### 4.1 `training_session`
Representa uma sessão de treino planejada ou executada.

| Campo | Tipo | Obrigatoriedade | Regra |
|---|---|---|---|
| `id` | uuid_v4 | Obrigatório | Identificador público estável |
| `organization_id` | uuid_v4 | Obrigatório | FK válida; sessão sem org é inválida |
| `team_id` | uuid_v4 | Obrigatório | FK válida ao módulo de equipes |
| `created_by_user_id` | uuid_v4 | Obrigatório | Treinador autor da sessão |
| `microcycle_id` | uuid_v4 | Condicional | NULL apenas se `standalone = true` |
| `standalone` | boolean | Obrigatório | `true` somente se sem microcycle_id |
| `status` | enum | Obrigatório | `DRAFT \| PLANNED \| SCHEDULED \| IN_PROGRESS \| COMPLETED \| CANCELLED`; ver §6.1 |
| `session_at` | timestamp_utc | Obrigatório | Data/hora de início planejado |
| `ended_at` | timestamp_utc | Condicional | Obrigatório ao encerrar |
| `duration_planned_minutes` | integer | Opcional | > 0 quando presente |
| `focus_*_pct` | integer (×7) | Opcional | 0–100 cada; soma ≤ 120 |
| `phase_focus_*` | boolean (×7) | Derivado | Automaticamente: campo ≥ 5% → true |
| `main_objective` | text | Opcional | — |
| `location` | text | Opcional | — |
| `intensity_target` | text | Opcional | — |
| `notes` | text | Opcional | — |
| `deleted_at` | timestamp_utc | Soft delete | Par obrigatório com `deleted_reason` |
| `deleted_reason` | text | Soft delete | Par obrigatório com `deleted_at` |

**Soft delete:** `(deleted_at IS NULL AND deleted_reason IS NULL) OR (deleted_at IS NOT NULL AND deleted_reason IS NOT NULL)` — violação é inválida.

### 4.2 `wellness_pre`
Dados subjetivos coletados do atleta antes do treino.

| Campo | Tipo | Regra |
|---|---|---|
| `id` | uuid_v4 | — |
| `training_session_id` | uuid_v4 | FK para `training_session` |
| `athlete_id` | uuid_v4 | FK para usuário atleta |
| `sleep_hours` | numeric | 0 ≤ valor ≤ 24 |
| `sleep_quality` | integer | 1 ≤ valor ≤ 5 |
| `created_at` | timestamp_utc | — |
| `deleted_at` / `deleted_reason` | timestamp_utc / text | Par soft-delete (INV-TRAIN-008) |

**Unicidade:** No máximo 1 registro ativo por `(training_session_id, athlete_id)` com `deleted_at IS NULL`.
**Janela:** Submissão bloqueada quando `NOW() >= session_at - 2h`.

### 4.3 `wellness_post`
Dados subjetivos coletados do atleta após o treino.

| Campo | Tipo | Regra |
|---|---|---|
| `id` | uuid_v4 | — |
| `training_session_id` | uuid_v4 | FK para `training_session` |
| `athlete_id` | uuid_v4 | FK para usuário atleta |
| `session_rpe` | numeric | 0 ≤ valor ≤ 10 |
| `minutes_effective` | integer | > 0 |
| `internal_load` | numeric | **Derivado automaticamente:** `minutes_effective × session_rpe` (trigger) |
| `created_at` | timestamp_utc | — |
| `deleted_at` / `deleted_reason` | timestamp_utc / text | Par soft-delete |

**Unicidade:** No máximo 1 registro ativo por `(training_session_id, athlete_id)` com `deleted_at IS NULL`.
**Janela:** Edição bloqueada quando `NOW() >= created_at + 24h`.

### 4.4 `exercise`
Exercício do catálogo da plataforma ou de uma organização.

| Campo | Tipo | Regra |
|---|---|---|
| `id` | uuid_v4 | — |
| `scope` | enum | `SYSTEM` ou `ORG`; fechado |
| `organization_id` | uuid_v4 | Obrigatório quando `scope = ORG`; NULL quando `scope = SYSTEM` |
| `created_by_user_id` | uuid_v4 | Obrigatório quando `scope = ORG` |
| `visibility_mode` | enum | `org_wide` ou `restricted`; aplicável apenas a `scope = ORG` |
| `deleted_at` / `deleted_reason` | timestamp_utc / text | Par soft-delete |

**Escopo SYSTEM:** Imutável por usuários de org; adaptação via `copy-to-org` cria novo registro `ORG`.
**Escopo ORG:** Default `visibility_mode = restricted`; compartilhamento exige ação explícita do criador.
**Tombstone (LAC-004 — RESOLVIDO):** Exercícios referenciados por sessões históricas NÃO PODEM sofrer hard-delete destrutivo. O mecanismo obrigatório é tombstone **reversível na própria tabela** (`exercises`), preservando `exercise_id` e snapshot mínimo de identificação (nome, scope, organization_id) para renderização histórica. O frontend DEVE exibir os dados do snapshot quando o exercício estiver em estado tombstone.

### 4.5 `exercise_acl`
Controle de acesso granular a exercícios ORG com `visibility_mode = restricted`.

| Campo | Tipo | Regra |
|---|---|---|
| `exercise_id` | uuid_v4 | FK para `exercise` com `scope = ORG` e `visibility_mode = restricted` |
| `user_id` | uuid_v4 | DEVE pertencer à mesma organização do exercício |

**Unicidade:** `(exercise_id, user_id)` DEVE ser único.
**Proibido:** ACL em exercício com `visibility_mode = org_wide` → 400/422.

### 4.6 `exercise_media`
Mídias vinculadas a um exercício.

| Campo | Tipo | Regra |
|---|---|---|
| `exercise_id` | uuid_v4 | FK para `exercise` |
| `media_type` | enum | `image`, `video`, `youtube_link`, `external_link` |
| `reference` | text | URL ou `asset_id`; NÃO PODE ser vazio |

### 4.7 `exercise_favorite`
Favorito de usuário para exercício.

**Unicidade:** `(user_id, exercise_id)` DEVE ser único. Favorito duplicado DEVE ser rejeitado.

### 4.8 `session_exercise`
Exercício vinculado a uma sessão, com posição determinística.

| Campo | Tipo | Regra |
|---|---|---|
| `session_id` | uuid_v4 | FK para `training_session` |
| `exercise_id` | uuid_v4 | FK para `exercise` visível ao treinador |
| `order_index` | integer | Único por sessão (`deleted_at IS NULL`); contíguo 1..N sem gaps; normalizado em reorder |
| `deleted_at` / `deleted_reason` | timestamp_utc / text | Par soft-delete |

### 4.9 `training_attendance`
Presença de atleta em sessão.

| Campo | Tipo | Regra |
|---|---|---|
| `training_session_id` | uuid_v4 | FK |
| `athlete_id` | uuid_v4 | FK |
| `status` | enum | `preconfirmed`, `present`, `absent`, `justified`; oficial apenas após encerramento |
| `source` | enum | `athlete_self`, `trainer`, `correction` |
| `correction_by_user_id` | uuid_v4 | Obrigatório quando `source = correction` |
| `correction_at` | timestamp_utc | Obrigatório quando `source = correction` |

**Presença oficial:** Consolidada somente no encerramento da sessão pelo treinador; registros anteriores são provisórios.

### 4.10 `training_pendency`
Pendência gerada no encerramento da sessão (presença inválida, atleta não resolvido).

| Campo | Tipo | Regra |
|---|---|---|
| `training_session_id` | uuid_v4 | FK; sessão encerrada NÃO é alterada |
| `reason` | text | Obrigatório; descrição da inconsistência |
| `resolved_at` | timestamp_utc | NULL enquanto pendente |
| `resolved_by_user_id` | uuid_v4 | Somente treinador pode marcar resolvido |

**Pendência NÃO é registro oficial:** É entidade separada vinculada à sessão encerrada.

### 4.11 `macrocycle` / `mesocycle` / `microcycle`
Hierarquia de periodização do planejamento.

| Entidade | Pai | Regra de datas |
|---|---|---|
| `macrocycle` | — | `start_date < end_date` (estrito) |
| `mesocycle` | `macrocycle` | `start_date < end_date` (estrito); sobreposição entre mesociclos é permitida |
| `microcycle` | `mesocycle` | `start_date < end_date` (estrito); DEVE estar 100% contido no intervalo do mesociclo pai; `week_start < week_end` (estrito) |

**Hierarquia obrigatória:** Não PODE existir `microcycle` sem `mesocycle` pai válido, nem `mesocycle` sem `macrocycle` pai válido.

### 4.12 `training_template`
Modelo reutilizável de sessão de treino.

**Unicidade:** Nome de template DEVE ser único por organização.

### 4.13 `training_analytics_cache`
Cache de analytics pré-calculados de carga/periodização.

**Unicidade:** `(team_id, microcycle_id, month, granularity)` DEVE ser único.
**Invalidação:** DEVE ser marcado dirty (`cache_dirty = true`, `calculated_at = NULL`) ao inserir, alterar ou remover `training_session` ou `wellness_post`.
**`granularity` — conjunto fechado (LAC-008 — RESOLVIDO):** `daily`, `weekly`, `monthly`, `microcycle`. Valores fora desse conjunto são inválidos (422). Quando `granularity = monthly`, o campo `month` é obrigatório e DEVE seguir o formato `date_only` (primeiro dia do mês). Nos demais casos, `month` DEVE ser nulo.

### 4.14 `training_ranking`
Ranking mensal de atletas por carga/wellness.

**Unicidade:** `(team_id, month_reference)` DEVE ser único.

### 4.15 `wellness_reminder`
Lembrete de wellness pendente para atleta.

**Atualização:** `responded_at` DEVE ser atualizado ao submeter `wellness_pre` ou `wellness_post` quando houver reminder pendente para `(training_session_id, athlete_id)`.

### 4.16 `audit_log`
Log de operações de mutação de sessões (append-only).

**Obrigatório em:** create, update, publish, close de `training_sessions`.

### 4.17 `data_access_log`
Log de acesso por staff a dados de atletas fora do escopo "self-only".

**Obrigatório em:** qualquer acesso de staff a dados de wellness de atleta.

---

## 5. Casos de Uso

### UC-TRAIN-001 — Criar Sessão de Treino

**Ator:** Treinador
**Pré-condição:** Autenticado; organização e equipe válidas.
**Fluxo:**
1. Treinador envia payload com dados da sessão.
2. Se `microcycle_id` presente e payload completo (duration_planned_minutes, location, main_objective), sistema cria com `status = SCHEDULED`.
3. Se payload incompleto, sistema cria com `status = DRAFT`.
4. Sistema registra `audit_log`.
5. Sistema retorna sessão criada com ID uuid_v4.

**Exceções:** `organization_id` inválido → 422. `microcycle_id` inválido → 422. `standalone = false` sem `microcycle_id` → 422.

---

### UC-TRAIN-002 — Editar Sessão de Treino

**Ator:** Treinador / Coordenador / Dirigente
**Pré-condição:** Sessão existe; ator autenticado com papel adequado.
**Fluxo:**
1. Sistema valida janela de edição conforme papel e status (§6.2, §6.3).
2. Sistema aplica mudança nos campos permitidos para o status atual.
3. Sistema registra `audit_log`.

**Exceções:** Sessão `readonly` → 403. Sessão `in_progress` → 403. Papel sem permissão para status → 403. Edição após 60 dias → 403. Campos não permitidos para status → 422.

---

### UC-TRAIN-003 — Encerrar Sessão de Treino

**Ator:** Treinador
**Pré-condição:** Sessão em `in_progress` ou `pending_review`.
**Fluxo:**
1. Treinador aciona encerramento.
2. Sistema consolida presença oficial dos atletas elegíveis e resolvidos.
3. Para atletas com dados inconsistentes, sistema cria entidades `training_pendency` com motivo.
4. Sessão transita para `readonly` (encerrada permanentemente).
5. Sistema registra `audit_log`.
6. Sistema invalida `training_analytics_cache` relacionado.

**Regra:** Encerramento NÃO É bloqueado por pendências; pendências são criadas e tratadas assincronamente.

---

### UC-TRAIN-004 — Submeter Wellness Pré-Treino

**Ator:** Atleta
**Pré-condição:** Autenticado como atleta; sessão existe; `NOW() < session_at - 2h`.
**Fluxo:**
1. Atleta submete dados de wellness_pre.
2. Sistema valida: não existe registro ativo para `(session_id, athlete_id)`; janela temporal válida.
3. Sistema persiste registro.
4. Sistema atualiza `wellness_reminders.responded_at` se houver reminder pendente.

**Exceções:** Fora da janela → 422. Registro duplicado ativo → 422.

---

### UC-TRAIN-005 — Submeter Wellness Pós-Treino

**Ator:** Atleta
**Pré-condição:** Autenticado como atleta; sessão existe.
**Fluxo:**
1. Atleta submete dados via formulário ou conversacionalmente (campos de formulário são opcionais).
2. Sistema valida `session_rpe` ∈ [0,10]; `sleep_hours` ∈ [0,24]; `sleep_quality` ∈ [1,5].
3. Sistema persiste registro; trigger calcula `internal_load = minutes_effective × session_rpe`.
4. Sistema marca caches `weekly` e `monthly` relacionados como `cache_dirty = true`.
5. Sistema dispara verificação de sobrecarga semanal para `week_start` da sessão.
6. Sistema atualiza `wellness_reminders.responded_at` se houver reminder pendente.
7. Sistema gera feedback do treinador virtual (1 reconhecimento + 1 orientação prática) e entrega ao atleta.

**Exceções:** `session_rpe` fora de [0,10] → 422. Registro duplicado ativo → 422. Edição após `created_at + 24h` → 403.

---

### UC-TRAIN-006 — Registrar Presença (Oficial)

**Ator:** Treinador
**Pré-condição:** Sessão existe; encerramento iniciado.
**Fluxo:**
1. Treinador registra status de presença (present / absent / justified) por atleta.
2. Sistema consolida como dado oficial apenas ao encerrar a sessão.

---

### UC-TRAIN-007 — Corrigir Presença

**Ator:** Treinador
**Pré-condição:** Sessão encerrada; treinador autenticado.
**Fluxo:**
1. Treinador submete correção com `source = correction`.
2. Sistema valida presença de `correction_by_user_id` e `correction_at` no payload.
3. Sistema persiste correção com trilha de auditoria.

**Exceções:** `correction_by_user_id` ausente → 422. `correction_at` ausente → 422.

---

### UC-TRAIN-008 — Consultar Analytics

**Ator:** Staff (coordenador, treinador, dirigente)
**Pré-condição:** Autenticado; acesso ao endpoint via HTTPBearer.
**Fluxo:**
1. Staff acessa endpoints de summary / weekly-load / deviation-analysis / prevention-effectiveness.
2. Sistema usa `threshold_critical = threshold_base × teams.alert_threshold_multiplier`.
3. Sistema registra `data_access_log` por acesso a dados de atletas.
4. Sistema retorna dados de cache (`cache_dirty = false`) ou recalcula se dirty.

---

### UC-TRAIN-009 — Exportar Relatório

**Ator:** Staff
**Pré-condição:** Autenticado; dentro do rate limit diário.
**Fluxo:**
1. Staff solicita export PDF de analytics ou athlete export.
2. Sistema valida rate limit: ≤ 5 exports analytics/dia por usuário; ≤ 3 athlete exports/dia por usuário.
3. Sistema cria job assíncrono via Celery.
4. Sistema retorna ID do job; staff consulta status assincronamente.
5. Artefato binário expira após **TTL de 7 dias** (configurável por tipo de export); URLs/tokens de download são invalidados na expiração; metadado do job é retido para trilha de auditoria.
6. Sistema faz cleanup automatizado de artefatos expirados.
7. Sistema registra `audit_log` da geração.

**Exceções:** Rate limit excedido → 429.

---

### UC-TRAIN-010 — Gerenciar Exercício ORG

**Ator:** Treinador
**Pré-condição:** Autenticado; papel `treinador` na organização.
**Fluxo (criar):**
1. Treinador submete dados do exercício.
2. Sistema define `scope = ORG`, `organization_id` da org do treinador, `visibility_mode = restricted` (default).
3. Sistema persiste exercício; treinador criador tem acesso garantido.

**Fluxo (adaptar SYSTEM):**
1. Treinador aciona `copy-to-org` em exercício SYSTEM.
2. Sistema cria cópia com `scope = ORG`, `visibility_mode = restricted`, `created_by_user_id` do treinador.
3. Exercício SYSTEM original permanece inalterado.

**Exceções:** Tentativa de PATCH/DELETE em `scope = SYSTEM` → 403.

---

### UC-TRAIN-011 — IA Sugere Rascunho de Treino

**Ator:** Treinador / Atleta (pedido de treino extra)
**Pré-condição:** Funcionalidade de IA habilitada.
**Fluxo:**
1. Ator solicita sugestão (exercícios / sessão / microciclo).
2. IA gera proposta com justificativa rastreável (wellness, carga recente, consistência, objetivos, dados de scout).
3. Sistema cria artefato com `status = DRAFT` e rótulo "editar antes de aprovar".
4. Treinador revisa e, mediante ação explícita, publica/agenda.

**Restrição absoluta:** Sistema NÃO PODE publicar ou agendar automaticamente qualquer proposta de IA.
**Restrição de sugestão:** Sugestão sem justificativa rastreável NÃO PODE ser apresentada como "recomendação"; DEVE ser rotulada como "ideia genérica".

---

### UC-TRAIN-012 — Atleta Visualiza Treino

**Ator:** Atleta
**Pré-condição:** Autenticado como atleta.
**Fluxo:**
1. Atleta acessa sua sessão de treino.
2. Sistema verifica compliance de wellness (§6.8).
3. Se em compliance: atleta vê conteúdo completo (exercícios, vídeos, instruções, objetivo).
4. Se fora de compliance: atleta vê apenas mínimo operacional (horário, local).
5. Sistema expõe mídias/instruções dos exercícios presentes na sessão, independente de `visibility_mode`.

---

## 6. Regras de Negócio Obrigatórias

### 6.1 Máquina de Estados da Sessão de Treino

O campo `status` de `training_session` DEVE obedecer ao enum canônico `training_state` de `DOMAIN_AXIOMS.json` (LAC-001 — RESOLVIDO):

```
DRAFT → PLANNED → SCHEDULED → IN_PROGRESS → COMPLETED
  │        │          │              │
  └────────┴──────────┴──────────────┴──→ CANCELLED (de qualquer estado não-terminal)
```

**Estados iniciais:** `DRAFT`, `PLANNED`.
**Estados terminais:** `COMPLETED`, `CANCELLED`.

**Transições permitidas:**

| De | Para |
|---|---|
| `DRAFT` | `PLANNED`, `CANCELLED` |
| `PLANNED` | `SCHEDULED`, `CANCELLED` |
| `SCHEDULED` | `IN_PROGRESS`, `CANCELLED` |
| `IN_PROGRESS` | `COMPLETED`, `CANCELLED` |
| `COMPLETED` | — (terminal) |
| `CANCELLED` | — (terminal) |

**Transições proibidas (explícitas):**
- `DRAFT → COMPLETED`
- `PLANNED → COMPLETED`
- `SCHEDULED → COMPLETED`
- `COMPLETED → IN_PROGRESS`
- `CANCELLED → *` (qualquer)

**Regra INV-TRAIN-018 — Payload completo (LAC-003 — RESOLVIDO):**

O conjunto **fechado e obrigatório** de campos que define "payload completo" é:

| Campo | Tipo |
|---|---|
| `team_id` | UUID |
| `microcycle_id` | UUID |
| `title` | string |
| `scheduled_date` | date |
| `duration_planned_minutes` | integer |
| `location` | string |
| `main_objective` | string |

Regra: se todos os 7 campos estiverem presentes e não-nulos → `status = SCHEDULED`. Qualquer campo ausente ou nulo → `status = DRAFT`. O sistema DEVE aplicar esta regra automaticamente na criação; o cliente NÃO PODE definir `status` explicitamente na criação.

> **Nota de implementação:** O campo `pending_review` referenciado em `INV-TRAIN-004` (janela de revisão do superior) DEVE ser interpretado como o estado `COMPLETED` neste contrato. A atualização formal do texto de `INV-TRAIN-004` em `INVARIANTS_TRAINING.md` é artefato obrigatório derivado desta decisão.

### 6.2 Janelas de Edição por Papel

| Papel | Status permitido | Janela |
|---|---|---|
| Treinador (autor) | `DRAFT` | Livre, até transição |
| Treinador (autor) | `PLANNED` | Livre, até transição |
| Treinador (autor) | `SCHEDULED` | Somente campos `notes`, `focus_*`, `intensity_target` e similares; bloqueado ≤ 10 min antes de `session_at` |
| Coordenador / Dirigente | `COMPLETED` | Até 24h após `ended_at` (limite não-inclusivo); apenas campos de revisão |
| Qualquer papel | `IN_PROGRESS` | Bloqueado completamente |
| Qualquer papel | `COMPLETED` (após janela 24h) | Bloqueado completamente |
| Qualquer papel | `CANCELLED` | Bloqueado completamente |

### 6.3 Imutabilidade Histórica por Tempo

Sessões com `session_at` **anterior a 60 dias** da data atual são **somente leitura**. Qualquer tentativa de edição DEVE retornar HTTP 403.

Esta regra opera de forma independente ao status; mesmo uma sessão em `draft` antiga de 61 dias é imutável.

### 6.4 Percentuais de Foco

O módulo DEVE enforçar:
- Cada campo `focus_*_pct` (7 campos: técnico, tático, físico, psicológico, cognitivo, coletivo, individual), quando presente, DEVE estar em `[0, 100]`.
- A soma dos 7 campos `focus_*_pct` DEVE ser `≤ 120`.
- Campos `phase_focus_*` DEVEM ser derivados automaticamente: `phase_focus_X = true` se e somente se `focus_X_pct >= 5%` (via trigger BEFORE, nunca por cliente).

### 6.5 Regras de Desvio de Planejamento

| Tipo de desvio | Threshold | Consequência |
|---|---|---|
| Desvio absoluto em qualquer foco | ≥ 20 pontos | Exige justificativa |
| Desvio agregado | ≥ 30% | Exige justificativa |
| Comprimento mínimo de justificativa | — | ≥ 50 caracteres |

### 6.6 Cálculo de Carga Interna

`internal_load` de `wellness_post` DEVE ser calculado pelo trigger `tr_calculate_internal_load` como:

```
internal_load = minutes_effective × session_rpe
```

O cliente NÃO PODE submeter `internal_load` diretamente; qualquer valor enviado pelo cliente DEVE ser ignorado ou rejeitado.

### 6.7 Threshold de Sobrecarga Semanal

```
threshold_critical = threshold_base × teams.alert_threshold_multiplier
```

Referências orientativas (não normativas): multiplicador 1.5 para categorias juvenis, 2.0 padrão, 2.5 adultos.
O valor **normativo** é sempre o `alert_threshold_multiplier` da equipe; valores hardcoded por categoria são proibidos.

### 6.8 Política de Compliance de Wellness (Atleta)

Para o atleta acessar o conteúdo completo da sessão (exercícios, vídeos, instruções, detalhes), o sistema DEVE verificar:

1. `wellness_pre` DO DIA submetido.
2. `wellness_post` DO ÚLTIMO TREINO REALIZADO submetido (quando existir último treino encerrado).

Se qualquer condição não for satisfeita: atleta acessa **apenas mínimo operacional** (horário, local). Bloqueio de conteúdo completo é consequência automática da política.

Definição de "último treino realizado": último `training_session` com `status = COMPLETED` do atleta/equipe, no escopo da **organização atual** do atleta. Atleta sem histórico na organização atual não possui "último treino realizado" — a condição 2 é automaticamente considerada satisfeita nesse caso (LAC-007 — RESOLVIDO parcialmente; ver §16 para pendência de decisão formal).

### 6.9 Visibilidade de Exercícios

Um exercício é visível ao treinador se e somente se:
- `scope = SYSTEM` (global), **OU**
- `scope = ORG` E `organization_id = org do treinador` E (`visibility_mode = org_wide` OU `created_by_user_id = treinador` OU `user_id do treinador ∈ exercise_acl`).

O backend É a autoridade de enforcement de visibilidade. Frontend PODE ocultar, mas não substitui a validação do backend.

Ao visualizar exercícios dentro de uma sessão, o atleta DEVE ver mídias/instruções de todos os exercícios presentes, independente de `scope` ou `visibility_mode`.

### 6.10 Rate Limiting de Exports

| Operação | Limite | Período | Rejeição |
|---|---|---|---|
| Export PDF de analytics | 5 por usuário | Dia calendário | HTTP 429 |
| Export de atleta | 3 por usuário | Dia calendário | HTTP 429 |

### 6.11 Badges de Wellness

| Badge | Critério |
|---|---|
| `monthly` | `response_rate >= 90%` no mês calendário |
| `streak` | 3 meses consecutivos cumprindo critério `monthly` |

### 6.12 Regras de Soft Delete

Todo soft delete no módulo DEVE obedecer ao par atômico:
- `(deleted_at IS NULL AND deleted_reason IS NULL)` **OU**
- `(deleted_at IS NOT NULL AND deleted_reason IS NOT NULL)`

Violação desta regra DEVE ser rejeitada por constraint de banco de dados.

### 6.13 Operações de Datetime

Todas as comparações de janela temporal e timestamps gerados em tasks Celery DEVEM usar `timezone.utc`. Timezone local é proibido em qualquer lógica de janela (INV-TRAIN-007).

---

## 7. Invariantes do Módulo

As invariantes abaixo são derivadas de `INVARIANTS_TRAINING.md` e são normativas para este contrato. A tabela referencia o ID canônico, a regra operacional e o mecanismo de verificação esperado.

| ID | Regra Operacional | Mecanismo de Verificação |
|---|---|---|
| INV-TRAIN-001 | Soma dos 7 `focus_*_pct` ≤ 120; cada campo ∈ [0,100] | CHECK constraint DB + teste de serviço |
| INV-TRAIN-002 | `wellness_pre` bloqueado quando `NOW() >= session_at - 2h` | Validação de serviço; teste de janela temporal |
| INV-TRAIN-003 | Edição de `wellness_post` bloqueada quando `NOW() >= created_at + 24h` | Validação de serviço; teste de janela temporal |
| INV-TRAIN-004 | Janela de edição por papel: autor 10min antes, superior 24h após `ended_at` | Validação de serviço; testes RBAC |
| INV-TRAIN-005 | Sessão com `session_at` > 60 dias: somente leitura (403) | Middleware/service; teste de idade de sessão |
| INV-TRAIN-006 | Ciclo de vida: DRAFT→PLANNED→SCHEDULED→IN_PROGRESS→COMPLETED (CANCELLED de qualquer estado) | State machine guard; testes de transição; alinhado ao DOMAIN_AXIOMS training_state |
| INV-TRAIN-007 | Celery tasks DEVEM usar `timezone.utc` | Revisão de código; lint rule |
| INV-TRAIN-008 | Par `(deleted_at, deleted_reason)` sempre consistente | CHECK constraint DB |
| INV-TRAIN-009 | Máximo 1 `wellness_pre` ativo por `(session_id, athlete_id)` | UNIQUE partial index (`deleted_at IS NULL`) |
| INV-TRAIN-010 | Máximo 1 `wellness_post` ativo por `(session_id, athlete_id)` | UNIQUE partial index (`deleted_at IS NULL`) |
| INV-TRAIN-011 | Desvio absoluto ≥ 20pts ou agregado ≥ 30% exige justificativa ≥ 50 chars | Validação de serviço |
| INV-TRAIN-012 | Rate limit: 5 analytics PDF/dia e 3 athlete exports/dia por usuário | Counter Redis/DB; HTTP 429 |
| INV-TRAIN-013 | Badge `monthly` ≥ 90% response_rate; `streak` = 3 meses consecutivos | Task de recálculo; testes de badge |
| INV-TRAIN-014 | `threshold_critical = threshold_base × teams.alert_threshold_multiplier` | Cálculo verificado em testes de analytics |
| INV-TRAIN-015 | Endpoints de analytics expostos com autenticação e threshold dinâmico | OpenAPI lint + testes de endpoint |
| INV-TRAIN-016 | Endpoints de attendance exigem autenticação; sem rota alternativa não autenticada | OpenAPI security review |
| INV-TRAIN-018 | Payload completo com `microcycle_id` → `status = SCHEDULED`; incompleto → `status = DRAFT` | Testes de criação de sessão |
| INV-TRAIN-019 | `audit_log` append-only em create/update/publish/close de sessões | Teste de persistência de auditoria |
| INV-TRAIN-020 | Trigger invalida `training_analytics_cache` em insert/update/delete de sessões | Teste de trigger DB |
| INV-TRAIN-021 | `internal_load` = `minutes_effective × session_rpe` calculado por trigger | Teste de trigger DB |
| INV-TRAIN-022 | Submissão de `wellness_post` marca caches `weekly`/`monthly` como dirty | Teste de side-effect |
| INV-TRAIN-023 | Submissão de `wellness_post` dispara verificação de sobrecarga semanal | Teste de integração Celery |
| INV-TRAIN-024 | Alertas críticos e badges emitidos via `NotificationService` + WebSocket | Teste de integração notificações |
| INV-TRAIN-025 | Exports LGPD/PDF gerados de forma assíncrona; cleanup de jobs expirados | Teste de job Celery; verificação de cleanup |
| INV-TRAIN-026 | Acesso de staff a dados de atleta registrado em `data_access_log` | Teste de audit log; revisão de endpoints |
| INV-TRAIN-027 | `refresh_training_rankings_task` recalcula caches dirty e atualiza `calculated_at` em UTC | Teste de task periódica |
| INV-TRAIN-029 | Edição controlada por status: `readonly`/`in_progress` bloqueiam; `pending_review` restringe; `scheduled` restringe | Testes de RBAC por status |
| INV-TRAIN-030 | `source = correction` exige `correction_by_user_id` e `correction_at` | CHECK constraint + validação de serviço |
| INV-TRAIN-031 | `phase_focus_*` derivado por trigger BEFORE; `phase_focus_X = true` se `focus_X_pct >= 5%` | Teste de trigger DB |
| INV-TRAIN-032 | `session_rpe` ∈ [0, 10] | CHECK constraint DB + validação de serviço |
| INV-TRAIN-033 | `sleep_hours` ∈ [0, 24] | CHECK constraint DB + validação de serviço |
| INV-TRAIN-034 | `sleep_quality` ∈ [1, 5] | CHECK constraint DB + validação de serviço |
| INV-TRAIN-035 | Nome de template DEVE ser único por organização | UNIQUE constraint DB |
| INV-TRAIN-036 | `training_ranking` único por `(team_id, month_reference)` | UNIQUE constraint DB |
| INV-TRAIN-037 | `start_date < end_date` em todos os ciclos (estrito) | CHECK constraint DB |
| INV-TRAIN-040 | OpenAPI DEVE declarar `GET /api/v1/health` (público, sem security) | OpenAPI lint gate |
| INV-TRAIN-041 | OpenAPI DEVE declarar `GET /api/v1/teams` com HTTPBearer + responses 200/422 | OpenAPI lint gate |
| INV-TRAIN-043 | `week_start < week_end` em microciclos (estrito) | CHECK constraint DB |
| INV-TRAIN-044 | `training_analytics_cache` único por `(team_id, microcycle_id, month, granularity)` | UNIQUE constraint DB |
| INV-TRAIN-045 | `order_index` único por `(session_id)` com `deleted_at IS NULL` | UNIQUE partial index DB |
| INV-TRAIN-046 | Inserção de wellness atualiza `wellness_reminders.responded_at` | Trigger ou service side-effect; teste |
| INV-TRAIN-047 | `exercise.scope` ∈ {SYSTEM, ORG}; conjunto fechado | CHECK constraint DB |
| INV-TRAIN-048 | PATCH/DELETE em `scope = SYSTEM` por usuário org → HTTP 403 | Teste de autorização |
| INV-TRAIN-049 | `exercise` com `scope = ORG` DEVE ter `organization_id` NOT NULL e FK ativa | NOT NULL + FK constraint DB |
| INV-TRAIN-050 | Favorito: `(user_id, exercise_id)` único | UNIQUE constraint DB |
| INV-TRAIN-051 | Visibilidade: usuário vê SYSTEM + ORG da própria org (respeitando `visibility_mode`/ACL) | Teste de filtro de visibilidade |
| INV-TRAIN-052 | `exercise_media.media_type` ∈ {image, video, youtube_link, external_link}; `reference` NOT NULL | CHECK + NOT NULL constraint |
| INV-TRAIN-053 | Exercício referenciado por sessão histórica NÃO PODE ser hard-deleted sem tombstone | Regra de serviço; teste de integridade referencial |
| INV-TRAIN-054 | Micro pertence a Meso; Meso pertence a Macro; não existe ciclo sem parent válido | FK constraints DB + validação de serviço |
| INV-TRAIN-055 | Sobreposição de datas entre mesociclos é permitida; sistema NÃO bloqueia | Ausência de CHECK de sobreposição; teste de validação |
| INV-TRAIN-056 | Microciclo DEVE estar 100% contido no intervalo do mesociclo pai | Validação de serviço; teste de datas |
| INV-TRAIN-057 | Sessão DEVE ter `microcycle_id` OU (`microcycle_id IS NULL` AND `standalone = true`) | CHECK constraint DB + validação |
| INV-TRAIN-058 | Exercícios de sessão: add/remove/reorder permitido apenas enquanto `status != readonly` | Guard de serviço; teste de status |
| INV-TRAIN-059 | `order_index` DEVE ser único, contíguo (1..N sem gaps) e determinístico; reorder normaliza gaps | Validação de serviço; teste de reorder |
| INV-TRAIN-060 | Default de `visibility_mode` para ORG: `restricted` | Default de coluna DB + teste de criação |
| INV-TRAIN-061 | Adaptação de SYSTEM: somente via `copy-to-org`; original SYSTEM inalterado | Guard de serviço; teste de cópia |
| INV-TRAIN-062 | Exercício adicionado à sessão DEVE ser visível ao treinador no momento da operação | Validação de serviço; teste de autorização cruzada |
| INV-TRAIN-063 | Atleta PODE pré-confirmar presença (`preconfirmed`); não constitui presença oficial | Regra de modelo; teste de status de presença |
| INV-TRAIN-064 | Presença oficial consolidada somente no encerramento da sessão pelo treinador | Guard de encerramento; teste de fluxo |
| INV-TRAIN-065 | Encerramento NÃO é bloqueado por inconsistências; inconsistências viram pendências | Teste de fluxo de encerramento parcial |
| INV-TRAIN-066 | Pendências vão para fila separada; sessão encerrada NÃO é alterada | Teste de isolamento de entidades |
| INV-TRAIN-067 | Atleta PODE auxiliar resolução de pendência; validação final é exclusiva do treinador | Teste de autorização de resolução |
| INV-TRAIN-068 | Atleta DEVE ver horário, exercícios e objetivo (read-only) antes do treino | Teste de visibilidade por papel |
| INV-TRAIN-069 | Atleta vê mídias/instruções de exercícios da sessão independente de `visibility_mode` | Teste de acesso a mídias por atleta |
| INV-TRAIN-070 | Pós-treino conversacional; campos de formulário são opcionais | Teste de submissão parcial |
| INV-TRAIN-071 | Fora de compliance de wellness → apenas mínimo operacional visível ao atleta | Teste de gate de compliance |
| INV-TRAIN-072 | IA envia mensagens ao atleta apenas como sugestão/apoio; não cria treino oficial | Teste de restrição de IA |
| INV-TRAIN-073 | Treinador NÃO vê conteúdo íntimo de conversa do atleta com IA; só alertas/resumos de risco | Revisão de endpoint; teste de privacidade |
| INV-TRAIN-074 | IA PODE explicar regras do jogo ao atleta sem alterar treino/agendamento | Teste de escopo de resposta IA |
| INV-TRAIN-075 | Rascunho de treino extra gerado por IA chega ao treinador como "editar antes"; sem publicação automática | Teste de fluxo de aprovação |
| INV-TRAIN-076 | Compliance wellness: `wellness_pre` do dia + `wellness_post` do último treino → desbloqueio de conteúdo completo | Teste de gate completo |
| INV-TRAIN-077 | Feedback virtual gerado ao atleta somente após conclusão do pós-treino conversacional | Teste de trigger de feedback |
| INV-TRAIN-078 | Visão de progresso pessoal bloqueada se fora de compliance de wellness | Teste de gate de progresso |
| INV-TRAIN-079 | Reconhecimento público usa apenas métricas agregadas; nunca conteúdo de conversa | Revisão de geração de feedback; teste de privacidade |
| INV-TRAIN-080 | IA PODE propor para treinador; toda proposta como DRAFT; publicação exige ação explícita | Teste de fluxo de aprovação de treinador |
| INV-TRAIN-081 | Sugestão com justificativa rastreável = "recomendação"; sem justificativa = "ideia genérica" com label distinto | Teste de rótulo de sugestão IA |
| INV-TRAIN-EXB-ACL-001 | `exercise` ORG DEVE ter `visibility_mode` ∈ {org_wide, restricted}; default: restricted | CHECK constraint DB |
| INV-TRAIN-EXB-ACL-002 | ACL em `visibility_mode = org_wide` → bloqueado (400/422) | Validação de serviço; teste |
| INV-TRAIN-EXB-ACL-003 | Usuário em ACL DEVE pertencer à mesma org do exercício | Validação de serviço; teste de cross-org |
| INV-TRAIN-EXB-ACL-004 | Apenas treinador criador PODE alterar `visibility_mode` e gerenciar ACL do próprio exercício | Guard RBAC explícito; teste de autorização |
| INV-TRAIN-EXB-ACL-005 | Criador mantém acesso ao próprio exercício independente da ACL | Lógica de visibilidade; teste de acesso do criador |
| INV-TRAIN-EXB-ACL-006 | `(exercise_id, user_id)` na ACL DEVE ser único | UNIQUE constraint DB |
| INV-TRAIN-EXB-ACL-007 | Mudanças de ACL/visibility NÃO invalidam leitura de `session_exercises` históricos | Teste de leitura de sessão histórica pós-mudança de ACL |

**Invariante descontinuada:**
- `INV-TRAIN-028`: DEPRECATED. Historicamente redundante com INV-TRAIN-001. NÃO criar novos ARs referenciando este ID.

---

## 8. Limites de Boundary com Outros Módulos

O módulo TRAINING opera dentro de limites explícitos. Cruzar esses limites sem mecanismo de integração aprovado constitui violação de contrato.

### 8.1 Boundary: Identity & Access (Autenticação)

| Direção | O que o módulo TRAINING faz | O que o módulo TRAINING NÃO faz |
|---|---|---|
| Consome | Valida tokens JWT emitidos pelo módulo de identidade | NÃO emite tokens; NÃO gerencia sessões HTTP |
| Consome | Lê `user_id`, `organization_id`, papel RBAC do token | NÃO gerencia criação ou revogação de usuários |

**Regra de isolamento:** O módulo TRAINING NÃO DEVE acessar tabelas do módulo `identity_access` diretamente. Toda informação de identidade DEVE ser obtida via token ou via contrato de API do módulo de identidade.

**Regra crítica:** Tabelas do módulo `identity_access` e tabelas do domínio `users` (de treinamento) DEVEM permanecer segregadas. Junções diretas entre essas tabelas constituem violação de boundary.

### 8.2 Boundary: Teams (Equipes)

| Direção | O que o módulo TRAINING faz |
|---|---|
| Consome | Lê `team_id` como chave de referência para `training_session`, `training_analytics_cache`, alertas |
| Consome | Lê `teams.alert_threshold_multiplier` para cálculo de `threshold_critical` |

**Regra:** O módulo TRAINING NÃO DEVE criar, editar ou excluir registros de equipes. Toda leitura de dados de equipes DEVE ser tratada como dado de entrada externo.

### 8.3 Boundary: Competitions (Competições)

| Direção | Regra |
|---|---|
| Nenhuma dependência direta | O módulo TRAINING NÃO DEVE referenciar entidades de competição, partidas ou escalações |

**Exceção futura:** Integração entre treino e dados de desempenho em jogo (scout) DEVE ser formalizada como novo contrato de integração antes de ser implementada. Não existe integração implícita autorizada.

### 8.4 Boundary: Notification Service

| Direção | O que o módulo TRAINING faz |
|---|---|
| Emite | Publica eventos de alerta de sobrecarga, badges, feedback de atleta para `NotificationService` |
| Emite | Solicita broadcast WebSocket para usuários-alvo |

**Regra:** O módulo TRAINING NÃO DEVE enviar notificações diretamente por canal externo (push, e-mail, SMS). DEVE sempre delegar ao `NotificationService`.

### 8.5 Boundary: Storage / Export Service

| Direção | Regra |
|---|---|
| Emite | Solicita geração e armazenamento de arquivos PDF via job Celery assíncrono |

**Regra:** O módulo TRAINING NÃO DEVE armazenar arquivos binários de export diretamente no banco relacional principal.

### 8.6 Boundary: IA / LLM Service

| Direção | Regra |
|---|---|
| Consome | Solicita geração de sugestões/rascunhos e geração de feedback pós-treino |

**Regra:** Toda resposta de IA que resulte em dados persistidos DEVE passar por revisão humana explícita antes da persistência como dado oficial. O módulo TRAINING NÃO DEVE persistir automaticamente qualquer saída de IA como dado oficial.

---

## 9. Eventos de Entrada e Saída

Todos os eventos DEVEM usar `timestamp_utc` e identificadores `uuid_v4`. O `event_type` DEVE pertencer ao conjunto canônico de `DOMAIN_AXIOMS.json#domain_enums.event_type` ou a extensão aprovada em `DOMAIN_AXIOMS_TRAINING.json`.

### 9.1 Eventos de Entrada (consumidos pelo módulo TRAINING)

| Evento | Origem | Descrição |
|---|---|---|
| `SESSION_STARTED` | Próprio módulo (trigger interno) | Transição para `in_progress`; ativa coleta de wellness |
| `SESSION_COMPLETED` | Próprio módulo (trigger interno) | Transição para `readonly`; dispara cálculo de analytics |

### 9.2 Eventos de Saída (emitidos pelo módulo TRAINING)

| Evento | Destino | Condição de emissão |
|---|---|---|
| `SESSION_STARTED` | NotificationService, AsyncAPI | Sessão transita para `in_progress` |
| `SESSION_COMPLETED` | NotificationService, AsyncAPI, Analytics | Sessão transita para `readonly` |
| Alerta de sobrecarga semanal | NotificationService + WebSocket | `threshold_critical` excedido após cálculo pós `wellness_post` |
| Badge de wellness (`monthly` / `streak`) | NotificationService + WebSocket | Critério de badge satisfeito |
| Feedback pós-treino do treinador virtual | App do atleta | Após conclusão do pós-treino conversacional |
| Evento de job de export | Celery / Storage Service | Solicitação de export PDF |
| Invalidação de cache | Interno (trigger DB) | Insert/update/delete em `training_session` ou `wellness_post` |

**Restrição:** Nenhum evento de saída DEVE expor conteúdo íntimo de conversa de atleta com IA. Alertas de risco DEVEM ser enviados como resumo de risco, sem texto literal de conversa.

---

## 10. Dependências Permitidas

O módulo TRAINING PODE depender dos seguintes componentes externos, desde que acessados via interface contratada:

| Componente | Tipo | Uso autorizado | Uso proibido |
|---|---|---|---|
| `identity_access` | Módulo interno | Validação de token; leitura de `user_id`, `organization_id`, papel RBAC | Tabelas diretas; criação de usuários |
| `teams` | Módulo interno | Leitura de `team_id`, `alert_threshold_multiplier` | Criação/edição de equipes |
| `NotificationService` | Serviço interno | Emissão de alertas, badges, feedback | Envio direto por canal externo |
| `Celery` | Infraestrutura | Jobs de export, recálculo de rankings, verificação de sobrecarga | Jobs síncronos que bloqueiam a API |
| `Redis` | Infraestrutura | Cache de analytics, contadores de rate limit | Armazenamento de dados de negócio persistentes |
| `PostgreSQL` | Infraestrutura | Persistência de todas as entidades do módulo | — |
| `Storage Service` | Serviço interno | Armazenamento de arquivos PDF de export | Armazenamento de dados relacionais |
| `IA / LLM Service` | Serviço externo | Sugestões, rascunhos, feedback pós-treino | Publicação automática de dados oficiais |

**Dependência proibida:** O módulo TRAINING NÃO DEVE importar ou acoplar diretamente a módulos de `competitions`, `matches` ou `scouting` sem contrato formal de integração aprovado.

---

## 11. Dados Sensíveis e Regras de Proteção

### 11.1 Classificação de Dados Sensíveis

| Entidade / Campo | Classificação LGPD | Motivo |
|---|---|---|
| `wellness_pre.*` (sono, dor, disponibilidade) | Dado de saúde (Art. 11 LGPD) | Informação subjetiva de saúde do atleta |
| `wellness_post.*` (RPE, feedback, dificuldade) | Dado de saúde (Art. 11 LGPD) | Carga interna e percepção de esforço |
| `training_attendance.*` | Dado pessoal (Art. 5 LGPD) | Presença/ausência individual |
| Conversas atleta ↔ IA | Dado pessoal sensível | Conteúdo potencialmente íntimo |
| `data_access_log.*` | Metadado de acesso | Trilha de auditoria de acesso a dados de saúde |

### 11.2 Regras de Acesso

- **Self-only:** Atleta DEVE acessar apenas seus próprios dados de wellness. Acesso a dados de outros atletas requer papel superior explícito.
- **Staff com log obrigatório:** Coordenador/dirigente/preparador físico que acesse dados de wellness de atleta fora do escopo "self-only" DEVE gerar entrada em `data_access_log` com `user_id`, `athlete_id`, `accessed_at` e recurso acessado.
- **Isolamento multi-tenant:** Dados de `organization_id = X` NÃO DEVEM ser acessíveis por usuários de `organization_id = Y`. Toda query de dados de sessão, wellness, exercício ORG e analytics DEVE incluir filtro por `organization_id`.

### 11.3 Regras de Exportação (LGPD)

- Exports de dados de atleta DEVEM ser gerados de forma assíncrona com rastreabilidade (job_id, solicitante, timestamp).
- Exports DEVEM expirar após TTL definido; arquivos expirados DEVEM ser removidos por cleanup automatizado.
- Acesso ao arquivo de export DEVE ser autenticado e autorizado; link de download não pode ser público ou não expirado.

### 11.4 Privacidade de Conversas com IA (LAC-006 — RESOLVIDO)

- Conteúdo íntimo de conversa do atleta com a IA NÃO DEVE ser armazenado de forma que seja acessível ao treinador.
- O sistema DEVE armazenar apenas **metadados minimizados de risco** (sem texto de conversa, sem transcrição) em tabela dedicada, com retenção de **180 dias**.
- As categorias e níveis de risco são definidos por **catálogo fechado** governado por produto e compliance; nenhuma categoria de risco PODE ser adicionada sem aprovação formal do catálogo.
- O treinador recebe apenas o **rótulo da categoria de risco** e data/hora do evento — sem qualquer trecho de conversa.
- Reconhecimento e feedback público de atleta DEVEM usar exclusivamente métricas agregadas (taxa de resposta, frequência de presença) — nunca conteúdo textual de conversa.
- Metadados de risco DEVEM seguir a política de purge de `data_access_log` (§12.4) ao final dos 180 dias de retenção.

---

## 12. Requisitos de Auditoria

### 12.1 Audit Log de Sessões (`audit_log`)

DEVE ser gerado um registro em `audit_log` (append-only — nenhum registro PODE ser alterado ou excluído) para as seguintes operações em `training_sessions`:

| Operação | Campos mínimos do log |
|---|---|
| Criação (`create`) | `session_id`, `user_id`, `action = CREATE`, `timestamp_utc`, `payload_snapshot` |
| Atualização (`update`) | `session_id`, `user_id`, `action = UPDATE`, `timestamp_utc`, `fields_changed`, `before_snapshot`, `after_snapshot` |
| Publicação (`publish`) | `session_id`, `user_id`, `action = PUBLISH`, `timestamp_utc` |
| Encerramento (`close`) | `session_id`, `user_id`, `action = CLOSE`, `timestamp_utc`, `pendencies_count` |

### 12.2 Data Access Log

DEVE ser gerado um registro em `data_access_log` para todo acesso de staff a dados de wellness de atleta fora do escopo "self-only":

| Campo | Descrição |
|---|---|
| `accessor_user_id` | Identificador do staff que acessou |
| `target_athlete_id` | Identificador do atleta cujos dados foram acessados |
| `resource` | Endpoint ou recurso acessado |
| `accessed_at` | timestamp_utc do acesso |

### 12.3 Auditoria de Exports

Todo job de export DEVE registrar: `job_id`, `requested_by_user_id`, `export_type`, `requested_at`, `completed_at`, `status`, `expiry_at`.

### 12.4 Requisitos de Retenção (LAC-002 — RESOLVIDO)

| Log | Retenção mínima | Acesso | Purge |
|---|---|---|---|
| `audit_log` | 5 anos | Apenas papéis administrativos de segurança/compliance | Purge irreversível após prazo, salvo legal hold ativo |
| `data_access_log` | 2 anos | Apenas papéis administrativos de segurança/compliance | Purge irreversível após prazo, salvo legal hold ativo |

Regras adicionais:
- Ambos os logs são **append-only**; nenhum registro PODE ser alterado ou excluído durante o período de retenção.
- Campos sensíveis DEVEM ser minimizados na origem e, quando aplicável, pseudonimizados (e.g., substituir valores de campo por hash irreversível) sem comprometer rastreabilidade.
- O módulo DEVE suportar flag de **legal hold** por período de sessão ou atleta, bloqueando purge automatizado enquanto o hold estiver ativo.
- Purge DEVE ser realizado por processo administrativo controlado, com log do próprio ato de purge em sistema separado de auditoria.

---

## 13. Erros de Contrato e Violações

### 13.1 Formato de Erro Canônico

Todo erro HTTP público do módulo TRAINING DEVE seguir o formato `Problem` (RFC 7807 + extensões HB Track), conforme `DOMAIN_AXIOMS.json#error_axioms`:

```json
{
  "type": "<string: URI de tipo de erro>",
  "title": "<string: descrição legível>",
  "status": <integer: HTTP status code>,
  "traceId": "<string: trace_id format>",
  "detail": "<string: opcional>",
  "instance": "<string: opcional>",
  "code": "<string: opcional, padrão ^[A-Z0-9_\\-]{2,64}$>",
  "requestId": "<string: opcional>",
  "errors": ["<array: opcional, erros de validação>"]
}
```

**Proibido:** Resposta de erro sem `traceId`. Resposta de erro sem `status`. Content-type diferente de `application/problem+json` para erros canônicos.

### 13.2 Mapeamento de Erros de Contrato

| Situação | HTTP Status | `code` sugerido |
|---|---|---|
| Tentativa de edição de sessão `readonly` | 403 | `TRAINING_SESSION_READONLY` |
| Tentativa de edição fora da janela temporal | 403 | `TRAINING_EDIT_WINDOW_EXPIRED` |
| Tentativa de edição de sessão com `session_at` > 60 dias | 403 | `TRAINING_SESSION_HISTORICAL_IMMUTABLE` |
| Papel insuficiente para operação no status | 403 | `TRAINING_INSUFFICIENT_ROLE` |
| PATCH/DELETE em exercício `scope = SYSTEM` | 403 | `EXERCISE_SYSTEM_IMMUTABLE` |
| Treinador não-criador tentando alterar ACL | 403 | `EXERCISE_ACL_UNAUTHORIZED` |
| ACL adicionada a exercício `org_wide` | 400 | `EXERCISE_ACL_INVALID_SCOPE` |
| `wellness_pre` submetido fora de janela | 422 | `WELLNESS_PRE_WINDOW_CLOSED` |
| `wellness_post` editado após 24h | 403 | `WELLNESS_POST_EDIT_WINDOW_EXPIRED` |
| Wellness duplicado (ativo) | 422 | `WELLNESS_DUPLICATE_ACTIVE` |
| `session_rpe` fora de [0,10] | 422 | `WELLNESS_RPE_OUT_OF_RANGE` |
| `sleep_hours` fora de [0,24] | 422 | `WELLNESS_SLEEP_HOURS_INVALID` |
| `sleep_quality` fora de [1,5] | 422 | `WELLNESS_SLEEP_QUALITY_INVALID` |
| Soma de `focus_*_pct` > 120 | 422 | `TRAINING_FOCUS_SUM_EXCEEDED` |
| Desvio sem justificativa mínima | 422 | `TRAINING_DEVIATION_JUSTIFICATION_REQUIRED` |
| Rate limit de export excedido | 429 | `EXPORT_RATE_LIMIT_EXCEEDED` |
| Sessão sem `microcycle_id` e sem `standalone = true` | 422 | `TRAINING_SESSION_INVALID_PLACEMENT` |
| `order_index` com gap ou colisão | 422 | `SESSION_EXERCISE_ORDER_INVALID` |
| Exercício não visível ao treinador | 403 | `EXERCISE_NOT_VISIBLE` |
| `source = correction` sem campos obrigatórios | 422 | `ATTENDANCE_CORRECTION_INCOMPLETE` |
| Usuário de ACL de org diferente | 422 | `EXERCISE_ACL_CROSS_ORG` |
| Transição de estado inválida | 422 | `TRAINING_STATE_TRANSITION_INVALID` |

### 13.3 Violações Críticas de Contrato

As situações abaixo constituem **violação crítica de contrato** e DEVEM bloquear merge/deploy:

1. Rota pública de training não declarada no OpenAPI (`contracts/openapi/openapi.yaml`).
2. Resposta de erro sem `traceId` em endpoint canônico.
3. IA publicando ou agendando treino sem ação explícita do treinador.
4. Acesso de staff a wellness de atleta sem registro em `data_access_log`.
5. Hard-delete de exercício referenciado por sessão histórica sem mecanismo de tombstone.
6. `internal_load` calculado pelo cliente em vez do trigger de banco.
7. Timestamp sem UTC em job Celery de janela temporal.
8. `training_session` criada sem `organization_id` válido.

---

## 14. Critérios de Aceite Verificáveis

Cada critério DEVE ser verificável por teste automatizado, lint ou revisão formal documentada.

### 14.1 Estado e Ciclo de Vida

- [ ] **CA-TRAIN-001:** Sessão criada com payload completo + `microcycle_id` persiste com `status = SCHEDULED`.
- [ ] **CA-TRAIN-002:** Sessão criada com payload incompleto persiste com `status = DRAFT`.
- [ ] **CA-TRAIN-003:** Tentativa de transição de `readonly → qualquer_estado` retorna HTTP 403.
- [ ] **CA-TRAIN-004:** Tentativa de transição `cancelled → qualquer_estado` retorna HTTP 403.
- [ ] **CA-TRAIN-005:** Sessão com `session_at` há 61 dias ou mais retorna HTTP 403 em qualquer tentativa de edição.

### 14.2 Wellness e Janelas Temporais

- [ ] **CA-TRAIN-006:** `wellness_pre` submetido quando `NOW() = session_at - 2h` (exato) retorna HTTP 422.
- [ ] **CA-TRAIN-007:** `wellness_pre` submetido quando `NOW() < session_at - 2h` persiste com sucesso.
- [ ] **CA-TRAIN-008:** Edição de `wellness_post` quando `NOW() = created_at + 24h` (exato) retorna HTTP 403.
- [ ] **CA-TRAIN-009:** Segundo registro ativo de `wellness_pre` para mesmo `(session_id, athlete_id)` retorna HTTP 422.
- [ ] **CA-TRAIN-010:** `session_rpe = -0.01` retorna HTTP 422; `session_rpe = 10` persiste com sucesso; `session_rpe = 10.01` retorna HTTP 422.
- [ ] **CA-TRAIN-011:** `internal_load` no registro persistido equals `minutes_effective × session_rpe`; campo enviado pelo cliente é ignorado.
- [ ] **CA-TRAIN-012:** Submissão de `wellness_post` marca `training_analytics_cache` correspondente com `cache_dirty = true`.

### 14.3 Focus e Desvios

- [ ] **CA-TRAIN-013:** Sete campos `focus_*_pct` todos em 18 (soma = 126) retorna HTTP 422.
- [ ] **CA-TRAIN-014:** Sete campos `focus_*_pct` todos em 17 (soma = 119) persiste com sucesso.
- [ ] **CA-TRAIN-015:** `focus_tecnico_pct = 5` resulta em `phase_focus_tecnico = true` automaticamente (sem envio pelo cliente).
- [ ] **CA-TRAIN-016:** `focus_tecnico_pct = 4` resulta em `phase_focus_tecnico = false` automaticamente.
- [ ] **CA-TRAIN-017:** Desvio absoluto ≥ 20 pts sem justificativa (ou com justificativa < 50 chars) retorna HTTP 422.

### 14.4 Exercícios e ACL

- [ ] **CA-TRAIN-018:** PATCH em exercício `scope = SYSTEM` por treinador retorna HTTP 403.
- [ ] **CA-TRAIN-019:** DELETE em exercício `scope = SYSTEM` por treinador retorna HTTP 403.
- [ ] **CA-TRAIN-020:** `copy-to-org` cria novo exercício com `scope = ORG`, `visibility_mode = restricted`, exercício SYSTEM original inalterado.
- [ ] **CA-TRAIN-021:** Exercício ORG criado sem especificar `visibility_mode` persiste com `visibility_mode = restricted`.
- [ ] **CA-TRAIN-022:** Adição de ACL em exercício `visibility_mode = org_wide` retorna HTTP 400 ou 422.
- [ ] **CA-TRAIN-023:** Adição de usuário de org diferente na ACL retorna HTTP 422.
- [ ] **CA-TRAIN-024:** Treinador B tentando alterar ACL de exercício criado pelo treinador A retorna HTTP 403.
- [ ] **CA-TRAIN-025:** Treinador criador acessa próprio exercício ORG mesmo sem estar listado na ACL.
- [ ] **CA-TRAIN-026:** Treinador sem visibilidade ao exercício retorna HTTP 403 ao tentar adicionar exercício à sessão.
- [ ] **CA-TRAIN-027:** Sessão histórica encerrada com exercício referenciado: exercício soft-deletado; sessão ainda lê dados do exercício sem erro.
- [ ] **CA-TRAIN-028:** Mudança de ACL de exercício não altera leitura de `session_exercises` de sessão histórica.

### 14.5 Periodização e Estrutura

- [ ] **CA-TRAIN-029:** `microcycle` com `start_date` fora do intervalo do mesociclo pai retorna HTTP 422.
- [ ] **CA-TRAIN-030:** Dois mesociclos com datas sobrepostas na mesma equipe/macrociclo persistem com sucesso.
- [ ] **CA-TRAIN-031:** `training_session` sem `microcycle_id` e sem `standalone = true` retorna HTTP 422.
- [ ] **CA-TRAIN-032:** `order_index` duplicado na mesma sessão retorna HTTP 422; reorder normaliza gaps em 1..N.

### 14.6 Presença e Encerramento

- [ ] **CA-TRAIN-033:** Encerramento de sessão com atleta com dados inconsistentes: sessão transita para `readonly`; pendência criada com motivo; sessão NÃO é alterada após encerramento.
- [ ] **CA-TRAIN-034:** Correção de presença sem `correction_by_user_id` retorna HTTP 422.
- [ ] **CA-TRAIN-035:** Pré-confirmação de atleta (`preconfirmed`) não altera status de presença oficial antes do encerramento.

### 14.7 Analytics e Compliance

- [ ] **CA-TRAIN-036:** Sexto request de analytics PDF no mesmo dia retorna HTTP 429.
- [ ] **CA-TRAIN-037:** Analytics com `threshold_critical` usa `teams.alert_threshold_multiplier`; valor diferente do multiplicador retorna analytics incorreto detectável.
- [ ] **CA-TRAIN-038:** Acesso de staff a dados de wellness de atleta registra entrada em `data_access_log`.

### 14.8 Atleta e Compliance de Wellness

- [ ] **CA-TRAIN-039:** Atleta sem `wellness_pre` do dia acessa sessão e vê apenas horário e local; exercícios não retornados.
- [ ] **CA-TRAIN-040:** Atleta em compliance com wellness acessa sessão e vê exercícios + mídias completos.
- [ ] **CA-TRAIN-041:** Atleta vê mídias de exercício `scope = ORG restricted` presente em sua sessão (visibilidade segue sessão, não exercício).

### 14.9 IA e Restrições

- [ ] **CA-TRAIN-042:** Sugestão de IA para treinador cria artefato com `status = DRAFT`; nenhum agendamento automático ocorre.
- [ ] **CA-TRAIN-043:** Sugestão sem justificativa rastreável é rotulada como "ideia genérica"; não exibida como "recomendação".
- [ ] **CA-TRAIN-044:** Endpoint de treinador não expõe texto literal de conversa de atleta com IA.

### 14.10 Formato e Contratos Globais

- [ ] **CA-TRAIN-045:** `GET /api/v1/health` declarado no OpenAPI sem `security`; retorna 200 em smoke test.
- [ ] **CA-TRAIN-046:** `GET /api/v1/teams` declarado com `security: HTTPBearer`; retorna 401 sem token.
- [ ] **CA-TRAIN-047:** Toda resposta de erro de endpoint do módulo TRAINING contém `traceId` e `status` conforme Problem schema.
- [ ] **CA-TRAIN-048:** Soft delete de qualquer entidade com `deleted_at NOT NULL` e `deleted_reason IS NULL` é rejeitado por constraint de banco.

---

## 15. Artefatos Obrigatórios Derivados

Os seguintes artefatos DEVEM existir e permanecer alinhados com este contrato. Divergência entre artefatos constitui violação técnica de contrato.

| Artefato | Caminho | Status Atual | Obrigação |
|---|---|---|---|
| Invariantes do módulo | `docs/hbtrack/modulos/training/INVARIANTS_TRAINING.md` | Existente — **requer atualização** | INV-TRAIN-006 e INV-TRAIN-004 DEVEM refletir state machine `DRAFT→PLANNED→SCHEDULED→IN_PROGRESS→COMPLETED→CANCELLED` (LAC-001) |
| Especificação OpenAPI | `contracts/openapi/paths/training.yaml` + `openapi.yaml` | Referenciado | DEVE declarar todos os endpoints públicos do módulo |
| Schemas OpenAPI | `contracts/schemas/training/` | Referenciado | DEVE conter schemas de request/response de todas as entidades públicas |
| TRD (Technical Reference) | `docs/hbtrack/modulos/training/TRD_TRAINING.md` | Existente | DEVE permanecer alinhado à versão do OpenAPI |
| PRD Baseline | `docs/hbtrack/modulos/training/PRD_BASELINE_ASIS_TRAINING.md` | Existente | DEVE ser atualizado quando novos FRs são adicionados ao TRD |
| Axiomas de domínio — extensão TRAINING | `docs/hbtrack/modulos/training/DOMAIN_AXIOMS_TRAINING.json` | Ausente / A criar | DEVE ser criado se o módulo precisar estender enums globais |
| Matriz de testes | A criar | Ausente | DEVE mapear todos os CAs de §14 para testes implementados |
| Playbook de migração de banco | Via Alembic migration + playbooks | Referenciado | DEVE existir migration para cada alteração de schema |

**Regra de alinhamento de versão:** Todo artefato DEVE referenciar a mesma versão do TRD. Divergência de versão entre artefatos DEVE bloquear merge via gate de governança.

---

## 16. Lacunas — Registro de Decisões

Histórico de lacunas identificadas na emissão v1.0.0 e seu estado de resolução.

| LAC | Título | Status |
|---|---|---|
| LAC-001 | Divergência de state machine | ✅ RESOLVIDO |
| LAC-002 | Política de retenção de audit logs | ✅ RESOLVIDO |
| LAC-003 | Definição de "payload completo" para INV-TRAIN-018 | ✅ RESOLVIDO |
| LAC-004 | Mecanismo de tombstone para exercícios | ✅ RESOLVIDO |
| LAC-005 | TTL de jobs de export | ✅ RESOLVIDO |
| LAC-006 | Metadados de risco de IA | ✅ RESOLVIDO |
| LAC-007 | "Último treino realizado" para atletas transferidos | ⚠️ DECISÃO INCORRETA — requer revisão |
| LAC-008 | Granularidade de `training_analytics_cache` | ✅ RESOLVIDO |

---

### LAC-001 — ✅ RESOLVIDO — Divergência entre Status Operacional e Enum Canônico

**Decisão:** `INV-TRAIN-006` passa a usar o enum canônico do `DOMAIN_AXIOMS.json`: `DRAFT`, `PLANNED`, `SCHEDULED`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED`. Os estados `pending_review` e `readonly` são descontinuados. O estado `COMPLETED` equivale semanticamente ao antigo `readonly`. A janela de revisão do superior (INV-TRAIN-004) opera sobre o estado `COMPLETED`.

**Artefatos impactados:** `INVARIANTS_TRAINING.md` (INV-TRAIN-006 e INV-TRAIN-004 devem ser atualizados); `TRD_TRAINING.md`; OpenAPI schemas.

---

### LAC-002 — ✅ RESOLVIDO — Política de Retenção de Audit Logs

**Decisão:** `audit_log` retido por 5 anos; `data_access_log` retido por 2 anos. Acesso restrito a papéis administrativos de segurança/compliance. Purge irreversível ao término do prazo, salvo legal hold ativo. Campos sensíveis minimizados e pseudonimizados na origem quando aplicável. Incorporado em §12.4.

---

### LAC-003 — ✅ RESOLVIDO — Definição de "Payload Completo" para INV-TRAIN-018

**Decisão:** O conjunto canônico fechado de campos obrigatórios para `status = SCHEDULED` é: `team_id`, `microcycle_id`, `title`, `scheduled_date`, `duration_planned_minutes`, `location`, `main_objective`. A ausência ou nulidade de qualquer um desses campos resulta em `status = DRAFT`. Incorporado em §6.1 (regra INV-TRAIN-018).

---

### LAC-004 — ✅ RESOLVIDO — Mecanismo de Tombstone para Hard-Delete de Exercícios

**Decisão:** Tombstone **reversível na própria tabela** `exercises`. O registro NÃO é removido fisicamente; um campo de estado tombstone é ativado, preservando `exercise_id` e snapshot mínimo de identificação (nome, scope, organization_id) para renderização histórica. Frontend DEVE exibir dados do snapshot quando exercício estiver em tombstone. Incorporado em §4.4.

---

### LAC-005 — ✅ RESOLVIDO — TTL de Jobs de Export

**Decisão:** TTL padrão de **7 dias**, configurável por tipo de export. Artefato binário e URLs/tokens são removidos/invalidados na expiração. Metadado do job permanece para trilha de auditoria. Incorporado em UC-TRAIN-009 (§5).

---

### LAC-006 — ✅ RESOLVIDO — Metadados de Risco de IA

**Decisão:** Alertas de risco compostos exclusivamente por **metadados minimizados** (sem conteúdo de conversa). Categorias de risco definidas por catálogo fechado governado por produto e compliance. Retenção de **180 dias** em tabela dedicada, com purge posterior. Incorporado em §11.4.

---

### LAC-007 — ⚠️ DECISÃO INCORRETA — "Último Treino Realizado" para Atletas Transferidos

> **ATENÇÃO:** A decisão registrada nesta LAC está incorreta — o texto colado é idêntico ao de LAC-006 (metadados de risco de IA) e não responde à pergunta desta LAC.

**Lacuna original:** INV-TRAIN-076 exige `wellness_post` do "último treino realizado". Comportamento indefinido quando atleta foi transferido entre equipes ou não possui histórico na organização atual.

**Decisão parcial incorporada em §6.8:** "Último treino realizado" = último `training_session` com `status = COMPLETED` na **organização atual** do atleta. Atleta sem histórico na organização atual tem a condição 2 de wellness automaticamente satisfeita.

> ⚠️ **PENDENTE:** A questão de transferência entre **equipes dentro da mesma organização** não foi decidida. Se o atleta mudou de equipe A para equipe B na mesma org, o "último treino" refere-se ao da equipe anterior ou apenas da equipe atual? Esta decisão deve ser formalizada antes da implementação de INV-TRAIN-076.

---

### LAC-008 — ✅ RESOLVIDO — Granularidade de `training_analytics_cache`

**Decisão:** Conjunto fechado: `daily`, `weekly`, `monthly`, `microcycle`. Quando `granularity = monthly`, campo `month` é obrigatório (formato `date_only`, primeiro dia do mês); nos demais casos, `month` DEVE ser nulo. Incorporado em §4.13.

---
