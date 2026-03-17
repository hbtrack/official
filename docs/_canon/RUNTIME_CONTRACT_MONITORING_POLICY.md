# RUNTIME_CONTRACT_MONITORING_POLICY.md
> Documento normativo — SSOT para monitoramento de contratos em produção no HB Track.
> Versão: 1.0.0 | Status: active | Criado: 2026-03-17
> Decisão: ADR-029

## 1. Princípio

Contratos violados em produção = dados corrompidos ou funcionalidades quebradas para atletas e treinadores.
O sistema deve detectar automaticamente qualquer divergência entre o comportamento real da API e o contrato OpenAPI.

## 2. O Que Monitorar

| # | O que | Como detectar | Alerta |
|---|---|---|---|
| M1 | Respostas com status code não documentado no contrato | Middleware de validação | Imediato |
| M2 | Payloads que violam JSON Schema (campos ausentes, tipos errados) | Middleware de validação | Imediato |
| M3 | Latência p99 > 2x do SLA definido no contrato | Prometheus + alertmanager | 5 min |
| M4 | Taxa de erro HTTP 5xx > 1% em qualquer endpoint por 5 min | Prometheus | 5 min |
| M5 | Taxa de erro HTTP 4xx > 20% em qualquer endpoint por 5 min | Prometheus | 10 min |
| M6 | Contrato drift (schema em produção diverge do contrato commitado) | Gate no deploy pipeline | Bloqueio de deploy |

## 3. Ferramentas Recomendadas

| Ferramenta | Uso | Obrigatório |
|---|---|---|
| **Sentry** | Captura de exceções de runtime + alertas de erro | Sim (pós-v1.0) |
| **OpenTelemetry** | Instrumentação de traces e métricas (sem vendor lock-in) | Sim (pós-v1.0) |
| **Prometheus + Grafana** | Métricas de negócio + dashboards | Sim (pós-v1.0) |
| **Optic** | Contract drift detection — compara tráfego real com OpenAPI | Recomendado |
| **FastAPI middleware** | Validação inline de request/response contra schema | Sim (em implementação) |

## 4. Middleware de Validação (FastAPI)

Toda resposta da API deve ser validada contra o contrato OpenAPI antes de retornar ao cliente.
Implementar como middleware ASGI em `Hb Track - Backend/src/shared/middleware/contract_validation.py`:

```python
# Lógica esperada (a ser implementada no generate_code worker):
# 1. Interceptar response
# 2. Validar status code contra operação do OpenAPI
# 3. Validar body contra response schema do OpenAPI
# 4. Se inválido → logar violation + retornar resposta com header X-Contract-Violation: true
# 5. Nunca bloquear resposta em produção — apenas alertar (modo observação)
```

Modo de operação:
- **Desenvolvimento:** modo bloqueante (lança exceção se violação detectada)
- **Staging:** modo bloqueante (falha o teste de integração)
- **Produção:** modo observação (loga + alerta, nunca bloqueia usuário)

## 5. Alertas Obrigatórios

### Nível CRÍTICO (alerta imediato → ação em < 15 min)
- Contract violation detectada em produção (M1, M2)
- Taxa de erro 5xx > 5% por 2 minutos (M4)

### Nível ALTO (alerta em < 1h)
- Latência p99 > 2s por 5 minutos (M3)
- Taxa de erro 5xx entre 1-5% por 5 minutos (M4)

### Nível MÉDIO (relatório diário)
- Taxa de erro 4xx > 20% por 10 minutos (M5)
- Endpoints sem chamadas por > 7 dias (possível feature abandonada)

## 6. Conexão com o Pipeline CDD

| Evento | Ação automática |
|---|---|
| Contract violation detectada em produção | Criar `BLOCKED_CONTRACT_CONFLICT` no backlog |
| Drift detectado entre tráfego e contrato | Acionar worker `contract_revision` para o módulo afetado |
| SLA violado por > 24h | Criar ADR de performance para o módulo afetado |
| Error rate > 5% persistente | Trigger de rollback automático (ver DEPLOY_PIPELINE.md) |

## 7. Relatórios de Monitoramento

Relatórios gerados em: `_reports/runtime/`

| Relatório | Frequência | Path |
|---|---|---|
| Contract violations daily | Diário | `_reports/runtime/contract_violations_<date>.json` |
| SLA compliance weekly | Semanal | `_reports/runtime/sla_compliance_<week>.json` |
| Error rate summary | Diário | `_reports/runtime/error_rate_<date>.json` |

## 8. Gate

`MONITORING_POLICY_GATE` (order 15I) verifica:
- Se `RUNTIME_CONTRACT_MONITORING_POLICY.md` existe → PASS
- Se ADR-029 existe → PASS
- Se nenhum existe → SKIP_NOT_APPLICABLE (pré-implementação)
- Se apenas um existe → DEGRADED

## 9. Referências

- ADR: `docs/_canon/decisions/ADR-029-runtime-monitoring.md`
- Deploy: `docs/_canon/DEPLOY_PIPELINE.md` (rollback automático conectado ao monitoramento)
- Arquitetura: `docs/_canon/CODE_ARCHITECTURE.md` (middleware de validação no layer Interface)
- Reports: `_reports/runtime/` (gerados em produção, não commitados)
