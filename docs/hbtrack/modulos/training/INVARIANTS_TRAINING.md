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
| INV-TRAIN-001 | A soma dos percentuais de foco (7 campos `focus_*_pct`) deve ser ≤ 120. Valores individuais, quando presentes, devem estar em [0..100]. | `TrainingSession` | Regra de produto | Teste unitário de validação de payload; query de auditoria para detectar violações históricas |
| INV-TRAIN-002 | Submissão/edição de `wellness_pre` é bloqueada quando NOW ≥ `session_at` - 2h | `WellnessPre` | Regra de produto | Teste de tentativa de edição tardia; validação temporal no endpoint |
| INV-TRAIN-003 | Edição de `wellness_post` é bloqueada quando NOW ≥ `created_at` + 24h (limite não-inclusivo) | `WellnessPost` | Regra de produto | Teste de tentativa de edição após janela; validação temporal no endpoint |
| INV-TRAIN-004 | Janela de edição depende de papel e estado: Autor (treinador) pode editar sessão "scheduled" até 10 min antes de `session_at` (não-inclusivo). Superior (coordenador/dirigente) pode editar "pending_review" até 24h após `ended_at` (não-inclusivo). | `TrainingSession` | Regra de produto + RBAC | Teste de autorização temporal por papel; tentativa de edição fora da janela |
| INV-TRAIN-005 | Sessões com `session_at` mais antigas que 60 dias são somente leitura; qualquer tentativa de edição é bloqueada | `TrainingSession` | Regra de produto | Teste de tentativa de edição de sessão histórica; flag `readonly` computado dinamicamente |
| INV-TRAIN-006 | Status permitido em `training_sessions`: `draft`, `scheduled`, `in_progress`, `pending_review`, `readonly` | `TrainingSession` | Regra de produto + DOMAIN_AXIOMS | Validação de enum no schema; teste de tentativa de estado inválido |

## Regras de uso
1. Nenhum endpoint pode violar invariantes.
2. Nenhuma automação assíncrona pode violar invariantes.
3. Nenhuma UI pode assumir transição que quebre invariantes.
4. Toda violação deve bloquear merge ou exigir exceção formal.

## Relação com outros documentos
- `DOMAIN_RULES_TRAINING.md`
- `TEST_MATRIX_TRAINING.md`

## Nota sobre workflow de estados
O workflow alvo canônico de `TrainingSession` definido em `.contract_driven/DOMAIN_AXIOMS.json` é:

**"DRAFT" → "PLANNED" → "SCHEDULED" → "IN_PROGRESS" → "COMPLETED" → "CANCELLED"**

Porém, INV-TRAIN-006 registra os estados operacionais atuais implementados: `draft`, `scheduled`, `in_progress`, `pending_review`, `readonly`.

**Esta divergência está documentada em `CONTRACT_TRAINING.md` §16 (LAC-001)** e deve ser reconciliada em decisão arquitetural futura.
          
Controla o ciclo operacional do treino e determina permissões de edição e fechamento.

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
Nome do template é único por organização.
Evita ambiguidade na seleção e reutilização de templates.

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