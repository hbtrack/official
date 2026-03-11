# SPEC — CONNECTIVITY_DIAGNOSTIC_CONTRACT

---
## 1. Identidade

**Nome canônico:** `CONNECTIVITY_DIAGNOSTIC_CONTRACT`
**Versão:** `v1.0.0`
**Escopo:** diagnóstico determinístico de conectividade entre frontend local e backend remoto na VPS
**Objetivo:** identificar e classificar a causa raiz de falhas de conexão com evidência reproduzível
**Linguagem de implementação:** Python apenas
**Política operacional:** scripts `.py` apenas; sem `.sh` e sem `.ps1`

---
## 2. Problema que o contrato resolve

Hoje, quando o frontend local falha ao acessar a API remota, a investigação tende a ser manual, não determinística e dispersa entre navegador, VPS, proxy, backend e banco.

Este contrato define um mecanismo padronizado para:

* validar a configuração da URL da API usada pelo frontend
* testar resolução DNS
* testar alcance de porta TCP
* testar handshake HTTP/HTTPS
* validar compatibilidade de protocolo
* validar CORS para origem local
* validar saúde do backend
* validar saúde das dependências expostas pelo backend
* classificar a falha em categorias estáveis
* gerar relatório estruturado com causa raiz provável

---

## 3. Artefatos canônicos

### 3.1 Script local

`tools/diagnostics/diagnose_connectivity.py`

Responsável por executar os checks de ponta a ponta.

### 3.2 Configuração

`config.py`

Fonte única de verdade para:

* URL base da API
* origem local esperada do frontend
* timeout padrão
* endpoint de health
* endpoint de ready
* política de TLS
* códigos de saída

### 3.3 Endpoint backend — liveness/health

`GET /health`

Responsável por declarar:

* se a API está viva
* status das dependências essenciais
* modo detalhado e estável para automação

### 3.4 Endpoint backend — readiness

`GET /ready`

Responsável por declarar:

* se o backend está apto a servir tráfego real
* falha se dependências críticas não estiverem operacionais

### 3.5 Relatório

`_reports/connectivity_diagnostic_report.json`

Opcionalmente também:
`_reports/connectivity_diagnostic_report.md`

---

## 4. Resultado esperado

Ao final da execução, o sistema deve retornar:

1. **exit code determinístico**
2. **root_cause_code**
3. **root_cause_summary**
4. **evidências por etapa**
5. **recomendação objetiva de correção**

Exemplo de saída conceitual:

```json
{
  "status": "fail",
  "root_cause_code": "CORS_BLOCKING_LOCALHOST",
  "root_cause_summary": "API responde, mas não autoriza a origem http://localhost:3000",
  "checks": [
    {"name": "frontend_api_url", "status": "pass"},
    {"name": "dns_resolution", "status": "pass"},
    {"name": "tcp_connectivity", "status": "pass"},
    {"name": "http_health", "status": "pass"},
    {"name": "cors_preflight", "status": "fail"}
  ],
  "recommended_action": "Adicionar origem local à whitelist CORS do backend"
}
```

---

## 5. Entradas obrigatórias

O script deve aceitar, via `config.py` e/ou CLI, as seguintes entradas:

* `api_base_url`
* `frontend_origin`
* `health_path`
* `ready_path`
* `timeout_seconds`
* `verify_tls`
* `expected_local_env_file` opcional
* `frontend_env_var_names` lista ordenada de variáveis candidatas

Exemplo conceitual:

```python
API_BASE_URL = "https://api.hbtrack.com"
FRONTEND_ORIGIN = "http://localhost:3000"
HEALTH_PATH = "/health"
READY_PATH = "/ready"
TIMEOUT_SECONDS = 8
VERIFY_TLS = True
FRONTEND_ENV_VAR_NAMES = [
    "NEXT_PUBLIC_API_URL",
    "VITE_API_URL",
    "REACT_APP_API_URL"
]
```

---

## 6. Pré-condições

Para o contrato produzir causa raiz completa, devem ser verdadeiras as seguintes premissas:

1. O backend remoto deve estar publicamente acessível por domínio/IP ou proxy reverso válido.
2. O backend deve expor `/health`.
3. O backend deve expor `/ready`.
4. O `/health` deve incluir checks internos estruturados.
5. O frontend deve ter uma variável canônica de URL da API.
6. O script deve conseguir descobrir ou receber explicitamente a origem local do frontend.

Se 2, 3 ou 4 não forem verdade, o diagnóstico ainda roda, mas fica limitado à camada de borda HTTP/TCP.

---

## 7. Ordem obrigatória de execução dos checks

A ordem é parte do contrato. O script não deve “pular para o fim”.

### Check 1 — Configuração local do frontend

Objetivo: descobrir qual URL da API o frontend realmente está usando.

Validações:

* variável existe
* URL é sintaticamente válida
* não está vazia
* não aponta para `localhost` indevidamente quando o backend é remoto
* protocolo é permitido (`http` ou `https`)

Falhas classificáveis:

* `FRONTEND_API_URL_MISSING`
* `FRONTEND_API_URL_INVALID`
* `FRONTEND_API_URL_LOCALHOST_MISUSE`

---

### Check 2 — Parse estrutural da URL

Objetivo: decompor host, porta, esquema e path base.

Validações:

* host presente
* porta resolvida implicitamente ou explicitamente
* esquema coerente

Falhas:

* `API_URL_PARSE_ERROR`

---

### Check 3 — Resolução DNS

Objetivo: verificar se o host da API resolve.

Validações:

* resolução A/AAAA ou equivalente
* latência básica de resolução

Falhas:

* `API_HOST_UNRESOLVED`

---

### Check 4 — Conectividade TCP

Objetivo: verificar se a porta da API está aberta.

Validações:

* conexão socket com timeout
* host/porta alcançáveis

Falhas:

* `API_PORT_CLOSED`
* `API_TCP_TIMEOUT`

---

### Check 5 — Handshake TLS

Executado apenas se `https`.

Objetivo: validar certificado e handshake.

Validações:

* certificado válido
* hostname compatível
* cadeia válida
* handshake completo

Falhas:

* `TLS_CERT_INVALID`
* `TLS_HOSTNAME_MISMATCH`
* `TLS_HANDSHAKE_FAILED`

---

### Check 6 — HTTP reachability

Objetivo: verificar se a API responde em nível HTTP.

Requisições mínimas:

* `GET {api_base_url}{health_path}`
* opcional fallback para `/`

Validações:

* resposta recebida
* status code
* content-type aceitável
* latência
* redirects inesperados

Falhas:

* `API_HTTP_UNREACHABLE`
* `API_HTTP_TIMEOUT`
* `API_HEALTH_ENDPOINT_MISSING`
* `API_UNEXPECTED_REDIRECT`

---

### Check 7 — Mixed content / coerência de protocolo

Objetivo: detectar incompatibilidade entre frontend e API.

Validações:

* frontend em `https` chamando API `http` pública é inválido no browser
* detectar cenário provável de bloqueio

Falhas:

* `MIXED_CONTENT_RISK`

---

### Check 8 — CORS preflight

Objetivo: simular o que o browser faz.

Requisição:
`OPTIONS {api_base_url}{candidate_api_path}`

Headers mínimos:

* `Origin: {frontend_origin}`
* `Access-Control-Request-Method: GET`

Validações:

* `Access-Control-Allow-Origin`
* `Access-Control-Allow-Methods`
* `Access-Control-Allow-Headers` quando aplicável
* coerência entre origem solicitada e resposta

Falhas:

* `CORS_BLOCKING_ORIGIN`
* `CORS_METHOD_NOT_ALLOWED`
* `CORS_HEADERS_NOT_ALLOWED`

---

### Check 9 — Health semântico do backend

Objetivo: verificar se a API está viva e expõe estado interno útil.

Requisição:
`GET /health`

Validações:

* JSON válido
* campo `status`
* mapa `checks`
* granularidade mínima exigida

Falhas:

* `HEALTH_RESPONSE_INVALID`
* `HEALTH_SCHEMA_INVALID`

---

### Check 10 — Readiness do backend

Objetivo: verificar se o sistema está pronto para tráfego real.

Requisição:
`GET /ready`

Validações:

* resposta 200 apenas se dependências críticas estiverem operacionais
* resposta != 200 quando o backend está “up” mas não “ready”

Falhas:

* `BACKEND_NOT_READY`

---

### Check 11 — Dependências internas

Objetivo: identificar se o problema real está atrás da API.

Dependências mínimas sugeridas:

* banco de dados
* Redis
* worker/fila
* storage externo, se crítico

Falhas:

* `DATABASE_DOWN`
* `DATABASE_DEGRADED`
* `REDIS_DOWN`
* `QUEUE_DOWN`
* `DEPENDENCY_DEGRADED`

---

### Check 12 — Classificação de causa raiz

Objetivo: escolher uma causa raiz principal, sem ambiguidade excessiva.

Regra:

* a primeira falha estrutural bloqueante na cadeia domina a classificação
* falhas posteriores viram evidência secundária, não causa raiz principal

Exemplo:

* se DNS falhar, não faz sentido classificar como CORS
* se TCP falhar, não faz sentido classificar como erro de banco
* se `/health` responde e mostra DB falha, causa raiz é DB, não “erro de conexão”

---

## 8. Contrato do endpoint `/health`

### 8.1 Requisitos

O endpoint `/health` deve:

* retornar JSON
* ter schema estável
* ser barato de executar
* distinguir estado global e estado por dependência
* não depender de parsing textual informal

### 8.2 Resposta mínima canônica

```json
{
  "status": "ok",
  "service": "hb-track-api",
  "timestamp": "2026-03-09T12:00:00Z",
  "checks": {
    "api": {
      "status": "ok"
    },
    "database": {
      "status": "ok",
      "latency_ms": 12
    },
    "redis": {
      "status": "ok",
      "latency_ms": 3
    },
    "queue": {
      "status": "ok"
    }
  }
}
```

### 8.3 Valores permitidos

`status` em nível global e por check:

* `ok`
* `degraded`
* `fail`

### 8.4 Regra de agregação

* `ok`: todos os checks críticos em `ok`
* `degraded`: pelo menos um check não crítico em `degraded/fail`, sem bloquear operação essencial
* `fail`: qualquer dependência crítica em `fail`

---

## 9. Contrato do endpoint `/ready`

### 9.1 Semântica

`/ready` responde se o backend pode receber tráfego de aplicação real.

### 9.2 Regras

* retornar `200` apenas quando dependências críticas estiverem operacionais
* retornar `503` quando não estiver pronto

### 9.3 Resposta mínima

```json
{
  "status": "ready",
  "critical_checks": {
    "database": "ok",
    "api": "ok"
  }
}
```

Ou em falha:

```json
{
  "status": "not_ready",
  "critical_checks": {
    "database": "fail",
    "api": "ok"
  }
}
```

---

## 10. Taxonomia canônica de causa raiz

### 10.1 Configuração

* `FRONTEND_API_URL_MISSING`
* `FRONTEND_API_URL_INVALID`
* `FRONTEND_API_URL_LOCALHOST_MISUSE`
* `API_URL_PARSE_ERROR`

### 10.2 Rede

* `API_HOST_UNRESOLVED`
* `API_PORT_CLOSED`
* `API_TCP_TIMEOUT`

### 10.3 TLS / protocolo

* `TLS_CERT_INVALID`
* `TLS_HOSTNAME_MISMATCH`
* `TLS_HANDSHAKE_FAILED`
* `MIXED_CONTENT_RISK`

### 10.4 HTTP

* `API_HTTP_UNREACHABLE`
* `API_HTTP_TIMEOUT`
* `API_HEALTH_ENDPOINT_MISSING`
* `API_UNEXPECTED_REDIRECT`

### 10.5 Browser / CORS

* `CORS_BLOCKING_ORIGIN`
* `CORS_METHOD_NOT_ALLOWED`
* `CORS_HEADERS_NOT_ALLOWED`

### 10.6 Backend

* `HEALTH_RESPONSE_INVALID`
* `HEALTH_SCHEMA_INVALID`
* `BACKEND_NOT_READY`
* `API_RETURNED_500`

### 10.7 Dependências

* `DATABASE_DOWN`
* `DATABASE_DEGRADED`
* `REDIS_DOWN`
* `QUEUE_DOWN`
* `DEPENDENCY_DEGRADED`

### 10.8 Controle

* `PASS`
* `BLOCKED_INPUT`
* `ERROR_INFRA`
* `UNKNOWN_FAILURE`

---

## 11. Exit codes

Compatível com sua convenção operacional:

* `0` = `PASS`
* `2` = `FAIL_ACTIONABLE`
* `3` = `ERROR_INFRA`
* `4` = `BLOCKED_INPUT`

### Regra de mapeamento

* erro corrigível por config, CORS, URL, health, readiness, dependência => `2`
* falha de infraestrutura do próprio mecanismo de diagnóstico => `3`
* entrada ausente, config insuficiente ou contrato incompleto => `4`

---

## 12. Saída JSON obrigatória

O relatório JSON deve conter no mínimo:

```json
{
  "contract": "CONNECTIVITY_DIAGNOSTIC_CONTRACT",
  "version": "v1.0.0",
  "status": "fail",
  "exit_code": 2,
  "root_cause_code": "DATABASE_DOWN",
  "root_cause_summary": "API acessível, porém health declara banco indisponível",
  "inputs": {
    "api_base_url": "https://api.hbtrack.com",
    "frontend_origin": "http://localhost:3000"
  },
  "checks": [
    {
      "name": "frontend_api_url",
      "status": "pass",
      "evidence": "NEXT_PUBLIC_API_URL=https://api.hbtrack.com"
    },
    {
      "name": "dns_resolution",
      "status": "pass",
      "evidence": "api.hbtrack.com -> 203.0.113.10"
    },
    {
      "name": "tcp_connectivity",
      "status": "pass",
      "evidence": "443 reachable"
    },
    {
      "name": "health",
      "status": "fail",
      "evidence": "database.status=fail"
    }
  ],
  "recommended_action": "Validar disponibilidade do PostgreSQL e credenciais do backend na VPS"
}
```

---

## 13. Saída Markdown opcional

O relatório markdown deve resumir:

* contexto
* inputs usados
* resultado final
* causa raiz
* checks executados
* evidências
* ação recomendada

Isso é útil para `_reports/` e handoff para auditor/testador.

---

## 14. Regras de implementação

1. Implementação em Python.
2. Sem shell scripts.
3. Sem depender do navegador para coletar evidência primária.
4. Sem parsing frágil de texto quando houver JSON canônico.
5. Cada check deve ser isolado em função própria.
6. A classificação final deve ser reproduzível com a mesma entrada.
7. Timeout padrão deve ser configurável.
8. O script não deve mascarar exceções sem registrá-las no relatório.
9. O script deve continuar coletando evidência quando possível, mas respeitando bloqueios lógicos de cadeia.
10. O contrato deve separar:

* falha do ambiente alvo
* falha do próprio script
* entrada insuficiente

---

## 15. Estrutura sugerida do código

```text
tools/
  diagnostics/
    diagnose_connectivity.py
    checks/
      check_frontend_config.py
      check_dns.py
      check_tcp.py
      check_tls.py
      check_http.py
      check_cors.py
      check_health.py
      check_ready.py
      classify_root_cause.py
    models/
      diagnostic_result.py
      check_result.py
    reporters/
      write_json_report.py
      write_md_report.py
config.py
_reports/
```

---

## 16. Critérios de aceite (DoD)

A implementação só está pronta quando:

1. Detecta URL inválida do frontend.
2. Detecta host não resolvido.
3. Detecta porta fechada.
4. Detecta TLS inválido.
5. Detecta CORS bloqueando origem local.
6. Detecta `/health` ausente ou malformado.
7. Detecta `/ready` não pronto.
8. Detecta banco indisponível via `/health`.
9. Gera relatório JSON estável.
10. Retorna exit code correto.
11. Executa apenas com Python.
12. Não depende de inspeção manual para classificar a falha principal.

---

## 17. Matriz mínima de testes do próprio diagnóstico

### Caso 1

Frontend aponta para `localhost` indevido
Esperado: `FRONTEND_API_URL_LOCALHOST_MISUSE`

### Caso 2

Domínio inexistente
Esperado: `API_HOST_UNRESOLVED`

### Caso 3

Porta fechada
Esperado: `API_PORT_CLOSED`

### Caso 4

Certificado inválido
Esperado: `TLS_CERT_INVALID`

### Caso 5

API responde, mas sem CORS para localhost
Esperado: `CORS_BLOCKING_ORIGIN`

### Caso 6

API responde 200 em `/health`, mas schema inválido
Esperado: `HEALTH_SCHEMA_INVALID`

### Caso 7

API no ar, `/ready` = 503
Esperado: `BACKEND_NOT_READY`

### Caso 8

`/health` informa `database=fail`
Esperado: `DATABASE_DOWN`

### Caso 9

Tudo saudável
Esperado: `PASS`

---

## 18. Limites explícitos do contrato

Para não prometer mais do que o sistema pode provar:

1. O script não inspeciona o browser real; ele simula checks relevantes.
2. Causa raiz de banco depende de `/health` expor esse estado.
3. Mixed content é inferido a partir dos protocolos configurados.
4. O contrato não substitui observabilidade de produção; ele cobre diagnóstico operacional rápido de conectividade.

---

## 19. Evoluções futuras recomendadas

Versão futura pode incluir:

* teste real de endpoint de negócio além de `/health`
* comparação entre env do frontend e contrato OpenAPI
* validação de DNS reverso / SNI / proxy
* diagnóstico de websocket, se existir
* modo CI para validar ambiente antes de deploy
* integração com evidência em `_reports/`

---

## 20. Decisão arquitetural recomendada

Não implemente só o script.

Implemente o pacote completo abaixo, porque só ele fecha a cadeia de causa raiz:

* `diagnose_connectivity.py`
* `GET /health`
* `GET /ready`
* JSON schema estável para `/health`
* relatório `_reports/connectivity_diagnostic_report.json`


