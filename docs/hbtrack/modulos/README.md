# Módulos — DOMAIN_AXIOMS_<MODULE>.json

Quando `domain_axioms.module_extension_policy.allow_module_extensions` for `true`, um módulo pode declarar **somente extensões explícitas** (sem sobrescrever axiomas globais) via:

`docs/hbtrack/modulos/<module>/DOMAIN_AXIOMS_<MODULE>.json`

Regras canônicas (enforcement em `scripts/validate_contracts.py`):
- o arquivo deve existir **exatamente** no path acima
- o JSON deve ter raiz `domain_axioms_module`
- o contrato estrutural do arquivo é o JSON Schema `contracts/schemas/shared/domain_axioms_module.schema.json`
- o arquivo deve declarar `delta_only=true` e `local_invariants_may_only_restrict=true`
- extensões são aceitas apenas quando explicitamente permitidas por política; `event_type` é o caso canônico (global fechado, extensível via DELTA_ONLY)
- extensões nunca podem colidir com valores do conjunto global
- para `event_type`, extensões devem declarar metadados verificáveis por valor (`name`, `semantic_id`, `description`, `payload_constraints`)
