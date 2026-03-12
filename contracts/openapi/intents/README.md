# OpenAPI Intents (`.intent.yaml`)

Este diretório contém manifestos de **intenção** (DSL) para geração determinística de contratos em
`contracts/openapi/paths/<module>.yaml`.

Fluxo:

1. Editar `contracts/openapi/intents/<module>.intent.yaml`
2. Rodar `python3 scripts/contracts/validate/api/compile_api_intent.py --module <module> --apply`

Regras:

- O compiler é **fail-closed**: se qualquer gate falhar, nenhum arquivo em `contracts/openapi/paths/` é alterado.
- Erros são emitidos no formato estruturado (`--format json`) com `artifact`, `json_path` e `location` (linha/coluna).

## Round-trip (exemplo)

Intent inválida (colisão de `semantic_id` local com o registry global):

`python3 scripts/contracts/validate/api/compile_api_intent.py --module ai_ingestion --intent contracts/openapi/intents/examples/ai_ingestion.invalid.intent.yaml --format json`

Intent corrigida + aplicação:

`python3 scripts/contracts/validate/api/compile_api_intent.py --module ai_ingestion --apply --format json`
