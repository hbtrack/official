# ADR-007: Estratégia de Autenticação — JWT RS256 com refresh rotation

- Status: Accepted
- Date: 2026-03-15
- Deciders: Equipe HB Track
- Tags: security, authentication, jwt, identity_access
- Resolves: ARCH-001

## Context

O HB Track expõe uma API HTTP multi-módulo com endpoints protegidos em todos os 16 módulos canônicos. Placeholders em templates já referenciavam `Authorization: Bearer <token>` e JWT, mas nenhuma ADR formal definia: algoritmo de assinatura, claims obrigatórias, lifetime de tokens, estratégia de refresh, ou mecanismo de revogação.

Sem essa decisão, nenhum contrato de módulo com endpoints protegidos pode ser finalizado (`BLOCKED_MISSING_ARCH_DECISION` por ARCH-001).

O sistema é stateless por princípio (ARCHITECTURE.md §2 FastAPI) e opera com identidade gerenciada exclusivamente pelo módulo `identity_access`.

## Decision

### Algoritmo de assinatura

**RS256** (RSASSA-PKCS1-v1_5 com SHA-256, par de chaves assimétricas).

Rejeitado HS256: exige compartilhamento do secret entre todos os serviços que verificam tokens — incompatível com o módulo de `identity_access` como único emissor soberano.

Rejeitado ES256: curva elíptica com segurança equivalente em assinatura menor, mas adota suporte mais limitado em libs Python/PostgreSQL e adiciona complexidade sem ganho prático neste estágio.

### Par de chaves

| Item | Decisão |
|------|---------|
| Chave privada | `JWT_PRIVATE_KEY` — variável de ambiente (PEM, RSA 2048 bits mínimo) |
| Chave pública | `JWT_PUBLIC_KEY` — variável de ambiente; exposta em `GET /.well-known/jwks.json` |
| Rotação | A cada 90 dias (ver ADR-012 — SECRETS_POLICY) |

### Claims obrigatórias no access token

| Claim | Tipo | Semântica |
|-------|------|-----------|
| `sub` | `string` (UUID v4) | ID do usuário — sempre `users.id` |
| `iss` | `string` | `"hbtrack"` — fixo |
| `aud` | `string` | `"hbtrack-api"` — fixo |
| `iat` | `integer` | Unix timestamp de emissão |
| `exp` | `integer` | Unix timestamp de expiração |
| `jti` | `string` (UUID v4) | ID único do token — usado para revogação |
| `roles` | `array<string>` | Roles do usuário (ver ADR-008) |
| `teamId` | `string` (UUID v4) ou `null` | Time ativo no contexto da sessão |

Claims adicionais somente via ADR formal — não adicionar claims ad hoc.

### Lifetimes

| Token | Duração | Rationale |
|-------|---------|-----------|
| Access token | **15 minutos** | Janela curta limita exposição se interceptado |
| Refresh token | **7 dias** (sliding window com rotation) | Equilíbrio entre UX e segurança |

Refresh token rotation: a cada uso do refresh token, um novo par (access + refresh) é emitido e o refresh anterior é invalidado.

### Armazenamento do refresh token

O refresh token é armazenado no banco (`identity_access.refresh_tokens`) com `jti`, `userId`, `expiresAt`, `revokedAt`. Não é armazenado em cookie nem em localStorage do cliente — a estratégia de transmissão é definida por contrato do frontend.

### Revogação

Revogação explícita (logout, troca de senha, evento de segurança) via Redis:
- `jti` inserido em set Redis com TTL igual ao tempo restante do token.
- Verificação do jti blacklist ocorre apenas quando o token ainda é válido pelo `exp`.
- Não há verificação de blacklist em cada request de rotina — apenas em fluxos de revogação.

### Endpoint de emissão

`POST /identity-access/auth/token` — módulo `identity_access`. Não expor em outros módulos.

### Endpoint de chave pública

`GET /.well-known/jwks.json` — retorna a chave pública em formato JWK Set (RFC 7517). Sem autenticação. Cache-Control: `max-age=3600`.

## Consequences

### Positive
- Módulo `identity_access` é o único emissor — soberania de autenticação clara.
- RS256 permite verificação de token em qualquer módulo sem acesso ao secret.
- Claims explícitas e tipadas permitem enforcement de authz sem consulta extra ao banco em requests normais.
- Refresh rotation + Redis blacklist cobre os principais vetores de comprometimento de token.

### Negative
- Par de chaves RSA adiciona complexidade operacional vs HS256 (gestão de chave pública, rotação).
- Blacklist Redis é um ponto adicional de infraestrutura para fluxos de revogação.
- Lifetime de 15min para access token exige refresh frequente — custo de UX em clientes que não implementam refresh automático.

## Alternatives Considered

- **HS256**: mais simples, mas exige secret compartilhado entre módulos. Rejeitado: incompatível com soberania do `identity_access`.
- **ES256**: mesma recomendação criptográfica do RS256 com chave menor, mas suporte em bibliotecas Python menos consolidado. Rejeitado para v0; candidato a revisão em v2.0.
- **Sessão server-side (cookie + session store)**: stateful, incompatível com FastAPI stateless e workers Celery. Rejeitado.
- **Opaque tokens (OAuth introspection)**: requer chamada de rede para validar cada token. Rejeitado: latência incompatível com o modelo de módulo único.

## Links

- Resolves: `docs/_canon/ARCHITECTURE_DECISION_BACKLOG.md` ARCH-001
- Related: `docs/_canon/SECURITY_RULES.md`, `docs/_canon/decisions/ADR-008-authz-strategy.md`
- Related: `docs/_canon/decisions/ADR-012-secrets-policy.md` (gestão da chave privada)
- Boundary: módulo `identity_access` — `docs/_canon/ARCHITECTURE.md` §6 (decisões registradas)
