# DEPRECATED_PATTERNS — HB Track (Referência Histórica)

**Status:** LEGACY (fora do escopo de auditoria dos gates)  
**Objetivo:** Preservar conhecimento histórico de paths, comandos e padrões obsoletos sem contaminar gates binários.

---

## 📋 Regras de Uso

1. Este arquivo **NÃO** é validado por `doc_gates.py`
2. Contratos e agents **NÃO** devem mencionar paths/tokens obsoletos diretamente
3. Use termos genéricos nos contratos (ex: "legacy audit paths") e referencie este arquivo se necessário

---

## 🚫 Paths Obsoletos

### _reports/audit (DEPRECATED v1.0.0 → v1.2.0)

**Path antigo:**
```
_reports/audit/<RUN_ID>/
```

**Substituído por:**
```
docs/hbtrack/evidence/AR_<id>/executor_main.log
```

**Motivo:** Evidence pack canônico com path determinístico.

**Migração:**
- ARs antigas podem referenciar `_reports/audit` em contexto histórico
- Novo código **MUST** usar apenas `docs/hbtrack/evidence/`

---

## 🚫 Status Obsoletos

### 🔬 EM TESTE (DEPRECATED v1.0.0 → v1.2.0)

**Status antigo:**
```
🔬 EM TESTE
```

**Substituído por:**
Fluxo completo: 🔲 PENDENTE → 🏗️ EM_EXECUCAO → ✅ SUCESSO → ✅ VERIFICADO

**Motivo:** Status intermediário confuso; novo fluxo é mais claro:
- Executor: ✅ SUCESSO
- Testador: ✅ SUCESSO (confirmação)
- Humano: ✅ VERIFICADO (selo final)

---

## 🚫 Nomenclaturas Antigas

### "Fronted" → "Frontend" (Typo corrigido v1.1.0)

**Path antigo:**
```
Hb Track - Fronted/
```

**Path correto:**
```
Hb Track - Frontend/
```

**ARs relacionadas:** AR_014, AR_015

---

## 📚 Referências Históricas

### ARs que mencionam padrões obsoletos

- AR_023: Triple-run determinism (menciona path antigo)
- AR_024: Dev Flow v1.1.0 (menciona EM TESTE)
- AR_026: Executor Contract v2.0 (menciona _reports/audit)
- AR_034: Governança de Plans (menciona path antigo)

**Nota:** Essas ARs são históricas e preservadas para auditoria. Não devem ser alteradas retroativamente.

---

## ⚠️ Avisos para Novos Desenvolvedores

1. **Nunca use** paths mencionados neste arquivo em código novo
2. **Sempre consulte** `docs/_canon/contratos/` para padrões atuais
3. **Se encontrar** referência a deprecated patterns em código ativo, corrija e referencie a AR de migração

---

**Última atualização:** 2026-02-22  
**Versão do protocolo no momento da criação:** v1.2.0
