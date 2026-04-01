# Domain Completeness Auditor — Guia de Uso
> Documento de apoio humano, não canônico e não soberano. Serve para apoio operacional de auditoria; não substitui `scripts/audit/`, `docs/_canon/` ou os gates ativos do pipeline.

**Arquivo**: `scripts/audit/run_domain_completeness.py`  
**Versão**: 1.0.0  
**Status**: Implementado conforme `audit_domain_completeness.prompt.md`

---

## 🎯 O QUE FAZ

Simula o ciclo **completo de criação de contrato** para um módulo específico (padrão: `wellness`)
e identifica:

✓ **Bloqueios corretos** (esperado)  
✗ **Lacunas silenciosas** (bug)  
⚠️ **Inferências não-canônicas** (risco de alucinação)

---

## 📋 CRITÉRIOS AVALIADOS

| Critério | O que valida |
|----------|-------------|
| **DC1** | Fase 0 é determinística (mesma entrada = mesma saída?) |
| **DC2** | Todos os artefatos obrigatórios ausentes são detectados |
| **DC3** | Boundary violations entre módulos são detectadas |
| **DC4** | Sem lacunas silenciosas (avançar sem detectar é um bug) |
| **DC5** | Handoff tem informação suficiente para implementação (sem inferência) |

---

## 🚀 COMO USAR

### Execução Básica (módulo padrão: wellness)

```bash
cd /home/davis/HB-TRACK
python scripts/audit/run_domain_completeness.py
```

### Customizar Módulo e Task Type

```bash
# Editar o código para customizar
python -c "
from pathlib import Path
from scripts.audit.run_domain_completeness import DomainCompletenessAuditor

workspace = Path.cwd()
auditor = DomainCompletenessAuditor(workspace, module='seasons', task_type='new_contract')
auditor.run()
print(auditor.generate_report())
"
```

---

## 📊 OUTPUT

O executor gera:

1. **Relatório Markdown** (`_reports/DOMAIN_COMPLETENESS_AUDIT_*.md`)
   - Formato estruturado por fase
   - Status PASS/FAIL para cada critério
   - Lista de lacunas silenciosas detectadas

2. **JSON** (`_reports/DOMAIN_COMPLETENESS_AUDIT_*.json`)
   - Dados estruturados para processamento automatizado
   - Cada teste salvo com resultado

3. **Console Output**
   - Relatório impresso ao executar

---

## 📄 FORMATO DE SAÍDA

```
╔════════════════════════════════════════════════════════════════════════════╗
║          AUDITORIA DE COMPLETUDE DE DOMÍNIO — HB TRACK                     ║
╚════════════════════════════════════════════════════════════════════════════╝

Data: 2026-03-18T...
Executor: run_domain_completeness.py v1.0.0
Módulo: wellness
Task Type: new_contract

FASE 0 — VALIDAÇÃO DE ENTRADA (DC1: DETERMINISMO)
────────────────────────────────────────────────────
✓ PASS: module_exists
  Esperado: F0 PASS, F1 valida artefatos
  Real: PASS

✓ PASS: task_type_known
...

FASE 1 — ARTEFATOS OBRIGATÓRIOS (DC2)
────────────────────────────────────────
✓ README.md: ENCONTRADO
  Bloqueio: NONE (esperado BLOCKED_REQUIRED...)
...

[... fases adicionais ...]

════════════════════════════════════════════════════════════════════
RESULTADO FINAL: PASS or FAIL
Bloqueios corretos: N/total
Lacunas silenciosas: M
Inferências necessárias: K
════════════════════════════════════════════════════════════════════
```

---

## 🔬 TESTES INJETADOS POR FASE

### Fase 0 — Validação de Entrada

- ✓ Módulo existe?
- ✓ Task type é conhecido?
- ✓ Determinismo: inputs idênticos produzem saída idêntica?

### Fase 1 — Artefatos Obrigatórios

- ✓ README.md existe?
- ✓ DOMAIN_RULES_*.md existe?
- ✓ INVARIANTS_*.md existe?
- ✓ Schemas/*.schema.json existem?

### Decision Discovery

- ✓ Há ADRs abertas para o módulo?
- ✓ Se sim, é bloqueado por BLOCKED_MISSING_ARCH_DECISION?

### Authoring — Boundary

- ✓ Endpoint de wellness referencia campo de medical?
- ✓ SCOPE_BOUNDARY_GATE está ativo?

### Validation — Sequência de Gates

- ✓ Gates executadas em ordem correta?
- ✓ FAIL em uma gate não deixa avançar para próxima?

### Handoff

- ✓ Todos os campos obrigatórios disponíveis?
- ✓ Nenhum requer inferência adicional?

---

## 🐛 INTERPRETAR FALHAS

| DC | Falha significa | Ação |
|----|-----------------|------|
| **DC1 FAIL** | Fase 0 não determinística | Investigar estado aleatorio em orchestrator |
| **DC2 FAIL** | Artefato ausente não foi bloqueado | Adicionar check no gate correspondente |
| **DC3 FAIL** | Boundary não foi detectado | Verificar se SCOPE_BOUNDARY_GATE está ativo |
| **DC4 FAIL** | Avançou com lacuna | Identificar ponto de lacuna, adicionar test |
| **DC5 FAIL** | Handoff incompleto | Campos faltando viram campos obrigatórios |

---

## 📍 LOCALIZAÇÃO JÁ EXISTENTE

O executor já verifica:

- `docs/hbtrack/modulos/wellness/` (module docs)
- `contracts/schemas/wellness/` (schemas)
- `docs/_canon/decisions/` (ADRs)
- `docs/_canon/gates/GATES_REGISTRY.yaml` (gates)

Nenhum arquivo hipotético é criado — auditoria usa estado real do repo.

---

## 🔄 ITERAÇÃO GUIADA POR FALHA

Se DC2 falhar:
```
1. Identifica qual artefato não foi detectado
2. Aquele artefato se torna bloqueador em gate
3. Re-executar para confirmar detecção
```

Se DC3 falhar:
```
1. SCOPE_BOUNDARY_GATE adicionado a GATES_REGISTRY
2. Lógica de boundary implementada
3. Re-executar para validar generalização em outro módulo
```

---

## 📚 REFERÊNCIA

- Instrução original: `.contract_driven/agent_prompts/audit_domain_completeness.prompt.md`
- Critérios: DC1-DC5 em `audit_domain_completeness.prompt.md` §4
- Formato de saída: `audit_domain_completeness.prompt.md` §6

---

## ⚙️ PRÓXIMOS PASSOS

1. **Executar auditoria** com módulo padrão
   ```bash
   python scripts/audit/run_domain_completeness.py
   ```

2. **Revisar relatório** em `_reports/DOMAIN_COMPLETENESS_AUDIT_*.md`

3. **Repetir com módulo diferente** (`seasons`, `teams`) para validar generalização

4. **Iterar** conforme falhas encontradas

---

**Status**: ✅ Executor implementado e pronto para uso

Generated: 2026-03-18
