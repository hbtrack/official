## Prompt Operacional — Criar/alterar contrato OpenAPI (paths de módulo)

**Objetivo**: criar ou atualizar `contracts/openapi/paths/TRAINING.yaml` com determinismo, usando apenas convenções explícitas.

### Entrada esperada (do humano)
- `module` (lower_snake_case) — deve existir na taxonomia do LAYOUT.
- `resource`/entidade(s) alvo (nome, singular/plural).
- operações desejadas (List/Get/Create/Patch/Delete) + requisitos (authz, filtros, paginação, etc.).

### Leitura mínima obrigatória (ordem)
1. `.contract_driven/CONTRACT_SYSTEM_RULES.md`
2. `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md`
3. `.contract_driven/templates/api/api_rules.yaml` (**SSOT de API**)
4. `.contract_driven/templates/api/MODULE_PROFILE_REGISTRY.yaml` (surface/target do módulo — o agente não escolhe)
5. `generated/resolved_policy/TRAINING.sync.resolved.yaml` (policy resolvida — deve existir após compiler)
6. `docs/_canon/SYSTEM_SCOPE.md`
7. `docs/hbtrack/modulos/TRAINING/MODULE_SCOPE_TRAINING.md`
8. `docs/hbtrack/modulos/TRAINING/DOMAIN_RULES_TRAINING.md`
9. `docs/hbtrack/modulos/TRAINING/INVARIANTS_TRAINING.md`
10. Contratos atuais: `contracts/openapi/openapi.yaml` + `contracts/openapi/paths/TRAINING.yaml` (se existir)

### Bloqueios (falhar cedo)
- Se `module` não existir no LAYOUT (seção 2): **bloquear** com `BLOCKED_MISSING_MODULE`.
- Se o path alvo estiver fora do layout canônico: **bloquear** com `BLOCKED_MISSING_CANON_ARTIFACT`.
- Se uma convenção necessária não estiver explícita em `api_rules.yaml`: **bloquear** com `BLOCKED_MISSING_API_CONVENTION`.
- Se houver conflito entre fontes no mesmo nível (ex.: dois docs dizendo coisas diferentes): **bloquear** com `BLOCKED_CONTRACT_CONFLICT`.

### Procedimento
1. Validar que o arquivo alvo é exatamente `contracts/openapi/paths/TRAINING.yaml`.
2. Usar **somente** templates canônicos de `.contract_driven/templates/api/api_rules.yaml` (seção `contract_templates`).
3. Se existir ADR aplicável, o agente não pode propor alternativa conflitante sem abrir nova ADR ou revisão formal da existente.
4. Instanciar `contract_templates.openapi_path_module_yaml` para o módulo.
5. Preencher placeholders apenas quando houver evidência explícita:
   - nomes técnicos (module, resource) devem ser consistentes com LAYOUT.
   - nomes de campos/JSON devem seguir `api_rules` (camelCase).
6. Garantir:
   - paginação conforme `api_rules` quando endpoint retornar coleção;
   - erros conforme a SSOT (ver `api_rules` + `.contract_driven/DOMAIN_AXIOMS.json` para shape de erro);
   - segurança OWASP (BOLA/BOPLA/BFLA) aplicada por operação.
7. Atualizar `contracts/openapi/openapi.yaml` apenas quando necessário (ex.: adicionar `$ref` do novo path file).
8. Rodar o compiler determinístico (gera policy resolvida + manifesto + cópia derivada do contrato):
   - `python3 scripts/contracts/validate/api/compile_api_policy.py --module TRAINING --surface sync`
9. Rodar gates:
   - `python3 scripts/validate_contracts.py`

### Saída
- `contracts/openapi/paths/TRAINING.yaml` atualizado.
- Se necessário, `contracts/openapi/openapi.yaml` atualizado para referenciar o path file.
- `generated/resolved_policy/TRAINING.sync.resolved.yaml` atualizado.
- `generated/contracts/openapi/paths/TRAINING.yaml` atualizado (cópia derivada).
- `generated/manifests/TRAINING.sync.traceability.yaml` atualizado.
