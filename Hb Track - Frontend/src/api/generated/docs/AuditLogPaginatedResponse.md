# AuditLogPaginatedResponse

Resposta paginada de logs de auditoria.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**items** | [**Array&lt;AuditLog&gt;**](AuditLog.md) | Lista de logs de auditoria | [default to undefined]
**page** | **number** | Página atual | [default to undefined]
**limit** | **number** | Itens por página | [default to undefined]
**total** | **number** | Total de registros | [default to undefined]

## Example

```typescript
import { AuditLogPaginatedResponse } from './api';

const instance: AuditLogPaginatedResponse = {
    items,
    page,
    limit,
    total,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
