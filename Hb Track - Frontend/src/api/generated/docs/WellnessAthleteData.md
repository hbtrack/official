# WellnessAthleteData

Dados de um atleta no dashboard de wellness.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**athlete_id** | **string** | ID do atleta | [default to undefined]
**athlete_name** | **string** | Nome do atleta | [default to undefined]
**athlete_nickname** | **string** |  | [optional] [default to undefined]
**position** | **string** |  | [optional] [default to undefined]
**status** | **string** | Status: complete, partial, none, absent | [default to undefined]
**has_wellness_pre** | **boolean** | Preencheu wellness pré | [default to undefined]
**has_wellness_post** | **boolean** | Preencheu wellness pós | [default to undefined]
**is_absent** | **boolean** | Atleta ausente na sessão | [default to undefined]
**monthly_response_rate** | **number** | Taxa de resposta mensal (%) | [optional] [default to 0.0]
**has_monthly_badge** | **boolean** | Badge de comprometimento (≥90%) | [optional] [default to false]
**reminders_sent_count** | **number** | Lembretes enviados no mês | [optional] [default to 0]
**wellness_pre** | [**WellnessPreData**](WellnessPreData.md) |  | [optional] [default to undefined]
**wellness_post** | [**WellnessPostData**](WellnessPostData.md) |  | [optional] [default to undefined]

## Example

```typescript
import { WellnessAthleteData } from './api';

const instance: WellnessAthleteData = {
    athlete_id,
    athlete_name,
    athlete_nickname,
    position,
    status,
    has_wellness_pre,
    has_wellness_post,
    is_absent,
    monthly_response_rate,
    has_monthly_badge,
    reminders_sent_count,
    wellness_pre,
    wellness_post,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
