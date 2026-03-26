---
module: "training"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: true
contract_path_ref: "../../../../contracts/openapi/paths/training.yaml"
schemas_ref: "../../../../contracts/schemas/training/"
type: "invariants"
---

# INVARIANTS_TRAINING.md

## Objetivo
Registrar invariantes do módulo `training`.

## Definição
Invariantes são condições que devem permanecer verdadeiras independentemente do fluxo, endpoint ou interface.

## Invariantes globais vinculantes
- `.contract_driven/DOMAIN_AXIOMS.json`
- `docs/_canon/GLOBAL_INVARIANTS.md`

## Tabela de invariantes
| ID | Invariante | Entidades | Fonte | Como verificar |
|---|---|---|---|---|
| INV-TRAIN-001 | A soma dos percentuais de foco (7 campos `focus_*_pct`) deve ser ≤ 120.00 após arredondamento. **Política de precisão (RC-2):** cada campo é aceito com até 2 casas decimais; o servidor trunca para 2 casas (ROUND_HALF_UP) antes de calcular a soma. A comparação é feita APÓS o arredondamento. Valores individuais, quando presentes, devem estar em [0.00..100.00]. Caso de borda: 33.33 + 33.33 + 33.34 = 100.00 ✅ · 33.34 × 4 = 133.36 ❌ (422). A regra nunca rejeita por imprecisão de ponto flutuante do cliente. | `TrainingSession` | Regra de produto + RC-2 | Teste unitário de validação de payload; caso de borda com 33.33% × 3; caso overflow 1e308 (schema `maximum: 100` bloqueia) |
| INV-TRAIN-002 | Submissão/edição de `wellness_pre` é bloqueada quando `NOW_UTC ≥ deadline_utc` onde `deadline_utc = session_at_utc - 2h + 30s` (tolerância de clock skew). **Política temporal (RC-3):** (1) toda comparação temporal usa UTC exclusivamente — client-side é apenas hint visual; (2) tolerância de ±30s para compensar clock skew entre cliente e servidor; (3) resposta de erro 400 deve incluir campo `deadline_utc` no body. | `WellnessPre` | Regra de produto + RC-3 | Teste com `frozen_time` (unittest.mock.patch); teste de clock skew (envio às deadline_utc - 29s deve passar; às deadline_utc + 31s deve rejeitar); verificar campo `deadline_utc` no erro |
| INV-TRAIN-003 | Edição de `wellness_post` é bloqueada quando `NOW_UTC ≥ created_at_utc + 24h` (limite não-inclusivo). **Política temporal (RC-3):** mesmas regras de UTC/clock skew de INV-TRAIN-002 se aplicam. Tolerância de ±30s. Erro 400 com `deadline_utc` no body. | `WellnessPost` | Regra de produto + RC-3 | Teste de tentativa de edição após janela; validação temporal com frozen time |
| INV-TRAIN-004 | Janela de edição depende de papel e estado: Autor (treinador) pode editar sessão "scheduled" até 10 min antes de `session_at` (não-inclusivo). Superior (coordenador/dirigente) pode editar "pending_review" até 24h após `ended_at` (não-inclusivo). | `TrainingSession` | Regra de produto + RBAC | Teste de autorização temporal por papel; tentativa de edição fora da janela |
| INV-TRAIN-005 | Sessões com `session_at` mais antigas que 60 dias são somente leitura; qualquer tentativa de edição é bloqueada | `TrainingSession` | Regra de produto | Teste de tentativa de edição de sessão histórica; flag `readonly` computado dinamicamente |
| INV-TRAIN-006 | Status de `training_session` segue FSM fechada de 7 estados canônicos (ADR-017): `DRAFT`, `SCHEDULED`, `PUBLISHED`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED`, `ARCHIVED`. Transições arbitrárias são rejeitadas. ARCHIVED é estado terminal somente-sistema (automação 60 dias pós-COMPLETED). FI-007: sessão COMPLETED é imutável por edição destrutiva. | `TrainingSession` | ADR-017 + DOMAIN_AXIOMS.json `training_state_machine` | Validação de enum no schema; teste de transição inválida (ex.: DRAFT→COMPLETED); teste de tentativa de edição destrutiva em COMPLETED |

## Regras de uso
1. Nenhum endpoint pode violar invariantes.
2. Nenhuma automação assíncrona pode violar invariantes.
3. Nenhuma UI pode assumir transição que quebre invariantes.
4. Toda violação deve bloquear merge ou exigir exceção formal.

## Relação com outros documentos
- `DOMAIN_RULES_TRAINING.md`
- `TEST_MATRIX_TRAINING.md`

## Nota sobre workflow de estados
O workflow canônico de `TrainingSession` está definido em `.contract_driven/DOMAIN_AXIOMS.json → training_state_machine` (ADR-017):

**DRAFT → SCHEDULED/PUBLISHED → IN_PROGRESS → COMPLETED → ARCHIVED (sistema)**
**DRAFT/SCHEDULED/PUBLISHED/IN_PROGRESS → CANCELLED**

INV-TRAIN-006 foi atualizado em 2026-03-16 para refletir os 7 estados canônicos do ADR-017.
Divergências pré-existentes com estados legados (`pending_review`, `readonly`) foram encerradas (LAC-001 resolvido).

## INV-TRAIN-007
Operações de datetime em tasks Celery devem usar timezone UTC (timezone.utc) para comparações e timestamps.
Evita drift por timezone local e garante determinismo em jobs de transição/cálculo.

## INV-TRAIN-008
(deleted_at IS NULL AND deleted_reason IS NULL) OR (deleted_at IS NOT NULL AND deleted_reason IS NOT NULL).
Soft delete auditável e reversível: não existe "exclusão sem motivo".

## INV-TRAIN-009
No máximo 1 wellness_pre ativo por (training_session_id, athlete_id).
Soft-delete aware (único quando deleted_at IS NULL).
Impede duplicidade de respostas pré-treino por sessão, protegendo analytics e alertas.

## INV-TRAIN-010
No máximo 1 wellness_post ativo por (training_session_id, athlete_id).
Soft-delete aware (único quando deleted_at IS NULL).
Evita duplicidade de RPE/carga interna por sessão.

## INV-TRAIN-011
- Desvio significativo: >= 20 pts em qualquer foco (absoluto).
- Desvio agregado significativo: >= 30% (agregado).
- Justificativa mínima para desvios: >= 50 caracteres.
Desvios precisam ser rastreáveis e explicáveis para auditoria e para calibrar planejamento.

## INV-TRAIN-012
Rate limiting diário:
- Analytics PDF: máximo 5/dia por usuário.
- Athlete export: máximo 3/dia por usuário.
Protege a plataforma contra abuso/custos de geração e reduz risco operacional.

## INV-TRAIN-013
Badges de wellness:
- monthly: response_rate >= 90% no mês.
- streak: 3 meses consecutivos cumprindo critério.
Incentiva consistência de resposta wellness e melhora qualidade de dados.

## INV-TRAIN-014
Alertas de sobrecarga semanal usam multiplicador por equipe:
threshold_critical = threshold_base * teams.alert_threshold_multiplier.
(Referência de produto: 1.5 juvenis, 2.0 padrão, 2.5 adultos.)
Threshold dinâmico é essencial para evitar falsos positivos em diferentes categorias/idades.

## INV-TRAIN-015
O módulo Training Analytics expõe endpoints de summary/weekly-load/deviation-analysis/prevention-effectiveness via router + services, com threshold dinâmico baseado em team.alert_threshold_multiplier.
Analytics precisa ser acessível por staff para tomada de decisão e prevenção.

## INV-TRAIN-016
Endpoints de attendance exigem autenticação; rota scoped alternativa (teams/{team_id}/trainings/{id}/attendance) não é exposta no agregador.
Presença é dado sensível operacional; não deve haver rota "paralela" exposta sem governança.

## INV-TRAIN-017
Transições de estado de `training_session` seguem exclusivamente o mapa canônico de ADR-017. Somente as seguintes transições são válidas:
`DRAFT→SCHEDULED`, `DRAFT→CANCELLED`, `SCHEDULED→PUBLISHED`, `SCHEDULED→DRAFT`, `SCHEDULED→CANCELLED`, `PUBLISHED→IN_PROGRESS`, `PUBLISHED→SCHEDULED`, `PUBLISHED→CANCELLED`, `IN_PROGRESS→COMPLETED`, `IN_PROGRESS→CANCELLED`, `COMPLETED→ARCHIVED`.
Qualquer outra transição (ex.: `DRAFT→COMPLETED`, `COMPLETED→IN_PROGRESS`, qualquer transição a partir de `ARCHIVED` ou `CANCELLED`, `PUBLISHED→DRAFT`, `IN_PROGRESS→SCHEDULED`) deve ser rejeitada com `422 TRAINING_INVALID_STATE_TRANSITION`.
**RC-1 (matriz de transições proibidas):** ver `STATE_MODEL_TRAINING.md § "Transições explicitamente proibidas (matriz completa)"` para todos os 20 casos documentados com motivo e invariante.
Guard de transição deve verificar estado atual no banco ANTES de aceitar operação (SELECT FOR UPDATE ou equivalente).
Fonte: ADR-017, TRAIN-DEC-026, STATE_MODEL_TRAINING.md.

## INV-TRAIN-018
Ao criar training_session com microcycle_id:
- Se payload estiver "completo" (ex.: duration_planned_minutes, location, main_objective), status inicial = scheduled.
- Caso contrário, status inicial = draft.
Sessões originadas do planejamento podem nascer agendadas quando já têm dados mínimos.

## INV-TRAIN-019
Ações create/update/publish/close em training_sessions registram audit_logs (append-only).
Treinos impactam métricas, saúde e decisões; auditoria é requisito de compliance/operacional.

## INV-TRAIN-020
Trigger tr_invalidate_analytics_cache invalida training_analytics_cache quando training_sessions é inserido/alterado/removido.
Evita analytics "stale" e mantém consistência de métricas weekly/monthly.

## INV-TRAIN-021
Trigger tr_calculate_internal_load calcula wellness_post.internal_load automaticamente (minutes_effective × session_rpe).
Padroniza cálculo de carga interna e evita divergência entre clientes.

## INV-TRAIN-022
Ao submeter wellness_post, o sistema deve marcar caches weekly e monthly relacionados como dirty (cache_dirty=true; calculated_at=NULL).
Wellness pós altera carga/RPE e precisa refletir rapidamente nos dashboards.

## INV-TRAIN-023
Ao submeter wellness_post, deve ser possível disparar verificação de sobrecarga semanal para a semana da sessão (week_start) usando multiplicador da equipe.
Integra wellness/carga com prevenção de overtraining de forma automática.

## INV-TRAIN-024
Alertas críticos e badges relevantes geram NotificationService + broadcast via WebSocket (para usuários-alvo).
Notificações reduzem latência operacional (coordenação e prevenção).

## INV-TRAIN-025
Exports LGPD/relatórios PDF devem ser gerados de forma assíncrona via job (Celery), com cleanup de jobs expirados e auditabilidade.
Evita bloquear UI, garante rastreabilidade e reduz risco de reprocessamentos.

## INV-TRAIN-026
Quando staff acessa dados de atletas (ex.: wellness) fora do "self-only", deve registrar data_access_logs/audit logs conforme política LGPD.
Compliance LGPD: rastrear acesso a dados pessoais/saúde.

## INV-TRAIN-027
A task refresh_training_rankings_task recalcula caches dirty e marca cache_dirty=false, atualizando calculated_at em UTC.
Mantém analytics consistentes sem depender apenas de eventos em tempo real.

## INV-TRAIN-028
DEPRECATED. ID histórico redundante para a mesma regra de INV-TRAIN-001.
Mantido para compatibilidade com histórico de testes; não criar novos ARs referenciando INV-TRAIN-028.

## INV-TRAIN-029
Edição de training_sessions é controlada por estado:
- readonly: bloqueia completamente
- in_progress: bloqueia completamente
- pending_review: permite apenas campos de revisão
- scheduled: permite apenas subconjunto (notes, focus_*, intensity_target, etc.)
- draft: edição livre
Evita inconsistência operacional durante execução e consolida revisão pós-treino.

## INV-TRAIN-030
Quando attendance.source = 'correction', os campos correction_by_user_id e correction_at são obrigatórios.
Correções administrativas precisam de trilha de auditoria explícita.

## INV-TRAIN-031
phase_focus_* é derivado automaticamente quando percentuais correspondentes >= 5%, via trigger BEFORE + constraints de consistência.
Normaliza flags por foco sem depender do cliente e garante consistência com percentuais.

## INV-TRAIN-032
session_rpe deve estar entre 0 e 10 (inclusive).
RPE fora do domínio invalida cálculos de carga interna.

## INV-TRAIN-033
sleep_hours deve estar entre 0 e 24 (inclusive).
Evita valores inválidos e melhora qualidade do dado de sono.

## INV-TRAIN-034
sleep_quality deve estar entre 1 e 5 (inclusive).
Mantém consistência com UI (escala 1–5) e com cálculos derivados (readiness).

## INV-TRAIN-035
Todo `training_session` DEVE declarar `individualization_mode` explicitamente (campo obrigatório).
Valor deve ser um dos 3 modos canônicos: `COLLECTIVE_UNIFORM`, `COLLECTIVE_WITH_VARIANTS`, `INDIVIDUAL_ONLY` (TRAIN-DEC-044).
- `COLLECTIVE_UNIFORM`: todos os atletas seguem os mesmos blocos e cargas.
- `COLLECTIVE_WITH_VARIANTS`: mesmos blocos; variações por atleta via `block_athlete_variant`.
- `INDIVIDUAL_ONLY`: sessão para atleta(s) específico(s) — reabilitação, return-to-play.
Não existem dois tipos de entidade sessão (coletiva vs individual). O modo é atributo, não tipo.
Vinculado a: `INV-TRAIN-016` (dois loops explícitos), `TRAIN-DEC-016`, `TRAIN-DEC-044`.

## INV-TRAIN-082
Nome do template de sessão é único por organização (`name` UNIQUE dentro de `organization_id`).
Evita ambiguidade na seleção e reutilização de templates.
(Movido de INV-TRAIN-035 em 2026-03-16 para liberar INV-TRAIN-035 para individualization_mode.)

## INV-TRAIN-083
**Regra de Soma Elástica para blocos de sessão (OPEN-005, resolvido 2026-03-16).**

Constraint: `SUM(session_block.durationMinutes) ≤ durationPlannedMinutes + MIN(durationPlannedMinutes × 0.10, 10)`

Comportamento dentro da tolerância:
- Emite **Warning** visível no frontend (não é erro bloqueante).
- Gera item de baixa severidade na `attention_queue` (campos obrigatórios: `severity`, `reason`, `target_entity` — conforme TRAIN-DEC-027).

Comportamento fora da tolerância: **rejeita** a operação (422) com mensagem clara indicando o excesso em minutos.

Transições **NÃO bloqueadas** por esta regra: `PUBLISHED`, `COMPLETED`.
Rationale: respeita a autoridade soberana do treinador e a realidade imprevisível das quadras de handebol. O sistema deve alertar, não obstruir.

Vinculado a: OPEN-005, TRAIN-DEC-027, INV-TRAIN-006 (FSM), `session_block` contract (DEFER-TRAIN-P2-006).

## INV-TRAIN-036
Ranking mensal é único por (team_id, month_reference).
Evita duplicidade de ranking e garante idempotência de recálculos mensais.

## INV-TRAIN-037
start_date < end_date (estrito).
Planejamento inválido (datas invertidas) quebra microciclos e relatórios.

## INV-TRAIN-040
O OpenAPI deve declarar GET /api/v1/health (operationId health_api_v1_health_get), público (sem security) e com response 200.
Gate de contrato: endpoint health é âncora de observabilidade e smoke tests.

## INV-TRAIN-041
O OpenAPI deve declarar GET /api/v1/teams (operationId get_teams_api_v1_teams_get) com security HTTPBearer (ou equivalente) e responses 200/422.
Gate de contrato: Training depende de teams; contrato precisa ser estável e autenticado.

## INV-TRAIN-043
week_start < week_end (estrito).
Microciclo deve representar um intervalo temporal válido para agregações semanais.

## INV-TRAIN-044
training_analytics_cache é único por (team_id, microcycle_id, month, granularity).
Evita duplicidade de cache e garante lookup determinístico para dashboards.

## INV-TRAIN-045
order_index é único por sessão (session_id, order_index) quando deleted_at IS NULL.
Drag-and-drop e ordenação determinística dependem de order_index sem colisões.

## INV-TRAIN-046
Ao inserir wellness_pre/wellness_post, o sistema atualiza wellness_reminders.responded_at quando houver reminder pendente.
Permite métricas de lembretes/resposta e auditoria de engajamento wellness.

## INV-TRAIN-047
Todo exercício DEVE pertencer a um escopo válido: SYSTEM ou ORG.
Exercícios SYSTEM são instalados pela plataforma.
Exercícios ORG são criados por usuários da organização.
Separar exercícios do sistema dos exercícios personalizados pela organização permite catálogo curado + customização sem comprometer integridade.

## INV-TRAIN-048
Usuários da organização NÃO PODEM editar ou excluir exercícios instalados (scope = SYSTEM).
Qualquer tentativa de PATCH/DELETE por usuário não-plataforma DEVE retornar 403.
Protege o catálogo base da plataforma contra alterações acidentais ou indevidas.

## INV-TRAIN-049
Todo exercício criado pela organização (scope = ORG) DEVE estar vinculado a exatamente uma organização válida (organization_id NOT NULL, FK ativa).
Impede exercícios ORG "órfãos" e garante isolamento multi-tenant.

## INV-TRAIN-050
Um usuário só PODE favoritar o mesmo exercício uma vez.
Constraint de unicidade em (user_id, exercise_id).
Favoritos duplicados poluem a lista e geram inconsistência de contagem.

## INV-TRAIN-051
Usuário só PODE ver exercícios SYSTEM + exercícios ORG da própria organização, respeitando visibility_mode e ACL quando aplicável.
Backend é a autoridade de enforcement (não apenas frontend).
Multi-tenant + ACL: impede vazamento cross-org e respeita restrições de compartilhamento.

## INV-TRAIN-052
Todo item de mídia vinculado ao exercício DEVE informar tipo válido (ex.: image, video, youtube_link, external_link) e referência válida (URL ou asset_id).
Evita mídias "vazias" e garante renderização confiável no frontend.

## INV-TRAIN-053
Exercício referenciado por sessão histórica NÃO PODE ser removido de forma a invalidar leitura da sessão (soft-delete preserva referência).
Se houver hard-delete, deve haver regra de tombstone ou fallback.
Sessões históricas são artefatos de auditoria; remover exercícios referenciados degrada dados e compliance.

## INV-TRAIN-EXB-ACL-001
Todo exercício ORG DEVE possuir visibility_mode válido: org_wide ou restricted.
Default para novos exercícios ORG: restricted (apenas criador vê; compartilhar exige ação explícita).
Controla quem visualiza exercícios ORG e abre caminho para ACL granular. Default restricted segue princípio de menor privilégio: apenas criador vê por padrão.

## INV-TRAIN-EXB-ACL-002
ACL por usuário só PODE existir para exercício ORG com visibility_mode = restricted.
Tentativa de adicionar ACL em exercício com visibility_mode = org_wide DEVE ser bloqueada (400/422).
ACL em exercício org_wide é redundante e gera confusão operacional.

## INV-TRAIN-EXB-ACL-003
Usuário incluído na ACL de um exercício DEVE pertencer à mesma organização do exercício.
Backend DEVE validar membership da organização antes de inserir na ACL.
Previne vazamento cross-org de exercícios proprietários.

## INV-TRAIN-EXB-ACL-004
Apenas o treinador criador do exercício ORG PODE alterar visibility_mode e gerenciar ACL.
Outro treinador da mesma org NÃO PODE modificar ACL/visibilidade de exercício alheio (403).
O papel RBAC de "Treinador" é identificador explícito (não inferido de categoria genérica).
Evita que treinadores sobreponham configurações de compartilhamento de colegas. RBAC explícito previne falsos positivos em guards baseados em inferência de papel.

## INV-TRAIN-EXB-ACL-005
O treinador criador DEVE manter acesso ao próprio exercício ORG independentemente da ACL (restritiva ou não).
Não é necessário o criador estar listado explicitamente na ACL.
Impede que o criador perca acesso ao próprio conteúdo por configuração de ACL.

## INV-TRAIN-EXB-ACL-006
Um usuário NÃO PODE aparecer duplicado na ACL do mesmo exercício.
Constraint de unicidade em (exercise_id, user_id).
Duplicidade na ACL gera inconsistência de remoção e riscos de query.

## INV-TRAIN-EXB-ACL-007
Mudanças de ACL/visibility_mode NÃO PODEM invalidar a leitura de sessões históricas que já referenciam o exercício.
O backend DEVE permitir leitura de session_exercises independentemente do ACL/visibility atual do exercício referenciado.
Sessões históricas são imutáveis (INV-TRAIN-005); ACL restritiva posterior não pode degradar auditoria ou leitura de dados consolidados.

## INV-TRAIN-054
Um Microciclo DEVE pertencer a um Mesociclo válido, e um Mesociclo DEVE pertencer a um Macrociclo válido.
Não pode existir micro/meso "solto" (sem parent_cycle_id apontando para ciclo existente do tipo correto).
Reforça a integridade hierárquica do planejamento. Ciclos "soltos" degradam rastreabilidade e analytics de periodização.

## INV-TRAIN-055
Mesociclos da mesma equipe/macrociclo PODEM se sobrepor em datas.
O sistema NÃO deve bloquear sobreposição nem forçar ajuste automático.
Periodização de handebol admite mesociclos simultâneos (ex.: preparatório físico e competitivo técnico-tático). Bloquear sobreposição impediria planejamento real.

## INV-TRAIN-056
As datas (start_date, end_date) do Microciclo DEVEM estar 100% contidas no intervalo do Mesociclo pai.
Microciclo que extrapola é inválido (422).
Garante coerência temporal da hierarquia macro→meso→micro sem deixar semanas "vazando" fora do mesociclo planejado.

## INV-TRAIN-057
Toda sessão DEVE estar vinculada a um Microciclo (via microcycle_id) OU estar marcada explicitamente como avulsa (microcycle_id IS NULL + flag standalone).
Sessão sem vínculo e sem flag é inválida.
Evita sessões "invisíveis" ao planejamento, permitindo ao treinador treinos fora da periodização (amistosos, reforço).

## INV-TRAIN-058
O treinador PODE adicionar/remover/reordenar exercícios enquanto a sessão NÃO estiver encerrada (status != readonly).
Após encerrar, a estrutura de exercícios é histórica e NÃO pode ser alterada.
NOTA: Este é o princípio geral. INV-TRAIN-004 (janela por papel) e INV-TRAIN-029 (regras por status) são refinamentos que operam DENTRO deste princípio.
Permite ajustes de última hora no treino (realidade operacional) sem degradar o histórico consolidado.

## INV-TRAIN-059
Dentro de uma sessão, a ordem dos exercícios (order_index) DEVE ser:
- Única por sessão (sem duplicidade),
- Contígua (1..N sem gaps),
- Determinística.
Reorder DEVE normalizar gaps.
Ordem determinística garante reprodutibilidade do treino e UX consistente no drag-and-drop.

## INV-TRAIN-060
Ao criar exercício de scope ORG, o default de visibility_mode DEVE ser "restricted" (apenas o treinador criador vê).
Compartilhar com outros treinadores exige ação explícita do criador (ACL ou mudança para org_wide).
Princípio de menor privilégio. Evita exposição acidental de exercícios proprietários do treinador.

## INV-TRAIN-061
Exercícios SYSTEM NÃO podem ser editados por usuários de org. Ao "adaptar", o sistema DEVE criar uma cópia ORG (via copy-to-org) e o treinador edita a cópia.
O exercício SYSTEM original permanece inalterado.
Preserva o catálogo global. Adaptações locais são cópias ORG rastreáveis.

## INV-TRAIN-062
Um exercício só PODE ser adicionado a uma sessão se for visível ao treinador naquele momento: SYSTEM (global), ORG criado por ele, ou ORG compartilhado via ACL com ele.
Exercício ORG restricted sem ACL para o treinador → 403.
Impede que treinador B monte sessão com exercício privado do treinador A.

## INV-TRAIN-063
O atleta PODE pré-confirmar presença no app (status = preconfirmed), mas isso NÃO constitui presença oficial.
A presença oficial só é consolidada pelo treinador no encerramento da sessão (INV-TRAIN-064).
Dá ao atleta engajamento antecipado sem retirar do treinador a autoridade sobre presença oficial.

## INV-TRAIN-064
O sistema só PODE consolidar presença oficial (presente/ausente/justificado) no momento do encerramento da sessão pelo treinador.
Antes do encerramento, registros de presença são provisórios/rascunho.
Evita que presença parcial antes do treino vire dado oficial sem validação humana.

## INV-TRAIN-065
Se no encerramento houver atleta não elegível ou dado não resolvido, o sistema DEVE permitir encerrar.
Itens inconsistentes NÃO viram oficiais; viram "pendências" com motivo, rastreáveis em fila separada (INV-TRAIN-066).
Prioriza o encerramento do treino (realidade operacional) sobre perfeição de dados. Pendências são tratadas posteriormente sem bloquear o fluxo.

## INV-TRAIN-066
Pendências geradas no encerramento (presença inválida, atleta não resolvido etc.) DEVEM ir para fila/tela separada "Pendências do Treino".
A sessão encerrada NÃO é alterada; pendências são entidades próprias vinculadas à sessão.
Separar pendências da sessão concluída preserva integridade do histórico e dá ao treinador UX dedicada para resolução assíncrona.

## INV-TRAIN-067
O atleta PODE ajudar a resolver pendências (ex.: confirmar identidade), mas NÃO PODE transformar pendência em dado oficial sozinho.
A validação final de qualquer pendência é exclusiva do treinador.
Engaja o atleta sem delegar autoridade de validação oficial.

## INV-TRAIN-068
O atleta DEVE conseguir ver, antes do treino: horário, lista de exercícios e objetivo da sessão (quando existir), sem depender de preencher formulários.
Esta é informação read-only na perspectiva do atleta.
Permite ao atleta se preparar mentalmente e logisticamente para o treino.

## INV-TRAIN-069
Se um exercício está no treino do atleta, o atleta DEVE poder ver as mídias/instruções do exercício, independente da visibility_mode do exercício (SYSTEM ou ORG).
A visibilidade por mídia segue a sessão, não o exercício.
Atleta precisa das instruções/vídeos para executar corretamente, independente de quem criou o exercício.

## INV-TRAIN-070
O pós-treino do atleta (RPE, dificuldade, dores, feedback) DEVE poder ser registrado de forma conversacional (texto/voz), sem exigir formulário rígido como pré-requisito.
Campos de formulário, se existirem, DEVEM ser opcionais.
Reduz atrito para o atleta e aumenta taxa de resposta pós-treino. Formulário rígido é barreira para adolescentes.

## INV-TRAIN-071
Se o atleta NÃO cumprir a política de wellness obrigatória (INV-TRAIN-076), o sistema DEVE:
- Permitir ver o mínimo operacional (horário do treino, local).
- Bloquear conteúdo completo (exercícios, vídeos, instruções e detalhes).
O bloqueio de conteúdo é consequência da política, não regra independente.
Incentivo positivo: compliance com wellness desbloqueia valor (conteúdo). Atleta nunca fica "no escuro" sobre horário/local.

## INV-TRAIN-072
A IA PODE enviar mensagens automáticas ao atleta, mas SEMPRE como sugestão/apoio (tom não-imperativo) e NÃO PODE criar/publicar treino oficial automaticamente.
Toda geração de treino pela IA passa por "editar antes" do treinador (INV-TRAIN-075, INV-TRAIN-080).
O treinador humano é a autoridade. IA é ferramenta de apoio, não tomador de decisão.

## INV-TRAIN-073
O treinador NÃO PODE ver conteúdo íntimo das conversas do atleta com a IA.
O treinador só recebe alertas/resumos de risco (safety), sem expor texto íntimo.
O atleta é dono do conteúdo da conversa.
Confiança atleta ↔ IA depende de privacidade. Treinador recebe informação acionável sem violação de intimidade.

## INV-TRAIN-074
A IA PODE explicar regras e situações de jogo (2 minutos, superioridade numérica, 7m, princípios táticos) mesmo que o treino do dia não cite o tema.
Conteúdo educativo NÃO altera treino/agendamento; é informativo.
Atleta tem curiosidade além do treino do dia. Conteúdo educativo aumenta literacia tática sem interferir no planejamento.

## INV-TRAIN-075
Se o atleta pedir "treino extra", a IA PODE gerar um rascunho, mas o rascunho DEVE chegar ao treinador como "editar antes de aprovar".
O sistema NÃO PODE publicar/agendar automaticamente. Publicação só após ação explícita do treinador.
Mantém o treinador humano como gatekeeper de tudo que vira treino oficial. Evita risco de IA sugerir treino inadequado.

## INV-TRAIN-076
Para o atleta acessar conteúdo completo do treino (exercícios, vídeos, instruções e detalhes), o sistema DEVE exigir:
1) wellness pré DO DIA; e
2) wellness pós DO ÚLTIMO TREINO realizado (quando existir).
Se algum estiver faltando, o atleta vê apenas mínimo operacional (horário, local), sem conteúdo completo.
"Último treino realizado" = último treino encerrado/concluído do atleta/equipe.
Incentiva compliance contínua do atleta com wellness, criando ciclo virtuoso: preencher wellness → desbloquear conteúdo → preparar-se melhor → desempenho.

## INV-TRAIN-077
Quando o atleta concluir o pós-treino conversacional, o sistema DEVE gerar e entregar feedback curto do treinador virtual contendo:
1) 1 reconhecimento (esforço/consistência), e
2) 1 orientação prática (técnica/tática/recuperação) aplicável ao próximo treino.
Se o atleta NÃO concluir o pós-treino, o sistema NÃO gera feedback.
Recompensa imediata por completar pós-treino. Orientação prática conecta feedback a ação futura.

## INV-TRAIN-078
O atleta só PODE visualizar a aba/visão de progresso pessoal (histórico e comparativos de evolução) quando estiver em conformidade com a política de check-ins obrigatórios (INV-TRAIN-076).
Se não estiver em conformidade, vê apenas visão básica do dia.
Reforça incentivo de compliance: progressão pessoal é desbloqueada por participação contínua.

## INV-TRAIN-079
Qualquer reconhecimento/feedback gerado para valorizar o atleta (consistência, participação) DEVE ser individual e NÃO PODE expor conteúdo íntimo de conversa do atleta para terceiros.
O treinador recebe apenas resumos/alertas conforme INV-TRAIN-073.
Proteção de dados sensíveis. Reconhecimento público usa apenas métricas agregadas (taxa de resposta, frequência), não conteúdo de conversa.

## INV-TRAIN-080
A IA PODE ajudar o treinador sugerindo exercícios, montando sessões e propondo planejamento (microciclo/agenda), mas toda proposta DEVE ser criada como rascunho ("editar antes").
O sistema NÃO pode publicar/agendar automaticamente. Publicação/agendamento ocorre APENAS após ação explícita do treinador.
(Generaliza INV-TRAIN-075 para o contexto do treinador.)
O treinador DEVE revisar toda proposta antes de publicar. IA é copiloto, não autopiloto.

## INV-TRAIN-081
Toda sugestão da IA para o treinador (exercício/sessão/planejamento) DEVE incluir justificativa mínima (curta e objetiva) baseada em sinais do sistema (wellness, carga recente, consistência, objetivo do microciclo, dados de jogo/scout).
Sugestões sem justificativa NÃO PODEM ser apresentadas como recomendação (apenas como "ideia genérica" com label distinto).
Justificativa rastreável permite ao treinador avaliar qualidade da sugestão e cria feedback loop para melhoria do modelo de IA.
---

## Invariantes — decisões arquiteturais Fase 1 (adicionadas 2026-03-16)

> **Materializadas a partir de ARCH_DECISIONS_TRAINING.md (DSS). Data: 2026-03-16.**
> Estes INV-IDs são sequência contínua após INV-TRAIN-083.

## INV-TRAIN-084
Toda `training_session` deve possuir pelo menos um `SessionObjective` com `deletedAt IS NULL` antes de transitar de `DRAFT`.
Sessão sem objetivo operacional não tem propósito verificável e não pode ser publicada (TRAIN-DEC-004, DR-TRAIN-011).

## INV-TRAIN-085
Todo `SessionObjective` deve declarar `origin` como um dos valores canônicos: `NEED_DETECTED`, `COMPETITIVE_FOCUS`, `DEVELOPMENT_GOAL`, `MANUAL_COACH_RATIONALE`.
Quando `origin = MANUAL_COACH_RATIONALE`, o campo `originNotes` é obrigatório (mínimo 10 caracteres).
Objetivo sem origem é dado incompleto — rejeitar. TRAIN-DEC-005, DR-TRAIN-012, DR-TRAIN-013.

## INV-TRAIN-086
Sessão só pode transitar de `DRAFT` para `PUBLISHED` ou `SCHEDULED` se satisfizer TODOS os seguintes:
1. Pelo menos um `SessionObjective` ativo
2. `sessionAt` definido
3. Pelo menos um `SessionBlock`
4. `coach_assignment` definido
5. `team_scope` e/ou `athlete_scope` definidos
TRAIN-DEC-006, DR-TRAIN-014.

## INV-TRAIN-087
Toda `ExecutionRecord` deve referenciar `sessionId` (obrigatório).
Opcionalmente pode referenciar `blockId` e/ou `prescriptionLineId`.
`ExecutionRecord` sem contexto de sessão é inválido. TRAIN-DEC-007, DR-TRAIN-015.

## INV-TRAIN-088
Campos `plannedContent` e `actualContent` de `ExecutionRecord` são imutáveis após criação.
`plannedContent` nunca é sobrescrito por `actualContent`.
O sistema não pode aceitar PATCH que modifique `plannedContent` em record existente.
TRAIN-DEC-008, DR-TRAIN-017.

## INV-TRAIN-089
`ExecutionRecord` com `executionType` em `[LIVE_ADJUSTMENT, CONSTRAINT_OVERRIDE]` exige:
- `adjustmentReasonType` preenchido (valor do conjunto canônico `live_adjustment_reason_type`)
- `coachRationale` preenchido (mínimo 5 caracteres)
`ExecutionRecord` com `executionType` em `[ALTERNATE_EXERCISE, LOAD_RECALCULATION]` exige `adjustmentReasonType`.
TRAIN-DEC-009, DR-TRAIN-018, DR-TRAIN-019.

## INV-TRAIN-090
Todo `FeedbackThread` deve ter `contextType` e `contextRefId` preenchidos.
Feedback sem contexto operacional identificado é rejeitado (400).
TRAIN-DEC-010, DR-TRAIN-020.

## INV-TRAIN-091
Todo `FeedbackThread` deve ter `conversationOutcome` preenchido com valor do conjunto canônico.
Conversa sem consequência operacional é rejeitada.
`FOLLOWUP_SCHEDULED` exige `followUpAt`. `COMMITMENT_MADE` exige `commitmentText`. `DECISION_RECORDED` exige `decisionText`.
TRAIN-DEC-015, DR-TRAIN-021, DR-TRAIN-022.

## INV-TRAIN-092
Atleta com `restriction_profile` ativo de nível crítico ou `return_to_play_guard` ativo não pode receber prescrição executável sem override explícito auditado.
Override deve ser registrado via módulo `audit` com `createdByUserId` de usuário com permissão de `OVERRIDE_RESTRICTION`.
TRAIN-DEC-012, DR-TRAIN-025.

## INV-TRAIN-093
Campos derivados (`readiness_score`, `dropout_risk_signal`, `engagement_signal`) são view-only.
Não podem ser persistidos como fonte primária de verdade.
A fonte primária é sempre o dado coletado original.
TRAIN-DEC-014, DR-TRAIN-028.

## INV-TRAIN-094
Todo `AttentionQueueItem` deve ter: `severity` (valores canônicos: LOW, MEDIUM, HIGH, CRITICAL), `reasonCode` (valores canônicos de `attention_queue_reason_code`), `targetEntityType` e `targetEntityId`.
Item sem qualquer desses campos é rejeitado.
TRAIN-DEC-027, DR-TRAIN-038.

## INV-TRAIN-095
O módulo `training` não pode entregar notificação diretamente ao atleta ou treinador.
Deve emitir `notification_intent` para o módulo `notifications`.
TRAIN-DEC-022, DR-TRAIN-040.

## INV-TRAIN-096
O módulo `training` deve registrar fatos auditáveis enviando eventos ao módulo `audit`.
Operações: create/update/publish/start/complete/cancel em `training_sessions`, `execution_records`, `constraint_overrides`.
Não pode manter trilha de auditoria informal interna ao módulo.
TRAIN-DEC-023, DR-TRAIN-041.

## INV-TRAIN-097
O módulo `training` consome dados de `medical` (`restriction_profile`, `return_to_play_guard`) como somente leitura.
Nenhum endpoint de `training` pode criar, editar ou deletar entidades soberanas do módulo `medical`.
TRAIN-DEC-024, DR-TRAIN-042.

## INV-TRAIN-098
O módulo `training` consome a policy de autorização do módulo `identity_access`.
Não redefine permissões. Guards de transição de estado e acesso a dados devem consultar policy de `identity_access`.
TRAIN-DEC-025, DR-TRAIN-043.

## INV-TRAIN-099
O módulo `training` referencia exclusivamente `exercise_id + exercise_version_id` do módulo `exercises`.
Nunca embute propriedades do `Exercise` diretamente em entidades de `training`.
Sessão histórica preserva `exercise_version_id` imutavelmente — alteração de `ExerciseVersion` posterior não afeta registro histórico.
TRAIN-DEC-047, TRAIN-DEC-048, DR-TRAIN-045.

## INV-TRAIN-100
**Freshness SLA para sinais derivados (M3).**
Campos derivados (`readiness_score`, `dropout_risk_signal`, `engagement_signal`, `training_analytics_cache`) têm SLA de atualização máxima de 2 horas.
Sinais com `calculated_at < NOW_UTC - 2h` devem ser marcados como stale (flag `is_stale: true`) e o cliente notificado.
Após marcação como stale, o próximo acesso via API deve acionar recálculo assíncrono (Celery) com prioridade normal.
SLA de 2h não se aplica durante `IN_PROGRESS` de sessão — nesse caso o sinal é atualizado em tempo real (event-driven).
Trigger `tr_invalidate_analytics_cache` (INV-TRAIN-020) é o mecanismo de invalidação imediata; este INV define o SLA máximo de tolerância a staleness.
Fonte: TRAIN-DEC-014, DR-TRAIN-028, INV-TRAIN-093.

## INV-TRAIN-101
**Soft-delete scope policy (M1).**
Todas as entidades SSOT do módulo `training` têm soft-delete obrigatório com campos `deleted_at` e `deleted_reason` em par indissociável (INV-TRAIN-008).
Escopo de aplicação:
- `training_sessions`: soft-delete ✅ (confirmed)
- `session_blocks`: soft-delete obrigatório — `order_index` deve ser recalculado após soft-delete (INV-TRAIN-045, INV-TRAIN-059)
- `execution_records`: soft-delete obrigatório — registros de execução são auditáveis; exclusão física é proibida (DR-TRAIN-026)
- `session_objectives`, `feedback_threads`: soft-delete obrigatório
- `wellness_pre`, `wellness_post`: soft-delete obrigatório (unicidade soft-delete aware — INV-TRAIN-009, INV-TRAIN-010)
Entidades de lookup (enums, tipos) são imutáveis e não têm soft-delete.
Hard-delete é proibido para qualquer entidade listada acima. Tentativa retorna 422.

