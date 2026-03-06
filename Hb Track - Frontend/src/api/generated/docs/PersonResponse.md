# PersonResponse

Schema de resposta de Person (V1.2)  Inclui todos os dados relacionados (contatos, endereços, documentos, mídias).

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**deleted_at** | **string** |  | [optional] [default to undefined]
**deleted_reason** | **string** |  | [optional] [default to undefined]
**created_at** | **string** | Data de criação (UTC) | [default to undefined]
**updated_at** | **string** | Data da última atualização (UTC) | [default to undefined]
**id** | **string** | ID único do recurso (UUID v4) | [default to undefined]
**first_name** | **string** | Primeiro nome | [default to undefined]
**last_name** | **string** | Sobrenome | [default to undefined]
**birth_date** | **string** |  | [optional] [default to undefined]
**gender** | [**GenderEnum**](GenderEnum.md) |  | [optional] [default to undefined]
**nationality** | **string** |  | [optional] [default to undefined]
**notes** | **string** |  | [optional] [default to undefined]
**full_name** | **string** | Nome completo | [default to undefined]
**contacts** | [**Array&lt;PersonContactResponse&gt;**](PersonContactResponse.md) | Contatos | [optional] [default to undefined]
**addresses** | [**Array&lt;PersonAddressResponse&gt;**](PersonAddressResponse.md) | Endereços | [optional] [default to undefined]
**documents** | [**Array&lt;PersonDocumentResponse&gt;**](PersonDocumentResponse.md) | Documentos | [optional] [default to undefined]
**media** | [**Array&lt;PersonMediaResponse&gt;**](PersonMediaResponse.md) | Mídias | [optional] [default to undefined]
**primary_phone** | **string** |  | [optional] [default to undefined]
**primary_email** | **string** |  | [optional] [default to undefined]
**cpf** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { PersonResponse } from './api';

const instance: PersonResponse = {
    deleted_at,
    deleted_reason,
    created_at,
    updated_at,
    id,
    first_name,
    last_name,
    birth_date,
    gender,
    nationality,
    notes,
    full_name,
    contacts,
    addresses,
    documents,
    media,
    primary_phone,
    primary_email,
    cpf,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
