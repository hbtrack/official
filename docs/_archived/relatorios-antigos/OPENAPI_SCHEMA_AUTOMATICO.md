<!-- STATUS: DEPRECATED | arquivado -->

# ✅ Schema OpenAPI Automático

## Status: IMPLEMENTADO

### O que já está funcionando ✅

1. **Schema Pydantic definido:** [AuthContextResponse](../Hb%20Track%20-%20Backend/app/api/v1/routers/auth.py#L171-L202)
2. **Endpoint com response_model:** [GET /auth/context](../Hb%20Track%20-%20Backend/app/api/v1/routers/auth.py#L503-L510)
3. **OpenAPI gerado automaticamente:** http://localhost:8000/docs

---

## Como Funciona

```
┌──────────────────────────────────────────────────────┐
│  Pydantic Model (AuthContextResponse)                │
│  ↓                                                   │
│  FastAPI (@router.get + response_model)              │
│  ↓                                                   │
│  OpenAPI Schema (automático)                         │
│  ↓                                                   │
│  /docs (Swagger UI) + /openapi.json                  │
└──────────────────────────────────────────────────────┘
```

**Zero trabalho manual:**
- ❌ Não escrever YAML
- ❌ Não manter schema duplicado
- ❌ Não documentar fora do código

---

## Endpoints Disponíveis

### 📄 Swagger UI (Interativo)
```
http://localhost:8000/docs
```
- Interface interativa
- Testar endpoints diretamente
- Ver schema completo
- Fazer requests autenticados

### 📄 ReDoc (Documentação)
```
http://localhost:8000/redoc
```
- Documentação limpa e navegável
- Boa para leitura
- Exportável como PDF

### 📄 OpenAPI JSON (Raw)
```
http://localhost:8000/openapi.json
```
- Schema JSON completo
- Usar para gerar clients
- CI/CD validation

---

## Exemplo: AuthContextResponse no OpenAPI

### Schema Gerado Automaticamente

```json
{
  "AuthContextResponse": {
    "type": "object",
    "required": ["user_id", "role_code", "is_superadmin"],
    "properties": {
      "user_id": {
        "type": "string",
        "title": "User Id"
      },
      "person_id": {
        "type": "string",
        "nullable": true,
        "title": "Person Id"
      },
      "role_code": {
        "type": "string",
        "title": "Role Code"
      },
      "is_superadmin": {
        "type": "boolean",
        "default": false,
        "title": "Is Superadmin"
      },
      "organization_id": {
        "type": "string",
        "nullable": true,
        "title": "Organization Id"
      },
      "organization_name": {
        "type": "string",
        "nullable": true,
        "title": "Organization Name"
      },
      "permissions": {
        "type": "object",
        "additionalProperties": {"type": "boolean"},
        "default": {},
        "description": "Mapa canônico de permissões resolvido",
        "title": "Permissions"
      },
      "system_state": {
        "type": "object",
        "additionalProperties": true,
        "default": {},
        "description": "Estado do sistema (temporada, onboarding) separado de permissões",
        "title": "System State"
      },
      "team_registrations": {
        "type": "array",
        "items": {"$ref": "#/components/schemas/TeamRegistrationContext"},
        "default": [],
        "title": "Team Registrations"
      }
    }
  }
}
```

---

## Gerar TypeScript Types Automaticamente

### Opção 1: openapi-typescript
```bash
npm install -D openapi-typescript

npx openapi-typescript http://localhost:8000/openapi.json \
  -o src/types/api-generated.ts
```

**Resultado:**
```typescript
// src/types/api-generated.ts (GERADO AUTOMATICAMENTE)
export interface components {
  schemas: {
    AuthContextResponse: {
      user_id: string
      person_id: string | null
      role_code: string
      is_superadmin: boolean
      organization_id: string | null
      organization_name: string | null
      permissions: Record<string, boolean>
      system_state: Record<string, any>
      team_registrations: TeamRegistrationContext[]
      // ...
    }
  }
}
```

### Opção 2: openapi-generator
```bash
npm install -g @openapitools/openapi-generator-cli

openapi-generator-cli generate \
  -i http://localhost:8000/openapi.json \
  -g typescript-fetch \
  -o src/api-client
```

---

## Validação de Contrato em CI/CD

### Checar se schema mudou (breaking changes)
```bash
# Salvar snapshot do schema
curl http://localhost:8000/openapi.json > openapi-snapshot.json

# Em CI: Comparar com snapshot anterior
npx @openapitools/openapi-diff \
  openapi-snapshot-previous.json \
  openapi-snapshot.json \
  --fail-on-incompatible
```

---

## Versionamento

### Quando criar v2?

**CRIAR NOVA VERSÃO SE:**
- ❌ Renomear campo (ex: `user_id` → `userId`)
- ❌ Mudar tipo (ex: `string` → `number`)
- ❌ Remover campo obrigatório
- ❌ Mudar formato (ex: `ISO8601` → `timestamp`)

**OK SEM VERSIONAR:**
- ✅ Adicionar campo novo com default
- ✅ Tornar campo nullable
- ✅ Adicionar enum value
- ✅ Mudar descrição/documentação

### Como versionar:

```python
# app/api/v1/routers/auth.py (V1 - atual)
@router.get("/context", response_model=AuthContextResponse)
async def get_context(...):
    ...

# app/api/v2/routers/auth.py (V2 - nova versão)
@router.get("/context", response_model=AuthContextResponseV2)
async def get_context_v2(...):
    ...
```

**URLs:**
- V1: `http://localhost:8000/api/v1/auth/context`
- V2: `http://localhost:8000/api/v2/auth/context`

---

## Checklist

- [x] **Schema Pydantic:** AuthContextResponse definido
- [x] **response_model:** Endpoint usa response_model=AuthContextResponse
- [x] **OpenAPI gerado:** /docs e /openapi.json funcionando
- [x] **Versionamento:** VERSÃO 1.0 documentada
- [x] **Contrato congelado:** Avisos de breaking changes
- [ ] **Gerar types:** Configurar openapi-typescript no CI
- [ ] **Snapshot testing:** Validar schema em CI/CD

---

## Próximos Passos (Opcional)

1. **Automatizar geração de types:**
   ```json
   // package.json
   {
     "scripts": {
       "generate-types": "openapi-typescript http://localhost:8000/openapi.json -o src/types/api.ts"
     }
   }
   ```

2. **Pre-commit hook:**
   ```bash
   # .husky/pre-commit
   npm run generate-types
   git add src/types/api.ts
   ```

3. **CI validation:**
   ```yaml
   # .github/workflows/api-contract.yml
   - name: Validate API Contract
     run: |
       curl http://localhost:8000/openapi.json > openapi.json
       npx @openapitools/openapi-diff \
         openapi-snapshot.json openapi.json \
         --fail-on-incompatible
   ```

---

**Status:** ✅ **SCHEMA OPENAPI FUNCIONANDO**  
**Documentação:** http://localhost:8000/docs  
**Schema JSON:** http://localhost:8000/openapi.json  
**Próximo passo:** Gerar types TypeScript automaticamente (opcional)
