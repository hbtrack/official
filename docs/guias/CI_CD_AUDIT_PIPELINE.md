# CI/CD Audit Pipeline — HB Track

Integração automática de auditorias de qualidade no pipeline de deployable.

---

## 1. Visão Geral

Dois workflows complementares executam continuamente:

| Workflow | Frequência | `Trigger | Escopo | Gate |
|----------|-----------|---------|--------|------|
| **Domain Completeness Audit** | Toda **segunda-feira 09:00 UTC** | Schedule + Manual + PR | 16 módulos (DC1–DC5) | Regredir em completude de domínio = bloqueio |
| **Context Efficiency Audit** | Todo **1º do mês 09:00 UTC** | Schedule + Manual + PR | Boot mínimo (CE1–CE5) | Boot exceded budget = bloqueio |

---

## 2. Domain Completeness Audit

**Arquivo**: `.github/workflows/domain-completeness-audit.yml`

**Propósito**: Verificar que todos 16 módulos mantêm DC1–DC5 (determinismo, artefatos, boundary gates, gaps, materialização).

**Schedule**: Toda segunda-feira às 09:00 UTC

**Disparo Manual**:
```bash
# GitHub UI: Actions → Domain Completeness Audit → Run workflow
# ou via CLI:
gh workflow run domain-completeness-audit.yml \
  -f module=wellness \
  -f verbose=true
```

**Outputs**:
- `_reports/DOMAIN_COMPLETENESS_ALL_MODULES_*.md` (markup)
- `_reports/DOMAIN_COMPLETENESS_ALL_MODULES_*.json` (metrics)
- PR comment automático (se acionado via PR)
- Artifact upload (90–365 dias retenção)

**Critérios PASS**:
- ✅ DC1: Determinismo (hash consistente)
- ✅ DC2: Artefatos obrigatórios presentes
- ✅ DC3: Boundary gates testados
- ✅ DC4: Zero silent gaps
- ✅ DC5: Handoff implementável

**FAIL Esperado**:
- ❌ Módulo sem CONTRACT ou GATES_REGISTRY
- ❌ Boundary gate não encontrada
- ❌ Handoff sem campo obrigatório
- ❌ Determinismo alterado

---

## 3. Context Efficiency Audit

**Arquivo**: `.github/workflows/context-efficiency-audit.yml`

**Propósito**: Verificar que boot mínimo respeita orçamento de palavras sem perda de determinismo (regras críticas alcançáveis ≤2 hops).

**Schedule**: Dia 1º de cada mês às 09:00 UTC

**Disparo Manual**:
```bash
# GitHub UI: Actions → Context Efficiency Audit → Run workflow
gh workflow run context-efficiency-audit.yml -f verbose=true
```

**Outputs**:
- `_reports/CONTEXT_EFFICIENCY_AUDIT_*.md` (markup + tabelas)
- `_reports/CONTEXT_EFFICIENCY_AUDIT_*.json` (structured)
- PR comment automático (se acionado via PR)
- Artifact upload (365 dias retenção)

**Critérios PASS** (todos requeridos):
- ✅ **CE1**: Budget respeitado (3 artefatos ≤ limites)
  - `AGENT_INSTRUCTIONS.md`: 450 palavras (atual: 378)
  - `CONTRACT_PIPELINE.md`: 600 palavras (atual: 338)
  - `pre_contract_orchestrator.prompt.md`: 700 palavras (atual: 394)
  - **Total**: ≤1750 palavras (atual: 1110 = 63.4%)

- ✅ **CE2**: Pointers rastreáveis (4 regras críticas via ponteiros explícitos)
  - Bloqueios canônicos (19 códigos) → AGENT_INSTRUCTIONS.md §5
  - Task type → worker mapping → AGENT_INSTRUCTIONS.md §4
  - Condição bloqueio pré-contrato → CONTRACT_SYSTEM_RULES.md §22
  - Precedência conflito → CONTRACT_SYSTEM_RULES.md §5

- ✅ **CE3**: Sem regras órfãs (todas as regras RULES §2–§23 alcançáveis via boot)
- ✅ **CE4**: Sem redundância (nenhuma regra aparece 2x no boot)
- ✅ **CE5**: Sem defaults implícitos (flows não dependem de contexto não-carregado)

**FAIL Esperado**:
- ❌ Artefato boot excede budget
- ❌ Regra crítica não tem ponteiro rastreável
- ❌ Regra RULES §N órfã (inacessível desde boot)
- ❌ Redundância detectada entre artefatos
- ❌ Default implícito em flow

---

## 4. Combinação: Semanal + Mensal

### Semana

```
Seg (DC Audit)  Ter  Qua  Qui  Sex  Sab  Dom
    ✓ PASS
    (16 módulos validados)
```

### Mês

```
Seg (DC Audit)    ... [semanas] ...    1º (CE Audit)
    ✓ PASS                                ✓ PASS
    (16 módulos)                          (Boot + regras)
```

**Estratégia**:
- **DC Semanal**: Captura regressões em definitório rápido
- **CE Mensal**: Valida convergência de boot (orçamento + alcançabilidade)
- **Manual Any Time**: Verificador ad-hoc (pré-deploy, post-refactor)

---

## 5. Resultados e Actions

### ✅ PASS

Ambos workflows retornam `exit 0`:

```yaml
- name: Set job status
  run: |
    echo "✅ All audits PASSED"
    exit 0  # Job marks as success
```

**Efeito**: PR pode ser mergeada (se audits são required status checks).

### ❌ FAIL

Ambos workflows retornam `exit 1`:

```yaml
- name: Set job status
  if: failure()
  run: |
    echo "❌ Audit FAILED"
    exit 1  # Job marks as failure
```

**Efeito**: PR bloqueada até correção (se status check required).

---

## 6. Configuração como Status Check Required

Para forçar que PRs passem nos audits:

1. **GitHub Settings → Branches**
2. **Add required status check** → `context_efficiency_audit`, `domain_completeness_audit`
3. **Enforce for admins**: ✓

Agora:
- PRs não podem ser merged sem ✅ de ambos
- Admin pode override (audit FAIL = merge com aviso)
- Blame aparece no author, não reviewer

---

## 7. Logs e Debugging

### Ver logs de execução

```bash
# GitHub UI:
1. Go to repo → Actions
2. Click workflow (e.g., "Domain Completeness Audit")
3. Click run instance → "domain_completeness_audit" job
4. View full logs (expandir steps)

# ou via CLI:
gh run view <run-id> --log domain_completeness_audit
```

### Download artifact local

```bash
# List artifacts:
gh run list -w domain-completeness-audit.yml --limit 1

# Download:
gh run download <run-id> -n domain-completeness-audit-<id>
cat audit_output.txt
```

### Re-run manually

```bash
# If latest run failed:
gh run rerun <run-id>

# With new inputs:
gh workflow run domain-completeness-audit.yml -f module=wellness -f verbose=true
```

---

## 8. Roadmap (Futuro)

### Curto Prazo
- [ ] Slack notification on audit FAIL (webhook)
- [ ] Email digest (mensal)
- [ ] Dashboard integration (Grafana / Datadog)

### Médio Prazo
- [ ] Parallel execution (speedup 30s → 10s)
- [ ] Historical trends (gráfico de budget/hops ao longo do mês)
- [ ] Diff report (o que mudou desde última run)

### Longo Prazo
- [ ] Machine learning anomaly detection (budget outliers)
- [ ] Predictive alerts (budget trajectory)
- [ ] Auto-remediation (mover conteúdo para boot_condicional)

---

## 9. Referência Rápida

### Disparar audit manualmente

```bash
# Domain Completeness (um módulo)
gh workflow run domain-completeness-audit.yml -f module=wellness

# Domain Completeness (todos)
gh workflow run domain-completeness-audit.yml

# Context Efficiency
gh workflow run context-efficiency-audit.yml

# Com verbose
gh workflow run context-efficiency-audit.yml -f verbose=true
```

### Rodar localmente

```bash
# Domain Completeness
python scripts/audit/run_all_modules_audit.py

# Context Efficiency
python scripts/audit/run_context_efficiency_audit.py

# Específico (wellness)
python -c "
from scripts.audit.run_domain_completeness import DomainCompletenessAuditor
from pathlib import Path
auditor = DomainCompletenessAuditor(Path.cwd(), module='wellness')
auditor.run()
print(auditor.generate_report())
"
```

---

## 10. Troubleshooting

| Sintoma | Causa | Solução |
|---------|-------|--------|
| CE1 FAIL | Budget excedido | Mover conteúdo para hook/gate-conditional |
| CE2 FAIL | Regra critica sem ponteiro | Adicionar referência explícita via link ou section |
| DC3 FAIL | Boundary gate não achada | Verificar GATES_REGISTRY.yaml (gate_id ou name) |
| DC5 FAIL | Campo handoff faltando | Adicionar campo em CONTRACT_SYSTEM.yaml handoff |
| Timeout | Muito lento | Rodar módulo específico, não todos |

---

## Contato & Escalação

- **Audit logic**: Ver `scripts/audit/` (run_*.py)
- **Workflow config**: Ver `.github/workflows/` 
- **Rules sources**: Ver `docs/_canon/AGENT_INSTRUCTIONS.md`
- **Gate definitions**: Ver `docs/_canon/gates/GATES_REGISTRY.yaml`

