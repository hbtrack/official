## Prompt Operacional — Criar contrato AsyncAPI

**Objetivo**: criar ou revisar contratos de eventos em `contracts/asyncapi/` sem improviso estrutural.

### Leitura mínima
1. `.contract_driven/CONTRACT_SYSTEM_RULES.md`
2. `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md`
3. `docs/_canon/BOOT_PROFILES.md`
4. `docs/hbtrack/modulos/<MODULE>/DOMAIN_RULES_<MODULE>.md`
5. `docs/hbtrack/modulos/<MODULE>/INVARIANTS_<MODULE>.md`
6. `contracts/asyncapi/asyncapi.yaml`

### Bloqueios
- `BLOCKED_MISSING_MODULE`
- `BLOCKED_MISSING_CANON_ARTIFACT`
- `BLOCKED_CONTRACT_CONFLICT`

### Saída
- canais, mensagens e schemas AsyncAPI escritos no path canônico
- cross-ref explícita com módulo e contrato soberano relacionado
