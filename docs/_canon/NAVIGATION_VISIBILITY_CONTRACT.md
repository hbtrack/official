---
doc_type: canon
version: "1.0.0"
status: active
state_semantics: target-state
owner: product-owner
related_docs:
  - docs/_canon/UX_SHELL_CONTRACT.md
  - docs/_canon/MODULE_MAP.md
  - docs/_canon/SYSTEM_SCOPE.md
---

# NAVIGATION_VISIBILITY_CONTRACT.md

## 0. Objetivo
Define como módulos e rotas devem aparecer na navegação do HB Track.

## 0.1 Limite de autoridade
Este contrato define taxonomia visual e regras de visibilidade da navegação.
Ele não altera a taxonomia técnica oficial dos módulos, que permanece definida em `docs/_canon/MODULE_MAP.md`.
Nenhum item visual deste contrato cria módulo novo fora dos 17 módulos canônicos.

## 1. Estratégia oficial de visibilidade
- Exibir a visão completa da plataforma na navegação.
- Módulos indisponíveis na fase atual aparecem visíveis, porém desabilitados.

## 2. Taxonomia visual inicial

### Início
- Dashboard

### Organização
- Teams
- Seasons
- Users

### Planejamento Técnico
- Training
- Exercises

### Jogo e Competição
- Competitions
- Matches
- Scout
- Video

### Performance e Saúde
- Wellness
- Medical
- Analytics
- Reports
- AI Ingestion

### Administração
- Conta e Acesso
- Audit

### Top bar capabilities
- Notificações
- Command palette
- Breadcrumbs
- User menu

## 3. Estado inicial da primeira shell reimplementada

### Ativos
- Dashboard
- Teams
- Seasons
- Training
- Users
- Conta e Acesso

### Capabilities ativas na top bar
- Notificações
- Command palette
- Breadcrumbs
- User menu

### Visíveis, porém desabilitados
- Competitions
- Matches
- Scout
- Video
- Wellness
- Medical
- Exercises
- Analytics
- Reports
- AI Ingestion
- Audit

## 4. Mapeamento visual de módulos transversais
- `identity_access` → Conta e Acesso
- `notifications` → capability da top bar no primeiro batch
- `audit` → item disabled em Administração no primeiro batch

## 5. Regras
- Itens do menu não podem ser definidos por conveniência do executor.
- Toda inclusão, exclusão ou reordenação deve citar este contrato.
- A política visual de módulos indisponíveis deve ser consistente.

## 6. Critérios de aceite
A navegação só pode ser aprovada se:
- respeitar agrupamento oficial
- respeitar visibilidade por role
- respeitar rollout por versão
- respeitar contexto operacional

## 7. Revisão planejada
A matriz detalhada de visibilidade por role no nível operacional será definida na revisão 1.0.1, após a implementação da shell base.
Até essa revisão, este contrato governa:
- taxonomia visual
- módulos ativos no primeiro batch
- módulos disabled no primeiro batch
- capabilities da top bar
