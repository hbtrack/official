# ADR-018: HYBRID Persistence Pattern

- Status: Accepted
- Date: 2026-03-16
- Deciders: Equipe HB Track
- Tags: architecture, persistence, event-sourcing, hybrid, training, platform
- Promotes: TRAIN-DEC-029, TRAIN-DEC-030, TRAIN-DEC-031

---

## Context

O HB Track opera sobre dois tipos fundamentalmente distintos de dados:

1. **Estado operacional mutável** — agregados que passam por um ciclo de vida definido (DRAFT → … → COMPLETED). Requerem leitura e escrita eficientes do estado atual. CRUD é o padrão adequado.
2. **Fatos históricos imutáveis** — eventos que ocorreram em um ponto no tempo (presença marcada, sessão iniciada, carga registrada). Sobrescrever esses dados destrói valor analítico e auditável.

Sistemas que tratam ambos da mesma forma incorrem em um de dois problemas:
- **CRUD puro para tudo**: perde histórico de fatos; análise retrospectiva fica dependente de snapshots frágeis.
- **Event sourcing puro para tudo**: complexidade excessiva para entidades de estado simples; custo de infraestrutura injustificado.

O módulo `training` foi o primeiro a manifestar essa tensão: sessões têm ciclo de vida (CRUD adequado), mas presença, execução e observações são fatos históricos (append-only adequado).

---

## Decision

Módulos HB Track que possuem **ambos os tipos de dado** são classificados como **HYBRID** e devem seguir este padrão:

### Parte CRUD

Gerencia o **estado operacional atual** do agregado:
- Ciclo de vida do agregado (criação, edição, transições de estado)
- Dados de planejamento e configuração
- Templates e estruturas de design-time

Operações: `POST`, `GET`, `PATCH`, `DELETE` (soft) sobre o agregado.

### Parte append-only

Gerencia **fatos com valor histórico** que nunca devem ser sobrescritos:
- Eventos que ocorreram em um tempo `T` observado
- Fatos cuja replay ou reprocessamento tem valor de negócio real
- Dados que servem de fonte primária para cálculos analíticos

Operações: `POST` apenas (fato novo). Nunca `PATCH` ou `DELETE` destrutivo.

### Critérios obrigatórios para classificar um dado como append-only

Um fato só é append-only se satisfizer **todos** os critérios:

1. Valor de negócio do histórico é explícito (não especulativo).
2. Escrita é naturalmente factual (evento ocorrido em tempo `T` observado).
3. Pelo menos um caso de replay ou projeção é real, não hipotético.
4. Idempotência está definida (`dedupe_key` ou `idempotency_key`).
5. Versionamento de schema de evento está definido.
6. Política de reprocessamento está definida.
7. Observabilidade para falhas de projeção existe.
8. Retenção e custo são aceitáveis.
9. A equipe consegue depurar o fluxo com segurança.
10. CRUD com tabela de auditoria **não** resolve o mesmo problema de forma mais simples.

Se qualquer critério falhar, usar CRUD com `audit_log` append-only separado.

### Distinção obrigatória de timestamps

Todo fato append-only deve registrar explicitamente:
- `observed_at` — quando o fato ocorreu no mundo real
- `ingested_at` — quando o HB Track recebeu o registro (set pelo servidor)

Esses campos não podem ser inferidos como iguais a menos que a regra de mapeamento estabeleça isso explicitamente.

### Fatos append-only canônicos do módulo `training`

| Fato | Entidade | Evento emitido |
|---|---|---|
| `presence_registered` | Presença de atleta em sessão | `TRAINING_ATTENDANCE_MARKED` |
| `session_started` | Início efetivo de sessão | `SESSION_STARTED` |
| `session_finished` | Conclusão de sessão | `SESSION_COMPLETED` |
| `drill_completed` | Conclusão de exercício por atleta | — (Fase 2) |
| `load_recorded` | Registro de carga realizada | — (Fase 2) |
| `coach_observation_added` | Observação qualitativa do treinador | — (Fase 2) |

### O que é CRUD no módulo `training`

- Agregado `training_session` e seu ciclo de vida
- `session_block`, `session_objective`
- `session_templates` e `planning_periodization`
- `mesocycle`, `microcycle`

---

## Consequences

### Positive

- Histórico de fatos preservado e auditável; reprocessamento possível.
- Estado operacional simples de consultar e atualizar sem overhead de event sourcing.
- Separação explícita facilita raciocínio sobre o que é mutável vs. imutável.
- Alinhado com padrão de mercado: Teamworks AMS, Bridge, XPS mantêm distinção clara entre planejamento (mutável) e fatos realizados (imutável).

### Negative

- Fluxo HYBRID é mais complexo que CRUD puro — requer consumidor claro para cada tipo de dado.
- Risco de classificação errada (dado CRUD tratado como append-only ou vice-versa); os 10 critérios acima mitigam esse risco.

---

## Alternatives Considered

- **CRUD puro para tudo**: rejeitado — perde fatos históricos de execução; impossibilita analytics retroativo confiável.
- **Event sourcing puro para tudo**: rejeitado — complexidade injustificada para entidades de estado operacional simples (sessões, ciclos); custo de infraestrutura não justificado pelo valor.
- **CRUD + audit table universal**: aceitável como fallback quando os 10 critérios append-only não são todos satisfeitos. Não é HYBRID.

---

## Links

- Related docs: `docs/hbtrack/decisoes/ARCH_DECISIONS_TRAINING.md` (TRAIN-DEC-029, TRAIN-DEC-030, TRAIN-DEC-031)
- Related contracts: `contracts/openapi/paths/training.yaml` (`POST /{id}/start`, `POST /{id}/complete`, `POST /{id}/attendance`)
- Related axioms: `.contract_driven/DOMAIN_AXIOMS.json` (`event_type`: `SESSION_STARTED`, `SESSION_COMPLETED`, `TRAINING_ATTENDANCE_MARKED`)
