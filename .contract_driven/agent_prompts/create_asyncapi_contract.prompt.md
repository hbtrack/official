## Prompt Operacional — Criar contrato AsyncAPI

**Objetivo**: criar ou revisar contratos de eventos em `contracts/asyncapi/` sem improviso estrutural.

### Leitura mínima
1. `.contract_driven/CONTRACT_SYSTEM_RULES.md`
2. `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md`
3. `.contract_driven/COMPETITIVE_BENCHMARK_PROTOCOL.md` (**obrigatório quando houver decisão de design de eventos a apresentar**)
4. `docs/_canon/AGENT_INSTRUCTIONS.md §7`
5. `docs/hbtrack/modulos/<MODULE>/DOMAIN_RULES_<MODULE>.md`
6. `docs/hbtrack/modulos/<MODULE>/INVARIANTS_<MODULE>.md`
7. `contracts/asyncapi/asyncapi.yaml`

### Bloqueios
- `BLOCKED_MISSING_MODULE`
- `BLOCKED_MISSING_CANON_ARTIFACT`
- `BLOCKED_CONTRACT_CONFLICT`

### Regra de benchmark
Quando houver decisão de design de eventos a ser apresentada ao humano (ex.: granularidade do evento, naming, topologia de canais, payload vs. referência), aplicar obrigatoriamente o benchmark competitivo conforme `COMPETITIVE_BENCHMARK_PROTOCOL.md` antes de apresentar as opções.

### Saída
- canais, mensagens e schemas AsyncAPI escritos no path canônico
- cross-ref explícita com módulo e contrato soberano relacionado
- campo `benchmark_basis` em decisões de design registradas
