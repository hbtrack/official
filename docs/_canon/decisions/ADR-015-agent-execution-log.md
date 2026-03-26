# ADR-015: Política de Log de Execução de Agente (Agent Execution Log)

- Status: Accepted
- Date: 2026-03-15
- Deciders: Equipe HB Track
- Tags: agent-governance, observability, cdd, pre-contract-orchestrator
- Resolves: ARCH-009
- Priority: importante — deferido v0.5 (implementação em v0.5; estrutura pode ser usada manualmente antes)

## Context

O HB Track usa um modelo de desenvolvimento Contract-Driven com pré-contrato orquestrado por agente (ver `.contract_driven/agent_prompts/pre_contract_orchestrator.prompt.md`). O agente toma decisões sobre fases, bloqueadores encontrados, artefatos consultados e worker de destino. Sem log de execução, não existe rastreabilidade dessas decisões, impossibilitando:

- Auditoria de "por que o agente decidiu X" após o fato.
- Identificação de loops ou conflitos repetidos entre execuções.
- Correlação entre um artefato de contrato gerado e a sessão de agente que o originou.
- Evidência para gates de governança que verificam o fluxo pré-contrato.

## Decision

### Localização e formato de arquivos

- Diretório: `_reports/agent_execution/`
- Gitignore: `_reports/agent_execution/` deve estar em `.gitignore` (logs operacionais, não artefatos de contrato).
- Um arquivo por sessão de agente: `YYYY-MM-DD_<sessionId>.json`
  - Onde `sessionId` é UUID v4 gerado pelo orquestrador no início da sessão.
- Encoding: UTF-8.

### Estrutura do registro JSON (array de entradas no arquivo)

```json
{
  "schemaVersion": "1.0",
  "sessionId": "<UUID v4>",
  "startedAt": "<ISO8601+Z>",
  "endedAt": "<ISO8601+Z>",
  "module": "<nome_do_módulo_canônico ou null>",
  "taskType": "<new_module|new_contract|contract_revision|new_state_model|new_ui_contract|architecture_review>",
  "entries": [
    {
      "timestamp": "<ISO8601+Z>",
      "phase": "<ROUTING|FOUNDATION_CHECK|DECISION_DISCOVERY|DOMAIN_ASSEMBLY|WORKER_HANDOFF>",
      "result": "<PASS|BLOCK|SKIP|HANDOFF>",
      "blocksEmitted": ["<BLOCKER_CODE>"],
      "artifactsRead": ["<caminho_relativo_do_artefato>"],
      "workerDest": "<nome_do_worker_prompt ou null>",
      "decisionsConsulted": ["<ARCH-NNN>"],
      "notes": "<texto livre opcional — contexto adicional>"
    }
  ]
}
```

Fases canônicas:

| Fase | Descrição |
|------|-----------|
| `ROUTING` | Phase 0 — determinação do tipo de tarefa e módulo |
| `FOUNDATION_CHECK` | Phase 1 — verificação de artefatos fundacionais |
| `DECISION_DISCOVERY` | Phase 2 — verificação de ADRs pendentes |
| `DOMAIN_ASSEMBLY` | Phase 3 — montagem do contexto de domínio |
| `WORKER_HANDOFF` | Phase 4 — handoff para worker específico |

### Política de retenção

- 30 dias (alinhado com `ADR-011` — logs operacionais de infraestrutura).
- Após 30 dias: arquivo pode ser deletado. Não há obrigação de archive.
- Script de purge: `scripts/ops/purge_retention.py` (a ser implementado em v0.5) incluirá `_reports/agent_execution/` na rotina.

### Integração com gates

- Este log **não substitui** os artefatos de contrato (OpenAPI, AsyncAPI, schemas JSON).
- O gate `ARCH_DECISION_PRESENCE_GATE` usa o backlog de ADRs, não o log de agente, para bloquear contratos.
- O log de agente é **evidência suplementar** para auditoria pós-fato, não input de gate automático para v0.

### Criação manual (antes de v0.5)

Até a implementação do `pre_contract_orchestrator` como ferramenta automatizada, o log pode ser criado manualmente pelo agente em cada sessão de trabalho de pré-contrato. A estrutura JSON acima é o formato canônico independente de ser gerado automaticamente ou manualmente.

### Data safety no log de agente

- `artifactsRead`: apenas caminhos de arquivo — nunca conteúdo dos artefatos.
- `notes`: texto livre de contexto técnico — sem PHI, sem CREDENTIALS, sem PII de usuários do sistema.
- `actorId` de usuário final: não registrado no log de agente (log de desenvolvimento, não de operação).

## Consequences

### Positive
- Rastreabilidade de decisões do agente durante desenvolvimento — cadeia de evidência para governança CDD.
- Identifica padrões de bloqueio recorrentes (ex: ARCH-NNN sempre bloqueando o mesmo módulo).
- Possibilita correlação entre sessão de agente e contrato gerado via `sessionId`.

### Negative
- Criação manual em v0.x adiciona overhead ao fluxo de agente.
- Sem automação de purge em v0, arquivo cresce indefinidamente até v0.5.
- Estrutura JSON pode evoluir (schema version `1.0` — mudanças incrementais com bump de versão).

## Alternatives Considered

- **Log integrado ao módulo `audit` de produção**: acoplamento inadequado — log de desenvolvimento de agente não deve estar misturado com auditoria de eventos de negócio. Rejeitado.
- **Sem log estruturado — apenas notas em PRs**: não machine-readable, difícil de correlacionar automaticamente. Rejeitado.
- **OpenTelemetry spans para agente**: adequado para sistemas altamente automatizados em escala, overhead excessivo para v0. Candidato para v2+.

## Links

- Resolves: `docs/_canon/ARCHITECTURE_DECISION_BACKLOG.md` ARCH-009
- Related: `.contract_driven/agent_prompts/pre_contract_orchestrator.prompt.md` (emite os logs)
- Related: `docs/_canon/decisions/ADR-011-retention-policy.md` (30 dias retenção)
- Related: `docs/_canon/decisions/ADR-013-logging-policy.md` (data safety rules)
