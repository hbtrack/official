## Prompt Operacional — Criar docs mínimas de módulo

**Objetivo**: garantir o pacote mínimo de documentação normativa do módulo em `docs/hbtrack/modulos/<module>/`.

### Leitura mínima obrigatória (ordem)
1. `.contract_driven/CONTRACT_SYSTEM_RULES.md`
2. `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md`
3. `.contract_driven/GLOBAL_TEMPLATES.md` (índice/regras)
4. templates SSOT: `.contract_driven/templates/modulos/*`
5. `docs/_canon/SYSTEM_SCOPE.md`
6. `docs/_canon/HANDBALL_RULES_DOMAIN.md` (somente se o gatilho aplicar; link sempre presente no header)

### Bloqueios (falhar cedo)
- Se `module` não existir no LAYOUT: **bloquear** com `BLOCKED_MISSING_MODULE`.
- Se faltar artefato canônico exigido pela tarefa e não houver evidência: **bloquear** com `BLOCKED_MISSING_CANON_ARTIFACT`.
- Se o gatilho do handebol (RULES seção 12) aplicar e não houver referência explícita: **bloquear** com `BLOCKED_MISSING_CANON_ARTIFACT`.

### Artefatos mínimos (sempre)
Criar (ou atualizar) exatamente estes arquivos:
- `docs/hbtrack/modulos/<module>/README.md`
- `docs/hbtrack/modulos/<module>/MODULE_SCOPE_<MODULE>.md`
- `docs/hbtrack/modulos/<module>/DOMAIN_RULES_<MODULE>.md`
- `docs/hbtrack/modulos/<module>/INVARIANTS_<MODULE>.md`
- `docs/hbtrack/modulos/<module>/TEST_MATRIX_<MODULE>.md`

### Regras obrigatórias
- Todos os arquivos acima **devem** incluir o header YAML canônico (ver `.contract_driven/templates/modulos/snippets/module_human_docs_header.yaml`, referenciado por `.contract_driven/GLOBAL_TEMPLATES.md` seção 3).
- `handball_semantic_applicability` deve ser `true` somente quando o gatilho do handebol (RULES seção 12) se aplicar.
- Cross-references devem apontar para:
  - `docs/_canon/SYSTEM_SCOPE.md`
  - `docs/_canon/HANDBALL_RULES_DOMAIN.md` (quando aplicável por semântica)
  - `contracts/openapi/paths/<module>.yaml`
  - `contracts/schemas/<module>/`

### Procedimento recomendado
1. Criar primeiro o pacote mínimo acima usando as templates SSOT em `.contract_driven/templates/modulos/*` (sem placeholders não-resolvidos).
2. Criar docs condicionais apenas quando aplicáveis (STATE_MODEL, PERMISSIONS, ERRORS, UI_CONTRACT, SCREEN_MAP).
3. Rodar `python3 scripts/validate_contracts.py` e corrigir `REQUIRED_ARTIFACT_PRESENCE_GATE` / `MODULE_DOC_CROSSREF_GATE` quando falhar.
