# AuditLog

Log de auditoria de ação crítica.  Referência: R31/R32 — log obrigatório com quem/quando/o quê/contexto.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **string** | Identificador único do log | [default to undefined]
**organization_id** | **string** | UUID da organização (R34 - clube único V1) | [default to undefined]
**season_id** | **string** |  | [optional] [default to undefined]
**resource_type** | **string** | Tipo do recurso auditado (ex: match, training_session, wellness_post) | [default to undefined]
**resource_id** | **string** | UUID do recurso afetado | [default to undefined]
**action** | **string** | Ação executada (ex: game_finalize, wellness_post_update) | [default to undefined]
**actor_membership_id** | **string** | UUID do vínculo (membership) do ator | [default to undefined]
**actor_role_code** | [**ActorRoleCode**](ActorRoleCode.md) | Papel do ator no momento da ação | [default to undefined]
**occurred_at** | **string** | Momento em que a ação ocorreu | [default to undefined]
**request_id** | **string** |  | [optional] [default to undefined]
**ip_address** | **string** |  | [optional] [default to undefined]
**metadata** | **{ [key: string]: any; }** |  | [optional] [default to undefined]
**created_at** | **string** | Timestamp de criação do registro | [default to undefined]

## Example

```typescript
import { AuditLog } from './api';

const instance: AuditLog = {
    id,
    organization_id,
    season_id,
    resource_type,
    resource_id,
    action,
    actor_membership_id,
    actor_role_code,
    occurred_at,
    request_id,
    ip_address,
    metadata,
    created_at,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
