# UI_CONTRACT_GUIDE.md

## Objetivo
Consolidar fundamentos, tokens e padrões transversais de interface para contratos de UI no HB Track.

---

## Parte 1: Fundamentos de UI

### Princípios
- clareza
- consistência
- acessibilidade
- responsividade
- previsibilidade
- feedback imediato

### Fundamentos Visuais
- grid
- spacing
- tipografia
- densidade
- contraste
- ícones
- estados de foco
- navegação por teclado

### Estados Globais de UI
- loading
- empty
- success
- error
- disabled
- offline
- partial-data

### Responsividade
- breakpoints: mobile-first (360, 768, 1024, 1440)
- targets primários: mobile e desktop (navegadores modernos)

### Acessibilidade
- contraste mínimo: WCAG 2.1 AA
- semântica e labels: todo input deve ter label visível ou `aria-label`
- foco visível: obrigatório

---

## Parte 2: Design System

### Tokens de Design
- color
- typography
- spacing
- radius
- elevation
- border
- iconography
- motion

### Componentes Base
- button
- input
- select
- textarea
- checkbox
- radio
- switch
- modal
- drawer
- table
- card
- badge
- tabs
- toast
- empty-state
- pagination

### Regras de Composição
- não criar variante sem motivação de produto
- preferir composição a duplicação
- documentar props e estados no Storybook (quando existir)
- alinhar labels e conteúdo ao glossário de domínio (`DOMAIN_GLOSSARY.md`)

---

## Artefatos Relacionados
- `docs/_canon/DOMAIN_GLOSSARY.md`
- `contracts/schemas/<module>/` (para data types de inputs)
- `docs/hbtrack/modulos/<module>/UI_CONTRACT_<MODULE>.md` (para contratos específicos de módulo)
