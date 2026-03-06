# AuthContextResponse

Contexto completo para o frontend (papel + vínculos + permissões).  VERSÃO: 1.0  ⚠️ CONTRATO CONGELADO: - NÃO renomear campos sem versionar (v1 → v2) - NÃO mudar tipos sem versionar - Adicionar campos novos = OK (default values) - Remover campos = CRIAR NOVA VERSÃO  CONTRATO FIXO - Sempre retorna todos os campos (null se não aplicável). O frontend deve considerar este o contrato padrão após login.  ARQUITETURA CANÔNICA: - permissions: Mapa canônico (app/core/permissions_map.py) resolvido - system_state: Estado do sistema (temporada, onboarding) separado - ExecutionContext é a fonte da verdade - Este schema é apenas um espelho

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**user_id** | **string** |  | [default to undefined]
**person_id** | **string** |  | [optional] [default to undefined]
**role_code** | **string** |  | [default to undefined]
**is_superadmin** | **boolean** |  | [optional] [default to false]
**organization_id** | **string** |  | [optional] [default to undefined]
**organization_name** | **string** |  | [optional] [default to undefined]
**membership_id** | **string** |  | [optional] [default to undefined]
**current_season_id** | **string** |  | [optional] [default to undefined]
**current_season_name** | **string** |  | [optional] [default to undefined]
**team_registrations** | [**Array&lt;TeamRegistrationContext&gt;**](TeamRegistrationContext.md) |  | [optional] [default to undefined]
**permissions** | **{ [key: string]: boolean; }** | Mapa canônico de permissões resolvido | [optional] [default to undefined]
**system_state** | **{ [key: string]: any; }** | Estado do sistema (temporada, onboarding) separado de permissões | [optional] [default to undefined]

## Example

```typescript
import { AuthContextResponse } from './api';

const instance: AuthContextResponse = {
    user_id,
    person_id,
    role_code,
    is_superadmin,
    organization_id,
    organization_name,
    membership_id,
    current_season_id,
    current_season_name,
    team_registrations,
    permissions,
    system_state,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
