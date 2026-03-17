## Prompt Operacional — Criar workflow Arazzo

**Objetivo**: criar ou revisar workflows em `contracts/workflows/<module>/` com dependência explícita de `operationId` soberano.

### Leitura mínima
1. `.contract_driven/CONTRACT_SYSTEM_RULES.md`
2. `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md`
3. `docs/_canon/CONTRACT_PIPELINE.md`
4. `contracts/openapi/openapi.yaml`
5. `docs/hbtrack/modulos/<MODULE>/TEST_MATRIX_<MODULE>.md`

### Bloqueios
- `BLOCKED_MISSING_MODULE`
- `BLOCKED_ARAZZO_OPENAPI_LINK_MISSING`
- `BLOCKED_CONTRACT_CONFLICT`

### Saída
- workflow `.arazzo.yaml` no módulo correto
- cada `operationId` referenciado existe no OpenAPI root
