# Domain/Persistence Deep Diff — Módulo Training

> Auditoria técnica de repositório contract-driven.
> Data: 2026-04-23
> Escopo: domínio, persistência e casos de uso do módulo `training`
> Regras aplicadas: AGAUDIT v1.1 — Prompt 3

---

## Resumo executivo

| Métrica | Valor |
|---|---|
| Fontes analisadas | 9 arquivos (4 canon + 5 runtime) |
| Achados totais | 5 |
| Causas-raiz | 4 |
| Erros confirmados | 4 |
| Drifts prováveis | 1 |
| Severidade CRÍTICA | 1 |
| Severidade ALTA | 2 |
| Severidade MÉDIA | 2 |

**Veredicto geral:** O módulo training tem um bug de FSM crítico que permite transições de estado canonicamente proibidas (DRAFT→PUBLISHED, SCHEDULED→IN_PROGRESS), uma lacuna de persistência que torna 6 campos do domínio efetivamente perdidos após cada save, e dois guards de invariante ausentes na camada de aplicação. Nenhum desses achados é derivado de outro — são causas-raiz independentes que requerem ação direta.

---

## Fontes analisadas

**Canon:**
- `docs/hbtrack/modulos/training/STATE_MODEL_TRAINING.md` — FSM canônico com transições explicitamente proibidas
- `docs/hbtrack/modulos/training/DOMAIN_RULES_TRAINING.md` — 54 regras de domínio (DR-TRAIN-001..054)
- `docs/hbtrack/modulos/training/INVARIANTS_TRAINING.md` — invariantes de sistema (INV-TRAIN-*)
- `docs/hbtrack/modulos/training/PERMISSIONS_TRAINING.md` — tabela de permissões por operationId e role

**Runtime:**
- `src/training/domain/rules.py` — VALID_TRANSITIONS dict + funções assert_*
- `src/training/domain/entities/sessions.py` — dataclass TrainingSession
- `src/training/application/sessions/commands.py` — CreateTrainingSessionUseCase, TransitionTrainingSessionUseCase
- `src/training/infrastructure/models/sessions.py` — TrainingSessionModel (ORM)
- `src/training/infrastructure/repository/sessions.py` — TrainingSessionRepository.save() + _to_domain()

---

## Achados

---

### ACHADO-DP-001

```
ACHADO-ID: ACHADO-DP-001
Categoria: Violação de FSM canônico — transições proibidas permitidas
Módulo: training / domínio
Severidade: crítica
Estado: erro confirmado
Camadas em conflito: domínio (rules.py) ← canon (STATE_MODEL_TRAINING.md)
```

**Descrição:**

O dicionário `VALID_TRANSITIONS` em `src/training/domain/rules.py:136-161` inclui duas transições que o canon explicitamente proíbe:

1. `DRAFT → PUBLISHED` — o FSM canônico exige que DRAFT passe por SCHEDULED antes de atingir PUBLISHED. A rota direta DRAFT→PUBLISHED é **explicitamente proibida** em STATE_MODEL_TRAINING.md.
2. `SCHEDULED → IN_PROGRESS` — o FSM canônico exige que SCHEDULED passe por PUBLISHED antes de atingir IN_PROGRESS. A rota direta SCHEDULED→IN_PROGRESS é **explicitamente proibida** em STATE_MODEL_TRAINING.md.

Toda validação de transição no módulo passa por `assert_valid_transition()` (rules.py:170-178), que delega para `VALID_TRANSITIONS`. O bug está na definição do dict, não na função de validação em si.

**Evidência A — runtime (`src/training/domain/rules.py:136-161`):**
```python
VALID_TRANSITIONS: dict[TrainingSessionStatus, set[TrainingSessionStatus]] = {
    TrainingSessionStatus.DRAFT: {
        TrainingSessionStatus.SCHEDULED,
        TrainingSessionStatus.PUBLISHED,   # ← PROIBIDO pelo canon
        TrainingSessionStatus.CANCELLED,
    },
    TrainingSessionStatus.SCHEDULED: {
        TrainingSessionStatus.PUBLISHED,
        TrainingSessionStatus.IN_PROGRESS, # ← PROIBIDO pelo canon
        TrainingSessionStatus.CANCELLED,
    },
    ...
}
```

**Evidência B — canon (STATE_MODEL_TRAINING.md):**

O STATE_MODEL_TRAINING.md define explicitamente as rotas obrigatórias:
- DRAFT → SCHEDULED → PUBLISHED (rota obrigatória para publicação)
- SCHEDULED → PUBLISHED → IN_PROGRESS (rota obrigatória para iniciar sessão)

E lista como **transições proibidas** (seção "Transições Explicitamente Proibidas"):
- `DRAFT → PUBLISHED`
- `SCHEDULED → IN_PROGRESS`

**Evidência C — INV-TRAIN-017 (INVARIANTS_TRAINING.md):**

INV-TRAIN-017 reforça que o grafo FSM é fechado e que transições fora do grafo canônico devem ser rejeitadas com `InvalidStatusTransition`.

**Impacto operacional:**

Com DRAFT→PUBLISHED permitido, um coach pode publicar uma sessão sem:
- Passar por SCHEDULED (onde notificações de planejamento são emitidas)
- Satisfazer as pré-condições de publicação (INV-TRAIN-086 / DR-TRAIN-014)

Com SCHEDULED→IN_PROGRESS permitido, uma sessão pode entrar em andamento sem:
- Ter sido publicada para os atletas
- Ter o snapshot de conteúdo planejado imutabilizado (INV-TRAIN-088)

**Causa-raiz:**

`VALID_TRANSITIONS` foi escrito com um grafo mais permissivo do que o canon define — provavelmente por omissão durante a implementação inicial.

**Correção mínima:**

```python
VALID_TRANSITIONS: dict[TrainingSessionStatus, set[TrainingSessionStatus]] = {
    TrainingSessionStatus.DRAFT: {
        TrainingSessionStatus.SCHEDULED,   # removido: PUBLISHED
        TrainingSessionStatus.CANCELLED,
    },
    TrainingSessionStatus.SCHEDULED: {
        TrainingSessionStatus.PUBLISHED,   # removido: IN_PROGRESS
        TrainingSessionStatus.CANCELLED,
    },
    TrainingSessionStatus.PUBLISHED: {
        TrainingSessionStatus.SCHEDULED,
        TrainingSessionStatus.IN_PROGRESS,
        TrainingSessionStatus.CANCELLED,
    },
    ...
}
```

**Testes de regressão necessários:**

Após a correção, qualquer teste que chame `DRAFT→PUBLISHED` ou `SCHEDULED→IN_PROGRESS` diretamente deve falhar com `InvalidStatusTransition`. Se passarem, o teste está usando um caminho que bypassa a validação canônica.

**Bloqueia merge?:** sim — bug de lógica de negócio com impacto direto no produto

**Classificação:** erro confirmado (divergência intencional ou omissão — não é drift de sincronização)

---

### ACHADO-DP-002

```
ACHADO-ID: ACHADO-DP-002
Categoria: Gap de persistência — campos de domínio não mapeados no ORM
Módulo: training / persistência
Severidade: alta
Estado: erro confirmado
Camadas em conflito: domínio (entities/sessions.py) ↔ persistência (models/sessions.py, repository/sessions.py)
```

**Descrição:**

A entidade de domínio `TrainingSession` (`src/training/domain/entities/sessions.py`) declara 6 campos que **não existem** no modelo ORM (`src/training/infrastructure/models/sessions.py`) nem são mapeados no repositório (`save()` e `_to_domain()`):

| Campo do domínio | ORM | Repository.save() | Repository._to_domain() |
|---|---|---|---|
| `planned_content_snapshot` | ausente | ausente | ausente |
| `post_review_completed_by_user_id` | ausente | ausente | ausente |
| `post_review_deadline_at` | ausente | ausente | ausente |
| `post_review_completed` | ausente | ausente | ausente |
| `continuity_notes` | ausente | ausente | ausente |
| `objective_origin` | ausente | ausente | ausente |

O efeito prático é que esses campos existem no objeto Python em memória, mas:
- Nunca são persistidos quando `repository.save()` é chamado
- Nunca são recuperados quando `_to_domain()` reconstrói a entidade do banco
- São silenciosamente perdidos a cada ciclo save/load sem nenhum erro

**Evidência A — campos presentes no domínio (`src/training/domain/entities/sessions.py`):**

A entidade TrainingSession declara (via dataclass):
```python
planned_content_snapshot: Optional[dict] = None
post_review_completed_by_user_id: Optional[uuid.UUID] = None
post_review_deadline_at: Optional[datetime] = None
post_review_completed: Optional[bool] = None
continuity_notes: Optional[str] = None
objective_origin: Optional[str] = None
```

**Evidência B — campos ausentes no ORM (`src/training/infrastructure/models/sessions.py`):**

`TrainingSessionModel` não tem nenhuma das 6 colunas correspondentes. O banco nunca teve essas colunas (não há migration pendente para elas).

**Evidência C — repository não persiste:**

`TrainingSessionRepository.save()` e `_to_domain()` não referenciam nenhum dos 6 campos — confirmando que o gap de ORM implica gap de persistência total.

**Impacto canonicamente referenciado:**

- `planned_content_snapshot` é referenciado em INV-TRAIN-088: "conteúdo planejado é imutável após PUBLISHED" — sem persistência, esse invariante não pode ser verificado nem restaurado após reinicialização
- `post_review_*` campos são necessários para o fluxo de revisão pós-sessão (DR-TRAIN-049 e adjacentes)
- `continuity_notes` suporta planejamento de microciclo (DR-TRAIN-041)
- `objective_origin` necessário para DR-TRAIN-013 (validação de originNotes quando MANUAL_COACH_RATIONALE)

**Causa-raiz:**

A entidade de domínio foi expandida (provavelmente para suportar features em desenvolvimento ou canon atualizado) sem criar a migration Django correspondente nem atualizar o repositório.

**Correção mínima:**

1. Criar migration adicionando as 6 colunas ao `TrainingSessionModel`
2. Atualizar `save()` para persistir os 6 campos
3. Atualizar `_to_domain()` para reconstruí-los

**Correção ideal:**

Verificar se todos os campos são necessários para o MVP atual. Se `post_review_*` são para uma feature futura, mover para uma migration planejada e remover da entidade até a feature estar pronta — evitar campos "fantasmas" que existem em memória mas não em storage.

**Bloqueia merge?:** sim — dados silenciosamente perdidos a cada ciclo de persistência

**Classificação:** erro confirmado (ORM e repositório desatualizados em relação ao domínio)

---

### ACHADO-DP-003

```
ACHADO-ID: ACHADO-DP-003
Categoria: Guard de invariante ausente — pré-condições de publicação não verificadas
Módulo: training / aplicação
Severidade: alta
Estado: erro confirmado
Camadas em conflito: aplicação (commands.py) ← canon (INVARIANTS_TRAINING.md / DOMAIN_RULES_TRAINING.md)
```

**Descrição:**

`TransitionTrainingSessionUseCase.execute()` em `src/training/application/sessions/commands.py` executa a transição de estado validando apenas:
1. Se o ator tem permissão (via `_guard`)
2. Se a transição está no `VALID_TRANSITIONS` (via `assert_valid_transition`)

Mas **não verifica** as pré-condições mandatórias para a transição `→ PUBLISHED` definidas em INV-TRAIN-086 e DR-TRAIN-014:

| Pré-condição | Canon | Verificado no use case? |
|---|---|---|
| `sessionAt` deve estar definido e no futuro | DR-TRAIN-014 | ✗ ausente |
| ≥ 1 SessionObjective associado | DR-TRAIN-014 | ✗ ausente |
| ≥ 1 SessionBlock associado | DR-TRAIN-014 | ✗ ausente |
| `individualizationMode` definido | INV-TRAIN-086 | ✗ ausente |

**Evidência A — use case (`src/training/application/sessions/commands.py` — TransitionTrainingSessionUseCase):**

```python
class TransitionTrainingSessionUseCase:
    def execute(self, inp: TransitionTrainingSessionInput) -> TrainingSession:
        session = self._guard.load_for_transition(inp)
        session.status = inp.target_status
        self._repo.save(session)
        return session
```

A chamada `_guard.load_for_transition()` verifica permissões e transição válida pelo FSM — mas não contém a lógica de pré-condições de publicação.

**Evidência B — canon (INV-TRAIN-086 em INVARIANTS_TRAINING.md):**

INV-TRAIN-086 define: "A transição `→ PUBLISHED` só é permitida se: (a) `sessionAt` está definido e está no futuro, (b) existe ≥1 SessionObjective ativo, (c) existe ≥1 SessionBlock, (d) `individualizationMode` está definido."

**Evidência C — canon (DR-TRAIN-014 em DOMAIN_RULES_TRAINING.md):**

DR-TRAIN-014 reforça as mesmas condições como regras de domínio (não apenas invariantes).

**Impacto:**

Uma sessão pode ser publicada (e tornar-se visível para atletas) sem ter conteúdo planejado (`sessionAt` no passado, sem blocos, sem objetivo). Isso viola o contrato de negócio e pode causar confusão operacional — atletas recebem notificação de sessão publicada sem conteúdo.

**Causa-raiz:**

O guard `_guard.load_for_transition()` implementa apenas RBAC e FSM. A camada de pré-condições de negócio para a transição específica `→ PUBLISHED` não foi implementada no use case.

**Correção mínima:**

Adicionar ao `TransitionTrainingSessionUseCase.execute()`, antes de `session.status = inp.target_status`:

```python
if inp.target_status == TrainingSessionStatus.PUBLISHED:
    self._enforce_publish_preconditions(session)
```

Com `_enforce_publish_preconditions()` verificando:
- `session.session_at` definido e `> datetime.now(utc)`
- `len(session.objectives) >= 1`
- `len(session.blocks) >= 1`
- `session.individualization_mode is not None`

**Bloqueia merge?:** sim — invariante de negócio não aplicado permite estado incoerente

**Classificação:** erro confirmado (guard de pré-condição ausente — não é drift)

---

### ACHADO-DP-004

```
ACHADO-ID: ACHADO-DP-004
Categoria: Regra de domínio não verificada na criação — individualizationMode
Módulo: training / aplicação
Severidade: média
Estado: drift provável
Camadas em conflito: aplicação (commands.py) ← canon (DOMAIN_RULES_TRAINING.md)
```

**Descrição:**

DR-TRAIN-030 (DOMAIN_RULES_TRAINING.md) define: "`individualizationMode` é obrigatório para criação de sessão". O campo existe no schema de entrada (`CreateTrainingSessionIn`) como `Optional`, e `CreateTrainingSessionUseCase.execute()` não verifica se o campo foi fornecido.

**Evidência A — use case (`CreateTrainingSessionUseCase`):**

O use case cria a `TrainingSession` sem checar `individualization_mode is not None`. O campo pode chegar como `None` e a sessão é criada sem erro.

**Evidência B — schema (`src/training/schemas/sessions.py:70`):**

```python
class CreateTrainingSessionIn(Schema):
    ...
    # individualizationMode está ausente do schema de entrada
```

O schema `CreateTrainingSessionIn` não declara `individualization_mode` — o campo está ausente do input, o que significa que não há como o cliente fornecê-lo na criação, e a validação no use case não pode ter nada a verificar. **Isso configura uma situação dupla**: o campo é obrigatório pelo canon mas não está exposto no endpoint de criação.

**Evidência C — canon (DR-TRAIN-030):**

DR-TRAIN-030 marca `individualizationMode` como obrigatório no ato de criação — a omissão no schema de input implica que toda sessão criada viola essa regra canônica.

**Impacto:**

Toda sessão criada via API tem `individualizationMode = null`, violando DR-TRAIN-030. Quando o guard de publicação for implementado (ACHADO-DP-003), toda sessão existente no banco falhará na pré-condição de publicação por ausência de `individualizationMode`.

**Causa-raiz:**

O campo `individualizationMode` não foi incluído no schema de criação nem validado no use case. Pode ser um campo adicionado ao canon após a implementação inicial do endpoint (drift iterativo).

**Correção mínima:**

1. Adicionar `individualization_mode: str` ao `CreateTrainingSessionIn` (sem Optional, para forçar o cliente a fornecer)
2. Adicionar validação no `CreateTrainingSessionUseCase` verificando valores válidos (`"individual"`, `"group"`, `"hybrid"` — ou os valores canônicos definidos em DOMAIN_RULES_TRAINING.md)

**Bloqueia merge?:** não imediatamente (sem guard de publicação, o campo nulo não causa erro visível), mas bloqueia após ACHADO-DP-003 ser corrigido

**Classificação:** drift provável (campo canônico adicionado ao domínio sem atualização do endpoint)

---

### ACHADO-DP-005

```
ACHADO-ID: ACHADO-DP-005
Categoria: Regra de domínio não verificada na criação — sessão sem objetivo
Módulo: training / aplicação
Severidade: média
Estado: erro confirmado
Camadas em conflito: aplicação (commands.py) ← canon (DOMAIN_RULES_TRAINING.md)
```

**Descrição:**

DR-TRAIN-011 define: "Uma sessão deve ter pelo menos um `SessionObjective` para transitar de DRAFT para qualquer estado". Adicionalmente, DR-TRAIN-014 exige ≥1 `SessionObjective` para publicação. O `CreateTrainingSessionUseCase` não cria nenhum `SessionObjective` por default e não exige que um seja fornecido no payload de criação.

O resultado é que o estado DRAFT admite sessões sem objetivo, o que é tecnicamente permitido pelo canon (DRAFT é um rascunho). Porém:

1. A validação de transição de DRAFT → SCHEDULED deveria exigir ≥1 objetivo (DR-TRAIN-011 — "para transitar de DRAFT para qualquer estado")
2. A ausência de objetivo não é notificada ao usuário em nenhum momento antes da tentativa de publicação

**Evidência A — use case (`CreateTrainingSessionUseCase`):**

`execute()` cria a `TrainingSession` e retorna. Não há criação de `SessionObjective` inicial nem validação de que pelo menos um foi incluído no payload.

**Evidência B — canon (DR-TRAIN-011):**

"Para transitar de DRAFT para qualquer estado (SCHEDULED, CANCELLED), a sessão deve ter pelo menos 1 objetivo ativo."

**Nota sobre classificação:**

A regra DR-TRAIN-011 condiciona a **transição de DRAFT**, não a criação em DRAFT. Portanto, criar em DRAFT sem objetivo não é uma violação de DR-TRAIN-011 em si — a violação ocorre quando o coach tenta mover de DRAFT → SCHEDULED sem objetivo. O guard de transição deveria verificar isso, mas não verifica (similar ao ACHADO-DP-003 para publicação). O erro confirmado está no guard de transição ausente para DRAFT→SCHEDULED, não na criação.

**Impacto:**

Coach cria sessão sem objetivo, a move para SCHEDULED sem erro, e tenta publicar — onde (se ACHADO-DP-003 for corrigido) finalmente falha com erro de pré-condição. O fluxo de erros fica late e confuso para o usuário.

**Causa-raiz:**

`assert_valid_transition()` verifica apenas o grafo FSM — não as pré-condições de conteúdo por transição. A verificação de "≥1 objetivo" antes de DRAFT→SCHEDULED não foi implementada.

**Correção mínima:**

Adicionar ao `TransitionTrainingSessionUseCase.execute()`, para transição de DRAFT → SCHEDULED:

```python
if current_status == DRAFT and inp.target_status == SCHEDULED:
    if len(session.objectives) == 0:
        raise PreconditionError("DR-TRAIN-011: sessão deve ter ≥1 objetivo para ser agendada")
```

**Bloqueia merge?:** não imediatamente (sem guard, sessões sem objetivo progridem sem erro — problema de UX, não de consistência de dados)

**Classificação:** erro confirmado (guard ausente para pré-condição de transição DR-TRAIN-011)

---

## Agrupamento por causa-raiz

### CR-DP-001 — VALID_TRANSITIONS com arestas canonicamente proibidas

- **Achados originados:** ACHADO-DP-001
- **Arquivo:** `src/training/domain/rules.py:136-161`
- **Severidade consolidada:** crítica
- **Prioridade:** 1
- **Ação:** remover `PUBLISHED` de `DRAFT` e `IN_PROGRESS` de `SCHEDULED` no dict `VALID_TRANSITIONS`

---

### CR-DP-002 — Entidade de domínio expandida sem migration/repositório correspondente

- **Achados originados:** ACHADO-DP-002
- **Arquivos:** `src/training/infrastructure/models/sessions.py`, `src/training/infrastructure/repository/sessions.py`
- **Severidade consolidada:** alta
- **Prioridade:** 2
- **Ação:** criar migration com 6 colunas + atualizar `save()` e `_to_domain()`

---

### CR-DP-003 — Guard de pré-condições de transição não implementado

- **Achados originados:** ACHADO-DP-003 (→ PUBLISHED), ACHADO-DP-005 (DRAFT → SCHEDULED)
- **Arquivo:** `src/training/application/sessions/commands.py` — `TransitionTrainingSessionUseCase`
- **Severidade consolidada:** alta
- **Prioridade:** 3
- **Ação:** implementar verificações de pré-condição por transição alvo antes de atribuir `session.status`

---

### CR-DP-004 — individualizationMode ausente do schema de criação e do use case

- **Achados originados:** ACHADO-DP-004
- **Arquivos:** `src/training/schemas/sessions.py`, `src/training/application/sessions/commands.py`
- **Severidade consolidada:** média
- **Prioridade:** 4 (após CR-DP-003, pois o campo é uma das pré-condições de publicação)
- **Ação:** adicionar campo ao schema de input + validação no use case

---

## Tabela de achados por camada

| Camada | Achado | Severidade |
|---|---|---|
| Domínio — FSM | ACHADO-DP-001 (rules.py VALID_TRANSITIONS) | crítica |
| Persistência — ORM | ACHADO-DP-002 (6 campos sem coluna) | alta |
| Aplicação — guard | ACHADO-DP-003 (publish preconditions ausentes) | alta |
| Aplicação — input | ACHADO-DP-004 (individualizationMode ausente do schema) | média |
| Aplicação — guard | ACHADO-DP-005 (DRAFT→SCHEDULED sem verificação de objetivo) | média |

---

## Achados sem falsos positivos nesta análise

Todos os 5 achados têm evidência direta de código + referência canônica. Nenhum é derivado de outro achado desta análise.

A única dependência entre achados é de **prioridade operacional**: ACHADO-DP-004 (individualizationMode) torna-se um bloqueador visível apenas após ACHADO-DP-003 (guard de publicação) ser corrigido — mas ambos são bugs independentes com fixes independentes.

---

## Conexões com achados de outras análises

| Achado anterior | Relação |
|---|---|
| ACHADO-007 (runtime_findings) — migration pendente index | Mesmo módulo training/persistência; distinto — aquele é remoção de índice, este são campos ausentes |
| ACHADO-DP-001 (este) — FSM | Parcialmente mascarado pela ausência do guard de publicação (ACHADO-DP-003) — corrigir FSM sem corrigir o guard pode expor novos erros de fluxo |
| ACHADO-C-* (contract) — ErrorOut≠problem+json | Ortogonal — camada de API, não de domínio |
