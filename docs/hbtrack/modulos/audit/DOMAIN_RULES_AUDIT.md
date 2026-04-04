---
module: "audit"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: false
contract_path_ref: "../../../../contracts/openapi/paths/audit.yaml"
schemas_ref: "../../../../contracts/schemas/audit/"
type: "domain-rules"
updated: "2026-03-16"
---

# DOMAIN_RULES_AUDIT.md

## Objetivo
Registrar as regras de negócio do módulo `audit`.

## Fonte do domínio
- `docs/_canon/MODULE_SOURCE_AUTHORITY_MATRIX.yaml`
- `contracts/schemas/audit/audit_entry.schema.json`
- `docs/hbtrack/modulos/audit/INVARIANTS_AUDIT.md`
- Benchmarks de logging/auditoria permitidos via authority matrix (`OWASP`)

## Regras de negócio
| ID | Regra | Entidades afetadas | Fonte | Observações |
|---|---|---|---|---|
| DR-AUD-001 | `audit` é soberano do trilho imutável de ator, ação, alvo, instante, origem, correlação e resultado. | `AuditEntry` | Authority matrix `audit` | Fonte de evidência operacional |
| DR-AUD-002 | `beforeSummary` e `afterSummary` são resumos saneados do estado antes/depois; o módulo não deve replicar payloads integrais sensíveis sem contrato explícito. | `AuditEntry` | Authority matrix `must_not_infer` | Minimização de dados |
| DR-AUD-003 | `correlationId` agrupa etapas técnicas e funcionais de uma mesma operação distribuída no monólito modular. | `AuditEntry` | Authority matrix `correlation_id` | Rastreabilidade ponta a ponta |
| DR-AUD-004 | `audit` complementa a verdade dos módulos soberanos, mas não a substitui; o detalhe de domínio continua no módulo de origem. | `AuditEntry` | `SYSTEM_SCOPE.md` | Log não vira domínio |
| DR-AUD-005 | Toda ação sensível ou mudança relevante em contratos operacionais deve produzir evidência auditável, preferencialmente append-only. | `AuditEntry` | Global invariants + authority matrix | Governança e compliance |

## Limites de inferência
- Não copiar PII/PHI desnecessariamente para o trilho de auditoria.
- Não usar `audit` como storage de estado corrente do domínio.
- Não inferir payload completo a partir de rótulos ou summaries.

## Source Graph
- Entidades: [graph/entities.yaml](graph/entities.yaml)
- Endpoints: [graph/endpoints.yaml](graph/endpoints.yaml)
- Erros: [graph/errors.yaml](graph/errors.yaml)
