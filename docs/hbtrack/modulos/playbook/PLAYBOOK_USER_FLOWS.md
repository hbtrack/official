# PLAYBOOK_USER_FLOWS.md — Fluxos de Usuário (Playbook Animado) — v0.1

Status: DRAFT (Contract-Driven)
Escopo v1: quadra + ícones + setas (sem mídia, sem IA)
Owner model: TEAM-owner + Copy-on-share (Deep copy)

## 0) Convenções (canônicas)

- Quadra: 40m x 20m (render em escala pela UI).
- Coordenadas persistidas: x_norm/y_norm ∈ [0..1] (inclusive).
- Slots pt-BR (persistidos como enum): GOL, PE, PD, LE, LD, AC, PIV.
- Jogada aérea: support_state = CHAO | AEREO (apenas PLAYER).
- Publicação: is_published=true torna a jogada “estudável” pelo time (conforme visibility_mode).
- visibility_mode:
  - TEAM_ONLY: visível para membros do time autorizados.
  - RESTRICTED: visível apenas para creator + ACL (v0.1: ACL mínimo).

## 1) Personas e Objetivos

Treinador (Coach)
- Criar e organizar jogadas do time.
- Publicar jogadas para estudo.
- Prescrever jogadas em um treino/feedback.
- Copiar jogadas de um time para outro (copy-on-share).

Atleta
- Assistir/estudar jogadas do time.
- Reassistir e entender por frames (player leve).

## 2) Flow PLB-01 — Treinador cria um Playbook

Precondições
- Usuário é membro do time (team_id) com capability playbook.create.

Passos
1. Treinador acessa “Playbook do Time”.
2. Clica “Novo Playbook”.
3. Preenche:
   - title
   - category (ATAQUE/DEFESA/…)
   - visibility_mode (TEAM_ONLY ou RESTRICTED)
4. Salva.

BE
- POST /playbooks

Saída
- Playbook criado (PlaybookDTO).

Erros
- 403: sem permissão no team_id.
- 422: validação (title vazio, enum inválido).

## 3) Flow PLB-02 — Treinador cria uma Jogada (Play)

Precondições
- Playbook existe e pertence ao mesmo team_id.
- Usuário tem permissão de criação no time.

Passos
1. Dentro do Playbook, clica “Nova Jogada”.
2. Informa:
   - title
   - description (opcional)
3. Salva.

BE
- POST /plays

Saída
- Play criado com version=1 e is_published=false.

Erros
- 403: sem permissão.
- 422: validação.

## 4) Flow PLB-03 — Treinador edita Frames (Keyframes)

Objetivo
- Criar timeline de frames com duration e nota.

Precondições
- Play existe.
- Usuário tem permissão de edição (edit_own ou edit_any_team).

Passos
1. No Editor, vê timeline vazia.
2. Clica “Adicionar Frame”.
3. Define:
   - duration_ms
   - coach_note (opcional)
4. Repete para criar sequência (order_index começa em 0).

BE
- POST /plays/{play_id}/frames
- PATCH /frames/{frame_id} (se ajustar order/duração)

Regras
- order_index é único por play.
- order_index >= 0.

Erros
- 422: FrameOrderInvalid (duplicado, negativo).
- 403: sem permissão.

## 5) Flow PLB-04 — Treinador posiciona Ícones (Slots + Bola) por Frame

Objetivo
- Em cada frame, definir onde cada slot está e onde está a bola.

Precondições
- Frame existe.
- UI apresenta 7 slots + bola.
- Para cada frame deve existir exatamente 1 BALL.

Passos (por frame)
1. Treinador seleciona um frame na timeline.
2. Arrasta e solta os ícones na quadra (slots e bola).
3. Para jogada aérea:
   - Marca o slot como support_state=AEREO no frame.
4. Define posse:
   - has_ball=true no slot (ou ball_owner_slot_id, conforme contrato implementado).
5. Salva o frame.

BE
- PUT /frames/{frame_id}/states (replace-all determinístico)

Validações BE (v0.1 mínimas)
- Coordenadas dentro [0..1].
- Slots únicos por frame.
- Exatamente 1 BALL por frame.
- Regras de entidade (PLAYER requer slot_id + support_state; BALL não pode ter slot_id/support_state).

Erros (UX deve mostrar claramente)
- 422 CoordinatesOutOfRange
- 422 DuplicateSlotInFrame
- 422 BallStateCardinalityError
- 422 InvalidEntityState
- 422 SixMeterViolation (somente quando com bola e CHAO dentro dos 6m, para não bloquear jogada aérea)

## 6) Flow PLB-05 — Treinador desenha Setas/Simbologia (Annotations)

Objetivo
- Representar deslocamento/passe/drible com line_type canônico.

Precondições
- Frame existe.
- Usuário tem permissão de edição.

Passos (por frame)
1. Treinador seleciona ferramenta (MOVE / PASS / DRIBBLE etc).
2. Escolhe line_type:
   - SOLID (deslocamento)
   - DASHED (passe)
   - ZIGZAG (drible)
3. Desenha:
   - de um slot para outro (from_slot_id → to_slot_id), ou
   - de coordenada para coordenada (from_x/y → to_x/y)
4. Salva.

BE
- PUT /frames/{frame_id}/annotations (replace-all determinístico)

Erros
- 422: coordenadas fora de range
- 403: sem permissão

## 7) Flow PLB-06 — Treinador publica Jogada para o Time

Objetivo
- Tornar o conteúdo disponível no Player (para atletas/membros).

Precondições
- Play está consistente (passa validações).
- Usuário tem permissão publish_team.

Passos
1. Treinador clica “Publicar”.
2. Confirma que a jogada será estudável (TEAM_ONLY ou RESTRICTED conforme playbook).

BE
- POST /plays/{play_id}/publish

Saída
- is_published=true

Erros
- 403: sem permissão
- 409/422: se BE exigir consistência mínima antes de publicar (opcional v0.1)

## 8) Flow PLB-07 — Atleta estuda Jogada (Player read-only)

Precondições
- Atleta é membro do team_id.
- Jogada is_published=true e passa regras de visibility_mode/ACL.

Passos
1. Atleta abre “Jogadas do Time”.
2. Seleciona uma jogada.
3. Player carrega JSON leve (frames/states/annotations).
4. Atleta:
   - play/pause
   - step frame
   - vê coach_note por frame (se existir)

BE
- GET /plays/{play_id}

Regras
- Player nunca oferece edição.
- Em rede instável: payload leve; UI deve fazer preload do play completo.

Erros
- 403/404: sem permissão ou invisível (não vazar existência).

## 9) Flow PLB-08 — Copy-on-share (Treinador copia jogada para outro time)

Objetivo
- Reutilizar jogada em outro time, criando um novo objeto (sem edição cruzada).

Precondições
- Usuário tem permissão no time de origem para copiar (view + copy_to_team).
- Usuário tem permissão no time destino para criar (playbook.create ou play.create conforme desenho).
- Definir destino: target_team_id e opcional target_playbook_id.

Passos
1. No detalhe da jogada, treinador clica “Copiar para outro time”.
2. Escolhe o time destino (target_team_id).
3. (Opcional) escolhe playbook destino.
4. Confirma.

BE
- POST /plays/{play_id}/copy { target_team_id, target_playbook_id?, copy_mode="DEEP_COPY" }

Saída
- Novo play_id no time destino:
  - team_id=target_team_id
  - source_play_id preenchido
  - version=1
  - is_published=false (destino publica manualmente)

Erros
- 403: sem permissão em origem/destino
- 422: input inválido
- 500: erro infra de cópia (transação/constraints)

## 10) Flow PLB-09 — Prescrever jogada no Treino (Attachment)

Objetivo
- Garantir que atleta estude a jogada “do jeito que foi prescrito”, mesmo se o treinador editar depois.

Precondições
- Sessão de treino existe.
- Play existe e é visível ao treinador.
- Treinador tem permissão attach_to_training.

Passos
1. No Treino, treinador clica “Anexar jogada”.
2. Escolhe a jogada.
3. Confirma anexar a versão atual.

BE
- POST /training-sessions/{session_id}/attachments/plays
  body: { play_id, play_version }

Saída
- attachment_id criado e estável (imutável).

Notas
- O atleta acessa via “Treino do dia” e vê a jogada anexada (mesmo se não publicada no catálogo, se você permitir esse bypass).

## 11) Flow PLB-10 — Prescrever jogada no Feedback (Attachment)

Objetivo
- Explicar um ajuste tático pós-jogo/treino com animação.

Precondições
- Feedback existe.
- Treinador tem permissão attach_to_feedback.

Passos
1. No Feedback, treinador seleciona “Anexar jogada”.
2. Escolhe a jogada e confirma.

BE
- POST /athlete-feedback/{feedback_id}/attachments/plays
  body: { play_id, play_version }

Saída
- attachment_id criado.

## 12) Fluxos de erro (UX obrigatória)

E-PLB-01 Invariante bloqueia salvar
- Quando BE retorna 422, UI deve:
  - Mostrar erro com rótulo legível (ex.: “Bola duplicada no frame 3”)
  - Indicar no editor qual frame está inválido
  - Não perder o estado local do editor

E-PLB-02 Sem permissão
- UI deve esconder ações (publicar, copiar, editar) se capability não existe.
- Se ainda assim houver 403, mostrar “Sem permissão para esta ação”.

E-PLB-03 Recurso invisível
- GET /plays/{id} deve retornar 404 para quem não tem visibilidade (evitar enumeration).

## 13) Critérios de aceite (v0.1)

- Treinador cria playbook, cria play, cria frames, posiciona slots + bola, cria annotations e publica.
- Atleta consegue estudar (player) com play/pause e frames.
- Copy-on-share cria novo play no time destino e preserva lineage.
- Attachments registram play_id + play_version (estável).
- Nenhum conteúdo requer mídia; payload é JSON leve.