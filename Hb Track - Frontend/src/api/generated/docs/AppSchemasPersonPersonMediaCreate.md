# AppSchemasPersonPersonMediaCreate

Schema para criação de PersonMedia

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**media_type** | [**MediaTypeEnum**](MediaTypeEnum.md) | Tipo de mídia | [default to undefined]
**file_url** | **string** | URL do arquivo | [default to undefined]
**file_name** | **string** |  | [optional] [default to undefined]
**file_size** | **number** |  | [optional] [default to undefined]
**mime_type** | **string** |  | [optional] [default to undefined]
**is_primary** | **boolean** | Se é a mídia primária deste tipo | [optional] [default to false]
**description** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { AppSchemasPersonPersonMediaCreate } from './api';

const instance: AppSchemasPersonPersonMediaCreate = {
    media_type,
    file_url,
    file_name,
    file_size,
    mime_type,
    is_primary,
    description,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
