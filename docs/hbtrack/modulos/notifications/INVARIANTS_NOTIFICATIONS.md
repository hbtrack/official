---
module: "notifications"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: false
contract_path_ref: "../../../../contracts/openapi/paths/notifications.yaml"
schemas_ref: "../../../../contracts/schemas/notifications/"
type: "invariants"
updated: "2026-03-16"
---

# INVARIANTS_NOTIFICATIONS.md

## Objetivo
Registrar invariantes do módulo `notifications`.

## Definição
Invariantes são condições que devem permanecer verdadeiras independentemente do fluxo, endpoint ou interface.

## Invariantes globais vinculantes
- `.contract_driven/DOMAIN_AXIOMS.json`
- `docs/_canon/GLOBAL_INVARIANTS.md`

## Tabela de invariantes
| ID | Invariante | Entidades | Fonte | Como verificar |
|---|---|---|---|---|
| INV-NTF-001 | `id`, `recipientUserId`, `channelLabel` e `requestedAt` são obrigatórios. | `NotificationDelivery` | `notification_delivery.schema.json` | JSON Schema validation |
| INV-NTF-002 | `retryCount` permanece no intervalo `[0..10]`. | `NotificationDelivery` | Schema local | Range validation |
| INV-NTF-003 | Se `deliveredAt` estiver presente, então `deliveredAt >= requestedAt`. | `NotificationDelivery` | Regra temporal do módulo | Teste de contrato |
| INV-NTF-004 | Pelo menos uma referência contratual de origem deve existir: `notificationTemplateRef` ou `eventEnvelopeRef`. | `NotificationDelivery` | Regra de rastreabilidade do módulo | Teste de contrato |
| INV-NTF-005 | `notifications` não pode carregar política de acesso nem estado de negócio do módulo originador como fonte soberana. | `NotificationDelivery` | Authority matrix `must_not_infer` | Revisão de boundary |

## Relação com outros documentos
- `docs/hbtrack/modulos/notifications/DOMAIN_RULES_NOTIFICATIONS.md`
- `contracts/schemas/notifications/notification_delivery.schema.json`
