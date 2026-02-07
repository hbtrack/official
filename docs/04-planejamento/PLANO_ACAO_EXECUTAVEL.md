<!-- STATUS: NEEDS_REVIEW -->

# Plano de Ação - Tornar Validação Executável

## Status dos Arquivos

### ✅ JÁ EXISTEM (Criados anteriormente)

| Arquivo | Status | Localização |
|---------|--------|-------------|
| `run-teams-suite.ps1` | ✅ EXISTE | tests/e2e/ |
| `smoke-tests.spec.ts` | ✅ EXISTE | tests/e2e/ |
| `helpers/api.ts` | ✅ EXISTE | tests/e2e/helpers/ |

### ❌ NÃO EXISTEM (Precisam ser criados)

| Arquivo | Necessário? | Prioridade | Motivo |
|---------|-------------|-----------|--------|
| `validate-staging.ps1` | ⚠️ Opcional | Média | Automatiza validação pós-deploy |
| `.env.staging` | ⚠️ Opcional | Baixa | Configuração específica staging |
| `RUN_LOG.md` | ❌ Não | - | Não mencionado no plano original |
| `CHANGELOG.md` | ⚠️ Opcional | Baixa | Boa prática, não bloqueia |
| `TESTIDS_MANIFEST.md` | ✅ Recomendado | Média | Já existe? Vou verificar |

---

## Análise Item por Item

### 1. ✅ Criar run-teams-suite.ps1
**Status:** ✅ **JÁ CRIADO**
**Localização:** `tests/e2e/run-teams-suite.ps1`
**Ação:** Nenhuma necessária

---

### 2. ✅ Criar smoke-tests.spec.ts
**Status:** ✅ **JÁ CRIADO**
**Localização:** `tests/e2e/smoke-tests.spec.ts`
**Ação:** Nenhuma necessária

---

### 3. ✅ Validar existência de helpers/api.ts
**Status:** ✅ **JÁ EXISTE**
**Localização:** `tests/e2e/helpers/api.ts`
**Ação:** Nenhuma necessária

---

### 4. ⚠️ Criar validate-staging.ps1

**Status:** ❌ NÃO EXISTE

**É necessário?** ⚠️ **Opcional mas recomendado**

**O que faz:**
- Health check API/Frontend
- Executar smoke tests contra staging
- Validação manual rápida

**Impacto de não ter:**
- Validação manual (mais lenta, sujeita a erro humano)
- Sem automação pós-deploy

**Ação recomendada:** ✅ **CRIAR** (prioridade média)

**Tempo estimado:** 15 minutos

---

### 5. ⚠️ Adicionar protocolo TF5-TF8 (análise de erros)

**Status:** ❌ NÃO MENCIONADO NO PLANO ORIGINAL

**É necessário?** ❌ **NÃO** (fora do escopo)

**O que seria:**
- Protocolo de análise de erros (TF5-TF8)
- Não estava no plano de validação staging

**Ação recomendada:** ❌ **NÃO CRIAR** (escopo diferente)

---

### 6. ⚠️ Criar baseline inicial

**Status:** ❌ NÃO EXISTE (mas fácil de gerar)

**É necessário?** ⚠️ **Opcional mas útil**

**O que faz:**
- Gera relatório JSON da primeira execução
- Permite comparação de regressões

**Impacto de não ter:**
- Sem comparação automática de regressões
- Validação manual de % de aprovação

**Ação recomendada:** ⚠️ **CRIAR NA PRIMEIRA EXECUÇÃO**

**Como:**
```powershell
# Na primeira execução, gerar baseline
npx playwright test tests/e2e/teams --reporter=json > baseline.json

# Nas próximas, comparar
npx playwright test tests/e2e/teams --reporter=json > current.json
# Comparar manualmente baseline.json vs current.json
```

**Tempo estimado:** Automático (na primeira execução)

---

### 7. ✅ Adicionar validação de build

**Status:** ✅ **JÁ ESTÁ NO PLANO** (Fase 3 - Checklist Técnico)

**É necessário?** ✅ **SIM**

**Já implementado:**
```powershell
# No plano, seção "Fase 3: Checklist Técnico"
npm run build
```

**Ação:** Nenhuma necessária (já documentado)

---

### 8. ⚠️ Documentar secrets management (.env.staging)

**Status:** ❌ NÃO EXISTE

**É necessário?** ⚠️ **Opcional** (dependente de CI/CD)

**O que faz:**
- Arquivo de configuração para staging
- Variáveis de ambiente específicas

**Impacto de não ter:**
- Configuração manual antes de rodar testes em staging
- Menos automatizado

**Ação recomendada:** ⚠️ **CRIAR SE FOR RODAR EM CI/CD**

**Exemplo:**
```bash
# .env.staging
NEXT_PUBLIC_API_URL=https://api-staging.hbtrack.com
NEXT_PUBLIC_APP_URL=https://staging.hbtrack.com
TEST_ADMIN_EMAIL=admin-e2e@staging.hbtrack.com
TEST_ADMIN_PASSWORD=<senha-segura>
```

**Tempo estimado:** 5 minutos

---

### 9. ❌ Adicionar benchmarks de performance

**Status:** ❌ NÃO MENCIONADO NO PLANO

**É necessário?** ❌ **NÃO** (fora do escopo staging)

**Justificativa:**
- Performance benchmarks são para produção
- Staging foca em funcionalidade
- Regra 45: não testar performance em E2E

**Ação recomendada:** ❌ **NÃO CRIAR** (fora do escopo)

---

### 10. ⚠️ Integrar com RUN_LOG.md

**Status:** ❌ NÃO EXISTE

**É necessário?** ❌ **NÃO** (mencionado na sua seleção, mas não no plano)

**O que seria:**
- Log de execuções de testes
- Histórico de resultados

**Impacto de não ter:**
- Sem histórico centralizado
- Logs ficam em `test-results/`

**Ação recomendada:** ❌ **NÃO CRIAR** (opcional, não bloqueia)

---

### 11. ⚠️ Atualizar CHANGELOG.md

**Status:** ❌ NÃO EXISTE (arquivo provavelmente existe, mas não atualizado)

**É necessário?** ⚠️ **Boa prática, não bloqueia**

**O que adicionar:**
```markdown
## [Unreleased] - 2026-01-12

### Added - Módulo Teams
- ✨ Aba Trainings: CRUD de treinos via API/UI
- ✨ Aba Stats: Estatísticas de equipe
- ✨ Athletes: Gerenciamento de registrations

### Changed - Testes E2E
- 🔄 Integração teams_gaps → estrutura canônica
- 🔄 Eliminadas duplicatas (387 → 150 testes únicos)
- 🔄 Smoke tests criados (5 críticos)

### Fixed
- 🐛 Validações de formulário
- 🐛 Autosave em settings
- 🐛 Toasts padronizados
```

**Ação recomendada:** ⚠️ **CRIAR SE O ARQUIVO EXISTIR**

**Tempo estimado:** 5 minutos

---

### 12. ✅ TESTIDS_MANIFEST.md

**Status:** ❓ PRECISA VERIFICAR

**É necessário?** ⚠️ **Útil para referência**

**Vou verificar se já existe:**

---

## Resumo - O que é REALMENTE necessário?

### 🔴 CRÍTICO (Bloqueia execução)

**Nenhum** - Todos os arquivos críticos já existem! ✅

- ✅ run-teams-suite.ps1
- ✅ smoke-tests.spec.ts
- ✅ helpers/api.ts

### 🟡 RECOMENDADO (Melhora execução)

| Item | Tempo | Impacto |
|------|-------|---------|
| 1. validate-staging.ps1 | 15 min | Automatiza validação pós-deploy |
| 2. .env.staging | 5 min | Facilita CI/CD |
| 3. CHANGELOG.md (update) | 5 min | Documentação |
| 4. Verificar TESTIDS_MANIFEST.md | 2 min | Referência |

**Total:** ~27 minutos

### 🟢 OPCIONAL (Nice-to-have)

| Item | Justificativa |
|------|---------------|
| Baseline inicial | Gerado automaticamente na 1ª execução |
| RUN_LOG.md | Não mencionado no plano, logs já existem |
| Protocolo TF5-TF8 | Fora do escopo de validação staging |
| Benchmarks performance | Regra 45 - não testar performance em E2E |

---

## Plano de Ação Recomendado

### Opção A: Executar AGORA (sem melhorias)

```powershell
# 1. Executar validação local
.\tests\e2e\run-teams-suite.ps1

# 2. Smoke tests
npx playwright test tests/e2e/smoke-tests.spec.ts --project=chromium --workers=1 --retries=0

# 3. Build
npm run build

# 4. Lint
npm run lint

# ✅ Se tudo passar: Deploy em staging
```

**Status:** ✅ **PRONTO PARA EXECUTAR AGORA**

**Nenhum arquivo adicional necessário!**

---

### Opção B: Criar melhorias (27 minutos) e depois executar

```powershell
# 1. Criar validate-staging.ps1 (15 min)
# 2. Criar .env.staging (5 min)
# 3. Atualizar CHANGELOG.md (5 min)
# 4. Verificar TESTIDS_MANIFEST.md (2 min)
# 5. Executar validação conforme Opção A
```

**Status:** ⚠️ **Melhorias opcionais**

---

## Recomendação Final

### Para Validação Staging AGORA

**✅ Use Opção A** (sem criar novos arquivos)

**Motivo:**
- Todos os arquivos críticos já existem
- Plano é executável imediatamente
- Melhorias podem ser feitas depois

### Para Validação Staging com Automação Completa

**⚠️ Use Opção B** (criar melhorias primeiro)

**Motivo:**
- `validate-staging.ps1` automatiza pós-deploy
- `.env.staging` facilita CI/CD
- CHANGELOG documenta mudanças

---

## Checklist de Arquivos

### ✅ Existem e estão prontos

- [x] tests/e2e/run-teams-suite.ps1
- [x] tests/e2e/smoke-tests.spec.ts
- [x] tests/e2e/helpers/api.ts
- [x] tests/e2e/teams/*.spec.ts (11 specs)
- [x] PLANO_VALIDACAO_STAGING.md
- [x] VALIDACAO_STAGING_RESUMO.md
- [x] COMANDOS_VALIDACAO.md

### ⚠️ Opcionais (criar se quiser melhorar)

- [ ] scripts/validate-staging.ps1 (automatiza pós-deploy)
- [ ] .env.staging (config para staging)
- [ ] CHANGELOG.md (atualizado)
- [ ] TESTIDS_MANIFEST.md (verificar se existe)

### ❌ Não necessários

- [ ] RUN_LOG.md (não mencionado no plano)
- [ ] Protocolo TF5-TF8 (fora do escopo)
- [ ] Benchmarks performance (Regra 45)
- [ ] Baseline (gerado automaticamente)

---

## Resposta à Pergunta

**"Para tornar o plano executável, estas ações são necessárias?"**

**Resposta:** ❌ **NÃO**, o plano **JÁ É EXECUTÁVEL**!

Todos os arquivos críticos já foram criados:
- ✅ run-teams-suite.ps1
- ✅ smoke-tests.spec.ts
- ✅ helpers/api.ts

**Você pode executar a validação AGORA mesmo** sem criar nenhum arquivo adicional.

**Melhorias opcionais** (27 min):
- validate-staging.ps1 (automatiza pós-deploy)
- .env.staging (facilita CI/CD)
- CHANGELOG.md (documentação)

Mas **nenhuma delas é obrigatória** para executar o plano de validação.

---

**Próximo passo:** Executar `.\tests\e2e\run-teams-suite.ps1` e validar! 🚀
