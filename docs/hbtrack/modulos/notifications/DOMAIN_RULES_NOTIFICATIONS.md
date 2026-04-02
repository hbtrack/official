---
module: "notifications"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: false
contract_path_ref: "../../../../contracts/openapi/paths/notifications.yaml"
schemas_ref: "../../../../contracts/schemas/notifications/"
type: "domain-rules"
updated: "2026-03-16"
---

# DOMAIN_RULES_NOTIFICATIONS.md

## Objetivo
Registrar as regras de negócio do módulo `notifications`.

## Fonte do domínio
- `docs/_canon/MODULE_SOURCE_AUTHORITY_MATRIX.yaml`
- `contracts/schemas/notifications/notification_delivery.schema.json`
- `docs/hbtrack/modulos/notifications/INVARIANTS_NOTIFICATIONS.md`
- Artefatos assíncronos do módulo (`AsyncAPI`, `Arazzo`) quando aplicável
- `docs/hbtrack/modulos/notifications/graph/entities.yaml`
- `docs/hbtrack/modulos/notifications/graph/endpoints.yaml`
- `docs/hbtrack/modulos/notifications/graph/errors.yaml`

## Regras de negócio
| ID | Regra | Entidade afetada | Fonte | Observações |
|---|---|---|---|---|
| DR-NTF-001 | `notifications` é soberano do envelope de entrega: canal, destinatário, preferências, template referenciado, estado de entrega e retries. | `NotificationDelivery` | Authority matrix `notifications` | Módulo de entrega, não de negócio-fonte |
| DR-NTF-002 | Módulos de negócio emitem intenção/evento; `notifications` decide canal e lifecycle de entrega sem absorver o estado de negócio do módulo originador. | `NotificationDelivery` | Authority matrix `must_not_infer` | Boundary com módulos emissores |
| DR-NTF-003 | `notificationTemplateRef` e `eventEnvelopeRef` são referências contratuais da mensagem e substituem conteúdo ad hoc não documentado. | `NotificationDelivery` | Authority matrix `templates_referenced`, `event_envelope` | Conteúdo rastreável |
| DR-NTF-004 | `preferenceLabel` influencia seleção de canal/entrega, mas não substitui policy de acesso definida em `identity_access`. | `NotificationDelivery` | Authority matrix `must_not_infer` | Preferência ≠ autorização |
| DR-NTF-005 | Detalhes do provedor externo permanecem encapsulados por adapter interno; `notifications` expõe apenas contrato estável de entrega. | `NotificationDelivery` | `SYSTEM_SCOPE.md` | Isolamento de integração |

## Limites de inferência
- Não inventar conteúdo de negócio fora de `template`/`event envelope` contratados.
- Não mover política de acesso ou estado de domínio para `notifications`.
- Não expor semântica específica do provedor externo como parte do contrato público.

## Âncoras estruturadas
- A entidade soberana de entrega e seus campos mapeados para runtime estão em `docs/hbtrack/modulos/notifications/graph/entities.yaml`.
- O mapa mínimo de operações HTTP do módulo está em `docs/hbtrack/modulos/notifications/graph/endpoints.yaml`.
- O mapa mínimo de erros transport/domain do módulo está em `docs/hbtrack/modulos/notifications/graph/errors.yaml`.
