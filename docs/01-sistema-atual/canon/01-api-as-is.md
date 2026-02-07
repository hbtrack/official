<!-- STATUS: VERIFIED | evidencia: _generated/openapi.json -->

# API As-Is

## Fonte Canonica

- **Arquivo:** `docs/_generated/openapi.json`
- **Regenerar:** `python scripts/generate_docs.py --openapi` (de `C:\HB TRACK\Hb Track - Backend`)

## Convencoes Verificadas no OpenAPI

| Item | Valor | Evidencia |
|------|-------|-----------|
| Versao OpenAPI | 3.1.0 | verificado em openapi.json (campo `openapi`) |
| Titulo | "HB Tracking API" | verificado em openapi.json (campo `info.title`) |
| Base Path | `/api/v1/` | verificado em openapi.json (campo `paths.*`) |
| Autenticacao | Bearer Token | verificado em openapi.json (campo `components.securitySchemes.HTTPBearer`) |
| Formato IDs | UUID | verificado em openapi.json (parametros com `format: uuid`) |

## Convencoes NAO VERIFICADAS

Os itens abaixo nao foram encontrados explicitamente no OpenAPI gerado:

- Formato de erros padrao: NAO VERIFICADO
- Rate limiting headers: NAO VERIFICADO
- Versionamento de resposta: NAO VERIFICADO
- Paginacao padrao: NAO VERIFICADO (varia por endpoint)
