<!-- STATUS: DEPRECATED | arquivado -->

## Cache, headers e limits

- Cache headers (snapshots):
  - /dashboard/summary: X-Cache-TTL ~120s; X-Generated-At timestamp de geração.
  - /reports/operational-session, /reports/athlete-self: incluir X-Generated-At; cache control definido no backend (seguir OpenAPI).
  - /statistics* snapshots: seguir headers definidos; respeitar X-Generated-At.

- Rate limit:
  - Limites configurados via slowapi (ver app/core/rate_limit.py); handler padrão RateLimitExceeded.

- Timeout/erro:
  - Respostas de erro seguem padrão {error_code, message, details, timestamp, request_id}.

- Paginacao/ordenacao:
  - skip/limit (default 100); order_by whitelist em reports/alerts/matches.

- Observações:
  - Healthz sem auth.
  - Não logar secrets; logs estruturados com request_id.

Frontend:
  - Honrar headers de cache nos fetches; expor X-Generated-At para UX (data age).
