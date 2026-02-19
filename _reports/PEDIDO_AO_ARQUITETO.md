# PEDIDO AO ARQUITETO — HB TRACK EXECUTOR

**Data:** 2026-02-19  
**Agente:** Executor (Determinismo N10)  
**SSOT:** `docs/_canon/MANUAL_CANONICO_DETERMINISMO.md` (v2.0)

---

## STATUS DO PLANO UNIFICADO

✅ **PLANO UNIFICADO COMPLETO** — Todas as fases (0-4) concluídas com exit code 0.

### Fases Concluídas:
- ✅ **FASE 0:** Congelar a verdade (RUN-SSOT-2026-02-19-001)
- ✅ **FASE 1:** Promover manual a SSOT descoberto
- ✅ **FASE 2:** Atualizar SSOT com regras snapshot/VPS
- ✅ **FASE 3:** Eliminar drift do root Evidence Pack
- ✅ **FASE 4:** Enforcement anti-regressão (DOCS_CANON_CHECK)

### Evidence Pack Gerados:
- `_reports/audit/RUN-SSOT-2026-02-19-001/`
- `_reports/audit/RUN-SSOT-2026-02-19-002/`

### Gates Executados (exit 0):
- `DOCS_CANON_CHECK` → PASS
- `AUDIT_PACK_INTEGRITY` → PASS

---

## REQUISIÇÃO: INPUT CONTRACT PARA PRÓXIMA EXECUÇÃO

O Executor solicita ao Arquiteto a definição do próximo escopo de trabalho conforme contrato de input obrigatório:

### 1. MODE (OBRIGATÓRIO)
```yaml
mode: [PROPOSE_ONLY | EXECUTE]
```
**Pergunta:** Qual modo deseja para a próxima tarefa?

### 2. BRANCH & BASE_COMMIT (OBRIGATÓRIO)
```yaml
branch: ?
base_commit: ?
# OU indicar: working_tree_dirty: true
```
**Pergunta:** Qual branch/commit base para trabalhar?

### 3. IDENTIFICADORES (OBRIGATÓRIO)
```yaml
RUN_ID: ?  # Ex: RUN-SSOT-2026-02-19-003
CORR_ID: ? # Opcional: se for correção
```
**Pergunta:** Qual RUN_ID para próxima execução?

### 4. ESCOPO DA TAREFA
**Pergunta:** Qual a próxima tarefa/objetivo?

Opções sugeridas baseadas no contexto atual:

#### **Opção A:** Implementar Módulo AUTH (HBTRACKANBAN.md)
- **Contexto:** KANBAN indica módulo AUTH pendente
- **Tarefas candidatas:**
  - DB-AUTH-001: Tabela de usuários
  - BK-AUTH-001: API de autenticação/login
  - FR-AUTH-001: Interface de login
- **Gates requeridos:** `SCHEMA_PARITY`, `API_SPEC_PARITY`, `AUTH_FLOW_CHECK`
- **Exit code esperado:** 0 (PASS)

#### **Opção B:** Criar Gate de Validação de AUTH
- **Escopo:** Criar `AUTH_FLOW_CHECK` no GATES_REGISTRY
- **Validações:**
  - `schema.sql` contém tabelas person/auth
  - `openapi.json` contém rota `/api/v1/auth/login`
  - `alembic_state.txt` sincronizado
- **Exit code esperado:** 0 (PASS)

#### **Opção C:** Auditoria de Integridade Global
- **Escopo:** Executar todos os gates IMPLEMENTED do GATES_REGISTRY
- **Objetivo:** Evidence Pack completo do estado atual
- **Exit code esperado:** 0 (PASS) ou 2 (FAIL_ACTIONABLE)

#### **Opção D:** Outra tarefa definida pelo Arquiteto

### 5. SSOT BINDINGS (OBRIGATÓRIO)
```yaml
ssot_paths:
  - docs/_canon/MANUAL_CANONICO_DETERMINISMO.md
  - docs/_canon/_agent/GATES_REGISTRY.yaml
  - docs/_INDEX.yaml
  # Adicionar outros se aplicável
```
**Confirmação:** Paths SSOT estão corretos?

### 6. ALLOWLIST DE ESCRITA (SE APLICÁVEL)
```yaml
write_allowlist: ?  # Paths permitidos para modificação
# Ex: ["Hb Track - Backend/app/", "docs/_canon/"]
```
**Pergunta:** Quais paths podem ser modificados?

### 7. ROLLBACK PLAN (OBRIGATÓRIO)
```yaml
rollback_strategy: [git_revert | git_restore | custom]
```
**Confirmação:** Estratégia de rollback padrão (git revert) é aceitável?

---

## FORMATO DE RESPOSTA ESPERADO DO ARQUITETO

```yaml
# INPUT CONTRACT — PRÓXIMA EXECUÇÃO
execution:
  mode: PROPOSE_ONLY | EXECUTE
  run_id: RUN-[NOME]-2026-02-19-XXX
  corr_id: ~ # opcional
  
git:
  branch: main | feature/xxx
  base_commit: <hash> | HEAD
  dirty: false

task:
  objective: "[Descrição objetiva da tarefa]"
  scope: "[Escopo específico: arquivos/módulos afetados]"
  success_criteria: "[Critérios binários de sucesso]"
  
gates:
  required: [GATE_ID_1, GATE_ID_2, ...]  # Somente gates JÁ existentes
  expected_exit: 0 | 2
  
ssot:
  bindings:
    - docs/_canon/MANUAL_CANONICO_DETERMINISMO.md
    - docs/_canon/_agent/GATES_REGISTRY.yaml
  
write:
  allowlist: [path1, path2, ...]
  
rollback:
  strategy: git_revert
  commit_target: <hash_to_revert>
```

---

## HISTÓRICO DE ENTREGAS (REFERÊNCIA)

### RUN-SSOT-2026-02-19-002 (ÚLTIMO)
- **Objetivo:** Inserir política VPS no Manual Canônico
- **Exit Code:** 0 (PASS)
- **Gates:** DOCS_CANON_CHECK → PASS
- **Arquivos Modificados:**
  - `docs/_canon/MANUAL_CANONICO_DETERMINISMO.md` (linha 795)
  - `scripts/checks/check_docs_canon.py` (validação E009)
- **Evidence Pack:** `_reports/audit/RUN-SSOT-2026-02-19-002/`
- **Rollback:** `git revert` disponível

---

## PRÓXIMAS AÇÕES DO EXECUTOR

**Aguardando:** Input Contract completo do Arquiteto.

**Ao receber:**
1. Validar completude do Input Contract
2. Se modo = PROPOSE_ONLY: Gerar plano + gates + evidências esperadas
3. Se modo = EXECUTE: Aplicar patch + executar gates + gerar Evidence Pack
4. Reportar resultado com referências a `_reports/`

**BLOCKED_INPUT (4) se:**
- Input Contract incompleto
- Gate requerido não existe no GATES_REGISTRY
- Allowlist não cobre paths necessários
- SSOT bindings ausentes

---

**EXECUTOR READY — Aguardando direcionamento do Arquiteto.**
