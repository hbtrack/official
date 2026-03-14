# Configuração de Branch Protection

**Tipo:** Runbook de configuração  
**Última atualização:** 2026-03-14  
**Requisito:** hbtrack-governanca.md § 8.1

---

## Objetivo

Estabelecer enforcement server-side incontornável para garantir que contratos e SSOT não sejam quebrados sem revisão obrigatória.

---

## Pré-requisitos

- Permissões de administrador no repositório GitHub `hbtrack/official`
- Workflow `.github/workflows/contract-gates.yml` configurado e funcional
- Arquivo `.github/CODEOWNERS` criado

---

## Configuração de Branch Protection

### 1. Acessar configurações do repositório

```
GitHub → Repositório → Settings → Branches → Add branch protection rule
```

### 2. Configurar proteção para `main`

**Pattern:** `main`

#### 2.1 Require a pull request before merging

- ✅ **Require a pull request before merging** 
  - ✅ **Require approvals:** 1 approval mínimo
  - ✅ **Dismiss stale pull request approvals when new commits are pushed**
  - ✅ **Require approval of the most recent reviewable push**
  - ✅ **Require review from Code Owners** (crítico para CODEOWNERS)

#### 2.2 Require status checks to pass before merging

- ✅ **Require status checks to pass before merging**
  - ✅ **Require branches to be up to date before merging**
  - **Status checks required:**
    - `validate-contracts` (do workflow contract-gates.yml)

#### 2.3 Require conversation resolution before merging

- ✅ **Require conversation resolution before merging**

#### 2.4 Do not allow bypassing the above settings

- ✅ **Do not allow bypassing the above settings**
  - ⚠️ Remover exceções de administradores (enforcement absoluto)

#### 2.5 Restrict who can push to matching branches

- ✅ **Restrict who can push to matching branches**
  - Nenhum usuário pode fazer push direto
  - Apenas via PR aprovado

#### 2.6 Block force pushes

- ✅ **Block force pushes** (crítico para auditoria)

#### 2.7 Block deletions

- ✅ **Block deletions** (proteção contra perda acidental)

---

### 3. Configurar proteção para `develop` (opcional, mas recomendado)

**Pattern:** `develop`

Aplicar as mesmas regras de `main`, exceto:
- Permitir que `develop` requeira apenas reviews automáticas (sem CODEOWNERS obrigatório)
- Manter `validate-contracts` como check obrigatório

---

## Validação

Após configuração, validar:

### 1. Tentar push direto para `main` (deve falhar)

```bash
git checkout main
git commit --allow-empty -m "test: direct push"
git push origin main
```

**Esperado:** `ERROR: Branch protection rules prevent direct push`

### 2. Criar PR modificando SSOT sem aprovação de codeowner (deve bloquear merge)

```bash
git checkout -b test/codeowners
echo "# test" >> .contract_driven/CONTRACT_SYSTEM_RULES.md
git add .
git commit -m "test: modify SSOT"
git push origin test/codeowners
```

Criar PR no GitHub. **Esperado:** merge bloqueado até aprovação do(s) codeowner(s) configurado(s)

### 3. Criar PR que quebra contract gates (deve falhar CI)

```bash
git checkout -b test/break-contract
echo "invalid: yaml" >> contracts/openapi/openapi.yaml
git add .
git commit -m "test: break contract"
git push origin test/break-contract
```

Criar PR no GitHub. **Esperado:** 
- ❌ Status check `validate-contracts` falha
- 🚫 Merge bloqueado

---

## Troubleshooting

### Status check não aparece como obrigatório

1. Workflow precisa ter rodado pelo menos uma vez na branch protegida
2. Aguardar primeiro PR ou push para `main`/`develop` com workflow ativo
3. Verificar em Settings → Branches → Edit rule → Status checks

### CODEOWNERS não está funcionando

1. Verificar formato do arquivo `.github/CODEOWNERS`
2. Username GitHub deve ser precedido por `@`
3. Usuário deve ter permissão de escrita no repositório
4. Branch protection rule deve ter **"Require review from Code Owners"** habilitado

### Administrators podem bypassar proteções

- Por padrão, administradores podem ignorar branch protection
- Desabilitar em: Branch protection rule → **"Do not allow bypassing the above settings"**
- Remover exceção de administradores na seção "Allow specified actors to bypass required pull requests"

---

## Conformidade

Esta configuração atende:

- ✅ hbtrack-governanca.md § 8.1 — Controles incontornáveis (server‑side)
- ✅ hbtrack-governanca.md § 8.2 — CI fail‑closed
- ✅ hbtrack-governanca.md § 8.3 — Evidência de gates como artefato CI

---

## Referências

- [GitHub: About branch protection rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [GitHub: About CODEOWNERS](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)
- [GitHub: Required status checks](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/collaborating-on-repositories-with-code-quality-features/about-status-checks)
