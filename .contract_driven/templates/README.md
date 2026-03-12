# .contract_driven/templates

Este diretório contém as **templates oficiais** que antes estavam embutidas em `.contract_driven/GLOBAL_TEMPLATES.md`.

## Como instanciar
- Escolha a categoria:
  - `globais/`: templates para `docs/_canon/*` e ADRs (`docs/_canon/decisions/*`).
  - `modulos/`: templates para `docs/hbtrack/modulos/<module>/*` e schemas (`contracts/schemas/<module>/*`).
- Copie o arquivo de template para o path canônico do repositório (ex: `docs/_canon/ARCHITECTURE.md`).
- Substitua os placeholders `{{...}}`.

## Observações
- Templates canônicos de **OpenAPI/HTTP** não vivem em `globais/` nem `modulos/`: a SSOT é `.contract_driven/templates/API_RULES/API_RULES.yaml` (`hbtrack_api_rules.contract_templates`).
- Alguns nomes de arquivos usam placeholders (ex: `MODULE_SCOPE_{{MODULE_NAME_UPPER}}.md`): ao instanciar, gere o nome final (ex: `MODULE_SCOPE_TRAINING.md`).
- Todas as templates possuem um cabeçalho padrão (comentário) com `TEMPLATE`, `DEST` e `SOURCE` para uso determinístico por agentes.
