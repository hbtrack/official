# AthleteResponse

Resposta da API para GET /athletes/{id}.  V1.2: organization_id é derivado via team_registrations, não é campo direto.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **string** |  | [default to undefined]
**organization_id** | **string** |  | [optional] [default to undefined]
**person_id** | **string** |  | [default to undefined]
**athlete_name** | **string** |  | [default to undefined]
**athlete_nickname** | **string** |  | [optional] [default to undefined]
**birth_date** | **string** |  | [default to undefined]
**gender** | **string** |  | [optional] [default to undefined]
**registered_at** | **string** |  | [optional] [default to undefined]
**created_at** | **string** |  | [default to undefined]
**updated_at** | **string** |  | [default to undefined]
**shirt_number** | **number** |  | [optional] [default to undefined]
**main_defensive_position_id** | **number** |  | [optional] [default to undefined]
**secondary_defensive_position_id** | **number** |  | [optional] [default to undefined]
**main_offensive_position_id** | **number** |  | [optional] [default to undefined]
**secondary_offensive_position_id** | **number** |  | [optional] [default to undefined]
**athlete_rg** | **string** |  | [optional] [default to undefined]
**athlete_cpf** | **string** |  | [optional] [default to undefined]
**athlete_phone** | **string** |  | [optional] [default to undefined]
**athlete_email** | **string** |  | [optional] [default to undefined]
**guardian_name** | **string** |  | [optional] [default to undefined]
**guardian_phone** | **string** |  | [optional] [default to undefined]
**schooling_id** | **number** |  | [optional] [default to undefined]
**zip_code** | **string** |  | [optional] [default to undefined]
**street** | **string** |  | [optional] [default to undefined]
**neighborhood** | **string** |  | [optional] [default to undefined]
**city** | **string** |  | [optional] [default to undefined]
**address_state** | **string** |  | [optional] [default to undefined]
**address_number** | **string** |  | [optional] [default to undefined]
**address_complement** | **string** |  | [optional] [default to undefined]
**athlete_photo_path** | **string** |  | [optional] [default to undefined]
**state** | [**AthleteStateEnum**](AthleteStateEnum.md) |  | [default to undefined]
**injured** | **boolean** |  | [optional] [default to false]
**medical_restriction** | **boolean** |  | [optional] [default to false]
**suspended_until** | **string** |  | [optional] [default to undefined]
**load_restricted** | **boolean** |  | [optional] [default to false]
**deleted_at** | **string** |  | [optional] [default to undefined]
**athlete_age_at_registration** | **number** |  | [optional] [default to undefined]
**athlete_age** | **number** |  | [optional] [default to undefined]
**team_registrations** | **Array&lt;any&gt;** |  | [optional] [default to undefined]

## Example

```typescript
import { AthleteResponse } from './api';

const instance: AthleteResponse = {
    id,
    organization_id,
    person_id,
    athlete_name,
    athlete_nickname,
    birth_date,
    gender,
    registered_at,
    created_at,
    updated_at,
    shirt_number,
    main_defensive_position_id,
    secondary_defensive_position_id,
    main_offensive_position_id,
    secondary_offensive_position_id,
    athlete_rg,
    athlete_cpf,
    athlete_phone,
    athlete_email,
    guardian_name,
    guardian_phone,
    schooling_id,
    zip_code,
    street,
    neighborhood,
    city,
    address_state,
    address_number,
    address_complement,
    athlete_photo_path,
    state,
    injured,
    medical_restriction,
    suspended_until,
    load_restricted,
    deleted_at,
    athlete_age_at_registration,
    athlete_age,
    team_registrations,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
