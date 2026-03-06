# AppSchemasIntakeFichaUnicaPersonCreate

Dados da pessoa (persons).  Campos obrigatórios: first_name, last_name Campos derivados: full_name (gerado automaticamente)  REGRAS (FICHA.MD): - Ao menos um contato é obrigatório - Ao menos um e-mail é obrigatório nos contatos

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**first_name** | **string** |  | [default to undefined]
**last_name** | **string** |  | [default to undefined]
**birth_date** | **string** |  | [optional] [default to undefined]
**gender** | **string** |  | [optional] [default to undefined]
**nationality** | **string** |  | [optional] [default to 'brasileira']
**notes** | **string** |  | [optional] [default to undefined]
**contacts** | [**Array&lt;AppSchemasIntakeFichaUnicaPersonContactCreate&gt;**](AppSchemasIntakeFichaUnicaPersonContactCreate.md) |  | [optional] [default to undefined]
**documents** | [**Array&lt;AppSchemasIntakeFichaUnicaPersonDocumentCreate&gt;**](AppSchemasIntakeFichaUnicaPersonDocumentCreate.md) |  | [optional] [default to undefined]
**address** | [**AppSchemasIntakeFichaUnicaPersonAddressCreate**](AppSchemasIntakeFichaUnicaPersonAddressCreate.md) |  | [optional] [default to undefined]
**media** | [**AppSchemasIntakeFichaUnicaPersonMediaCreate**](AppSchemasIntakeFichaUnicaPersonMediaCreate.md) |  | [optional] [default to undefined]

## Example

```typescript
import { AppSchemasIntakeFichaUnicaPersonCreate } from './api';

const instance: AppSchemasIntakeFichaUnicaPersonCreate = {
    first_name,
    last_name,
    birth_date,
    gender,
    nationality,
    notes,
    contacts,
    documents,
    address,
    media,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
