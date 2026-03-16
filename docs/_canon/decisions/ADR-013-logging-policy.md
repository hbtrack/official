# ADR-013: Política de Logging e Observabilidade

- Status: Accepted
- Date: 2026-03-15
- Deciders: Equipe HB Track
- Tags: observability, logging, tracing, security, phi
- Resolves: ARCH-007
- Priority: importante — deferido v0.5 (estrutura de contrato pode ser criada antes; implementação completa em v0.5)

## Context

O HB Track tem múltiplos módulos Python/FastAPI sem política uniforme de logging. Sem padronização: logs são freeform (dificulta parsing), não há correlação de requisição entre serviços (sem trace ID), dados sensíveis podem aparecer acidentalmente em logs de debug, e eventos críticos de segurança (auth, deletes) podem não ser registrados.

Este ADR formaliza o padrão de logging estruturado, propagação de `X-Flow-ID` e as regras de data-safety em logs.

## Decision

### Formato e destino

- **Formato**: JSON estruturado em todas as saídas de log.
- **Destino**: `stdout` exclusivamente. Nenhum logger escreve em arquivo diretamente. O operador de infraestrutura (Docker, systemd, VPS) é responsável por coletar e redirecionar.
- **Biblioteca Python**: `structlog` com configuração de JSON renderer é preferida. Fallback: `logging` stdlib com `JsonFormatter` (ex: `python-json-logger`).
- **Formato de timestamp**: ISO 8601 + Z (conforme ADR-009): `2026-03-15T14:30:00.123Z`.

### Campos obrigatórios em todos os registros

```json
{
  "timestamp": "<ISO8601+Z>",
  "level": "<DEBUG|INFO|WARNING|ERROR|CRITICAL>",
  "service": "hbtrack-api",
  "module": "<nome_do_módulo_canônico>",
  "operation": "<nome_da_operação_ou_endpoint>",
  "flowId": "<UUID v4 do X-Flow-ID>"
}
```

Campos adicionais permitidos: `actorId` (UUID do usuário autenticado, nunca nome/email), `resourceId`, `durationMs`, `httpStatus`, `error` (apenas mensagem — sem stack trace com PII).

### Propagação de X-Flow-ID

- Toda requisição HTTP de entrada deve receber um `X-Flow-ID` (UUID v4).
- Se a requisição não tiver `X-Flow-ID` no header: o gateway/middleware gera um novo.
- O `flowId` deve ser propagado para:
  - Todos os logs da requisição naquele módulo.
  - Headers de saída para serviços downstream (workers Celery, chamadas HTTP internas).
  - Resposta HTTP (header `X-Flow-ID` presente).
- Middleware de FastAPI responsável pela injeção/extração do `flowId` no request context.

### Níveis de log por ambiente

| Ambiente | Nível mínimo | Observação |
|----------|-------------|-----------|
| Desenvolvimento | `DEBUG` | Todos os níveis habilitados |
| Staging | `INFO` | Sem DEBUG |
| Produção | `INFO` | Sem DEBUG; `ERROR` sempre emitido |

### Data safety em logs (obrigatório em todos os ambientes)

| Classe de dado (ADR-010) | Regra de log |
|--------------------------|-------------|
| `PHI` | **Nunca logar**; se unavoidável usar `[PHI_REDACTED]` |
| `CREDENTIALS` | **Nunca logar**; se unavoidável usar `[CREDENTIALS_REDACTED]` |
| `PII` | Mascaramento parcial quando necessário para debug: `jo***hn` |
| `BUSINESS_SENSITIVE` | `[REDACTED]` |
| `PUBLIC` | Sem restrição |

**Regra de exceção**: em nenhuma circunstância — incluindo exceções não tratadas, stack traces, logs de DEBUG — campos `PHI` ou `CREDENTIALS` entram em logs sem mascaramento.

### Eventos de segurança obrigatórios (sempre INFO ou superior)

Os eventos abaixo devem ser logados independente da configuração de nível:

| Evento | Campos obrigatórios | Módulo |
|--------|-------------------|--------|
| Autenticação bem-sucedida | `actorId`, `flowId`, `ipAddress` (mascarado: último octeto `*.x`) | `identity_access` |
| Falha de autenticação | `reason` (sem credencial), `flowId`, `ipAddress` | `identity_access` |
| Refresh de token | `actorId`, `flowId` | `identity_access` |
| Logout / revogação de token | `actorId`, `jti`, `flowId` | `identity_access` |
| Acesso a recurso proibido (403) | `actorId`, `resourceId`, `operation`, `flowId` | qualquer |
| Delete de recurso crítico | `actorId`, `resourceId`, `resourceType`, `flowId` | qualquer |
| Purge LGPD | `actorId`, `affectedUserId`, `fieldsAffected`, `flowId` | `users`, `audit` |

### Logs de analytics vs. logs de aplicação

- Logs de aplicação (este ADR): observabilidade operacional — erros, latência, auditoria de segurança.
- Eventos de analytics (comportamento do produto): responsabilidade do módulo `analytics` via eventos assíncronos — **não** misturar com logs de aplicação.

## Consequences

### Positive
- JSON estruturado viabiliza parsing automático, alertas e dashboards.
- `X-Flow-ID` permite correlacionar todos os logs de uma requisição entre módulos.
- Data safety rules previnem vazamento acidental de PHI por logs de debug.
- Eventos de segurança obrigatórios criam trilha de auditoria mínima mesmo sem módulo `audit` totalmente implementado.

### Negative
- Transição requer atualizar todos os `print()` e `logging.basicConfig()` existentes para `structlog`/JsonFormatter.
- Mascaramento de PII em logs torna debugging de issues de usuário específico mais lento.
- `INFO` em produção pode perder contexto de erros intermitentes que só aparecem em `DEBUG`.

## Alternatives Considered

- **OpenTelemetry desde o início**: padrão de indústria para traces distribuídos, mas requer collector, OTLP endpoint e overhead de infraestrutura. Candidato para v1.0+.
- **Logs de texto livre**: zero custo de implementação, mas impossível de parsear automaticamente. Rejeitado.
- **Syslog format**: mais antigo, menos expressivo que JSON para campos estruturados. Rejeitado.

## Links

- Resolves: `docs/_canon/ARCHITECTURE_DECISION_BACKLOG.md` ARCH-007
- Related: `docs/_canon/SECURITY_RULES.md`
- Related: `docs/_canon/decisions/ADR-010-sensitive-data-policy.md` (classes de sensibilidade)
- Related: `docs/_canon/decisions/ADR-012-secrets-policy.md` (nunca logar secrets)
- Related: `docs/_canon/decisions/ADR-009-datetime-timezone-standard.md` (formato de timestamp)
