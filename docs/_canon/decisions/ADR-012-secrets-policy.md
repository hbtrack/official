# ADR-012: Gerenciamento de Secrets e Política de Rotação

- Status: Accepted
- Date: 2026-03-15
- Deciders: Equipe HB Track
- Tags: security, secrets, rotation, credentials, infrastructure
- Resolves: ARCH-006

## Context

O HB Track usa credenciais de banco de dados, chaves JWT, API keys de serviços externos e secrets de CI/CD. Sem política formal, há risco de: secrets em repositório (falha crítica), ausência de rotação periódica (exposição prolongada em caso de vazamento) e ambiguidade entre ambientes (dev vs. prod).

Para v0, há uma arquitetura VPS single-node sem Vault. A política deve ser pragmática para o estágio atual e com caminho claro de evolução.

## Decision

### Ambientes e mecanismos por camada

| Ambiente | Mecanismo | Responsabilidade |
|----------|-----------|-----------------|
| Desenvolvimento local | `.env` (gitignored) com template em `.env.example` | Desenvolvedor |
| CI/CD (GitHub Actions) | GitHub Actions `secrets.*` — nunca hardcoded em workflow YAML | Mantenedor do repositório |
| Staging/Produção (VPS) | Variáveis de ambiente do SO injetadas pelo script de deploy | `scripts/deploy/inject_env.sh` (infra) |
| Testes automatizados | `.env.test` (gitignored) ou variáveis de ambiente | Pipeline CI |

**Regra inviolável**: nenhum secret ou valor de credential pode aparecer em:
- Qualquer arquivo versionado no repositório git (incluindo branches de feature, fixup commits)
- Logs de aplicação (ver ADR-013)
- Respostas de API (ver ADR-010 — CREDENTIALS nunca retornados)
- Arquivos de configuração não-gitignored

### Variáveis de ambiente canônicas

| Variável | Tipo | Módulo | Rotação |
|----------|------|--------|---------|
| `DATABASE_URL` | DSN PostgreSQL | todos | 90 dias |
| `REDIS_URL` | DSN Redis | `identity_access`, workers | 90 dias |
| `JWT_PRIVATE_KEY` | PEM RSA-2048 privada (base64 ou multiline) | `identity_access` | 90 dias |
| `JWT_PUBLIC_KEY` | PEM RSA-2048 pública (base64 ou multiline) | todos (verificação) | com `JWT_PRIVATE_KEY` |
| `SECRET_KEY` | String aleatória ≥ 32 bytes | aplicação (CSRF, sessões) | 180 dias |
| `SENTRY_DSN` | URL de telemetria | infra | never (rotate on leak) |
| `SMTP_*` | Credenciais de e-mail | `notifications` | on rotation do provedor |

### Geração e armazenamento de chaves JWT

1. Geração: `openssl genrsa -out private.pem 2048 && openssl rsa -in private.pem -pubout -out public.pem`
2. Armazenamento de desenvolvimento: `private.pem` e `public.pem` em diretório gitignored (`keys/`, listado em `.gitignore`).
3. Produção: exportar como variável de ambiente via `export JWT_PRIVATE_KEY="$(cat private.pem | base64 -w0)"` ou multiline literal. Nunca commitar os arquivos `.pem`.
4. Endpoint público: `/.well-known/jwks.json` expõe apenas a chave pública em formato JWK (sem campo privado `d`). Ver ADR-007.

### Política de rotação

| Secret | Período | Trigger adicional |
|--------|---------|------------------|
| Chaves JWT (`JWT_PRIVATE_KEY` + `JWT_PUBLIC_KEY`) | 90 dias | Imediato em caso de suspeita de vazamento |
| Credenciais de banco de dados | 90 dias | Imediato em demissão/saída de mantenedor |
| `SECRET_KEY` da aplicação | 180 dias | Imediato em suspeita de comprometimento |
| Tokens de API de terceiros | Conforme provedor | Imediato em caso de exposição |

Rotação de chave JWT requer:
1. Gerar novo par de chaves.
2. Publicar nova chave pública em `/.well-known/jwks.json` (manter chave antiga por 15 minutos para draining de tokens em voo).
3. Atualizar `JWT_PRIVATE_KEY` / `JWT_PUBLIC_KEY` no ambiente de produção e reiniciar serviço.
4. Após 15 minutos: remover chave antiga do JWKS.

### Auditoria de acesso a secrets

- Toda falha de autenticação que sugira credential comprometida deve gerar evento `CREDENTIAL_ANOMALY` no módulo `audit`.
- Não logar os valores de secrets — apenas o evento de anomalia com timestamp, IP e operação.

### Roadmap de evolução

| Versão | Ação |
|--------|------|
| v0 (atual) | `.env` + VPS env vars + GitHub Actions secrets |
| v0.5 | Script de rotação automatizada (`scripts/ops/rotate_keys.sh`) |
| v1.0 | Avaliar HashiCorp Vault ou AWS Secrets Manager se escala justificar |

## Consequences

### Positive
- `.env.example` com template evita ambiguidade sobre quais variáveis são necessárias.
- Rotação trimestral de chaves JWT com draining seguro minimiza janela de exposição.
- Caminho claro de evolução para vault sem reescrita de código.

### Negative
- Sem vault, não há controle de acesso granular a secrets individuais para v0.
- Rotação manual requer disciplina operacional e documentação de procedimento.
- `JWT_PRIVATE_KEY` como variável de ambiente (vs. arquivo em disco) pode ser exposta via `/proc/*/environ` em Linux — trade-off aceitável para v0.

## Alternatives Considered

- **HashiCorp Vault desde o início**: mais seguro, mas overhead de infraestrutura (um novo serviço + HA) não justificado para v0 single-node VPS. Candidato para v1.0+.
- **AWS Secrets Manager**: adequado se infraestrutura for migrada para AWS. Fora do escopo para VPS v0.
- **Chaves simétricas (HS256)**: rejeitado em ADR-007 — chave simétrica compartilhada não permite rotação sem downtime e não suporta JWKS público.

## Links

- Resolves: `docs/_canon/ARCHITECTURE_DECISION_BACKLOG.md` ARCH-006
- Related: `docs/_canon/SECURITY_RULES.md` (regras de credenciais)
- Related: `docs/_canon/decisions/ADR-007-auth-strategy.md` (JWT key management)
- Related: `docs/_canon/decisions/ADR-010-sensitive-data-policy.md` (CREDENTIALS class)
- Related: `docs/_canon/decisions/ADR-013-logging-policy.md` (nunca logar secrets)
