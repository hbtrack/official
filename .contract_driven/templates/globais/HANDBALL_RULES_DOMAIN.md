<!-- TEMPLATE: global-canon-template | DEST: docs/_canon/HANDBALL_RULES_DOMAIN.md | SOURCE: .contract_driven/templates/globais/HANDBALL_RULES_DOMAIN.md -->

# HANDBALL_RULES_DOMAIN.md

## Objetivo
Traduzir regras oficiais do handebol em linguagem de domínio para uso do produto.

## Fonte Primária
- Regras oficiais vigentes da modalidade indoor
- Atualizar versão e edição consultada:
  - `{{RULEBOOK_TITLE}}`
  - `{{RULEBOOK_VERSION}}`
  - `{{RULEBOOK_EFFECTIVE_DATE}}`

## Áreas de Regra Relevantes
- composição de equipe
- duração do jogo
- intervalos e time-out
- substituições
- goleiro
- área de gol
- tiros e reinícios
- sanções disciplinares
- bola e categorias
- critérios de mesa/controle quando aplicável

## Mapeamento Produto ↔ Regra
| Tema do Handebol | Regra de Produto | Módulos Impactados | Fonte oficial |
|---|---|---|---|
| {{HANDBALL_TOPIC}} | {{PRODUCT_RULE}} | {{MODULES}} | {{RULE_REFERENCE}} |

## Regra Transversal
Todo módulo que implementar lógica derivada da modalidade deve:
1. referenciar este documento;
2. citar a regra específica;
3. registrar eventual interpretação/localização do domínio.

## Observações
Este documento não substitui a regra oficial; ele traduz a regra para o domínio do sistema.
