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
| Desenvolvimento local | `.env` (gitignored) | Desenvolvedor |
| CI/CD (GitHub Actions) | GitHub Actions `secrets.*` — nunca hardcoded em workflow YAML | Mantenedor do repositório |
| Staging/Producao (VPS) | `/opt/hbtrack/<env>/.env` renderizado deterministicamente por `scripts/deploy/inject_env.sh` a partir do source graph operacional + GitHub environment secrets/vars | Mantenedor de operacoes |
| Testes automatizados | `.env.test` (gitignored) ou variáveis de ambiente | Pipeline CI |

SSOT estruturado vigente:

- `docs/_canon/graph/ops/environment_catalog.yaml`
- `docs/_canon/graph/ops/secrets_catalog.yaml`
- `docs/_canon/graph/ops/github_actions_catalog.yaml`

Regra:

- este ADR registra a politica de decisao
- o catalogo operacional de nomes e locais de secret vive em `docs/_canon/graph/ops/`
- alteracao em workflow, template, compose ou runtime que mude secret/variavel obrigatoria deve atualizar o source graph operacional no mesmo changeset
- deploy nao pode mais bootstrapar `.env` inline; o renderer operacional falha fechado se faltar valor obrigatorio

**Regra inviolável**: nenhum secret ou valor de credential pode aparecer em:
- Qualquer arquivo versionado no repositório git (incluindo branches de feature, fixup commits)
- Logs de aplicação (ver ADR-013)
- Respostas de API (ver ADR-010 — CREDENTIALS nunca retornados)
- Arquivos de configuração não-gitignored

### Variáveis de ambiente canônicas

O inventário obrigatório do sistema atual não vive mais em prose livre.

- runtime secrets vigentes: `docs/_canon/graph/ops/secrets_catalog.yaml`
- deploy/GitHub Environment secrets vigentes: `docs/_canon/graph/ops/github_actions_catalog.yaml`
- qualquer nome obrigatório ausente desses catálogos bloqueia o pipeline
- qualquer nome citado abaixo e ausente do catálogo deve ser tratado como drift documental

### Inventário runtime vigente

<!-- OPS_RUNTIME_SECRETS_BEGIN -->
- `SECRET_KEY`
- `DB_PASSWORD`
- `POSTGRES_PASSWORD`
- `JWT_PRIVATE_KEY`
- `JWT_PUBLIC_KEY`
- `CLOUDINARY_URL`
- `CLOUDINARY_API_KEY`
- `CLOUDINARY_API_SECRET`
- `RESEND_API_KEY`
- `GEMINI_API_KEY`
- `PACT_BROKER_BASE_URL`
- `PACT_BROKER_TOKEN`
<!-- OPS_RUNTIME_SECRETS_END -->

### Inventário GitHub Actions / Environment vigente

<!-- OPS_GITHUB_SECRETS_BEGIN -->
- `GITHUB_TOKEN`
- `VPS_HOST_STAGING`
- `VPS_HOST_PRODUCTION`
- `VPS_USER`
- `VPS_SSH_KEY`
- `SECRET_KEY`
- `DB_PASSWORD`
- `POSTGRES_PASSWORD`
- `JWT_PRIVATE_KEY`
- `JWT_PUBLIC_KEY`
- `CLOUDINARY_CLOUD_NAME`
- `CLOUDINARY_API_KEY`
- `CLOUDINARY_API_SECRET`
- `CLOUDINARY_URL`
- `RESEND_API_KEY`
- `GEMINI_API_KEY`
- `PACT_BROKER_TOKEN`
<!-- OPS_GITHUB_SECRETS_END -->

Nota de compatibilidade:

- `DATABASE_URL` ainda aparece no job de testes do workflow, mas o runtime Django usa `DB_*` em `config/settings.py`
- isso e catalogado em `docs/_canon/graph/ops/environment_catalog.yaml` como `ci_only`
- `JWT_SECRET` e `JWT_ALGORITHM=HS256` permanecem exclusivos do job de testes e nao fazem parte do contrato operacional de staging/producao
- `SENTRY_DSN` e credenciais SMTP nao fazem parte do sistema operacional vigente; se passarem a ser obrigatorios, devem entrar primeiro no source graph operacional

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

Contrato operacional de rotação:

- comando soberano de planejamento/checagem: `scripts/ops/rotate_keys.sh`
- source of truth de periodicidade/owner/triggers: `docs/_canon/graph/ops/secrets_catalog.yaml`
- qualquer alteração de período, ator ou trigger deve atualizar o catálogo no mesmo changeset

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
| v0 (atual) | `.env` + templates versionados + GitHub Actions secrets/vars + source graph operacional |
| v0.5 | compiler operacional para render de templates e validacao deterministica |
| v1.0 | Avaliar HashiCorp Vault ou AWS Secrets Manager se escala justificar |

## Consequences

### Positive
- `docs/_canon/graph/ops/` elimina ambiguidade sobre nomes, locais e consumidores de secrets.
- `scripts/deploy/render_env_from_contract.py` + `scripts/deploy/inject_env.sh` removem bootstrap manual e tornam o `.env` de VPS derivado do contrato operacional.
- Rotação trimestral de chaves JWT com draining seguro minimiza janela de exposição.
- Caminho claro de evolução para vault sem reescrita de código.

### Negative
- Sem vault, não há controle de acesso granular a secrets individuais para v0.
- Rotação manual requer disciplina operacional e documentação de procedimento.
- `JWT_PRIVATE_KEY` como variável de ambiente (vs. arquivo em disco) pode ser exposta via `/proc/*/environ` em Linux — trade-off aceitável para v0.
- Enquanto GitHub Environments não estiverem completos com todos os secrets obrigatórios, o deploy falhará fechado ao renderizar `.env`.

### Convenção operacional vigente para GitHub Environments

Nos jobs de deploy, os secrets abaixo devem existir no environment GitHub correspondente (`staging` ou `production`) com o mesmo nome canônico do runtime:

- `SECRET_KEY`
- `DB_PASSWORD`
- `JWT_PRIVATE_KEY`
- `JWT_PUBLIC_KEY`
- `CLOUDINARY_CLOUD_NAME`
- `CLOUDINARY_API_KEY`
- `CLOUDINARY_API_SECRET`
- `RESEND_API_KEY`
- `GEMINI_API_KEY`

Regras:

- `POSTGRES_PASSWORD` pode ser omitido no GitHub Environment e, nesse caso, será derivado de `DB_PASSWORD` pelo renderer operacional
- `CLOUDINARY_URL` pode ser omitido no GitHub Environment e, nesse caso, será derivado de `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET` e `CLOUDINARY_CLOUD_NAME`
- os jobs `deploy-staging` e `deploy-production` nao podem hardcodar valor de secret; a ligacao deve ser `${{ secrets.<NAME> }}`

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
