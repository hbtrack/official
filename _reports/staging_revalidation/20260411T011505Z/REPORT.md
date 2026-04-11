---
data_execucao_utc: "2026-04-11T01:15:05Z"
branch: chore/saneamento-completo-23-23
fase_avaliada: 4
host: staging.handballtrack.app
remote_ip: 191.252.185.34
resultado: PARTIAL_PASS
---

# Revalidação Fase 4 — Staging (2026-04-11)

> **NON-SOVEREIGN.** Este relatório é evidência de execução, não política. SSOT de fases permanece em `ROADMAP.md`.

## Escopo

Revalidar a Fase 4 (Ciclo 1 integrado em staging) com evidência **fresca** de runtime:
`/health`, smoke HTTP dos módulos do Ciclo 1, diff estrutural com OpenAPI SSOT e
execução dos replay packs locais.

Evidência bruta capturada em `_reports/staging_revalidation/20260411T011505Z/`.

## Veredito

**PARTIAL_PASS.**
- Runtime de staging está **de pé, saudável e servindo o stack completo** (nginx/1.27.5 + NinjaAPI + DB + Redis).
- Todos os 5 módulos do Ciclo 1 (`identity_access`, `users`, `teams`, `seasons`, `training`) estão **deployados e com JWT exigido**.
- O fluxo end-to-end autenticado **não pôde ser executado** porque o seed administrativo (`admin@hbtrack.demo`) **não existe em staging** — `POST /api/auth/login` devolve 401 para as credenciais canônicas de replay.
- Há uma **divergência de path** entre o OpenAPI servido em staging e o SSOT local: staging monta `training-sessions` sob `/api/training/training-sessions/*` enquanto o SSOT (`contracts/openapi/openapi.yaml`) usa `/api/training-sessions/*`. É uma divergência real de contrato, não um bug de normalização.

O saneamento local deixa de ser o bloqueador; **os bloqueadores restantes para declarar a Fase 4 DONE** são:
1. Provisionar (ou documentar o runbook de) seed administrativo em staging.
2. Executar os replay packs em modo live e registrar PASS.
3. Decidir se a divergência de prefixo `training-sessions` se resolve atualizando o SSOT ou a aplicação — depende de qual lado é correto.

## Evidência — runtime operacional

### 1. `/health`
```
GET https://staging.handballtrack.app/health
HTTP/2 200
content-type: application/json
server: nginx/1.27.5
x-flow-id: aac7d6c7-4513-4ff0-a05c-37fe9e4e3c94
strict-transport-security: max-age=31536000; includeSubDomains
x-content-type-options: nosniff
x-frame-options: DENY
referrer-policy: no-referrer-when-downgrade

{"status": "ok", "db": "ok", "redis": "ok"}
```
- TLS válido, HTTP/2 ativo, DB + Redis respondendo, flow_id propagado.
- IP remoto resolvido: `191.252.185.34`.
- Arquivos: `health.headers`, `health.body.json`, `health.meta.txt`.

### 2. OpenAPI publicada
- `GET /api/openapi.json` → HTTP 200, 217 202 bytes.
- `openapi=3.1.0`, `info.title="HB Track API"`, `info.version="1.0.0"`.
- **82 paths, 127 operações, 13 tags:**
  `ai_ingestion, audit, competitions, identity_access, matches, medical, notifications, seasons, teams, training, users, video, wellness`.
- Cobertura Ciclo 1: `auth=8`, `users=5`, `teams=6`, `seasons=3`, `training=18`.
- Arquivos: `openapi.json`, `openapi.headers`, `openapi.summary.json`.

### 3. Smoke HTTP dos módulos do Ciclo 1 (sem token)
| Endpoint | HTTP | Body |
|---|---|---|
| `POST /api/auth/login` (credenciais inválidas) | 401 | RFC 7807 — `"Credenciais inválidas."` |
| `GET /api/users` | 401 | RFC 7807 — `"Unauthenticated"` |
| `GET /api/teams` | 401 | RFC 7807 — `"Unauthenticated"` |
| `GET /api/seasons` | 401 | RFC 7807 — `"Unauthenticated"` |
| `GET /api/training/training-sessions` | 401 | RFC 7807 — `"Unauthenticated"` |
| `GET /api/does-not-exist` | 404 | NinjaAPI Not Found |

Interpretação: JWT middleware **efetivo** nos 5 módulos, erros em formato RFC 7807 conforme `docs/_canon/OPERATIONS.md`, rota desconhecida não vaza stacktrace.

### 4. Replay packs locais (modo estrutural)
```
python3 -m pytest tests/replay/staging/ -q
50 passed, 6 skipped, 1 warning in 0.29s
```
- Os 6 skipped correspondem aos testes em `class TestLive:` — pulam quando `HB_STAGING_URL` não está setada.
- Arquivo: `replay_structural.txt`.

### 5. Tentativa de replay live
- `POST /api/auth/login` com `admin@hbtrack.demo / HBTrack@demo2026` (credenciais canônicas em `scripts/replay/common.py`) → HTTP 401 `"Credenciais inválidas."`.
- Conclusão: o seed não está aplicado em staging. `run_live()` de qualquer replay pack falharia no passo 1.
- Arquivos: `login_seed.meta.txt`, `login_seed.body.json`.

## Divergências de contrato detectadas

Comparação normalizada entre `contracts/openapi/openapi.yaml` (SSOT) e `/api/openapi.json` servido em staging:

| Categoria | Situação |
|---|---|
| `users`, `teams`, `seasons`, `auth` | Paths idênticos entre SSOT e staging após normalização de prefixo `/api/` e snake_case de parâmetros. |
| `training-sessions` | **Divergência real.** SSOT: `/api/training-sessions/...`. Staging: `/api/training/training-sessions/...`. Afeta ~27 paths. |
| `exercises/{id}` vs `exercises/{exercise_id}` | Nome do parâmetro difere entre SSOT e staging. Requer alinhamento. |

Essa divergência **não bloqueia o /health nem a smoke**, mas deve ser resolvida antes da Fase 4 ser declarada DONE, porque Schemathesis contra staging falharia por paths ausentes.

## Próxima ação

1. Provisionar seed admin em staging (`admin@hbtrack.demo`) ou documentar o processo em `VPS/runbooks/`.
2. Executar `HB_STAGING_URL=https://staging.handballtrack.app python3 -m pytest tests/replay/staging/` e arquivar saída.
3. Decidir direção da reconciliação do prefixo `training-sessions` (ajustar SSOT ou router da aplicação) e regenerar artefatos.
4. Só então marcar Fase 4 como DONE no `ROADMAP.md`.

## Checksum das evidências

| Arquivo | Tamanho aproximado | Origem |
|---|---|---|
| `health.headers` | headers HTTP/2 completos | `curl -sS -D` |
| `health.body.json` | 43 B | `GET /health` |
| `openapi.json` | 217 202 B | `GET /api/openapi.json` |
| `openapi.summary.json` | resumo calculado | pós-processamento |
| `login_invalid.*`, `login_seed.*` | respostas 401 | `POST /api/auth/login` |
| `unauth_*.body.json` | respostas 401 | `GET /api/{modulo}` |
| `notfound.*` | resposta 404 | `GET /api/does-not-exist` |
| `replay_structural.txt` | saída pytest | replay packs modo estrutural |
