
## Prompt Operacional — Criar/atualizar contrato de UI (por módulo)

**Objetivo**: criar `docs/hbtrack/modulos/<module>/UI_CONTRACT_<MODULE>.md` e, quando necessário, `SCREEN_MAP_<MODULE>.md`, mantendo alinhamento com OpenAPI.

### Leitura mínima obrigatória (ordem)
1. `.contract_driven/CONTRACT_SYSTEM_RULES.md`
2. `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md`
3. `docs/_canon/UI_FOUNDATIONS.md` e `docs/_canon/DESIGN_SYSTEM.md`
4. `contracts/openapi/openapi.yaml` + `contracts/openapi/paths/<module>.yaml`
5. docs do módulo (README/MODULE_SCOPE/DOMAIN_RULES/INVARIANTS)

### Bloqueios (falhar cedo)
- Se `module` não existir no LAYOUT: **bloquear** com `BLOCKED_MISSING_MODULE`.
- Se não existir UI real (tela/form): **não criar** UI_CONTRACT (artefato condicional).
- Se o contrato de UI depender de endpoint inexistente no OpenAPI: **bloquear** com `BLOCKED_MISSING_CANON_ARTIFACT`.

### Regras
- UI_CONTRACT deve listar: telas/fluxos, estados (loading/empty/error/success), ações do usuário e os endpoints/operationIds correspondentes.
- Nenhum detalhe de API é inferido: a UI referencia apenas o que existe em OpenAPI.
- Usar templates SSOT quando aplicável:
  - `.contract_driven/templates/modulos/UI_CONTRACT_{{MODULE_NAME_UPPER}}.md`
  - `.contract_driven/templates/modulos/SCREEN_MAP_{{MODULE_NAME_UPPER}}.md`
- Header YAML canônico é obrigatório (ver `.contract_driven/templates/modulos/snippets/module_human_docs_header.yaml`, referenciado por `.contract_driven/GLOBAL_TEMPLATES.md` seção 3).

### Saída
- `docs/hbtrack/modulos/<module>/UI_CONTRACT_<MODULE>.md` (quando aplicável).
- `docs/hbtrack/modulos/<module>/SCREEN_MAP_<MODULE>.md` (quando aplicável).
