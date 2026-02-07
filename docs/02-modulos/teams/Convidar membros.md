<!-- STATUS: NEEDS_REVIEW -->

Sprint 1 — Convite + pendente na lista (MVP funcional)

Objetivo: convidar por email, aparecer como pendente, reenviar/cancelar.

Banco de Dados

 Garantir users.email case-insensitive (citext ou lowercase + unique index)

 Confirmar team_memberships.status suporta pendente|ativo (já suporta)

 (Se necessário) adicionar season_id em team_memberships para amarrar convite ao contexto atual

 Índices:

 team_memberships(team_id, status)

 team_memberships(person_id, team_id) (+ season_id se existir)

 password_resets(user_id, token_type, used, expires_at)

Backend

 POST /teams/{team_id}/invites

 aplicar matriz de permissões (dirigente/coordenador/treinador/super admin)

 checar convite existente:

 team_membership pendente no mesmo contexto OU

 password_resets welcome ativo (used=false e expires_at>now)

 criar/reutilizar user + person mínimo

 criar/reutilizar org_membership

 criar team_membership com status='pendente'

 criar password_resets com token_type='welcome' e expires_at=48h

 enviar email via Resend

 POST /teams/{team_id}/invites/{person_id}/resend

 só se token ainda válido (48h)

 DELETE /teams/{team_id}/invites/{person_id}

 invalidar token welcome

 remover/soft-delete membership pendente

Frontend

 Modal “Convidar Membro” (email + papel + msg opcional)

 Tela “Membros”:

 seção “Pendentes” (status pendente)

 ações: reenviar (habilitado só se token válido), cancelar

 Empty state + CTA “Convidar”

 Bloquear UI de convite para papéis sem permissão (mas backend manda)

UX/UI

 Estados de loading / success / error

 Mensagem “já existe convite pendente”

 Confirmação de cancelamento

Critérios de aceite

 Após enviar convite, aparece pendente sem refresh

 Reenviar funciona até 48h

 Cancelar remove da lista e invalida token

 Atleta/membro não conseguem convidar (403 no backend)

Sprint 2 — Primeiro acesso + finalizar cadastro (welcome flow completo)

Objetivo: convidado define senha, completa perfil, vira “ativo”.

Backend

 GET /auth/welcome/verify?token=...

 valida token (welcome, not used, not expired)

 retorna role e invitee_kind (derivado do role)

 POST /auth/welcome/complete

 valida token

 seta senha do usuário

 atualiza persons com dados do formulário

 se role=athlete: cria/atualiza athletes + vínculo equipe/temporada

 seta team_membership.status='ativo'

 marca token como used=true

 retorna sessão/login

Frontend

 Rota /welcome?token=...

 Step 1: criar senha

 Step 2: finalizar cadastro (form dinâmico por papel)

 ao sucesso: redirect para equipe e lista atualiza (pendente sai)

UX/UI

 Tela de erro para token expirado/cancelado/já usado

 Requisitos de senha visíveis

 Stepper claro (Senha → Cadastro)

Critérios de aceite

 Token válido leva ao fluxo completo

 Ao concluir, usuário entra logado e vira membro ativo

 Token não pode ser reutilizado

Sprint 3 — Robustez + auditoria + produto mais “profissional”

Objetivo: estabilidade, métricas, governança.

Banco de Dados

 (Opcional) tabela invitations para auditoria rica (mensagem, quem convidou, status)

 (Se não criar invitations) garantir logs em audit_logs

Backend

 Rate limit para invites e resend

 Padronizar erros: INVITE_EXISTS, INVITE_EXPIRED, INVITE_REVOKED, FORBIDDEN

 Tornar idempotente: reenviar não cria novo token se ainda válido

 Cobrir edge cases:

 email já existe e já é membro ativo → bloquear convite

 convite para outro team/season → permitido (se regra permitir)

 Testes completos (API + E2E)

Frontend

 Exibir “expira em Xh” e desabilitar reenviar automaticamente

 Busca/filtro em membros (ativos/pendentes)

 Página opcional “Convites pendentes” (por equipe/org)

UX/UI

 Copy refinada para cada papel

 Tooltips de permissões por papel

 Estados vazios consistentes e toasts padronizados

Critérios de aceite

 Fluxo resistente a duplicidade, clique duplo e race conditions

 Convites auditáveis e rastreáveis

 Zero acesso indevido (RBAC validado)

Ordem ideal de execução (para não quebrar o sistema)

Sprint 1 (convite + pendente)

Sprint 2 (welcome + finalizar cadastro)

Sprint 3 (hardening)

Se você já tem password_resets funcionando com email, dá para implementar Sprint 1 e 2 reaproveitando esse mecanismo quase inteiro, só adicionando a criação do team_membership pendente e a promoção para ativo no complete.


Checklist de E2E mínimos (Playwright):

 Permissão de convidar

 dirigente/coordenador/treinador veem o botão “Convidar”

 atleta/membro não veem e, se tentar pela URL/API, recebe 403

 Criar convite

 envia convite e aparece em “Pendentes” sem refresh

 tentar convidar o mesmo email de novo bloqueia (“já convidado”)

 Reenviar

 reenviar funciona enquanto token válido

 token expirado desabilita “Reenviar” (ou retorna erro esperado)

 Cancelar

 cancelar remove da lista e impede uso do token

 Welcome flow

 abrir /welcome?token=... válido

 setar senha + completar cadastro

 após concluir: membro vira Ativo e some de “Pendentes”

 RBAC do membro

 logado como membro: consegue ver agenda da equipe

 não consegue acessar rotas proibidas (treinos/jogos/admin etc.) → 403/redirect conforme regra



