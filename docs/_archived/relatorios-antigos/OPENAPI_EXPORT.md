<!-- STATUS: DEPRECATED | arquivado -->

# Export do OpenAPI (FastAPI) para o RAG Canônico

Objetivo: manter `openapi.json` atualizado como fonte única de contratos (rotas, schemas, exemplos, headers) para Treinos, Statistics, Reports e domínios adjacentes.

## Passo a passo
1) Subir o backend local (ou usar modo `--app` do uvicorn):
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```
2) Gerar o arquivo:
   ```bash
   curl http://localhost:8000/openapi.json -o RAG/openapi.json
   ```
   - Se tiver prefixo `/api/v1`, usar a URL completa (ex.: `http://localhost:8000/api/v1/openapi.json`).
3) Validar conteúdo:
   - Conferir se todas as rotas (Treinos/Statistics/Reports/Auth/Media/Matches/Wellness/Alerts) aparecem.
   - Conferir enums de status/roles.
   - Conferir exemplos 200/400/409/422 e headers `X-Cache-TTL`/`X-Generated-At` nos snapshots.
4) Versionar:
   - Registrar data/hora da geração e commit/hash do backend.
   - Substituir `RAG/openapi.json` existente (se houver).

## Boas práticas
- CI deve falhar se o OpenAPI estiver desatualizado em relação ao código.
- Manter exemplos realistas (UUIDs, datas ISO, percents) e contratos de erro padronizados (`error_code`, `message`, `details`, `timestamp`, `request_id`).
- Não publicar secrets ou URLs privadas no `openapi.json`.
