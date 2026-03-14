# scripts/

Tooling do workspace **HB Track (contract-driven)**.

## Entrypoints oficiais (governança contract-driven)

- `python3 scripts/validate_contracts.py` — executa os **contract gates** e gera `_reports/contract_gates/latest.json`.
- `scripts/git-hooks/pre-commit` — hook local que roda `scripts/validate_contracts.py` (CI deve executar o mesmo pipeline sem bypass).
- (Opcional) `source ./setup-env.sh && bash scripts/contract_gates/verify_tools.sh` — sanity check da toolchain (WSL-native).

SSOT do sistema:
- `.contract_driven/CONTRACT_SYSTEM_RULES.md`
- `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md`
- `.contract_driven/GLOBAL_TEMPLATES.md`
- `docs/_canon/CI_CONTRACT_GATES.md`

## Pastas principais

- `scripts/contracts/` — engine Python do pipeline de contract gates.
- `scripts/contract_gates/` — provisionamento/verificação das ferramentas externas usadas pelos gates.
- `scripts/git-hooks/` — hooks do git.

## Nota de escopo

Scripts de operações, DB, seeds e automações locais podem existir neste diretório, mas **não** podem introduzir uma governança paralela à trilogia `.contract_driven/*`.
