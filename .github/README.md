# .github

Configuração de governança e enforcement para o repositório HB Track.

## Estrutura

```
.github/
├── CODEOWNERS                    # Ownership obrigatório de artefatos normativos
├── BRANCH_PROTECTION_SETUP.md    # Runbook de configuração de branch protection
└── workflows/
    └── contract-gates.yml        # CI para validação de contratos
```

## Componentes

### CODEOWNERS

Define ownership obrigatório para:
- Sistema contract-driven (`.contract_driven/**`)
- Contratos técnicos (`contracts/**`)
- Documentação canônica (`docs/_canon/**`)
- Scripts de validação (`scripts/validate_contracts.py`, `scripts/contracts/validate/**`)

**Efeito:** PRs que modificam estes arquivos requerem aprovação explícita do(s) owner(s).

### workflows/contract-gates.yml

Workflow CI que:
- Roda em push/PR para `main` e `develop`
- Executa `python3 scripts/validate_contracts.py`
- Publica `_reports/contract_gates/` como artefato
- Bloqueia merge em caso de falha

**Status check:** `validate-contracts` (obrigatório em branch protection)

### BRANCH_PROTECTION_SETUP.md

Runbook detalhado para configuração de branch protection rules no GitHub, incluindo:
- Required status checks (`validate-contracts`)
- Required reviews (incluindo CODEOWNERS)
- Bloqueio de force-push e deleções
- Validação e troubleshooting

## Conformidade

Este setup atende aos requisitos de **hbtrack-governanca.md § 8.1**:

- ✅ Branch protection + required status checks
- ✅ CODEOWNERS para SSOT
- ✅ Bloqueio de force-push
- ✅ CI fail-closed

## Próximos passos

1. **Aplicar branch protection rules** seguindo [BRANCH_PROTECTION_SETUP.md](BRANCH_PROTECTION_SETUP.md)
2. **Validar enforcement** com testes de push direto e PR sem aprovação
3. **Evoluir CI** com adicionar gates de tool version, drift detection, etc.

---

*Implementado: 2026-03-14*
