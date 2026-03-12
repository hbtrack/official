<!-- TEMPLATE: global-canon-template | DEST: docs/_canon/CI_CONTRACT_GATES.md | SOURCE: .contract_driven/templates/globais/CI_CONTRACT_GATES.md -->

# CI_CONTRACT_GATES.md

## Stack Oficial de Validação
Este template reflete a stack fixa definida em `.contract_driven/CONTRACT_SYSTEM_RULES.md` seção 19.
Não substituir ferramentas sem atualizar RULES primeiro.

## Objetivo
Definir gates automáticos baseados em contrato.

## Pipeline Mínimo
1. Lint estrutural OpenAPI (Redocly CLI)
2. Lint rulesets customizados (Spectral)
3. Detecção breaking changes (oasdiff)
4. Testes contract/runtime HTTP (Schemathesis)
5. Validação schemas standalone (JSON Schema validator)
6. Validação AsyncAPI (quando aplicável)
7. Validação Arazzo (quando aplicável)
8. Build Storybook (quando UI existir)

## Gates

### Gate 1 — Redocly CLI
Objetivo: validação estrutural OpenAPI.
Exemplo:
```bash
redocly lint contracts/openapi/openapi.yaml
```

### Gate 2 — Spectral
Objetivo: validar rulesets customizados OpenAPI.
Exemplo:
```bash
spectral lint contracts/openapi/openapi.yaml --ruleset .spectral.yaml
```

### Gate 3 — oasdiff
Objetivo: detectar breaking changes entre baseline e revisão.
Exemplo:
```bash
oasdiff breaking contracts/openapi/baseline.yaml contracts/openapi/openapi.yaml
```

### Gate 4 — Schemathesis
Objetivo: testes contract-based HTTP.
Exemplo:
```bash
schemathesis run contracts/openapi/openapi.yaml --base-url={{API_BASE_URL}}
```

### Gate 5 — JSON Schema validator
Objetivo: validar schemas standalone.
Exemplo:
```bash
ajv validate -s contracts/schemas/{{MODULE_NAME}}/*.schema.json
```

### Gate 6 — AsyncAPI parser
Objetivo: validar contratos de eventos (quando aplicável).
Exemplo:
```bash
asyncapi validate contracts/asyncapi/asyncapi.yaml
```

### Gate 7 — Arazzo validator
Objetivo: validar workflows multi-step (quando aplicável).
Exemplo:
```bash
arazzo validate contracts/workflows/{{MODULE_NAME}}/*.arazzo.yaml
```

### Gate 8 — Storybook build
Objetivo: validar documentação de componentes UI (quando UI existir).
Exemplo:
```bash
npm run build-storybook
```

## Critérios de Falha
- contrato inválido
- guideline violada
- breaking change não autorizada
- incompatibilidade contratual
- schema inválido
- workflow inválido
- evento inválido
- build Storybook falhado

## Evidências
- logs do lint (Redocly + Spectral)
- diff de contrato (oasdiff)
- relatório de testes (Schemathesis)
- validação de schemas (JSON Schema)
- validação de eventos (AsyncAPI)
- validação de workflows (Arazzo)
- artefatos Storybook gerados

## Observação
Gates 6, 7 e 8 são condicionais:
- Gate 6 (AsyncAPI): somente quando módulo publica/consome eventos
- Gate 7 (Arazzo): somente quando módulo tem workflows multi-step
- Gate 8 (Storybook): somente quando módulo tem componentes UI
