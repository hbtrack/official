# ARCHIVED_NOTICE.md — Documentação Superseded

| Propriedade | Valor |
|---|---|
| ID | NOTICE-ARCHIVED-001 |
| Status | INFORMATIVO |
| Data | 2026-02-16 |
| Objetivo | Identificar docs legados superseded pela camada canônica |

---

## Convenção

Documentos listados abaixo **NÃO devem ser usados como fonte de verdade**.
A autoridade migrou para os documentos canônicos indicados na coluna "Superseded By".

Estes arquivos **não foram deletados** para preservar histórico e facilitar
buscas retroativas, mas **NÃO DEVEM ser editados**.

---

## Mapeamento: Documento Legado → Documento Canônico

| # | Documento Legado | Superseded By | Motivo |
|---|---|---|---|
| 1 | `docs/_ai/_context/approved-commands.yml` | `docs/_ai/_specs/approved_commands_registry.yaml` | YAML SSOT com schema validation substituiu o YML legado |
| 2 | `docs/_ai/_context/AGENT_GUARDRAILS.md` | `docs/_canon/_agent/AGENT_DRIFT_RULES.md` | Guardrails migrados para camada canônica de agente |
| 3 | `docs/_ai/_context/AGENT_CONSTRAINTS.md` | `docs/_canon/_agent/AGENT_ROLE_MATRIX.md` | Constraints de agente integrados ao Role Matrix canônico |
| 4 | `docs/_ai/_context/AGENT_RULES_ENGINE.md` | `docs/_canon/_agent/AI_ARCH_EXEC_PROTOCOL.md` | Rules engine superseded pelo protocolo de execução canônico |
| 5 | `docs/_ai/_guardrails/GUARDRAILS_INDEX.md` | `docs/_canon/_agent/AGENT_DRIFT_RULES.md` | Índice de guardrails consolidado nas drift rules |
| 6 | `docs/_ai/_guardrails/GUARDRAIL_POLICY_BASELINE.md` | `docs/_canon/05_MODELS_PIPELINE.md` | Policy de baseline integrada ao pipeline canônico |
| 7 | `docs/_ai/_guardrails/GUARDRAIL_POLICY_PARITY.md` | `docs/_canon/05_MODELS_PIPELINE.md` | Policy de parity integrada ao pipeline canônico |
| 8 | `docs/_ai/_guardrails/GUARDRAIL_POLICY_REQUIREMENTS.md` | `docs/_canon/05_MODELS_PIPELINE.md` | Policy de requirements integrada ao pipeline canônico |
| 9 | `docs/_ai/06_AGENT-PROMPTS.md` | `docs/_canon/06_AGENT_PROMPTS_MODELS.md` | Prompts migrados para camada canônica |
| 10 | `docs/_ai/07_AGENT_ROUTING_MAP.md` | `docs/_canon/07_AGENT_ROUTING_MAP.md` | Routing map migrado (SSOT agora é o canônico) |

---

## Status dos Documentos

- **ARCHIVED**: Não editar. Referência histórica apenas.
- **ACTIVE**: Documento canônico vigente (ver coluna "Superseded By").

## Orientação para Agents

Se um agente referenciar qualquer documento da coluna "Documento Legado",
**DEVE** ser redirecionado para o documento canônico correspondente.

A camada `docs/_ai/_context/` e `docs/_ai/_guardrails/` são consideradas
**ARCHIVED** em sua totalidade. Para contexto operacional de agente, usar
exclusivamente `docs/_canon/_agent/`.

---

**Gerado por:** Sprint P4 — Consolidação Documental
**Referência:** `docs/_canon/01_AUTHORITY_SSOT.md`
