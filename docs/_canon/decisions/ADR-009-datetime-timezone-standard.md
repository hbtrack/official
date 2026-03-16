# ADR-009: Padrão de Data/Hora e Política de Timezone — UTC obrigatório + RFC 3339

- Status: Accepted
- Date: 2026-03-15
- Deciders: Equipe HB Track
- Tags: data-conventions, datetime, timezone, matches, competitions
- Resolves: ARCH-003

## Context

`DATA_CONVENTIONS.md` §2 já define ISO 8601/RFC 3339 com sufixo `Z` e UTC como padrão de armazenamento. No entanto, não havia ADR formal elevando essas regras a decisão arquitetural vinculante, nem definindo o tratamento específico de:

- Eventos de partida que ocorrem em diferentes fusos horários (competições nacionais).
- Campo de timezone explícito obrigatório em eventos com localização geográfica.
- Política de conversão de exibição no frontend.
- Tratamento de durações de sessão de treino.

Sem esta ADR, campos `*_at`, `*_date` e `*_time` poderiam ser criados com semânticas inconsistentes entre módulos (`BLOCKED_MISSING_ARCH_DECISION` por ARCH-003).

## Decision

### Regra fundamental

**Todo timestamp é armazenado em UTC. Sem exceção.**

O backend nunca armazena hora local. Conversão para timezone local é exclusivamente responsabilidade do cliente (frontend ou consumidor da API).

### Formato canônico de wire (API → cliente)

Conforme `DATA_CONVENTIONS.md` §2 — esta ADR eleva esse padrão a normativo:

| Tipo | Formato | Exemplo |
|------|---------|---------|
| Evento pontual | `string` format `date-time` (RFC 3339) com `Z` obrigatório | `2026-03-15T18:30:00Z` |
| Data de calendário | `string` format `date` | `2026-03-15` |
| Duração | `string` format `duration` (ISO 8601) | `PT90M` |
| Intervalo | objeto `{ startAt, endAt }` ambos `date-time` | — |
| Apenas ano | `integer` format `int32` | `2026` |

**Proibido**: `+00:00` como sufixo (usar sempre `Z`), espaço entre data e hora, timestamp Unix sem documentação explícita.

### Campo `venueTimezone` obrigatório em eventos de partida

Partidas (`matches`) e eventos de competição (`competitions`) que ocorrem em local físico **devem incluir** o campo `venueTimezone` com o nome IANA da zona horária do local do evento.

```json
{
  "id": "...",
  "scheduledAt": "2026-03-15T18:30:00Z",
  "venueTimezone": "America/Sao_Paulo",
  "venue": "Arena Handball SP"
}
```

**Rationale**: jogos de competições nacionais podem ocorrer em locais com fuso diferente do clube base. O cliente precisa do timezone do local para exibição correta ao torcedor/atleta local.

`venueTimezone` não é obrigatório em:
- Sessões de treino (ocorrem na sede do clube, timezone inferível do time)
- Registros de wellness/medical (não têm localização geográfica relevante para exibição)

### PostgreSQL

Colunas de timestamp: sempre `TIMESTAMPTZ` (timestamp with time zone). Nunca `TIMESTAMP` sem timezone.

### Naming de campos — confirma DATA_CONVENTIONS.md §2.3

- Eventos: sufixo `At` na API (camelCase), `_at` no banco
- Datas: sufixo `Date` ou `On` na API, `_date` ou `_on` no banco
- Janelas: `startAt`/`endAt` na API, `start_at`/`end_at` no banco

## Consequences

### Positive
- UTC universal elimina ambiguidade entre módulos (matches, training, wellness, medical, analytics operam no mesmo espaço de tempo).
- `venueTimezone` resolve a necessidade real de apresentação localizada sem contaminar o armazenamento.
- Conforme com `DATA_CONVENTIONS.md` existente — sem breaking change para contratos existentes.

### Negative
- `venueTimezone` é campo adicional obrigatório em modelos de partida — aumenta tamanho de payload.
- Responsabilidade de conversão no frontend exige que todos os clientes implementem lógica de timezone — custo de desenvolvimento.

## Alternatives Considered

- **Armazenar hora local + timezone separado**: permite reconstrução de UTC, mas armazenamento dual é redundante e cria risco de inconsistência. Rejeitado.
- **Offset numérico em vez de IANA tz name**: `venueTimezone: -3` é ambíguo para horário de verão. Rejeitado: IANA tz name é preciso e suportado por Intl.DateTimeFormat no frontend.
- **Sempre UTC sem campo de timezone**: suficiente para a maioria dos casos, mas não cobre exibição localizada para jogos em outras regiões. Rejeitado para módulos `matches`/`competitions`.

## Links

- Resolves: `docs/_canon/ARCHITECTURE_DECISION_BACKLOG.md` ARCH-003
- SSOT de convenções: `docs/_canon/DATA_CONVENTIONS.md` §2 (este ADR eleva §2 a normativo)
- Módulos afetados: `matches`, `competitions`, `training`, `wellness`, `medical`, `analytics`, `seasons`
