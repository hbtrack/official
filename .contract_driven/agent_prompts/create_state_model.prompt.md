## Prompt Operacional — Criar/atualizar STATE_MODEL de módulo

**Objetivo**: criar `docs/hbtrack/modulos/<module>/STATE_MODEL_<MODULE>.md` quando existir ciclo de vida real (estados/transições) e alinhar com `.contract_driven/DOMAIN_AXIOMS.json` quando aplicável.

### Leitura mínima obrigatória (ordem)
1. `.contract_driven/CONTRACT_SYSTEM_RULES.md`
2. `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md`
3. `.contract_driven/DOMAIN_AXIOMS.json` (enums/máquinas globais)
4. template SSOT: `.contract_driven/templates/modulos/STATE_MODEL_{{MODULE_NAME_UPPER}}.md`
5. `docs/hbtrack/modulos/<module>/DOMAIN_RULES_<MODULE>.md`
6. `docs/hbtrack/modulos/<module>/INVARIANTS_<MODULE>.md`

### Bloqueios (falhar cedo)
- Se `module` não existir no LAYOUT: **bloquear** com `BLOCKED_MISSING_MODULE`.
- Se não houver evidência de estados/transições reais: **não criar** STATE_MODEL (artefato condicional).
- Se precisar criar/alterar enum/máquina de estados global e não houver regra explícita: **bloquear** com `BLOCKED_MISSING_CANON_ARTIFACT`.

### Regras
- O arquivo deve ter header YAML canônico (ver `.contract_driven/templates/modulos/snippets/module_human_docs_header.yaml`, referenciado por `.contract_driven/GLOBAL_TEMPLATES.md` seção 3).
- Se o módulo reutilizar uma máquina de estados global (ex.: `training_state_machine`), referenciar explicitamente a origem em `.contract_driven/DOMAIN_AXIOMS.json`.
- Se houver divergência entre o texto e os axiomas globais, os axiomas são soberanos; ajustar o texto para refletir.

### Saída
- `docs/hbtrack/modulos/<module>/STATE_MODEL_<MODULE>.md` (somente quando aplicável).
