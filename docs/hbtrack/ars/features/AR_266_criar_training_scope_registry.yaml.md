# AR_266 — Criar TRAINING_SCOPE_REGISTRY.yaml

**Status**: ✅ SUCESSO
**Versão do Protocolo**: 1.3.0

## Descrição
Criar docs/hbtrack/modulos/treinos/TRAINING_SCOPE_REGISTRY.yaml conforme exigido pela Seção 5.1 do DONE_CONTRACT_TRAINING.md.md.

Este arquivo classifica TODOS os itens do módulo TRAINING em exatamente um dos grupos: CORE, EXTENDED ou EXPERIMENTAL. Sem este arquivo, nenhum item CORE pode avançar para DONE_PRODUTO.

ESTRUTURA OBRIGATÓRIA DO ARQUIVO:
```yaml
# TRAINING_SCOPE_REGISTRY.yaml
# Artefato canônico de classificação de escopo — módulo TRAINING
# Autoridade: DONE_CONTRACT_TRAINING.md.md §4 + §5.1
# Versão: v1.0.0
# Última revisão: 2026-03-08

module: TRAINING
version: v1.0.0
last_revised: 2026-03-08
authority: DONE_CONTRACT_TRAINING.md.md §4

# Regra: todo item sem classificação explícita é inválido para DONE_PRODUTO
items:
  core:
    - id: training_sessions_lifecycle
      description: Sessões de treino — CRUD completo + lifecycle (DRAFT→PUBLISHED→CLOSED)
      contracts: [CONTRACT-TRAIN-001..018]
      invariants: [INV-TRAIN-001, INV-TRAIN-004, INV-TRAIN-005, INV-TRAIN-006, INV-TRAIN-008]
    - id: session_exercises
      description: Exercícios por sessão — add/remove/reorder/bulk
      contracts: [CONTRACT-TRAIN-019..024]
      invariants: [INV-TRAIN-045]
    - id: attendance_core
      description: Presença — list/add/batch/statistics
      contracts: [CONTRACT-TRAIN-025..028]
      invariants: [INV-TRAIN-016, INV-TRAIN-030, INV-TRAIN-063, INV-TRAIN-064]
    - id: wellness_pre
      description: Wellness pré-treino — list/add/get/update/request-unlock
      contracts: [CONTRACT-TRAIN-029..034]
      invariants: [INV-TRAIN-002, INV-TRAIN-009, INV-TRAIN-026]
    - id: wellness_post
      description: Wellness pós-treino — list/add/get/update
      contracts: [CONTRACT-TRAIN-035..039]
      invariants: [INV-TRAIN-003, INV-TRAIN-010, INV-TRAIN-021, INV-TRAIN-026]
    - id: training_cycles
      description: Ciclos de treino — CRUD + active query
      contracts: [CONTRACT-TRAIN-040..045]
      invariants: [INV-TRAIN-037]
    - id: training_microcycles
      description: Microciclos — CRUD + current + summary
      contracts: [CONTRACT-TRAIN-046..052]
      invariants: [INV-TRAIN-020, INV-TRAIN-043]
    - id: exercise_bank_core
      description: Banco de exercícios — list/get (acesso básico)
      contracts: [CONTRACT-TRAIN-053..056]
      invariants: [INV-TRAIN-047, INV-TRAIN-048, INV-TRAIN-051]
    - id: wellness_content_gate
      description: Gate de conteúdo wellness — controle de liberação de conteúdo pós-treino
      contracts: [CONTRACT-TRAIN-057]
      invariants: [INV-TRAIN-071, INV-TRAIN-076, INV-TRAIN-078]
    - id: export_core
      description: Exportação PDF de sessão — endpoint de download
      contracts: [CONTRACT-TRAIN-086..090]
      invariants: []
    - id: ai_coach_core
      description: IA Coach — apply-draft, justify-suggestion (fluxo canônico)
      contracts: [CONTRACT-TRAIN-100, CONTRACT-TRAIN-102, CONTRACT-TRAIN-104, CONTRACT-TRAIN-105]
      invariants: [INV-TRAIN-079, INV-TRAIN-080, INV-TRAIN-081]
    - id: analytics_deviation
      description: Análise de desvio por sessão
      contracts: [CONTRACT-TRAIN-011]
      invariants: [INV-TRAIN-011]
    - id: wellness_status_gate
      description: Status wellness por sessão (gate de conteúdo)
      contracts: [CONTRACT-TRAIN-012]
      invariants: [INV-TRAIN-026]

  extended:
    - id: attendance_pending_items
      description: Itens pendentes de presença — fila de pendências
      contracts: [CONTRACT-TRAIN-100]
      invariants: [INV-TRAIN-065, INV-TRAIN-066, INV-TRAIN-067, INV-TRAIN-068]
    - id: exercise_bank_acl
      description: Banco de exercícios — ACL, visibility, scope, mídia
      contracts: [CONTRACT-TRAIN-062..066]
      invariants: [INV-TRAIN-EXB-ACL-001..007]
    - id: exercise_favorites
      description: Favoritos do banco de exercícios
      contracts: [CONTRACT-TRAIN-060..061]
      invariants: [INV-TRAIN-050]
    - id: exercise_tags
      description: Tags do banco de exercícios
      contracts: [CONTRACT-TRAIN-057..059]
      invariants: []
    - id: wellness_rankings
      description: Rankings de wellness (analytics 90-day)
      contracts: [CONTRACT-TRAIN-074..075]
      invariants: []
    - id: top_performers
      description: Top performers por equipe
      contracts: [CONTRACT-TRAIN-076]
      invariants: []
    - id: training_alerts_suggestions
      description: Alertas e sugestões de treino (singleton trainingAlertsSuggestionsApi)
      contracts: [CONTRACT-TRAIN-077..085]
      invariants: []

  experimental:
    - id: training_suggestions_roteador
      description: Roteador de sugestões de treino (CAP-001) — endpoint /training-suggestions inativo
      contracts: []
      invariants: []
      note: deferred CAP-001; useSuggestions.ts deferred
    - id: ai_coach_chat
      description: Chat interativo com IA Coach — fora do OpenAPI canônico atual
      contracts: []
      invariants: []
      note: futuro; não materializado no OpenAPI vigente
```

O Executor DEVE criar o arquivo com esta estrutura e adaptar contratos/invariantes se detectar divergência com CONTRACT ou INVARIANTS vigentes.

## Critérios de Aceite
1) docs/hbtrack/modulos/treinos/TRAINING_SCOPE_REGISTRY.yaml existe. 2) Arquivo é YAML válido. 3) Contém chaves de topo: module, version, last_revised, items. 4) items contém exatamente as chaves: core, extended, experimental. 5) core tem pelo menos 8 entradas. 6) Cada entrada de core tem id, description e contracts definidos.

## Write Scope
- docs/hbtrack/modulos/treinos/TRAINING_SCOPE_REGISTRY.yaml

## Validation Command (Contrato)
```
python temp_validate_ar266.py
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_266/executor_main.log`

## Notas do Arquiteto
Classe: A (spec artifact). PROOF: N/A (governance). Arquivo novo — não existe ainda.

## Riscos
- Verificar contratos atuais em TRAINING_FRONT_BACK_CONTRACT.md antes de listar CONTRACT-TRAIN-* para cada item
- Se detectar item CORE não listado na descrição, adicionar — não remover itens

## Análise de Impacto
Artefato novo de governança. Escopo exclusivo: `docs/hbtrack/modulos/treinos/TRAINING_SCOPE_REGISTRY.yaml`.
Nenhum código de produto alterado. Sem impacto em API/FE/BE. Batch 35 — classe A.

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em 571249d
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python temp_validate_ar266.py`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-08T14:53:20.850646+00:00
**Behavior Hash**: 6a16aec52ff325517066a030c3cdcacba881cff784639a1e128ac108988d275c
**Evidence File**: `docs/hbtrack/evidence/AR_266/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em 571249d
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_266_571249d/result.json`
