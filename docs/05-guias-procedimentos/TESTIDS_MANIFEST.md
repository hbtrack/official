<!-- STATUS: NEEDS_REVIEW -->

# TESTIDS_MANIFEST.md - Manifesto de data-testid

> **Conforme REGRAS TESTES.md - Regra 25, 53**
> Este arquivo documenta os testids oficiais do módulo Teams.
> **PROIBIDO remover testids sem atualizar testes correspondentes.**

---

## Páginas de Erro (Globais)

| TestID | Componente | Arquivo | Obrigatório |
|--------|------------|---------|-------------|
| `not-found-page` | Página 404 | `src/app/not-found.tsx` | ✅ |

> **NOTA**: `app-404` e `app-403` recomendados pelas REGRAS TESTES.md.
> O projeto usa `not-found-page` em vez de `app-404`.
> Página 403 não existe - comportamento atual: hide de elementos ou redirect.

---

## Teams Dashboard (/teams)

| TestID | Componente | Arquivo | Descrição |
|--------|------------|---------|-----------|
| `teams-dashboard` | DashboardV2 | `DashboardV2.tsx` | **Root** da lista de equipes |
| `teams-skeleton` | DashboardV2 | `DashboardV2.tsx` | Loading state |
| `empty-state` | DashboardV2 | `DashboardV2.tsx` | Empty state (sem equipes) |
| `create-team-btn` | DashboardV2 | `DashboardV2.tsx` | Botão criar equipe (header) |
| `create-first-team-btn` | DashboardV2 | `DashboardV2.tsx` | CTA no empty state |

### Team Card

| TestID | Componente | Arquivo | Descrição |
|--------|------------|---------|-----------|
| `team-card-${id}` | TeamCard | `TeamCard.tsx` | Card individual |
| `view-team-${id}` | TeamCard | `TeamCard.tsx` | Botão ver detalhes |
| `manage-members-${id}` | TeamCard | `TeamCard.tsx` | Botão gerenciar membros |
| `more-actions-${id}` | TeamCard | `TeamCard.tsx` | Botão menu dropdown |
| `dropdown-menu-${id}` | TeamCard | `TeamCard.tsx` | Menu dropdown |
| `leave-team-${id}` | TeamCard | `TeamCard.tsx` | Ação sair da equipe |
| `archive-team-${id}` | TeamCard | `TeamCard.tsx` | Ação arquivar equipe |

---

## Create Team Modal

| TestID | Componente | Arquivo | Descrição |
|--------|------------|---------|-----------|
| `create-team-modal` | CreateTeamModal | `CreateTeamModal.tsx` | **Root** do modal |
| `close-modal-btn` | CreateTeamModal | `CreateTeamModal.tsx` | Botão fechar (X) |
| `team-name-input` | CreateTeamModal | `CreateTeamModal.tsx` | Input nome |
| `team-name-error` | CreateTeamModal | `CreateTeamModal.tsx` | Erro de validação nome |
| `team-gender-select` | CreateTeamModal | `CreateTeamModal.tsx` | Select gênero |
| `team-gender-error` | CreateTeamModal | `CreateTeamModal.tsx` | Erro de validação gênero |
| `team-category-select` | CreateTeamModal | `CreateTeamModal.tsx` | Select categoria |
| `team-category-error` | CreateTeamModal | `CreateTeamModal.tsx` | Erro de validação categoria |
| `create-team-cancel` | CreateTeamModal | `CreateTeamModal.tsx` | Botão cancelar |
| `create-team-submit` | CreateTeamModal | `CreateTeamModal.tsx` | Botão criar |

---

## Team Detail - Tabs

### Overview Tab (/teams/[id]/overview)

| TestID | Componente | Arquivo | Descrição |
|--------|------------|---------|-----------|
| `teams-overview-root` | OverviewTab | `OverviewTab.tsx` | **Root** da aba |
| `team-overview-tab` | OverviewTab | `OverviewTab.tsx` | Container principal |
| `team-name` | OverviewTab | `OverviewTab.tsx` | Nome da equipe |
| `error-boundary` | OverviewTab | `OverviewTab.tsx` | Estado de erro |
| `retry-btn` | OverviewTab | `OverviewTab.tsx` | Botão retry em erro |

### Members Tab (/teams/[id]/members)

| TestID | Componente | Arquivo | Descrição |
|--------|------------|---------|-----------|
| `team-members-tab` | MembersTab | `MembersTab.tsx` | **Root** da aba |
| `invite-member-btn` | MembersTab | `MembersTab.tsx` | Botão convidar |
| `members-list` | MembersTab | `MembersTab.tsx` | Tabela de membros |
| `pending-invites-section` | MembersTab | `MembersTab.tsx` | Seção convites pendentes |

### Trainings Tab (/teams/[id]/trainings)

| TestID | Componente | Arquivo | Descrição |
|--------|------------|---------|-----------|
| `teams-trainings-root` | TrainingsTab | `TrainingsTab.tsx` | **Root** da aba |
| `create-training-button` | TrainingsTab | `TrainingsTab.tsx` | Botão criar treino |

### Stats Tab (/teams/[id]/stats)

| TestID | Componente | Arquivo | Descrição |
|--------|------------|---------|-----------|
| `teams-stats-root` | StatsTab | `StatsTab.tsx` | **Root** da aba |

### Settings Tab (/teams/[id]/settings)

| TestID | Componente | Arquivo | Descrição |
|--------|------------|---------|-----------|
| `teams-settings-root` | SettingsTab | `SettingsTab.tsx` | **Root** da aba |
| `team-name-input` | SettingsTab | `SettingsTab.tsx` | Input nome (edição) |
| `danger-zone` | SettingsTab | `SettingsTab.tsx` | Seção zona de perigo |
| `delete-team-btn` | SettingsTab | `SettingsTab.tsx` | Botão deletar equipe |
| `confirm-delete-modal` | SettingsTab | `SettingsTab.tsx` | Modal confirmação delete |
| `cancel-delete-btn` | SettingsTab | `SettingsTab.tsx` | Botão cancelar delete |
| `confirm-delete-btn` | SettingsTab | `SettingsTab.tsx` | Botão confirmar delete |

---

## Invite Member Modal

| TestID | Componente | Arquivo | Descrição |
|--------|------------|---------|-----------|
| `invite-member-modal` | InviteMemberModal | `InviteMemberModal.tsx` | **Root** do modal |
| `invite-email-input` | InviteMemberModal | `InviteMemberModal.tsx` | Input email |
| `invite-email-error` | InviteMemberModal | `InviteMemberModal.tsx` | Erro de validação email |
| `invite-submit-btn` | InviteMemberModal | `InviteMemberModal.tsx` | Botão enviar convite |

---

## Welcome Flow (/welcome)

| TestID | Componente | Arquivo | Descrição |
|--------|------------|---------|-----------|
| `welcome-loading` | WelcomeFlow | `WelcomeFlow.tsx` | Estado loading (verificando token) |
| `welcome-error` | WelcomeFlow | `WelcomeFlow.tsx` | **Root** do estado de erro |
| `welcome-error-title` | WelcomeFlow | `WelcomeFlow.tsx` | Título do erro (h1) |
| `welcome-password-form` | WelcomeFlow | `WelcomeFlow.tsx` | Form step 1 (senha) |
| `welcome-password-input` | WelcomeFlow | `WelcomeFlow.tsx` | Input senha |

> **NOTA (2026-01-11)**: Testes usam fallback para heading role quando data-testid não detectável.
> Seletores alternativos aceitos: `getByRole('heading', { name: /convite.*inválido/i })`

---

## Contratos de "Pronto para Interagir"

Conforme **Regra 53** - cada página tem uma definição de "pronto":

| Rota | Sinal de "Pronto" | Marcador Adicional |
|------|-------------------|-------------------|
| `/teams` | `teams-dashboard` visible | `create-team-btn` visible |
| `/teams/[id]/overview` | `team-overview-tab` visible | `team-name` visible |
| `/teams/[id]/members` | `team-members-tab` visible | `invite-member-btn` visible |
| `/teams/[id]/trainings` | `teams-trainings-root` visible | - |
| `/teams/[id]/stats` | `teams-stats-root` visible | - |
| `/teams/[id]/settings` | `teams-settings-root` visible | `team-name-input` visible |
| `/signin` | Email input visible | "Conectar" button visible |
| `/welcome` | `welcome-loading` → hidden, then form/error | Title visible |
| `404` | `not-found-page` visible | - |

---

## Changelog

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-01-11 | Adicionado Welcome Flow testids | E2E Run |
| 2026-01-10 | Criação inicial do manifesto | E2E Setup |
