# FRONTEND_REIMPLEMENTATION_BATCH_01

> ⚠️ **ARTEFATO DERIVADO — NON-SOVEREIGN**: batch operacional de reimplementação.
> Não redefine contratos. Em conflito, prevalecem `docs/_canon/FRONTEND_CONTRACT.md`,
> `docs/_canon/UX_BRAND_CONTRACT.md`, `docs/_canon/UX_SHELL_CONTRACT.md`,
> `docs/_canon/AUTH_EXPERIENCE_CONTRACT.md`,
> `docs/_canon/NAVIGATION_VISIBILITY_CONTRACT.md` e os gates ativos.

## Objetivo

Abrir o primeiro batch de reimplementação do frontend para convergir o workspace real ao regime contratual ampliado.

## Entrada obrigatória

- `docs/_canon/FRONTEND_CONTRACT.md` atualizado
- `docs/_canon/UX_BRAND_CONTRACT.md` ativo
- `docs/_canon/UX_SHELL_CONTRACT.md` ativo
- `docs/_canon/AUTH_EXPERIENCE_CONTRACT.md` ativo
- `docs/_canon/NAVIGATION_VISIBILITY_CONTRACT.md` ativo
- `FRONTEND_CONTRACT_GATE` ativo em `validate_contracts.py`

## Pré-requisitos bloqueantes

Antes de reimplementar shell e telas, o workspace precisa expor a superfície mínima do target-state:

1. Auth recovery soberano
   - `contracts/openapi/paths/identity_access.yaml` deve materializar forgot/reset/new-password/confirm-reset
   - `docs/_canon/FEATURE_REGISTRY.yaml` deve rastrear explicitamente o fluxo de recuperação e a superfície visual `Conta e Acesso`
   - `.env.example` deve declarar `FRONTEND_URL`, `RESEND_API_KEY`, `RESEND_FROM_EMAIL` e `RESEND_FROM_NAME` como readiness ativa do target-state

2. Avatar readiness soberana
   - a superfície canônica de perfil deve expor campo de avatar
   - `.env.example` deve declarar baseline Cloudinary do target-state (`CLOUDINARY_URL`, `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_UPLOAD_PRESET`, `CLOUDINARY_ASSET`)

Sem esses pré-requisitos, o batch permanece aberto mas bloqueado para implementação final.

## Escopo executável do batch

1. Branding foundation
   - consumir logos e favicon oficiais a partir de `generated/images`
   - declarar Inter, Manrope e JetBrains Mono
   - declarar famílias de tokens canônicas e tokens semânticos de handebol
   - habilitar dark mode real

2. Shell autenticada do primeiro batch
   - reimplementar sidebar desktop colapsável
   - reimplementar drawer mobile com overlay, fechamento por clique externo, navegação e `Escape`
   - introduzir top bar com breadcrumbs, command palette, notificações, avatar circular, user menu e logout
   - materializar contexto de equipe, troca de equipe e temporada

3. Auth experience
   - reimplementar login com auth logos oficiais e tagline `Dados que decidem jogos`
   - adicionar forgot/reset/new password/confirm reset
   - alinhar o reset para envio transacional real via Resend usando `FRONTEND_URL`
   - preservar redirect pós-login

4. Navigation visibility
   - reorganizar menu pelos agrupamentos oficiais
   - materializar exatamente os módulos ativos do primeiro batch: `Dashboard`, `Teams`, `Seasons`, `Training`, `Users`, `Conta e Acesso`
   - materializar exatamente os módulos visíveis porém desabilitados: `Competitions`, `Matches`, `Scout`, `Video`, `Wellness`, `Medical`, `Exercises`, `Analytics`, `Reports`, `AI Ingestion`, `Audit`
   - materializar exatamente as capabilities ativas da top bar: `Notificações`, `Command palette`, `Breadcrumbs`, `User menu`
   - aplicar role-based visibility, contexto e badges

## Arquivos candidatos iniciais

- `frontend/index.html`
- `frontend/src/App.tsx`
- `frontend/src/index.css`
- `frontend/src/shared/layouts/AppLayout.tsx`
- `frontend/src/features/auth/pages/LoginPage.tsx`

## Fora de escopo deste batch

- refatoração ampla de backend fora da superfície mínima de auth recovery e avatar readiness
- expansão funcional de módulos além do rollout visual/navegacional do primeiro batch
- rollout operacional de módulos ainda disabled

## Done do batch

O batch só fecha quando:

- o frontend consumir assets oficiais de `generated/images`
- a shell obedecer `UX_SHELL_CONTRACT.md`
- auth obedecer `AUTH_EXPERIENCE_CONTRACT.md`
- navegação obedecer `NAVIGATION_VISIBILITY_CONTRACT.md`
- a prontidão de Resend, `FRONTEND_URL` e Cloudinary estiver explicitada na superfície soberana exigida
- `FRONTEND_CONTRACT_GATE` sair de FAIL
