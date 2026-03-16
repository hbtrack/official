# Quick Setup — Solo Dev (CI-only enforcement)

**Última atualização:** 2026-03-14  
**Requisito:** `hbtrack-governanca.md` § 8.1

## Objetivo

Habilitar enforcement server-side “sem bypass” para contratos/SSOT em cenário **solo developer**:
- mudanças somente via PR;
- **CI obrigatório** como required check;
- bypass permitido apenas para admins (emergências).

## Pré-requisitos (no repo)

- Workflow: `.github/workflows/contract-gates.yml`
- CODEOWNERS: `.github/CODEOWNERS`

## Passo a passo (GitHub UI)

1) `Settings → Rules → Rulesets → New ruleset`
2) Target branches:
   - `main`
   - `develop`
3) Regras mínimas:
   - ✅ Require a pull request before merging (**approvals: 0**)
   - ✅ Require status checks to pass:
     - `Contract Gates / Validate Contract Gates` (pull_request)
   - ✅ Require branches to be up to date
   - ✅ Block force pushes
   - ✅ (Opcional) Block deletions
   - ✅ Allow bypassing settings: **Admins only**

## Validação rápida (prova de enforcement)

1) Push direto em `main` deve falhar (GH013).
2) PR com gate FAIL deve bloquear merge.
3) PR com gate PASS deve permitir merge.

## Quando virar time

Trocar approvals para ≥ 1 e manter CODEOWNERS obrigatório para SSOT.

## Referência

Runbook completo: `.github/BRANCH_PROTECTION_SETUP.md`
