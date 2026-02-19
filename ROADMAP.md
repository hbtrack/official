([Past chat][1])([Past chat][1])([Past chat][1])([Past chat][1])

PLANO UNIFICADO (alinhado ao MANUAL_CANONICO_DETERMINISMO HB Track)

## Objetivo único
- [x] Promover `docs/_canon/MANUAL_CANONICO_DETERMINISMO.md (v2.0)` a SSOT operacional de verdade: "texto + enforcement + evidência"
- [x] Eliminar o drift do root de Evidence Package
- [x] Incorporar regra: snapshot é permitido
- [x] Incorporar regra: na VPS, só executa/deploya `.py`

## Premissas SSOT já comprovadas pelo seu Evidence Pack
- [x] Root canônico de Evidence Pack: `_reports/` (Manual + `GATES_REGISTRY.yaml` + `audit_runner.py` + evidência física do diretório)
- [x] Identificar drift: `run_capability_gates.py` escreve/printa `docs/_generated/_reports/...` (divergente e ainda nem existe na prática)

---

## FASE 0 — Congelar a verdade (sem "achismo")

### Entrega:
- [x] Criar RUN_ID único para esta tarefa (ex.: `RUN-SSOT-2026-02-19-001`)
  - [x] `context.json` com commit/branch/ambiente em `_reports/audit/<RUN_ID>/`
  - [x] `summary.json` com status por gate em `_reports/audit/<RUN_ID>/`
  - [x] `checks/<GATE_ID>/{stdout.log,stderr.log,result.json}` em `_reports/audit/<RUN_ID>/`

### Gate de validação:
- [x] Executar `AUDIT_PACK_INTEGRITY` (já existe no registry): `python scripts/checks/check_audit_pack.py ${RUN_ID}`

---

## FASE 1 — Promover o manual a SSOT "descoberto" (roteador)

### Patch mínimo:
- [x] Criar `docs/_canon/MANUAL_CANONICO_DETERMINISMO.md` (conteúdo v2.0)
- [x] Atualizar `docs/_INDEX.yaml` adicionando entrypoint required:
  - [x] `id: determinism_manual`
  - [x] `path: docs/_canon/MANUAL_CANONICO_DETERMINISMO.md`
  - [x] `mode: required`

### AC binário:
- [x] AC-1 PASS: arquivo existe no path canônico e declara "v2.0" e "Status: SSOT"
- [x] AC-2 PASS: `_INDEX.yaml` referencia o manual como required

### Evidência:
- [x] Coletar `git ls-files docs/_canon/MANUAL_CANONICO_DETERMINISMO.md`
- [x] Coletar `git grep -n "determinism_manual" docs/_INDEX.yaml`

### Rollback:
- [x] Executar `git revert <commit>` (sem force-push)

---

## FASE 2 — Atualizar o SSOT com suas 2 regras novas (sem ambiguidade)

### Mudanças obrigatórias no manual (v2.0):

#### A) Snapshot permitido
- [x] Remover a cláusula "snapshot banido" do manual
- [x] Substituir por regra objetiva: "Snapshot é PERMITIDO como mecanismo (baseline/guard/context capture), mas NÃO é prova suficiente de 'FUNCIONA' sozinho. Se um gate usar snapshot, isso MUST estar declarado no registry e o artefato MUST estar no Evidence Pack."

#### B) Política VPS: somente `.py`
- [x] Adicionar regra explícita: "Na VPS, apenas scripts Python (.py) são executados/deployados. Wrappers `.ps1`/`.sh` podem existir localmente como harness, mas MUST NOT ser requisito de operação na VPS."
  - **COMPLETA:** Seção 0.3.1 inserida (linha 795) via insert_vps_policy.py com UTF-8

### AC binário:
- [x] AC-3 PASS: o manual não contém "snapshot MUST NOT/banido"
- [x] AC-4 PASS: o manual contém a política "VPS: .py only" ✅

### Evidência:
- [x] Coletar `git grep -n "snapshot" docs/_canon/MANUAL_CANONICO_DETERMINISMO.md`
- [x] Coletar `git grep -n "VPS" docs/_canon/MANUAL_CANONICO_DETERMINISMO.md` ✅

### Rollback:
- [x] Executar `git revert <commit>`

---

## FASE 3 — Eliminar o drift do root de Evidence Pack (correção do writer divergente)

**Conclusão correta:** `_reports/` é o root canônico, então aqui não tem "debate", tem correção.

### Patch mínimo obrigatório:
- [x] Em `scripts/gates/run_capability_gates.py`: trocar qualquer definição do tipo `docs/_generated/_reports/...` para `_reports/audit/...`
- [x] Em `scripts/gates/run_capability_gates.py`: corrigir o `print` para `_reports/audit/{run_id}/`

### AC binário:
- [x] AC-5 PASS: não existe mais `docs/_generated/_reports` no arquivo
- [x] AC-6 PASS: ao executar, o runner cria `_reports/audit/<RUN_ID>/` (e não cria/usa `docs/_generated/_reports`)

### Evidência:
- [x] Coletar `git grep -n "docs/_generated/_reports" scripts/gates/run_capability_gates.py` → esperado: zero ocorrências
- [x] Executar com RUN_ID explícito e verificar filesystem:
  - [x] `_reports/audit/<RUN_ID>/` existe
  - [x] `docs/_generated/_reports/` continua inexistente (como hoje)

### Rollback:
- [x] Executar `git revert <commit>`

---

## FASE 4 — Enforcement anti-regressão (para nunca mais voltar)

**Contexto:** Sem enforcement, isso volta a quebrar. O mínimo é um gate docs-canônico.

### Implementar `DOCS_CANON_CHECK` (hoje MISSING no `GATES_REGISTRY.yaml`)

#### Patch mínimo:
- [x] Criar `scripts/checks/check_docs_canon.py` (Python; exit 0/2/3/4)
- [x] Atualizar `docs/_canon/_agent/GATES_REGISTRY.yaml`:
  - [x] `DOCS_CANON_CHECK.lifecycle: IMPLEMENTED`
  - [x] `DOCS_CANON_CHECK.command: python scripts/checks/check_docs_canon.py ${RUN_ID}`

#### O que esse gate MUST checar (binário):
- [x] Manual existe no path canônico
- [x] Manual está indexado no `docs/_INDEX.yaml`
- [x] `reports_root` do `GATES_REGISTRY.yaml` é `_reports`
- [x] Nenhum runner SSOT hardcode `docs/_generated/_reports` (pelo menos `run_capability_gates.py`)

#### Evidência:
- [x] Executar `python scripts/audit/audit_runner.py <RUN_ID> DOCS_CANON_CHECK`
- [x] Executar `python scripts/checks/check_audit_pack.py <RUN_ID>`

#### Rollback:
- [x] Executar `git revert <commit>`

---

## O que você não perguntou, mas é necessário para o plano ficar "fechado"

### 1. Qual runner é "canônico" para Evidence Pack?
- [x] Implementar regra: canônico é qualquer runner que produza Evidence Pack em `_reports/audit/<RUN_ID>/` no formato exigido pelo `check_audit_pack.py`
- [x] Garantir: Se `run_capability_gates.py` não cumprir o formato, é LEGADO com waiver (não fonte canônica)

### 2. Como tratar `.ps1/.sh` existentes no repo?
- [x] Implementar regra: podem existir localmente, mas MUST NOT ser requisito de validação/execução na VPS (via check_docs_canon.py [E009])
- [x] Garantir: Se algum gate "required" depender deles para operação na VPS, isso é FAIL até migrar para `.py` (enforcement adicionado) ✅

---

## Quando eu declaro DONE (regra objetiva)

Declaração DONE quando todos os critérios abaixo estão completados:
- [x] **(P1)** Manual v2.0 existe e está indexado como required
- [x] **(P2)** Manual reflete "snapshot permitido" e "VPS: .py only" ✅
- [x] **(P3)** `run_capability_gates.py` não referencia mais `docs/_generated/_reports` e escreve em `_reports/`
- [x] **(P4)** `DOCS_CANON_CHECK` está IMPLEMENTED e passa gerando Evidence Pack em `_reports/audit/<RUN_ID>/` validado por `check_audit_pack.py`

---

## Evidência de conclusão (RUN-SSOT-2026-02-19-001)

### Comandos executados com exit code 0:
1. `python scripts/checks/check_docs_canon.py` → PASS (0)
2. `python scripts/audit/audit_runner.py RUN-SSOT-2026-02-19-001 DOCS_CANON_CHECK` → SUCCESS
3. `python scripts/checks/check_audit_pack.py RUN-SSOT-2026-02-19-001 --root _reports` → SUCCESS: audit pack verified

### Arquivos modificados:
- `docs/_INDEX.yaml` - adicionado entrypoint `determinism_manual`
- `docs/_canon/MANUAL_CANONICO_DETERMINISMO.md` - seção 0.2 atualizada (snapshot permitido)
- `scripts/gates/run_capability_gates.py` - root corrigido para `_reports/audit/`
- `scripts/checks/check_docs_canon.py` - novo gate enforcer criado
- `docs/_canon/_agent/GATES_REGISTRY.yaml` - DOCS_CANON_CHECK promovido a IMPLEMENTED
- `docs/_canon/_agent/CORRECTION_WRITE_ALLOWLIST.yaml` - removidos tokens de citação contaminantes

### Evidência de conclusão (RUN-SSOT-2026-02-19-002 — PATCHSET-004)

#### Comandos executados com exit code 0:
1. `python scripts/checks/check_docs_canon.py` → **PASS (0)** ✅
2. `python scripts/audit/audit_runner.py RUN-SSOT-2026-02-19-002 DOCS_CANON_CHECK` → **SUCCESS** ✅
3. `python scripts/checks/check_audit_pack.py RUN-SSOT-2026-02-19-002 --root _reports` → **SUCCESS: audit pack verified** ✅

#### Arquivos modificados (PATCHSET-004):
- `insert_vps_policy.py` - Script de inserção UTF-8 determinístico (idempotente)
- `docs/_canon/MANUAL_CANONICO_DETERMINISMO.md` - Seção 0.3.1 adicionada (linha 795)
- `scripts/checks/check_docs_canon.py` - Validação [E009] adicionada para enforcement VPS .py-only

#### Status final:
**✅ PLANO UNIFICADO COMPLETO**

Todas as 4 fases (0-4) + Q&A + PATCHSET-004 concluídas com exit code 0.

