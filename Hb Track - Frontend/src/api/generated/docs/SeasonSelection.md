# SeasonSelection

Seleção de temporada.  mode=\'select\': usar season_id existente mode=\'create\': criar nova temporada para o ano especificado  REGRA: Temporada sempre 01/01 → 31/12 do ano vigente. Organizações/equipes são vinculadas a temporadas.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**mode** | **string** |  | [default to undefined]
**season_id** | **string** |  | [optional] [default to undefined]
**year** | **number** |  | [optional] [default to undefined]

## Example

```typescript
import { SeasonSelection } from './api';

const instance: SeasonSelection = {
    mode,
    season_id,
    year,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
