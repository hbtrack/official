# PIPELINE DOCUMENTATION INDEX
> Mapa de documentação do pipeline HB TRACK • 2026-03-20

---

## 📚 Suite Completa de Documentos

Você solicitou um mapeamento completo do pipeline real. Aqui estão os 4 documentos gerados, cada um com foco diferente:

---

### 1. 📊 **PIPELINE_MAPPING.json** (SSOT Estruturado)
**Localização**: [`PIPELINE_MAPPING.json`](PIPELINE_MAPPING.json)

**Conteúdo**: JSON estruturado com:
- ✅ pipeline_structure: 6 fases com gates, transitions, tarefas
- ✅ gates_summary: 21 gates completos (bloqueantes/não-bloqueantes)
- ✅ task_types: 14 task_types com workers e artifacts
- ✅ modules: 16 módulos canônicos com status e expected_surfaces
- ✅ boot_profiles: 4 profiles com required_sections
- ✅ worker_prompts: 18 workers listados
- ✅ ci_cd_workflows: 4 workflows
- ✅ canonical_paths: estrutura completa de filesystem

**Ideal para**: Parsing programático, automação, ferramentas, integração com scripts

---

### 2. 📖 **PIPELINE_REAL_MAP.md** (Guia Visual Expandido)
**Localização**: [`PIPELINE_REAL_MAP.md`](PIPELINE_REAL_MAP.md)

**Seções**:
1. **Visão Geral Executiva** — 1 tabela com contagens principais
2. **🔄 Pipeline — 6 Fases** — diagramas ASCII + descrição de cada fase
   - Fase 0: PRÉ-CONTRATO (9 gates)
   - Fase 1: DECISÃO ARQUITETURAL (condicional)
   - Fase 2: AUTORIA (8 task_types)
   - Fase 3: VALIDAÇÃO (10 gates)
   - Fase 4: READINESS (1 task_type)
   - Fase 5: HANDOFF
3. **🚪 16 Módulos Canônicos** — com domínios e responsáveis
4. **📦 Estrutura Canônica de Artefatos** — tree completa de contracts/, docs/
5. **🔌 Worker Prompts** — 18 workers categorizados
6. **🎯 Boot Profiles** — 4 profiles com triggers
7. **🚀 CI/CD Workflows** — 4 workflows com triggers
8. **⚠️ Regras Críticas** — 7 regras que não podem quebrar
9. **🔍 Debugging & Diagnostics** — comandos úteis

**Ideal para**: Leitura humana, explicações, documentação de produto

---

### 3. ⚡ **PIPELINE_QUICK_REFERENCE.md** (Referência Estruturada)
**Localização**: [`PIPELINE_QUICK_REFERENCE.md`](PIPELINE_QUICK_REFERENCE.md)

**Seções**:
1. **📌 Matriz de Orquestração** — fluxograma ASCII de Fase 0 → 5
2. **🎯 Mapa Task Type → Worker → Profile** — tabela de roteamento
3. **📦 Correspondência Task → Path de Saída** — mapping completo
4. **🔐 Gate Dependency Graph** — ASCII art com dependências
5. **🧭 Rotas de Entrada por Cenário** — 4 exemplos práticos
6. **⚡ Validações por Fase** — coverage de gates por fase
7. **📍 Artefatos SSOT** — 7 artefatos e quando atualizar
8. **🔄 Compilação API Policy** — quando executar
9. **🚨 Critério de Falha** — gates e remédios
10. **✅ Checklist Pré-Commit** — roteiro antes de commit

**Ideal para**: Desenvolvimento iterativo, debugging, fluxos específicos

---

### 4. 📋 **PIPELINE_SUMMARY.md** (1-Pager)
**Localização**: [`PIPELINE_SUMMARY.md`](PIPELINE_SUMMARY.md)

**Seções** (compactas):
1. **🎯 6 Fases Obrigatórias** — diagrama de sequência
2. **🚪 Task Types → Workers → Paths** — tabela concisa
3. **🔐 21 Gates (Ordem)** — lista flat com severidade
4. **16️⃣ Módulos Canônicos** — organizado por domínio
5. **🎛️ Boot Profiles** — 4 profiles com triggers
6. **📦 Canonical Paths** — estrutura resumida
7. **🔄 Validação Automática** — comando único
8. **⚠️ Regras Críticas** — 7 rules em bullets
9. **📋 Pré-Commit Checklist** — ações pré-git
10. **🔗 Documentação Canônica** — tabela de referências
11. **🆘 Troubleshooting Rápido** — erros comuns + soluções

**Ideal para**: Referência rápida em emergência, onboarding rápido, paste na aba do browser

---

## 📍 Como Usar Esta Suite

### Cenário A: "Quero entender a arquitetura geral"
```
Leia: PIPELINE_REAL_MAP.md → Overview + Fases
Consulte: PIPELINE_MAPPING.json para dados exatos
```

### Cenário B: "Preciso executar uma tarefa agora"
```
Consulte: PIPELINE_SUMMARY.md → fluxograma rápido
Drill-down: PIPELINE_QUICK_REFERENCE.md → rota de entrada específica
```

### Cenário C: "Tenho um erro no pipeline"
```
Check: PIPELINE_SUMMARY.md § Troubleshooting Rápido
Aprofunde: PIPELINE_QUICK_REFERENCE.md § Critério de Falha
Read: PIPELINE_REAL_MAP.md § [Fase relevante]
```

### Cenário D: "Preciso integrar com tooling"
```
Parse: PIPELINE_MAPPING.json em código
Ref: PIPELINE_QUICK_REFERENCE.md § Validações por Fase
Consulte: Scripts em scripts/contracts/validate/
```

---

## 🔗 Mapeamento: As 7 Questões → Respostas

| Questão do Pedido | MAPPING.json | REAL_MAP.md | QUICK_REF.md | SUMMARY.md |
|---|---|---|---|---|
| **1. Estrutura de Fases?** | ✅ pipeline_structure | ✅ §Pipeline - 6 Fases | ✅ §Matriz Orquestra | ✅ §6 Fases |
| **2. Quantos Gates & Status?** | ✅ gates_summary (21) | ✅ §Fases + tabelas | ✅ §Gate Dependency | ✅ §21 Gates |
| **3. Task Types & Workers?** | ✅ task_types (14) | ✅ §Worker Prompts | ✅ §Matrix Task→Worker | ✅ §Task Types |
| **4. Módulos Canônicos?** | ✅ modules (16) | ✅ §16 Módulos | ✅ (referência) | ✅ §16 Módulos |
| **5. Boot Profiles?** | ✅ boot_profiles (4) | ✅ §Boot Profiles | ✅ (referência) | ✅ §Boot Profiles |
| **6. Artefatos & Paths?** | ✅ canonical_paths | ✅ §Estrutura Canônica | ✅ §Gate Validation | ✅ §Paths |
| **7. CI/CD Workflows?** | ✅ ci_cd_workflows (4) | ✅ §CI/CD Workflows | ✅ (referência) | ✅ (inline) |

---

## 📊 Dados Resumidos (Quick Stats)

```
┌─────────────────────────────────────────────────┐
│ PIPELINE SNAPSHOT                               │
├─────────────────────────────────────────────────┤
│ Fases Obrigatórias          │ 6 (sequência total)  │
│ Gates de Validação          │ 21 (19 bloqueantes)  │
│ Task Types Ativos           │ 14 (11 contrato)     │
│ Módulos Canônicos           │ 16 (todos ready)     │
│ Boot Profiles               │ 4 (+ 1 default)      │
│ Worker Prompts              │ 18 (.contract_driven/) │
│ Workflows CI/CD             │ 4 (1 crítico)        │
│ Artefatos SSOT              │ 7 (global + local)   │
├─────────────────────────────────────────────────┤
│ Status Geral                │ ✅ PASS (2026-03-20) │
└─────────────────────────────────────────────────┘
```

---

## 🚀 Próxima Etapa: Atualizar docs/guias/produto/PIPELINE.md

Esses 4 documentos formam a base estruturada para atualizar o arquivo **PIPELINE.md** principal. Sugestão de incorporação:

```markdown
# PIPELINE.md (Estrutura Proposta)

## 1. Resumo de 1 Página
→ Incorporar PIPELINE_SUMMARY.md completo

## 2. Guia Detalhado por Fase
→ Expandir com PIPELINE_REAL_MAP.md § Fase [0-5]

## 3. Referência de Roteamento
→ Tabelas de PIPELINE_QUICK_REFERENCE.md

## 4. Dados Estruturados
→ Link ou embed de PIPELINE_MAPPING.json "ver dados completos"

## 5. Troubleshooting
→ PIPELINE_SUMMARY.md § Troubleshooting Rápido

## Apêndice: Referências Canônicas
→ Links para docs/_canon/CONTRACT_PIPELINE.md, etc.
```

---

## ✅ Checklist: Fases Documentadas

- [x] **Fase 0: PRÉ-CONTRATO** — 9 gates, boot profiles, validações
- [x] **Fase 1: DECISÃO ARQUITETURAL** — condicional, ADRs, decision_discovery
- [x] **Fase 2: AUTORIA** — 8 task_types, 18 workers, paths canônicos
- [x] **Fase 3: VALIDAÇÃO** — 10 gates semânticos, dependency graph
- [x] **Fase 4: READINESS** — elegibilidade, MODULE_REGISTRY, promotion
- [x] **Fase 5: HANDOFF** — evidência, SESSION_HANDOFF, commit
- [x] **Compilação API Policy** — trigger e comando
- [x] **16 Módulos Canônicos** — listados com expected_surfaces
- [x] **21 Gates Completos** — ordem, dependências, blocking_codes
- [x] **14 Task Types Ativos** — workers, profiles, stages_allowed
- [x] **4 Boot Profiles** — triggers, validações, required_sections
- [x] **18 Worker Prompts** — localizações e propósitos
- [x] **4 Workflows CI/CD** — triggers, stages, criticidade
- [x] **Artefatos SSOT** — 7 artefatos, paths, quando atualizar

---

## 📝 Notas Importantes

1. **Estes documentos são derivados** dos artefatos canônicos:
   - `docs/_canon/CONTRACT_PIPELINE.md`
   - `.contract_driven/TASK_CATALOG.yaml`
   - `.contract_driven/BOOT_PROFILES.yaml`
   - `docs/_canon/gates/GATES_REGISTRY.yaml`
   - `docs/_canon/MODULE_REGISTRY.yaml`

2. **Se algum canônico mudar**, esses 4 documentos podem ficar desatualizados. Mantenha os arquivos canônicos como SSOT.

3. **Recomendação**: Use PIPELINE_MAPPING.json como base para gerar estes docs automaticamente (CI/CD hook).

4. **Todos os 4 documentos** estão em `/home/davis/HB-TRACK/docs/guias/produto/` prontos para consulta.

---

**Data**: 2026-03-20 | **Status**: ✅ COMPLETO | **Próximo**: Integrar em PIPELINE.md
