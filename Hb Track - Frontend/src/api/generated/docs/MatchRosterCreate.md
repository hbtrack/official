# MatchRosterCreate

Schema para adicionar atleta ao roster (POST).  Campos obrigatórios (banco): - athlete_id: UUID da atleta - jersey_number: smallint > 0 - is_goalkeeper: boolean - is_available: boolean  Campos opcionais: - is_starting: boolean (nullable) - notes: text  Constraints: - UNIQUE (match_id, athlete_id) - RD18: Máximo 16 atletas por jogo  Regras: - RD4/RD7: Participação exige inscrição na temporada - RDB13: Bloquear se jogo finalizado

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**athlete_id** | **string** | ID da atleta (obrigatório) | [default to undefined]
**jersey_number** | **number** | Número da camisa (obrigatório, &gt;0) | [default to undefined]
**is_goalkeeper** | **boolean** | Indica se é goleira (obrigatório) | [default to undefined]
**is_available** | **boolean** | Indica se está disponível para jogar (obrigatório, default true) | [optional] [default to true]
**is_starting** | **boolean** |  | [optional] [default to undefined]
**notes** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { MatchRosterCreate } from './api';

const instance: MatchRosterCreate = {
    athlete_id,
    jersey_number,
    is_goalkeeper,
    is_available,
    is_starting,
    notes,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
