## Prompt Operacional — Criar/alterar contrato OpenAPI (paths de módulo)

**Objetivo**: criar ou atualizar `contracts/openapi/paths/<MODULE>.yaml` com determinismo, usando apenas convenções explícitas.

### Entrada esperada (do humano)
- `module` (lower_snake_case) — deve existir na taxonomia do LAYOUT.
- `resource`/entidade(s) alvo (nome, singular/plural).
- operações desejadas (List/Get/Create/Patch/Delete) + requisitos (authz, filtros, paginação, etc.).

### Leitura mínima obrigatória (ordem)
1. `.contract_driven/CONTRACT_SYSTEM_RULES.md`
2. `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md`
3. `.contract_driven/COMPETITIVE_BENCHMARK_PROTOCOL.md` (**obrigatório quando houver decisão de design de API a apresentar**)
4. `.contract_driven/templates/api/api_rules.yaml` (**SSOT de API**)
5. `.contract_driven/templates/api/MODULE_PROFILE_REGISTRY.yaml` (surface/target do módulo — o agente não escolhe)
6. `generated/resolved_policy/<MODULE>.sync.resolved.yaml` (policy resolvida — deve existir após compiler)
7. `docs/_canon/SYSTEM_SCOPE.md`
8. `docs/hbtrack/modulos/<module>/MODULE_SCOPE_<MODULE>.md`
9. `docs/hbtrack/modulos/<module>/DOMAIN_RULES_<MODULE>.md`
10. `docs/hbtrack/modulos/<module>/INVARIANTS_<MODULE>.md`
11. `docs/hbtrack/modulos/<module>/PERMISSIONS_<MODULE>.md` (quando existir)
12. `docs/hbtrack/modulos/<module>/ERRORS_<MODULE>.md` (quando existir)
13. Contratos atuais: `contracts/openapi/openapi.yaml` + `contracts/openapi/paths/<MODULE>.yaml` (se existir)

### Bloqueios (falhar cedo)
- Se `module` não existir no LAYOUT (seção 2): **bloquear** com `BLOCKED_MISSING_MODULE`.
- Se o path alvo estiver fora do layout canônico: **bloquear** com `BLOCKED_MISSING_CANON_ARTIFACT`.
- Se uma convenção necessária não estiver explícita em `api_rules.yaml`: **bloquear** com `BLOCKED_MISSING_API_CONVENTION`.
- Se houver conflito entre fontes no mesmo nível (ex.: dois docs dizendo coisas diferentes): **bloquear** com `BLOCKED_CONTRACT_CONFLICT`.

### Procedimento
1. Validar que o arquivo alvo é exatamente `contracts/openapi/paths/<MODULE>.yaml`.
2. Usar **somente** templates canônicos de `.contract_driven/templates/api/api_rules.yaml` (seção `contract_templates`).
3. Se existir ADR aplicável, o agente não pode propor alternativa conflitante sem abrir nova ADR ou revisão formal da existente.
   - Quando `api_rules.yaml` deixar margem de escolha (ex.: granularidade de recursos, estratégia de filtros, shape de payload), aplicar o **benchmark competitivo** (`COMPETITIVE_BENCHMARK_PROTOCOL.md`) antes de apresentar opções ao humano.
4. Instanciar `contract_templates.openapi_path_module_yaml` para o módulo.
5. Preencher placeholders apenas quando houver evidência explícita:
   - nomes técnicos (module, resource) devem ser consistentes com LAYOUT.
   - nomes de campos/JSON devem seguir `api_rules` (camelCase).
6. Garantir:
   - paginação conforme `api_rules` quando endpoint retornar coleção;
   - erros conforme a SSOT (ver `api_rules` + `.contract_driven/DOMAIN_AXIOMS.json` para shape de erro);
   - segurança OWASP (BOLA/BOPLA/BFLA) aplicada por operação.
   - usar `HTTPBearer` como único scheme para operações protegidas; `bearerAuth` e `security: - {}` são proibidos.
   - usar somente `../components/schemas/shared/problem.yaml` para erros HTTP públicos.
   - operações públicas só podem usar `security: []` quando a descrição da operação explicar por que ela é pública.
   - schemas de resposta de entidades estáveis devem reutilizar a shape soberana em `contracts/schemas/**` ou declarar `x-schema-ref-justification` explícita para qualquer delta HTTP.
   - operações protegidas devem documentar `500`.
   - operações com transição de estado, concorrência ou conflito de domínio devem documentar `409`.
   - endpoints de query analítica não podem usar `filterExpression` textual nem `data[].additionalProperties: true`; devem usar request/response soberanos com filtros estruturados e row envelope fixo.
7. Atualizar `contracts/openapi/openapi.yaml` apenas quando necessário (ex.: adicionar `$ref` do novo path file).
8. Rodar o compiler determinístico (gera policy resolvida + manifesto + bundle derivado consumível em `generated/contracts/openapi/**`):
   - `python3 scripts/contracts/validate/api/compile_api_policy.py --module <module> --surface sync`
9. Rodar gates:
   - `python3 scripts/validate_contracts.py`
10. Validar objetivamente antes de concluir:
   - zero `$ref` local quebrado em `generated/contracts/openapi/**`;
   - `contracts/openapi/**` e `generated/contracts/openapi/**` expõem a mesma superfície;
   - ausência total de `bearerAuth`, `security: - {}` e `common/error.yaml`;
   - zero operações protegidas sem `500`;
   - zero mutações contratuais sem `409` (exceto auth login/refresh/logout quando não houver conflito de recurso);
   - zero endpoints analíticos com DSL textual solta ou response rows abertas.

### Saída
- `contracts/openapi/paths/<MODULE>.yaml` atualizado.
- Se necessário, `contracts/openapi/openapi.yaml` atualizado para referenciar o path file.
- `generated/resolved_policy/<MODULE>.sync.resolved.yaml` atualizado.
- `generated/contracts/openapi/**` atualizado como bundle auto-contido.
- `generated/manifests/<MODULE>.sync.traceability.yaml` atualizado.
