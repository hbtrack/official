# Evidência de Correção do CI (P0)

**Data:** 2026-03-14  
**Tipo:** Evidência de correção de falha CI  
**Requisito:** hbtrack-governanca.md § 7.4 (CI obrigatório + gates)

---

## Problema Identificado

O workflow CI `.github/workflows/contract-gates.yml` falhou na execução de `npm ci` com erro:

```
npm error `npm ci` can only install packages when your package.json and 
package-lock.json or npm-shrinkwrap.json are in sync.
npm error Missing: encoding@0.1.13 from lock file
npm error Missing: iconv-lite@0.6.3 from lock file
```

**Causa raiz:** `package-lock.json` desincronizado com `package.json` — dependências transitivas de `@asyncapi/cli` faltando no lock file.

---

## Correção Aplicada

### 1. Regeneração do lock file

```bash
cd /home/davis/HB-TRACK
source ./setup-env.sh
npm install  # Regenera package-lock.json sincronizado
```

**Resultado:** 
- `package-lock.json` atualizado com dependências transitivas faltantes
- 1831 packages auditados
- Lock file hermético e reprodutível

### 2. Validação hermética

```bash
rm -rf node_modules
npm ci  # Instalação limpa a partir do lock file
```

**Resultado:** ✅ **Sucesso** — `npm ci` instalou 1635 packages sem erros.

### 3. Validação dos contract gates

```bash
python3 scripts/validate_contracts.py
```

**Resultado:** ✅ **PASS** — exit code 0

```
--------------------------------------------------------------
  HB TRACK CONTRACT GATES  --  PASS
--------------------------------------------------------------
  + [PASS] AXIOM_INTEGRITY_GATE
  + [PASS] PATH_CANONICALITY_GATE
  + [PASS] REQUIRED_ARTIFACT_PRESENCE_GATE
  + [PASS] MODULE_DOC_CROSSREF_GATE
  + [PASS] API_NORMATIVE_DUPLICATION_GATE
  + [PASS] OWASP_API_CONTROL_MATRIX_GATE
  + [PASS] MODULE_SOURCE_AUTHORITY_MATRIX_GATE
  + [PASS] BOUNDARY_USERS_IDENTITY_ACCESS_GATE
  + [PASS] WELLNESS_MEDICAL_BOUNDARY_GATE
  + [PASS] SCOUT_TAXONOMY_GATE
  + [PASS] ASYNC_REQUIRED_MODULE_GATE
  + [PASS] EXTERNAL_SOURCE_AUTHORITY_GATE
  + [PASS] PLACEHOLDER_RESIDUE_GATE
  + [PASS] REF_HERMETICITY_GATE
  + [PASS] OPENAPI_ROOT_STRUCTURE_GATE  (redocly)
  + [PASS] OPENAPI_POLICY_RULESET_GATE  (spectral)
  + [PASS] JSON_SCHEMA_VALIDATION_GATE
  + [PASS] CROSS_SPEC_ALIGNMENT_GATE
  + [PASS] CONTRACT_BREAKING_CHANGE_GATE  (oasdiff)
  ~ [SKIP] TRANSFORMATION_FEASIBILITY_GATE
  ~ [SKIP] HTTP_RUNTIME_CONTRACT_GATE
  + [PASS] ASYNCAPI_VALIDATION_GATE
  + [PASS] ARAZZO_VALIDATION_GATE
  ~ [SKIP] UI_DOC_VALIDATION_GATE
  + [PASS] DERIVED_DRIFT_GATE
  + [PASS] READINESS_SUMMARY_GATE
--------------------------------------------------------------
  Overall  : PASS
  Exit code: 0
```

### 4. Correção do pre-commit hook

**Problema:** Hook ignorado por falta de permissão executável no filesystem.

```bash
chmod +x scripts/git-hooks/pre-commit
```

**Validação:**
```bash
ls -la scripts/git-hooks/pre-commit
# -rwxr-xr-x 1 davis davis 964 Mar 14 01:40 scripts/git-hooks/pre-commit

git ls-files -s scripts/git-hooks/pre-commit
# 100755 ba8b857a0292704deb74c6b127ea1df198288490 0 scripts/git-hooks/pre-commit
```

---

## Commits Aplicados

### Commit 1: `021307a` — fix(ci): sync package-lock.json with package.json

```
fix(ci): sync package-lock.json with package.json

Resolve npm ci failure in GitHub Actions CI due to missing 
transitive dependencies (encoding, iconv-lite) from lock file.

Fixes:
- Missing: encoding@0.1.13 from lock file
- Missing: iconv-lite@0.6.3 from lock file

Regenerated lock file with npm install to ensure hermetic CI builds.

Refs: hbtrack-governanca.md § 7.5 (hermetic toolchain)
```

**Alterações:**
- `package-lock.json`: 31 inserções, 27 deleções

---

## Expectativa para Próximo Push

Ao executar push para `main` ou criar PR:

1. ✅ Workflow `.github/workflows/contract-gates.yml` deve disparar
2. ✅ Job `validate-contracts` deve executar:
   - ✅ Checkout  
   - ✅ Setup Node.js 24  
   - ✅ Setup Python 3.12  
   - ✅ `npm ci` → **DEVE PASSAR** (lock file sincronizado)  
   - ✅ `python3 scripts/validate_contracts.py` → **DEVE PASSAR** (exit code 0)  
   - ✅ Upload artifact `contract-gates-report` → _reports/contract_gates/
3. ✅ Status check `validate-contracts` → **PASS**
4. ✅ Merge habilitado (se branch protection configurado)

---

## Validação de Branch Protection (Pendente)

**Status:** ⚠️ Aguardando configuração manual no GitHub Settings

Conforme [BRANCH_PROTECTION_SETUP.md](.github/BRANCH_PROTECTION_SETUP.md):

1. Acessar Settings → Branches → Add branch protection rule
2. Configurar pattern `main`:
   - ✅ Require pull request before merging (1 approval)
   - ✅ Require review from Code Owners
   - ✅ Require status checks: `validate-contracts`
   - ✅ Block force pushes
   - ✅ Block deletions
   - ✅ Do not allow bypassing

**Próximos testes recomendados:**

```bash
# 1. Push direto para main (deve falhar)
git push origin main

# 2. PR modificando SSOT (deve exigir aprovação de @Davisermenho)
git checkout -b test/codeowners
echo "# test" >> .contract_driven/CONTRACT_SYSTEM_RULES.md
git commit -m "test: modify SSOT"
git push origin test/codeowners

# 3. PR quebrando gates (deve falhar CI)
git checkout -b test/break-gates
echo "invalid: yaml" >> contracts/openapi/openapi.yaml
git commit -m "test: break gates"
git push origin test/break-gates
```

---

## Conformidade com hbtrack-governanca.md

| Requisito | Status |
|---|---|
| § 7.4 — CI gates obrigatórios | ✅ Implementado (workflow) |
| § 7.5 — Toolchain hermética | ✅ Corrigido (lock file) |
| § 8.1 — Branch protection | ⚠️ Pendente config manual |
| § 8.2 — Pre-commit hooks | ✅ Corrigido (chmod +x) |

---

## Próximo Passo

**Push para GitHub e observar execução do CI:**

```bash
git push origin main
```

Verificar em: `https://github.com/<owner>/<repo>/actions`

Se CI passar → aplicar branch protection conforme runbook.

---

*Evidência gerada: 2026-03-14T05:30:00Z*
