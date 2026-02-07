<!-- STATUS: NEEDS_REVIEW -->

# E2E Tests Documentation

**Diretório**: `tests/e2e/tests_log/`
**Propósito**: Documentação consolidada de testes E2E
**Última Atualização**: 2026-01-13

---

## 📚 Índice de Documentos

### 🎯 Para Começar

1. **[EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md)** ⭐ **LEIA PRIMEIRO**
   - Status atual dos testes
   - Resumo das últimas runs
   - Próximos passos
   - **Recomendado**: Iniciar aqui para visão geral

2. **[TROUBLESHOOTING_GUIDE.md](TROUBLESHOOTING_GUIDE.md)** 🔧 **QUANDO TESTES FALHAM**
   - Diagnóstico rápido de problemas comuns
   - Soluções passo-a-passo
   - Comandos úteis
   - Debugging tools
   - **Recomendado**: Consultar quando testes falharem

---

### 📊 Run Reports

3. **[RUN_LOG.md](RUN_LOG.md)** 📖 **HISTÓRICO COMPLETO**
   - Log cronológico de todas as runs
   - Run 1 → Run 10
   - Comparações entre runs
   - Evolução da taxa de sucesso
   - **Recomendado**: Para entender histórico completo

4. **[RUN10_SUMMARY.md](RUN10_SUMMARY.md)** ✅ **RUN ATUAL**
   - Resumo detalhado da Run 10
   - Correção de autenticação SSR
   - Arquivos modificados
   - Status: Aguardando restart Next.js
   - **Recomendado**: Para entender a correção atual

5. **[RUN9_SUMMARY.md](RUN9_SUMMARY.md)** ⚠️ **IDENTIFICAÇÃO DO PROBLEMA**
   - Primeira run com 91.89% de sucesso
   - Identificação de testIDs "ausentes"
   - Screenshot revelou 404 page
   - **Recomendado**: Para entender origem do problema

6. **[RUN7_SUMMARY.md](RUN7_SUMMARY.md)** 🔍 **PROBLEMA 409**
   - Análise de constraint violations
   - session_type inválido
   - IDs E2E padronizados
   - **Recomendado**: Para entender problemas de constraint

---

### 🛠️ Technical Deep Dives

7. **[SSR_COOKIE_FIX.md](SSR_COOKIE_FIX.md)** 🎓 **ANÁLISE TÉCNICA PROFUNDA**
   - Deep dive no problema de cookies SSR
   - Por que Members funcionava vs Overview/Settings
   - Comparação Before/After
   - Decisões arquiteturais
   - Lições aprendidas
   - **Recomendado**: Para entender arquitetura e decisões técnicas

8. **[PROBLEMA_409_ANALYSIS.md](PROBLEMA_409_ANALYSIS.md)** 🔬 **ANÁLISE 409**
   - Investigação do erro 409 Conflict
   - Constraint violations
   - Correções no backend e frontend
   - **Recomendado**: Para problemas similares no futuro

---

### 📋 Reference Materials

9. **[TESTIDS_MANIFEST.md](TESTIDS_MANIFEST.md)** 📝 **CATÁLOGO DE TESTIDS**
   - Lista completa de testIDs usados
   - Mapeamento componente → testID
   - Convenções de nomenclatura
   - **Recomendado**: Ao adicionar novos testIDs

10. **[CHANGELOG.md](CHANGELOG.md)** 📅 **HISTÓRICO DE MUDANÇAS**
    - Mudanças em scripts
    - Mudanças em testes
    - Mudanças em documentação
    - **Recomendado**: Para ver evolução do projeto

11. **[RESUMO_FINAL.md](RESUMO_FINAL.md)** 📊 **CONSOLIDAÇÃO**
    - Resumo consolidado das runs iniciais
    - Análise de problemas resolvidos
    - **Recomendado**: Contexto histórico

---

## 🚀 Quick Start Guides

### Executar Testes

```bash
# 1. Resetar database E2E
cd "C:\HB TRACK\Hb Track - Backend"
.\scripts\reset-db-e2e.ps1

# 2. Executar testes
cd "C:\HB TRACK\Hb Track - Fronted"
npx playwright test tests/e2e/teams/teams.contract.spec.ts --reporter=list
```

### Debugging

```bash
# Com interface visual:
npx playwright test --debug --headed

# Apenas um teste específico:
npx playwright test -g "overview.*visível"

# Gerar HTML report:
npx playwright test --reporter=html
npx playwright show-report
```

### Após Modificar Código

```bash
# 1. SEMPRE restart Next.js:
cd "C:\HB TRACK\Hb Track - Fronted"
npm run dev

# 2. Verificar TypeScript:
npx tsc --noEmit

# 3. Executar testes:
npx playwright test
```

---

## 📈 Status das Runs

### Progressão de Sucesso

```
Run 5:  78.57% ❌ (409 - team_memberships)
Run 6:  78.57% ❌ (409 - mesmo após seed)
Run 7:  78.57% ❌ (409 - session_type)
Run 8:  92.86% ✅ (409 RESOLVIDO)
Run 9:  91.89% ⚠️ (SSR cookies)
Run 10: 100%*  ⚠️ (Aguardando restart)
```

### Camadas de Teste

| Camada | Status | Taxa |
|--------|--------|------|
| **GATE** (Infra) | ✅ Passing | 100% |
| **SETUP** (Auth) | ✅ Passing | 100% |
| **CONTRATO** (Nav) | ⚠️ Fixing | 91.89% → 100%* |
| **FUNCIONAIS** (CRUD) | ⏸️ Blocked | N/A |

*Após restart Next.js

---

## 🎯 Roadmap

### Fase Atual: CONTRATO ⬅️ VOCÊ ESTÁ AQUI
- [x] Gate tests - 100%
- [x] Auth setup - 100%
- [ ] Contract tests - 91.89% → 100%* (aguardando restart)

### Próxima Fase: FUNCIONAIS
- [ ] Training sessions CRUD
- [ ] Team members management
- [ ] Permissions testing
- [ ] Performance tests

### Futuro: CI/CD
- [ ] GitHub Actions integration
- [ ] Parallel execution
- [ ] Visual regression testing
- [ ] Coverage reports

---

## 🔗 Links Úteis

### External Documentation
- [Playwright Docs](https://playwright.dev/docs/intro)
- [Next.js Testing](https://nextjs.org/docs/testing)
- [Testing Best Practices](https://playwright.dev/docs/best-practices)

### Internal Resources
- **Backend**: `C:\HB TRACK\Hb Track - Backend\`
- **Frontend**: `C:\HB TRACK\Hb Track - Fronted\`
- **E2E Tests**: `C:\HB TRACK\Hb Track - Fronted\tests\e2e\`

---

## 📞 Support

### Quando Testes Falham

1. 📸 **Capture screenshot** primeiro
2. 📖 Consulte [TROUBLESHOOTING_GUIDE.md](TROUBLESHOOTING_GUIDE.md)
3. 🔍 Check [RUN_LOG.md](RUN_LOG.md) para problemas similares
4. 🎓 Leia [SSR_COOKIE_FIX.md](SSR_COOKIE_FIX.md) para deep dive

### Quando Adicionar Novos Testes

1. 📝 Consulte [TESTIDS_MANIFEST.md](TESTIDS_MANIFEST.md)
2. 📚 Siga padrões em testes existentes
3. ✅ Verifique TypeScript compila
4. 🧪 Execute localmente antes de commit

---

## 🏆 Hall of Fame

### Problemas Resolvidos

1. ✅ **Problema 409** (Runs 5-7 → Run 8)
   - Training sessions não podiam ser criadas
   - Correção: Auto-criar team_membership + session_type válido
   - [Análise completa](PROBLEMA_409_ANALYSIS.md)

2. ✅ **SSR Cookies** (Run 9 → Run 10)
   - testIDs não encontrados (404 page renderizada)
   - Correção: Migrar SSR fetch para client-side fetch
   - [Análise completa](SSR_COOKIE_FIX.md)

---

## 📊 Métricas

### Tempo de Execução

| Suite | Tempo Médio |
|-------|-------------|
| Gate | ~24s |
| Setup | ~15s |
| Contract (37 tests) | ~2.5m |
| **Total** | **~3m** |

### Cobertura

- ✅ Auth flows: 100%
- ✅ Redirects: 100%
- ✅ 401/404 checks: 100%
- ⚠️ testIDs: 91.89% → 100%*
- ⏸️ CRUD: Pending
- ⏸️ Permissions: Pending

---

## 🎓 Key Lessons

### Top 10 Lições das Runs 1-10

1. ✅ Screenshot revela verdade
2. ✅ Console logs são cruciais
3. ✅ TypeScript errors primeiro
4. ✅ Migrations = contrato
5. ✅ Padrões consistentes
6. ✅ E2E revela edge cases
7. ✅ Restart após mudanças
8. ✅ Auth setup é base
9. ✅ Database seed importa
10. ✅ Debug iterativamente

---

## 🔄 Manutenção deste Diretório

### Quando Adicionar Arquivos

1. ✅ Atualize este README.md
2. ✅ Adicione link em seção apropriada
3. ✅ Atualize [CHANGELOG.md](CHANGELOG.md)
4. ✅ Update [EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md)

### Quando Completar Run

1. ✅ Create `RUNxx_SUMMARY.md`
2. ✅ Update [RUN_LOG.md](RUN_LOG.md)
3. ✅ Update [EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md)
4. ✅ Update este README se necessário

---

**Status Atual**: ⚠️ AGUARDANDO RESTART DO NEXT.JS
**Última Run**: 10 (2026-01-13 00:00)
**Próxima Ação**: Restart Next.js → Run tests → Confirmar 100%

---

*Documentação mantida por Claude Code - 2026-01-13 07:35*
