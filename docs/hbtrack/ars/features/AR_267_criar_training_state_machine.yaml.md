# AR_267 — Criar TRAINING_STATE_MACHINE.yaml

**Status**: ✅ SUCESSO
**Versão do Protocolo**: 1.3.0

## Descrição
Criar docs/hbtrack/modulos/treinos/TRAINING_STATE_MACHINE.yaml conforme exigido pela Seção 5.2 do DONE_CONTRACT_TRAINING.md.md.

Este arquivo define o mapa formal de estados para todas as entidades stateful CORE do módulo. Sem ele, DONE_SEMANTICO = FALSE para qualquer entidade stateful CORE.

ESTRUTURA OBRIGATÓRIA DO ARQUIVO:
```yaml
# TRAINING_STATE_MACHINE.yaml
# Artefato canônico de máquina de estados — módulo TRAINING
# Autoridade: DONE_CONTRACT_TRAINING.md.md §5.2 + INVARIANTS_TRAINING.md
# Versão: v1.0.0
# Última revisão: 2026-03-08

module: TRAINING
version: v1.0.0
last_revised: 2026-03-08
authority: DONE_CONTRACT_TRAINING.md.md §5.2

# Regra: transição permitida no código mas ausente aqui derruba DONE_SEMANTICO
entities:

  - id: TrainingSession
    scope: CORE
    description: Sessão de treino — entidade central do módulo
    invariants: [INV-TRAIN-001, INV-TRAIN-004, INV-TRAIN-005, INV-TRAIN-006, INV-TRAIN-008]
    states:
      - DRAFT
      - PUBLISHED
      - CLOSED
      - DELETED
    initial_state: DRAFT
    transitions:
      - from: DRAFT
        to: PUBLISHED
        action: publish
        roles: [coach, admin]
        preconditions:
          - session must have at least one exercise or be valid per INV-TRAIN-006
        invariants: [INV-TRAIN-006]
      - from: DRAFT
        to: DELETED
        action: delete
        roles: [coach, admin]
        preconditions:
          - reason must be provided (query param)
        invariants: [INV-TRAIN-008]
      - from: PUBLISHED
        to: CLOSED
        action: close
        roles: [coach, admin]
        preconditions:
          - session date must be current or past
        invariants: [INV-TRAIN-006]
      - from: PUBLISHED
        to: DRAFT
        action: restore (from soft delete)
        roles: [coach, admin]
        preconditions: []
        invariants: [INV-TRAIN-008]
      - from: DELETED
        to: DRAFT
        action: restore
        roles: [coach, admin]
        preconditions: []
        invariants: [INV-TRAIN-008]
    forbidden_transitions:
      - from: CLOSED
        to: DRAFT
        reason: sessão fechada é imutável; reabrir requer nova AR/DEC
      - from: CLOSED
        to: PUBLISHED
        reason: sessão fechada é imutável

  - id: WellnessPre
    scope: CORE
    description: Wellness pré-treino preenchido pelo atleta antes da sessão
    invariants: [INV-TRAIN-002, INV-TRAIN-009, INV-TRAIN-026]
    states:
      - PENDING
      - SUBMITTED
      - UNLOCKED
    initial_state: PENDING
    transitions:
      - from: PENDING
        to: SUBMITTED
        action: submit (POST wellness_pre)
        roles: [athlete]
        preconditions:
          - atleta é participante da sessão
          - campo pre-treino obrigatório preenchido
        invariants: [INV-TRAIN-002, INV-TRAIN-009]
      - from: SUBMITTED
        to: UNLOCKED
        action: request-unlock
        roles: [athlete]
        preconditions:
          - motivo de desbloqueio fornecido
        invariants: []
      - from: UNLOCKED
        to: SUBMITTED
        action: resubmit (PATCH wellness_pre)
        roles: [athlete]
        preconditions: []
        invariants: [INV-TRAIN-002]
    forbidden_transitions:
      - from: SUBMITTED
        to: PENDING
        reason: athleta nao pode voltar a PENDING sem unlock aprovado

  - id: WellnessPost
    scope: CORE
    description: Wellness pós-treino preenchido pelo atleta após a sessão
    invariants: [INV-TRAIN-003, INV-TRAIN-010, INV-TRAIN-021, INV-TRAIN-026]
    states:
      - PENDING
      - SUBMITTED
    initial_state: PENDING
    transitions:
      - from: PENDING
        to: SUBMITTED
        action: submit (POST wellness_post)
        roles: [athlete]
        preconditions:
          - atleta é participante da sessão
          - sessão está CLOSED (wellness_content_gate ativo)
          - campo pós-treino obrigatório preenchido
        invariants: [INV-TRAIN-003, INV-TRAIN-010, INV-TRAIN-021]
    forbidden_transitions:
      - from: SUBMITTED
        to: PENDING
        reason: wellness post é imutável após submissão

  - id: AttendanceRecord
    scope: CORE
    description: Registro de presença por atleta por sessão
    invariants: [INV-TRAIN-016, INV-TRAIN-030, INV-TRAIN-063, INV-TRAIN-064]
    states:
      - ABSENT
      - PRESENT
      - JUSTIFIED_ABSENCE
    initial_state: ABSENT
    transitions:
      - from: ABSENT
        to: PRESENT
        action: mark present (POST/PATCH attendance)
        roles: [coach, admin]
        preconditions:
          - sessão está PUBLISHED ou CLOSED
        invariants: [INV-TRAIN-016, INV-TRAIN-030]
      - from: ABSENT
        to: JUSTIFIED_ABSENCE
        action: justify absence
        roles: [athlete, coach]
        preconditions:
          - motivo de justificativa fornecido
        invariants: [INV-TRAIN-064]
      - from: PRESENT
        to: ABSENT
        action: correction by coach
        roles: [coach, admin]
        preconditions: []
        invariants: []
      - from: JUSTIFIED_ABSENCE
        to: ABSENT
        action: revoke justification by coach
        roles: [coach, admin]
        preconditions: []
        invariants: []

  - id: CoachSuggestionDraft
    scope: CORE
    description: Rascunho de sugestão do IA Coach para o treinador
    invariants: [INV-TRAIN-079, INV-TRAIN-080, INV-TRAIN-081]
    states:
      - DRAFT
      - APPLIED
      - REJECTED
    initial_state: DRAFT
    transitions:
      - from: DRAFT
        to: APPLIED
        action: apply-draft (PATCH apply-draft)
        roles: [coach]
        preconditions:
          - coach revisou o draft antes de aplicar
        invariants: [INV-TRAIN-079]
      - from: DRAFT
        to: REJECTED
        action: justify-suggestion (POST justify-suggestion)
        roles: [coach]
        preconditions: []
        invariants: [INV-TRAIN-080]
    forbidden_transitions:
      - from: APPLIED
        to: DRAFT
        reason: draft aplicado é imutável
      - from: REJECTED
        to: DRAFT
        reason: draft rejeitado é imutável
```

O Executor DEVE criar o arquivo com esta estrutura. Checar invariantes vigentes em INVARIANTS_TRAINING.md antes de salvar.

## Critérios de Aceite
1) docs/hbtrack/modulos/treinos/TRAINING_STATE_MACHINE.yaml existe. 2) Arquivo é YAML válido. 3) Contém chaves de topo: module, version, entities. 4) entities tem pelo menos 4 entidades. 5) Cada entidade tem: id, scope, states, transitions. 6) Pelo menos uma entidade tem forbidden_transitions definido. 7) TrainingSession está presente com scope=CORE e states incluindo DRAFT, PUBLISHED, CLOSED.

## Write Scope
- docs/hbtrack/modulos/treinos/TRAINING_STATE_MACHINE.yaml

## Validation Command (Contrato)
```
python temp_validate_ar267.py
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_267/executor_main.log`

## Notas do Arquiteto
Classe: A (spec artifact). PROOF: N/A (governance). Arquivo novo — não existe ainda.

## Riscos
- Verificar invariantes vigentes em INVARIANTS_TRAINING.md para cada entidade antes de salvar
- Não inventar transições não suportadas pelo backend real — usar apenas transições já evidenciadas pelos testes

## Análise de Impacto
Artefato novo de governança. Escopo exclusivo: `docs/hbtrack/modulos/treinos/TRAINING_STATE_MACHINE.yaml`.
Nenhum código de produto alterado. Sem impacto em API/FE/BE. Batch 35 — classe A.

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em 571249d
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python temp_validate_ar267.py`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-08T14:55:14.791096+00:00
**Behavior Hash**: 9cf0f7d8a898c7286ddd9bdb889e1a9dc628d7135a996bd887857d526f3a1493
**Evidence File**: `docs/hbtrack/evidence/AR_267/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em 571249d
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python temp_validate_ar267.py`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-08T14:56:12.866434+00:00
**Behavior Hash**: 9cf0f7d8a898c7286ddd9bdb889e1a9dc628d7135a996bd887857d526f3a1493
**Evidence File**: `docs/hbtrack/evidence/AR_267/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em 571249d
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_267_571249d/result.json`
