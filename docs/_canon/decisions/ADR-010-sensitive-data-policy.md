# ADR-010: Classificação de Dados Sensíveis e Política de Mascaramento

- Status: Accepted
- Date: 2026-03-15
- Deciders: Equipe HB Track
- Tags: security, data-privacy, masking, pii, phi, lgpd
- Resolves: ARCH-004

## Context

O HB Track gerencia dados pessoais de atletas (nome, e-mail, data de nascimento), dados médicos (prontuário, histórico de lesões), dados de wellness (métricas fisiológicas) e credenciais de acesso. Sem taxonomia formal de sensibilidade, os módulos `users`, `medical`, `wellness` e `identity_access` não têm critério comum para decidir o que mascarar em logs, o que excluir de relatórios de analytics e o que exige consentimento especial (atletas menores).

Contexto regulatório: a LGPD (Lei 13.709/2018) classifica dados de saúde como dados sensíveis com tratamento mais restritivo.

Sem esta ADR, nenhum contrato que crie campos de dados pessoais ou médicos pode ser finalizado sem aviso (`BLOCKED_MISSING_ARCH_DECISION` por ARCH-004).

## Decision

### Taxonomia de classificação de sensibilidade

| Classe | Sigla | Descrição | Exemplos |
|--------|-------|-----------|---------|
| Informação Pessoal Identificável | `PII` | Dados que identificam diretamente uma pessoa natural | `name`, `email`, `phone`, `birthDate`, `documentNumber`, `address` |
| Informação de Saúde Pessoal | `PHI` | Dados de saúde física ou mental vinculados a um indivíduo | Registros médicos, histórico de lesões, métricas de wellness, resultados de testes físicos, diagnósticos |
| Credenciais | `CREDENTIALS` | Dados de autenticação e autorização | `password` (hash), `refreshToken`, chaves privadas, API keys |
| Dados de Negócio Sensíveis | `BUSINESS_SENSITIVE` | Dados internos com impacto competitivo | Negociações de transferência, contratos financeiros de atletas |

Campos sem classificação explícita são tratados como `PUBLIC` por padrão. Campos novos em módulos `users`, `medical`, `wellness`, `identity_access` devem ser classificados explicitamente em `PERMISSIONS_<MODULE>.md` ou no schema JSON de contrato.

### Política de mascaramento em logs

| Classe | Política de log |
|--------|----------------|
| `PII` | Mascaramento parcial: primeiros 2 + `***` + últimos 2 caracteres. Ex: `jo***hn` para nome, `jo***@mail.com` para email |
| `PHI` | Mascaramento total: substituir por `[PHI_REDACTED]` |
| `CREDENTIALS` | Mascaramento total: substituir por `[CREDENTIALS_REDACTED]` |
| `BUSINESS_SENSITIVE` | Mascaramento total: substituir por `[REDACTED]` |
| `PUBLIC` | Sem mascaramento |

**Regra**: nenhum log de aplicação pode conter `PHI` ou `CREDENTIALS` não mascarados, independente do nível de log (`DEBUG`, `INFO`, `ERROR`).

### Política de analytics e relatórios

- `PHI` nunca entra em payloads ou relatórios de analytics individualizados.
- Analytics de wellness e performance: somente agregados (médias de grupo, distribuições) — sem granularidade individual para roles `member`.
- `coach`, `coordinator` e `admin` podem acessar métricas individuais de atletas via endpoints específicos do módulo (com enforcement RBAC via ADR-008).
- `PII` em relatórios: somente como identificador de exibição (nome/avatar) nos módulos que explicitamente precisam, com base em RBAC.

### Consentimento e atletas menores

- Atletas com `birthDate` indicando idade inferior a 18 anos na data de criação da conta: consentimento do responsável legal obrigatório antes de coletar `PHI`.
- A verificação de idade é responsabilidade do módulo `users` no momento de registro.
- Campos de PHI de menores são marcados com `minorConsent: true` no schema de contrato quando aplicável.
- Política de retenção específica para menores: ver ADR-011.

### Campos obrigatoriamente classificados por módulo

| Módulo | Campos PHI | Campos PII | Campos CREDENTIALS |
|--------|-----------|-----------|-------------------|
| `users` | — | `name`, `email`, `phone`, `birthDate`, `documentNumber` | — |
| `medical` | todos os campos clínicos | `name` do atleta (via referência) | — |
| `wellness` | `hrv`, `sRPE`, métricas fisiológicas | — | — |
| `identity_access` | — | `email` | `passwordHash`, `refreshTokenHash` |

### Exposição via API

- `CREDENTIALS` nunca retornados em respostas de API. Hash de senha nunca exposto, mesmo para `admin`.
- `PHI` somente em responses de módulos com `PHI_AUTHORIZED` declarado para a operação em `PERMISSIONS_<MODULE>.md`.
- `PII` aplicar minimização: retornar apenas os campos necessários para a operação (não retornar nome completo se apenas `id` e `displayName` são necessários).

## Consequences

### Positive
- Taxonomia comum elimina decisões ad hoc por módulo sobre o que mascarar.
- Base formal para conformidade LGPD — dados de saúde tratados como dados sensíveis.
- Mascaramento em logs reduz risco de vazamento via observabilidade (stacks de erro, debug logs).
- Atletas menores têm proteção explícita desde o modelo.

### Negative
- Classificação de cada campo novo em contratos adiciona overhead ao fluxo de criação.
- Mascaramento parcial de PII em logs pode dificultar debugging de issues de produção envolvendo usuários específicos.
- `minorConsent` em schema requer implementação de verificação de idade no `users` — não é trivial.

## Alternatives Considered

- **Sem classificação formal (tratar tudo como sensível)**: reduz granularidade; torna inviável analytics legítimo. Rejeitado.
- **Classificação apenas em código (annotations Pydantic)**: não rastreável via contrato OpenAPI/JSON Schema. Rejeitado: deve estar no contrato, não na implementação.
- **DLP automático em logs**: ferramenta de Data Loss Prevention no pipeline de log. Adequada para escala, mas overhead de infraestrutura não justificado para v0. Candidato para v2+.

## Links

- Resolves: `docs/_canon/ARCHITECTURE_DECISION_BACKLOG.md` ARCH-004
- Related: `docs/_canon/SECURITY_RULES.md` (regra 6 — minimização), `docs/_canon/decisions/ADR-011-retention-policy.md`
- Related: `docs/_canon/decisions/ADR-007-auth-strategy.md`, `docs/_canon/decisions/ADR-008-authz-strategy.md`
- Regulatório: LGPD Lei 13.709/2018, especialmente Art. 5° XI (dados sensíveis) e Art. 11 (tratamento de dados sensíveis)
