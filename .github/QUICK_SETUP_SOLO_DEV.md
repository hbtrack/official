# Quick Setup: Branch Protection (Solo Developer)

**Tempo estimado:** 3 minutos  
**Para quem:** Desenvolvedor solo com enforcement real de CI

---

## ⚡ Configuração Rápida

### 1. Acesse as Configurações

```
https://github.com/hbtrack/official/settings/rules
```

Ou navegue: **Settings** → **Rules** → **Rulesets** (ou **Branches**)

---

### 2. Edite a Regra para `main`

Clique na regra existente para `main` (ou crie uma nova).

---

### 3. Configure Exatamente Assim

#### ✅ Require a pull request before merging
- **Required number of approvals:** `0`
- ❌ Dismiss stale pull request approvals: **Desabilitado**
- ❌ Require approval of the most recent push: **Desabilitado**
- ❌ Require review from Code Owners: **Desabilitado**

#### ✅ Require status checks to pass before merging
- ✅ **Habilitado**
- ✅ Require branches to be up to date before merging
- **Status checks required:**
  - `Contract Gates / Validate Contract Gates (pull_request)` ✅

#### ✅ Require conversation resolution before merging
- ✅ **Habilitado**

#### ❌ Require deployments to succeed
- ❌ **Desabilitado** (não aplicável)

#### ✅ Block force pushes
- ✅ **Habilitado**

#### ✅ Require linear history
- ⚠️ **Opcional** (seu critério)

#### ❌ Do not allow bypassing the above settings
- ❌ **Desabilitado** (permitir bypass para admin em emergências)

---

### 4. Salvar

Clique em **"Save changes"** ou **"Update"**

---

## ✅ Validação

### Teste 1: Push direto bloqueado

```bash
git checkout main
git commit --allow-empty -m "test: direct push"
git push origin main
```

**Esperado:** ❌ Erro: `Branch protection rules prevent direct push`

---

### Teste 2: PR com CI passando → Merge permitido

1. Vá no PR atual: https://github.com/hbtrack/official/pull/1
2. **CI deve estar verde** ✅
3. **Botão "Merge pull request" deve estar habilitado** ✅
4. **Não deve pedir aprovações** ✅

---

## 🎯 O que Isso Garante?

| Proteção | Como Funciona |
|---|---|
| **CI obrigatório** | Nenhum código entra em `main` sem passar em 25 gates |
| **Histórico limpo** | Todo merge via PR (rastreável) |
| **Sem bloqueio artificial** | 0 aprovações — você pode mergear após CI passar |
| **Audit trail** | Force-push bloqueado = histórico íntegro |
| **Emergências** | Admin bypass disponível se necessário |

---

## 🚀 Próximo Passo

Após configurar, faça merge do PR #1:

1. https://github.com/hbtrack/official/pull/1
2. Verificar: ✅ CI passou
3. Clicar: **"Merge pull request"**
4. Confirmar: **"Confirm merge"**

**Enforcement P0 estará 100% completo!** 🎉

---

*Configuração otimizada para: desenvolvedor solo + enforcement real*
