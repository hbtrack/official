# CI/CD Integration — Domain Completeness Auditor
> Documento de apoio humano, não canônico e não soberano. Serve para registro histórico de integração; não substitui `.github/workflows/`, `scripts/`, `docs/_canon/` ou `_reports/contract_gates/latest.json`.

**Data**: 2026-03-18  
**Status**: ✅ IMPLEMENTADO  
**Escopo**: Automação mensal + on-demand via GitHub Actions

---

## 🎯 Objetivo

Garantir que a pipeline de criação de contrato (orchetrador pré-contrato, gates, validation) continua satisfazendo aos 5 critérios de completude de domínio:

- **DC1**: Fase 0 determinística
- **DC2**: Artefatos obrigatórios detectados  
- **DC3**: Boundary detectado (cross-module)
- **DC4**: Sem lacunas silenciosas
- **DC5**: Handoff materializável (zero inferência)

---

## 📋 Arquitetura de CI/CD

### Workflow: `domain-completeness-audit.yml`

```yaml
Trigger:
  ├── Schedule: Toda segunda-feira 09:00 UTC (6:00 AM BRT)
  ├── Manual: Workflow dispatch com parâmetros
  └── PR events: Comentário automático com resultados
```

### Jobs

#### 1. `domain_completeness_audit` (Principal)

**Execução**:
- ✅ Setup Python 3.11
- ✅ Instala dependências (pyyaml)
- ✅ Executa audit completo (16 módulos) ou módulo específico
- ✅ Upload de relatórios em artifacts
- ✅ Comment automático se executado em PR
- ✅ Falha se algum módulo não passar

**Saídas**:
- `audit_output.txt` — Console output
- `_reports/DOMAIN_COMPLETENESS_ALL_MODULES_*.md` — Relatório markdown
- `_reports/DOMAIN_COMPLETENESS_ALL_MODULES_*.json` — Dados JSON

#### 2. `publish_audit_metrics` (Pós-processamento)

**Execução** (sempre, mesmo se audit falhar):
- ✅ Download dos relatórios
- ✅ Cria sumário de métricas
- ✅ Arquiva por 365 dias

---

## 🚀 Como Usar

### Opção 1: Audit Automático (Programado)

```
Toda segunda-feira às 09:00 UTC
↓
GitHub Actions executa `run_all_modules_audit.py`
↓
Relatório gerado em `_reports/`
↓
Métricas arquivadas
```

**Frequência**: Semanal (segunda-feira)

**Ação**: Nenhuma. Relatórios disponíveis em artifacts do workflow.

---

### Opção 2: Audit Manual (On-Demand)

#### Via GitHub Actions UI

1. Abrir repository
2. **Actions** → **Domain Completeness Audit**
3. **Run workflow**
4. Preencher inputs (opcional):
   - `module`: deixar em branco para todos os 16
   - `verbose`: true para debug detalhado

#### Via CLI (Local)

```bash
# Todos os 16 módulos
python scripts/audit/run_all_modules_audit.py

# Módulo específico
python -c "
from pathlib import Path
from scripts.audit.run_domain_completeness import DomainCompletenessAuditor

auditor = DomainCompletenessAuditor(Path.cwd(), module='wellness')
auditor.run()
print(auditor.generate_report())
"
```

---

### Opção 3: Audit em PR

Se o workflow rodar em contexto de PR, será adicionado comentário automaticamente:

```
## 🔍 Domain Completeness Audit Results

**Status**: ✅ All 16 modules passed!

### Audit Report
[... primeiras 50 linhas ...]

_Full reports available in artifacts._
```

---

## 📊 Formato de Saída

### Markdown Report

```
╔════════════════════════════════════════════════════════════════════════════╗
║       AUDITORIA DE COMPLETUDE — 16 MÓDULOS HB TRACK                       ║
╚════════════════════════════════════════════════════════════════════════════╝

SUMÁRIO EXECUTIVO
────────────────────────────────────────────────────────────────────────────────
✓ PASS: 16/16 módulos (100%)
✗ FAIL: 0/16 módulos (0%)

DESEMPENHO POR CRITÉRIO
────────────────────────────────────────────────────────────────────────────────
DC1 (Determinismo):    16/16 PASS (100%)
DC2 (Artefatos):       16/16 PASS (100%)
DC3 (Boundary):        16/16 PASS (100%)
DC4 (Gaps):            16/16 PASS (100%)
DC5 (Handoff):         16/16 PASS (100%)

MATRIZ DE RESULTADOS
────────────────────────────────────────────────────────────────────────────────
módulo               │ DC1 │ DC2 │ DC3 │ DC4 │ DC5 │ Final
────────────────────────────────────────────────────────────────────────────────
AI_INGESTION         │ ✓ │ ✓ │ ✓ │ ✓ │ ✓ │ PASS
[... 15 módulos mais ...]
────────────────────────────────────────────────────────────────────────────────

ESTATÍSTICAS GERAIS
────────────────────────────────────────────────────────────────────────────────
Bloqueios corretos: 64/64
Lacunas silenciosas: 0
Inferências necessárias: 0
```

### JSON Report

```json
{
  "ai_ingestion": {
    "passed": true,
    "dc1_determinism": true,
    "dc2_artifacts": true,
    "dc3_boundary": true,
    "dc4_gaps": true,
    "dc5_handoff": true,
    "final_status": "PASS",
    "correct_blocks": 4,
    "total_blocks": 4,
    "silent_gaps": 0,
    "inference_count": 0
  },
  ...
}
```

---

## 🔄 Fluxo de Falha

Se um módulo falhar:

### 1. Executar Audit Novamente (Debug)

```bash
python scripts/audit/run_domain_completeness.py
# Executará com warnings detalhados
```

### 2. Interpretar Resultado

```
✗ FAIL: DC3 (Boundary detection)

Isso significa: Gate de boundary não foi encontrada
Ação: Verificar se gate está em GATES_REGISTRY.yaml e ativa
```

### 3. Iterar Conforme Prompt §8

- **DC2 FAIL**: Adicionar artefato obrigatório ao repositório
- **DC3 FAIL**: Verificar se gate de boundary está definida e ativa
- **DC4 FAIL**: Adicionar teste de lacuna ao golden test suite
- **DC5 FAIL**: Adicionar campos ao schema de handoff

### 4. Re-executar para Validar

```bash
python scripts/audit/run_all_modules_audit.py
# Deve passar de novo
```

---

## 📈 Métricas Rastreadas

### Por Critério

- **DC1**: Determinismo (consistência de saída Phase 0)
- **DC2**: Artefatos (detecção de ausência)
- **DC3**: Boundary (detecção de cross-module)
- **DC4**: Gaps (lacunas silenciosas)
- **DC5**: Handoff (materializabilidade)

### Agregadas

- Total de módulos testados: 16
- Bloqueios corretos por módulo: 4
- Lacunas silenciosas globais: 0 (ideal)
- Inferências necessárias: 0 (ideal)

---

## 🛠️ Manutenção

### Adicionar Novo Módulo

1. Atualizar `docs/_canon/MODULE_REGISTRY.yaml` com novo módulo
2. Criar estrutura em `docs/hbtrack/modulos/{module}/`
3. Próxima execução de audit incluirá novo módulo automaticamente

### Atualizar Gate

1. Modificar `docs/_canon/gates/GATES_REGISTRY.yaml`
2. Re-run audit — gerará novo relatório refletindo mudança

### Escalar Schedule

1. Editar `.github/workflows/domain-completeness-audit.yml`
2. Modificar `cron:` (ex: para diariamente)
3. Commit e push

---

## 📁 Arquivos

| Arquivo | Propósito |
|---------|-----------|
| `scripts/audit/run_all_modules_audit.py` | Executor de audit para 16 módulos |
| `scripts/audit/run_domain_completeness.py` | Executor para módulo individual |
| `.github/workflows/domain-completeness-audit.yml` | Workflow CI/CD |
| `docs/guias/DOMAIN_COMPLETENESS_AUDITOR.md` | Guia de uso |
| `_reports/DOMAIN_COMPLETENESS_ALL_MODULES_*.md` | Relatórios (gerados) |
| `_reports/DOMAIN_COMPLETENESS_ALL_MODULES_*.json` | Dados (gerados) |

---

## ✅ Status de Implementação

- ✅ Executor single module criado
- ✅ Executor all modules criado
- ✅ GitHub Actions workflow criado
- ✅ Auditoria de 16 módulos: **100% PASS**
- ✅ Documentação CI/CD completa

---

## 🚀 Próximos Passos (Opcional)

1. **Alertas Automáticos**: Slack/email se audit falhar
2. **Dashboard**: Integrar métricas em dashboard DX
3. **Alertas de Gate**: Se descobrir nova gate, auditar automaticamente
4. **Relatórios Mensais**: Email resume ao time

---

## Referências

- **Prompt especi**: `.contract_driven/agent_prompts/audit_domain_completeness.prompt.md` §7-8
- **Gates**: `docs/_canon/gates/GATES_REGISTRY.yaml`
- **Módulos**: `docs/_canon/MODULE_REGISTRY.yaml`
- **Workflow**: `.github/workflows/domain-completeness-audit.yml`

---

Generated: 2026-03-18  
Status: ✅ PRODUCTION READY
