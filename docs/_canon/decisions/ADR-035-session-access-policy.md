# ADR-035: SessionAccessPolicy — Modelo de Autorização para Sessões de Treino

- Status: Accepted
- Date: 2026-04-22
- Deciders: Equipe HB Track
- Tags: security, authorization, bola, bfla, owasp, training
- Resolves: P14 (análise adversarial refactor training — .dev/decisões/rafatora_training.md §7.3)
- Supersedes: lógica dispersa em `assert_can_*` de `domain/rules.py` (Fase 4 do refactor training)

## Contexto

Durante o refactor do módulo `training` (commit `1422d446`, Fase 4), a classe `SessionAccessPolicy` foi introduzida em `src/training/domain/policies/session_access.py` para centralizar as regras de controle de acesso a sessões de treino. A análise adversarial posterior (21/04/2026) identificou que esta mudança de superfície de autorização foi commitada num refactor estrutural **sem ADR formal, sem RFC de segurança nem checklist OWASP explícito**.

Esta ADR formaliza retroativamente a decisão arquitetural e documenta o threat model coberto.

## Decisão

### 1. Centralização via `SessionAccessPolicy`

As verificações de autorização para sessões de treino são consolidadas na classe `SessionAccessPolicy` (application-friendly, domain-puro) em vez de dispersas em múltiplas funções `assert_can_*` em `domain/rules.py`.

**Benefícios**:
- Interface orientada a *intenção* (`require_readable`, `require_mutable`, `require_in_progress`, `require_cancellable`, `require_archivable`) em vez de verbos de operação
- Único ponto de auditoria para alterações de política
- Testável de forma isolada sem nenhuma dependência de framework

### 2. Cobertura de threats OWASP

| Ameaça | OWASP API | Como mitigada |
|---|---|---|
| BOLA (Broken Object Level Authorization) | API1:2023 | `require_readable`: staff acessa qualquer sessão; athlete só acessa sessão onde consta em `athlete_ids` |
| BFLA (Broken Function Level Authorization) | API5:2023 | `require_mutable`, `require_in_progress`, `require_cancellable`, `require_archivable`: só `STAFF_ROLES` ({admin, coordinator, coach}) podem executar operações de escrita |
| Excessive Data Exposure | API3:2023 | Não aplicável neste nível — coberto pelos schemas Pydantic de output |

#### `require_readable` — BOLA

```python
def require_readable(self, session, role, actor_id, athlete_ids):
    if role in STAFF_ROLES:
        return                         # staff vê todas as sessões do time
    if role == RoleLabel.ATHLETE:
        if actor_id not in athlete_ids:
            raise InsufficientPrivilege("BOLA: athlete não pertence a esta sessão")
        return
    raise InsufficientPrivilege(...)   # roles desconhecidos: acesso negado por padrão
```

**Invariante**: acesso negado por default — roles desconhecidos levantam `InsufficientPrivilege` mesmo sem correspondência explícita. Fail-closed.

#### `require_mutable` — BFLA

```python
def require_mutable(self, session, role):
    if role not in STAFF_ROLES:
        raise InsufficientPrivilege(...)
    if session.status not in MUTABLE_STATES:
        raise SessionNotMutable(...)
```

**Invariante**: athletes nunca modificam sessões (BFLA). Sessões fora de `MUTABLE_STATES` (`{DRAFT, PLANNED, PUBLISHED}`) não são modificáveis por ninguém.

### 3. `SessionGuard` — encapsulamento de padrão repetido

`SessionGuard` (mesmo arquivo) encapsula o padrão `load → NotFound → policy.require_* → return` que aparecia em 10+ UseCases. Não introduz nova lógica de autorização — apenas elimina repetição.

### 4. Propriedades de segurança mantidas

- `SessionAccessPolicy` não importa Django, não importa infrastructure — testável de forma pura.
- Não armazena estado — instanciável sem efeitos colaterais.
- Todos os métodos levantam `InsufficientPrivilege` (subtipo de `AuthorizationError`) que é mapeada para HTTP 403 em `api/errors.py`.
- `InsufficientPrivilege` nunca vaza informação sobre *por que* a negação ocorreu além da mensagem genérica (sem `session.id` ou `actor_id` na mensagem).

### 5. Cobertura de testes

| Cenário | Arquivo |
|---|---|
| Staff acessa qualquer sessão | `test_phase4_policy_guard_services.py` |
| Athlete BOLA: id correto | `test_phase4_policy_guard_services.py` |
| Athlete BOLA: id errado → 403 | `test_phase4_policy_guard_services.py` |
| BFLA: athlete tenta modificar → 403 | `test_restrictions.py`, `test_phase4_policy_guard_services.py` |
| Transições inválidas (FSM) | `test_state_machine.py`, `test_forbidden_transitions.py` |
| SessionGuard.require_session → NotFound | `test_phase4_policy_guard_services.py` |

## Alternativas consideradas

| Alternativa | Motivo de rejeição |
|---|---|
| Manter `assert_can_*` dispersos em `domain/rules.py` | Baixa coesão; sem ponto único de auditoria; dificulta testes |
| Middleware de autorização em `api/` | Acoplaria lógica de domínio ao layer HTTP; impede reutilização em jobs assíncronos |
| Django Ninja `permission_classes` | Não disponível no contexto de Router; requereria refatoração de todos os sub-routers |
| ABAC (Attribute-Based Access Control) | Over-engineering para 5 roles estáticos; escala se requisitos de multi-tenancy crescerem |

## Consequências

- **Positivo**: ponto único de enforcement, testável em isolamento, fail-closed
- **Positivo**: `SessionGuard` elimina ~40 linhas de boilerplate repetido em UseCases
- **Negativo**: a refatoração que introduziu `SessionAccessPolicy` não passou por RFC de segurança formal — mitigado por esta ADR retroativa + testes de cobertura validados
- **Dívida técnica**: `assert_can_*` em `domain/rules.py` ainda coexistem (shims). Serão removidos em N+2 junto com os demais shims (ver ADR-014 — Deprecation Policy).

## Referências

- ADR-008: Estratégia de Autorização (RBAC flat)
- ADR-017: Training Session State Machine (define MUTABLE_STATES)
- OWASP API Security Top 10 2023 — API1 (BOLA), API5 (BFLA)
- `src/training/domain/policies/session_access.py`
- `.dev/decisões/rafatora_training.md` §7.3 P14 (evidência da gap)
