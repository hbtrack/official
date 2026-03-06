# MatchEventList

Schema para listagem de eventos com paginação.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**items** | [**Array&lt;MatchEventSummary&gt;**](MatchEventSummary.md) |  | [default to undefined]
**total** | **number** |  | [default to undefined]
**page** | **number** |  | [default to undefined]
**size** | **number** |  | [default to undefined]
**pages** | **number** |  | [default to undefined]

## Example

```typescript
import { MatchEventList } from './api';

const instance: MatchEventList = {
    items,
    total,
    page,
    size,
    pages,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
