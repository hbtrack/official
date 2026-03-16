---
adr_id: ADR-SPORT-SCIENCE-RULES-001
title: Instituir SPORT_SCIENCE_RULES como artefato canônico de governança
status: accepted
date: 2026-03-14
decision_type: architecture_governance
scope: contract_system
affects:
  - CONTRACT_SYSTEM_LAYOUT.md
  - CONTRACT_SYSTEM_RULES.md
  - GLOBAL_TEMPLATES.md
  - MODULE_SOURCE_AUTHORITY_MATRIX.yaml
related:
  - DOMAIN_AXIOMS.json
  - DOMAIN_GLOSSARY.md
  - HANDBALL_RULES_DOMAIN.md
---

# Contexto

O HB Track já possui artefatos canônicos para:
- semântica de domínio (`DOMAIN_GLOSSARY`)
- verdade estrutural (`DOMAIN_AXIOMS`)
- regra oficial da modalidade (`HANDBALL_RULES_DOMAIN`)
- regras funcionais por módulo (`DOMAIN_RULES_<MODULE>`)

Existe uma lacuna para conteúdo técnico-científico aplicado ao esporte, como:
- wellness pré-sessão
- sRPE
- strain
- HRV
- protocolos de teste
- critérios de força, HIIT e readiness

Hoje esse conteúdo tende a ser promovido para artefatos incorretos, contaminando axiomas, regras funcionais ou regras oficiais da modalidade.

# Decisão

Instituir `SPORT_SCIENCE_RULES_<MODULE>.md` como novo artefato canônico por módulo.

Esse artefato passa a ser a fonte soberana para:
- métodos
- protocolos
- cálculos
- thresholds
- baterias de teste
- critérios técnico-científicos aplicados ao módulo

# Escopo normativo

`SPORT_SCIENCE_RULES_<MODULE>.md`:
- é canônico
- é por módulo
- é governado por `MODULE_SOURCE_AUTHORITY_MATRIX.yaml`
- não substitui `DOMAIN_AXIOMS`
- não substitui `DOMAIN_RULES_<MODULE>`
- não substitui `HANDBALL_RULES_DOMAIN`
- não substitui `DOMAIN_GLOSSARY`

# Fronteiras

## Pertence a SPORT_SCIENCE_RULES
- sRPE
- HRV
- strain
- readiness
- wellness pré-sessão
- protocolos de teste
- critérios de progressão de carga
- regras de interpretação fisiológica/funcional
- métodos de força, potência, HIIT, recuperação

## Não pertence a SPORT_SCIENCE_RULES
- axioma estrutural do handebol
- regra oficial IHF
- definição semântica de termo
- enum, formato ou convenção de dado
- regra puramente funcional do módulo sem conteúdo técnico-científico

# Autoridade de fontes

A promoção para `SPORT_SCIENCE_RULES_<MODULE>.md` deve respeitar `MODULE_SOURCE_AUTHORITY_MATRIX.yaml`.

Exemplo inicial:
- EHF: pode sustentar regras técnico-científicas específicas de handebol
- Aspetar: pode sustentar regras técnico-científicas aplicadas ao handebol
- ACSM: pode sustentar regras técnico-científicas transversais de exercício e treinamento
- ACSM não pode originar axioma estrutural específico de handebol

# Consequências

## Positivas
- evita contaminação de `DOMAIN_AXIOMS`
- evita mistura entre regra funcional e protocolo científico
- permite governança explícita de ACSM/Aspetar/EHF
- melhora determinismo na promoção de verdade

## Custos
- adiciona nova superfície canônica
- exige atualização de layout, rules e templates
- exige critério de aplicabilidade por módulo

# Implementação mínima

1. Adicionar `SPORT_SCIENCE_RULES_<MODULE>.md` ao `CONTRACT_SYSTEM_LAYOUT.md`
2. Adicionar a nova superfície ao `CONTRACT_SYSTEM_RULES.md`
3. Criar template em `GLOBAL_TEMPLATES.md`
4. Atualizar `MODULE_SOURCE_AUTHORITY_MATRIX.yaml`
5. Instanciar inicialmente para `training`

# Regra de aplicação

Se a afirmação for:
- estrutural do domínio → `DOMAIN_AXIOMS`
- funcional do módulo → `DOMAIN_RULES_<MODULE>`
- oficial da modalidade → `HANDBALL_RULES_DOMAIN`
- semântica de termo → `DOMAIN_GLOSSARY`
- método/protocolo/cálculo/threshold técnico-científico → `SPORT_SCIENCE_RULES_<MODULE>`

# Status de adoção inicial

Módulo inicial recomendado:
- `training`

Módulos candidatos futuros:
- `wellness`
- `analytics`
- `medical`
- `exercises`

# Decision

APPROVE `SPORT_SCIENCE_RULES_<MODULE>.md` as canonical module-level artifact for sport science methods, protocols, calculations, thresholds, and applied technical-scientific criteria.
