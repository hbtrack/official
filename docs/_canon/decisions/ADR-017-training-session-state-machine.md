# ADR-017: State Machine Canônica de `training_session`

- Status: Accepted
- Date: 2026-03-15
- Deciders: Equipe HB Track
- Tags: training, state-machine, domain-model, contract
- Resolves: LAC-001 (CONTRACT_TRAINING.md §16), DSS-TRAINING-002

---

## Context

Três fontes independentes descreviam a state machine de `training_session` de formas incompatíveis, configurando um `BLOCKED_CONTRACT_CONFLICT` latente identificado pelo estágio Decision Discovery:

| Fonte | Estados definidos | Natureza |
|---|---|---|
| `.contract_driven/DOMAIN_AXIOMS.json` (global) | `DRAFT → PLANNED → SCHEDULED → IN_PROGRESS → COMPLETED → CANCELLED` | Axioma global (alvo original) |
| `INVARIANTS_TRAINING.md` INV-TRAIN-006 | `draft → scheduled → in_progress → pending_review → readonly` | Implementação operacional atual (v0.x) |
| `.dev/arquitetura/ARCH-DEC-TRAIN.md` TRAIN-DEC-026 | `DRAFT → SCHEDULED/PUBLISHED → IN_PROGRESS → COMPLETED → CANCELLED/ARCHIVED` | Intenção arquitetural do produto (aprovada, não canonizada) |

Sem resolução, qualquer contrato que tocasse o campo `status` de `training_session` teria risco de usar a state machine errada. O conflito foi documentado em `CONTRACT_TRAINING.md §16` como LAC-001.

---

## Decision

### State machine canônica de `training_session`

A state machine canônica é baseada em **TRAIN-DEC-026** (`ARCH-DEC-TRAIN.md`), que reflete a intenção arquitetural do produto:

```
DRAFT ──────────────► SCHEDULED ──────► PUBLISHED ──────► IN_PROGRESS ──► COMPLETED ──► ARCHIVED
                          │                   │                                 │
                          ▼                   ▼                                 ▼
                       CANCELLED           CANCELLED                         CANCELLED
```

#### Estados canônicos (7 + substatus operacional)

| Estado | Semântica | Editável? | Visível ao atleta? |
|---|---|---|---|
| `DRAFT` | Sessão em rascunho, não publicada | Sim (livre) | Não |
| `SCHEDULED` | Sessão planejada internamente, não publicada ao atleta | Sim (subconjunto) | Não |
| `PUBLISHED` | Sessão publicada e visível ao atleta | Sim (campos limitados) | Sim |
| `IN_PROGRESS` | Sessão em execução | Não (bloqueado) | Sim |
| `COMPLETED` | Sessão encerrada e revisada — imutável por edição destrutiva | Não | Sim (histórico) |
| `CANCELLED` | Sessão cancelada com motivo registrado | Não | Sim (cancelada) |
| `ARCHIVED` | Sessão histórica arquivada (> 60 dias ou marcação explícita) | Não | Somente leitura |

#### Transições permitidas

| De | Para | Condição |
|---|---|---|
| `DRAFT` | `SCHEDULED` | Dados mínimos presentes |
| `DRAFT` | `CANCELLED` | Qualquer momento antes de PUBLISHED |
| `SCHEDULED` | `PUBLISHED` | Coach publica para o atleta |
| `SCHEDULED` | `DRAFT` | Rebaixamento por perda de campos mínimos |
| `SCHEDULED` | `CANCELLED` | — |
| `PUBLISHED` | `IN_PROGRESS` | `session_at` atingido e coach inicia |
| `PUBLISHED` | `SCHEDULED` | Despublicação explícita |
| `PUBLISHED` | `CANCELLED` | — |
| `IN_PROGRESS` | `COMPLETED` | Coach encerra sessão (com ou sem pending items — ver INV-TRAIN-065) |
| `IN_PROGRESS` | `CANCELLED` | Cancelamento lógico (não exclusão física) |
| `COMPLETED` | `ARCHIVED` | Automático após 60 dias ou marcação explícita |

Transições proibidas (exemplos): `DRAFT → COMPLETED`, `COMPLETED → IN_PROGRESS`, `ARCHIVED → qualquer estado`.

---

### Migração dos estados operacionais atuais (v0.x → v1.0)

Os estados em INV-TRAIN-006 refletem a implementação atual. O mapeamento para a state machine canônica é:

| Estado v0.x (INV-TRAIN-006) | Estado canônico (esta ADR) | Nota |
|---|---|---|
| `draft` | `DRAFT` | Equivalência direta |
| `scheduled` | `SCHEDULED` ou `PUBLISHED` | A implementação atual colapsa os dois; split obrigatório antes de v1.0 |
| `in_progress` | `IN_PROGRESS` | Equivalência direta |
| `pending_review` | Substatus de `IN_PROGRESS` (v0.x) → eliminado na migração | `pending_review` é a janela de revisão antes de `COMPLETED`; na state machine canônica, o coach simplesmente transita para `COMPLETED` quando a revisão está pronta. Se necessário como estado intermediário, deve ser formalizado como `UNDER_REVIEW` via ADR de extensão. |
| `readonly` | `ARCHIVED` | `readonly` era o estado de sessões > 60 dias; substituído por `ARCHIVED` com semântica equivalente |

**Cronograma de migração:**
- `v0.x`: estados operacionais atuais permanecem válidos; INV-TRAIN-006 permanece como descrição da implementação atual.
- `v1.0` (pré-produção): migração para state machine canônica. DOMAIN_AXIOMS.json global atualizado. INV-TRAIN-006 atualizado para refletir 7 estados canônicos.

---

### Atualização de DOMAIN_AXIOMS.json global

O estado `PLANNED` presente no axioma global (`DRAFT → PLANNED → SCHEDULED → IN_PROGRESS → COMPLETED → CANCELLED`) é **removido** da state machine de `training_session`. Não há correspondência operacional para `PLANNED`. A atualização do DOMAIN_AXIOMS.json global deve ocorrer no ciclo v1.0.

---

## Consequences

### Positive
- Fim do `BLOCKED_CONTRACT_CONFLICT` latente: única source of truth para `status` de `training_session`.
- `SCHEDULED` e `PUBLISHED` como estados distintos resolve a ambiguidade de visibilidade para o atleta.
- `ARCHIVED` como estado explícito elimina o estado `readonly` implícito baseado em cálculo de data.
- Transições explícitas e fechadas permitem enforcement por schema (enum restrito no OpenAPI).

### Negative
- Migração `scheduled → SCHEDULED/PUBLISHED` requer split na implementação antes de v1.0.
- `pending_review` precisa ser eliminado ou formalizado como `UNDER_REVIEW` — decisão postergada para v1.0.
- DOMAIN_AXIOMS.json global precisa ser atualizado (risco de impacto em outros módulos que referenciem o estado `PLANNED`).

---

## Alternatives Considered

- **Manter INV-TRAIN-006 como canônica**: rejeitado — não inclui `PUBLISHED` (visibilidade ao atleta) nem `ARCHIVED` (semântica explícita de histórico), ambos necessários para o produto.
- **Manter DOMAIN_AXIOMS.json como canônica**: rejeitado — inclui `PLANNED` sem correspondência operacional e não cobre `PUBLISHED` nem `ARCHIVED`.
- **Criar estado `UNDER_REVIEW` explícito**: postergado — pode ser formalizado via ADR de extensão se `pending_review` precisar de mapeamento explícito na state machine canônica.

---

## Impact Map

**Artefatos canônicos a atualizar:**
- `docs/hbtrack/modulos/training/INVARIANTS_TRAINING.md` — INV-TRAIN-006: atualizar para refletir 7 estados canônicos (milestone: v1.0)
- `.contract_driven/DOMAIN_AXIOMS.json` — remover `PLANNED` do training session workflow (milestone: v1.0)
- `contracts/openapi/paths/training.yaml` — campo `status`: substituir pattern genérico por enum restrito aos 7 estados canônicos (milestone: v1.0)
- `docs/hbtrack/modulos/training/CONTRACT_TRAINING.md §16` — marcar LAC-001 como resolvido por esta ADR

**Gates a executar:**
- `python3 scripts/contracts/validate/validate_contracts.py`

---

## Links

- Resolves: `CONTRACT_TRAINING.md §16` LAC-001
- Resolves: DSS-TRAINING-002 (Decision Discovery 2026-03-15)
- Source: `.dev/arquitetura/ARCH-DEC-TRAIN.md` TRAIN-DEC-026, TRAIN-DEC-035
- Related: `docs/hbtrack/modulos/training/INVARIANTS_TRAINING.md` INV-TRAIN-006
- Related: `docs/_canon/ARCHITECTURE_DECISION_BACKLOG.md` ARCH-011
- Related: `docs/hbtrack/modulos/training/ARCH_DECISIONS_TRAINING.md`
