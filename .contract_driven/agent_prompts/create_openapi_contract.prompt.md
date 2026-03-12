## Prompt Operacional — Criar/alterar contrato OpenAPI (paths de módulo)

**Objetivo**: criar ou atualizar `contracts/openapi/paths/<module>.yaml` com determinismo, usando apenas convenções explícitas.

### Entrada esperada (do humano)
- `module` (lower_snake_case) — deve existir na taxonomia do LAYOUT.
- `resource`/entidade(s) alvo (nome, singular/plural).
- operações desejadas (List/Get/Create/Patch/Delete) + requisitos (authz, filtros, paginação, etc.).

### Leitura mínima obrigatória (ordem)
1. `.contract_driven/CONTRACT_SYSTEM_RULES.md`
2. `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md`
3. `.contract_driven/templates/API_RULES/API_RULES.yaml` (**SSOT de API**)
4. `.contract_driven/templates/API_RULES/MODULE_PROFILE_REGISTRY.yaml` (surface/target do módulo — o agente não escolhe)
5. `generated/resolved_policy/<module>.sync.resolved.yaml` (policy resolvida — deve existir após compiler)
6. `docs/_canon/SYSTEM_SCOPE.md`
7. `docs/hbtrack/modulos/<module>/MODULE_SCOPE_<MODULE>.md`
8. `docs/hbtrack/modulos/<module>/DOMAIN_RULES_<MODULE>.md`
9. `docs/hbtrack/modulos/<module>/INVARIANTS_<MODULE>.md`
10. Contratos atuais: `contracts/openapi/openapi.yaml` + `contracts/openapi/paths/<module>.yaml` (se existir)

### Bloqueios (falhar cedo)
- Se `module` não existir no LAYOUT (seção 2): **bloquear** com `BLOCKED_MISSING_MODULE`.
- Se o path alvo estiver fora do layout canônico: **bloquear** com `BLOCKED_MISSING_CANON_ARTIFACT`.
- Se uma convenção necessária não estiver explícita em `API_RULES.yaml`: **bloquear** com `BLOCKED_MISSING_API_CONVENTION`.
- Se houver conflito entre fontes no mesmo nível (ex.: dois docs dizendo coisas diferentes): **bloquear** com `BLOCKED_CONTRACT_CONFLICT`.

### Procedimento
1. Validar que o arquivo alvo é exatamente `contracts/openapi/paths/<module>.yaml`.
2. Usar **somente** templates canônicos de `.contract_driven/templates/API_RULES/API_RULES.yaml` (seção `contract_templates`).
3. Instanciar `contract_templates.openapi_path_module_yaml` para o módulo.
4. Preencher placeholders apenas quando houver evidência explícita:
   - nomes técnicos (module, resource) devem ser consistentes com LAYOUT.
   - nomes de campos/JSON devem seguir `API_RULES` (camelCase).
5. Garantir:
   - paginação conforme `API_RULES` quando endpoint retornar coleção;
   - erros conforme a SSOT (ver `API_RULES` + `.contract_driven/DOMAIN_AXIOMS.json` para shape de erro);
   - segurança OWASP (BOLA/BOPLA/BFLA) aplicada por operação.
6. Atualizar `contracts/openapi/openapi.yaml` apenas quando necessário (ex.: adicionar `$ref` do novo path file).
7. Rodar o compiler determinístico (gera policy resolvida + manifesto + cópia derivada do contrato):
   - `python3 scripts/contracts/validate/api/compile_api_policy.py --module <module> --surface sync`
8. Rodar gates:
   - `python3 scripts/validate_contracts.py`

### Saída
- `contracts/openapi/paths/<module>.yaml` atualizado.
- Se necessário, `contracts/openapi/openapi.yaml` atualizado para referenciar o path file.
- `generated/resolved_policy/<module>.sync.resolved.yaml` atualizado.
- `generated/contracts/openapi/paths/<module>.yaml` atualizado (cópia derivada).
- `generated/manifests/<module>.sync.traceability.yaml` atualizado.
