# PersonMediaResponse

Schema de resposta de PersonMedia

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**deleted_at** | **string** |  | [optional] [default to undefined]
**deleted_reason** | **string** |  | [optional] [default to undefined]
**created_at** | **string** | Data de criação (UTC) | [default to undefined]
**updated_at** | **string** | Data da última atualização (UTC) | [default to undefined]
**id** | **string** | ID único do recurso (UUID v4) | [default to undefined]
**media_type** | [**MediaTypeEnum**](MediaTypeEnum.md) | Tipo de mídia | [default to undefined]
**file_url** | **string** | URL do arquivo | [default to undefined]
**file_name** | **string** |  | [optional] [default to undefined]
**file_size** | **number** |  | [optional] [default to undefined]
**mime_type** | **string** |  | [optional] [default to undefined]
**is_primary** | **boolean** | Se é a mídia primária deste tipo | [optional] [default to false]
**description** | **string** |  | [optional] [default to undefined]
**person_id** | **string** |  | [default to undefined]

## Example

```typescript
import { PersonMediaResponse } from './api';

const instance: PersonMediaResponse = {
    deleted_at,
    deleted_reason,
    created_at,
    updated_at,
    id,
    media_type,
    file_url,
    file_name,
    file_size,
    mime_type,
    is_primary,
    description,
    person_id,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
