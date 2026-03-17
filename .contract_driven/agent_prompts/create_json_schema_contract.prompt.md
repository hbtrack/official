## Prompt Operacional — Criar contrato JSON Schema

**Objetivo**: criar ou revisar schemas soberanos em `contracts/schemas/<module>/`.

### Leitura mínima
1. `.contract_driven/CONTRACT_SYSTEM_RULES.md`
2. `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md`
3. `docs/_canon/DATA_CONVENTIONS.md`
4. `docs/hbtrack/modulos/<MODULE>/DOMAIN_RULES_<MODULE>.md`
5. `docs/hbtrack/modulos/<MODULE>/INVARIANTS_<MODULE>.md`

### Bloqueios
- `BLOCKED_MISSING_MODULE`
- `BLOCKED_MISSING_CANON_ARTIFACT`
- `BLOCKED_FORMAT_VIOLATION`

### Saída
- `contracts/schemas/<module>/*.schema.json` válido em Draft 2020-12
- naming, formatos e invariantes alinhados ao canon
