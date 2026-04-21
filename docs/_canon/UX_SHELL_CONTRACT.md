---
doc_type: canon
version: "1.0.0"
status: active
state_semantics: target-state
owner: product-owner
related_docs:
  - docs/_canon/UX_BRAND_CONTRACT.md
  - docs/_canon/NAVIGATION_VISIBILITY_CONTRACT.md
---

# UX_SHELL_CONTRACT.md

## 0. Objetivo
Define a shell oficial da aplicação autenticada do HB Track Web.

## 1. Estrutura obrigatória
A shell autenticada deve conter:
- sidebar desktop colapsável
- drawer/sidebar mobile com overlay
- top bar
- área principal scrollável
- contexto de equipe/temporada
- menu do usuário

## 2. Sidebar oficial
### Comportamento
- Sidebar desktop fixa e colapsável.
- No mobile, a navegação vira drawer lateral com overlay.
- O drawer mobile fecha ao navegar, ao clicar fora e ao pressionar Escape.
- A sidebar deve suportar submenus, badges e visibilidade por role/contexto.

### Header da sidebar
- Expandida: usa `generated/images/logo.svg` ou `generated/images/logo-dark.svg`
- Colapsada: usa `generated/images/logo-icon.svg` ou `generated/images/logo-icon-dark.svg`

### Contexto operacional
A shell deve suportar:
- equipe ativa
- troca de equipe
- temporada ativa

## 3. Top bar oficial
### Elementos obrigatórios no primeiro batch
- botão hamburger no mobile
- breadcrumbs
- command palette
- notificações
- avatar do usuário
- menu do usuário
- logout

### Avatar do usuário
- A top bar deve exibir a foto de perfil do usuário quando disponível.
- O fallback para iniciais só é permitido quando não houver avatar.
- O avatar deve ser circular.

### Pipeline de avatar (target-state)
- O sistema deve suportar pipeline de avatar com processamento externo.
- Baseline inicial: Cloudinary.
- O frontend deve exibir o avatar processado quando disponível.
- Resultado visual esperado: avatar pronto para uso na top bar em formato circular.

## 4. Taxonomia estrutural da shell
A shell deve suportar agrupamento em seções:
- Início
- Organização
- Planejamento Técnico
- Jogo e Competição
- Performance e Saúde
- Administração

## 5. Responsividade
### Desktop
- sidebar visível
- top bar ajustada ao width da sidebar
- conteúdo com scroll independente

### Mobile
- drawer com overlay
- top bar com hamburger
- hierarquia funcional preservada

## 6. Critérios de aceite
A shell só pode ser aprovada se:
- respeitar branding oficial
- existir paridade desktop/mobile
- suportar contexto operacional
- suportar avatar, user menu e logout
- suportar command palette e notificações no primeiro batch