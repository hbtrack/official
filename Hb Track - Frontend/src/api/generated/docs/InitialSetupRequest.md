# InitialSetupRequest

Requisição de setup inicial para dirigente

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**organization_name** | **string** | Nome da organização | [default to undefined]
**organization_code** | **string** |  | [optional] [default to undefined]
**season_year** | **number** | Ano da temporada inicial | [default to undefined]
**season_name** | **string** |  | [optional] [default to undefined]
**season_starts_at** | **string** | Data de início da temporada | [default to undefined]
**season_ends_at** | **string** | Data de término da temporada | [default to undefined]

## Example

```typescript
import { InitialSetupRequest } from './api';

const instance: InitialSetupRequest = {
    organization_name,
    organization_code,
    season_year,
    season_name,
    season_starts_at,
    season_ends_at,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
