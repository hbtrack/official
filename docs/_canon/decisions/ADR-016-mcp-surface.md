# ADR-016: Exposição de Ferramentas Canônicas via MCP — Adiada para pós-v1.0

- Status: Deferred
- Date: 2026-03-15
- Deciders: Equipe HB Track
- Tags: mcp, agent-tools, external-integration, security
- Resolves: ARCH-010
- Deferred-Until: v1.0 em produção estável com revisão de segurança dedicada

## Context

O HB Track usa agentes (Copilot + orquestrador pré-contrato) que invocam ferramentas via tool calling. O Model Context Protocol (MCP) é um protocolo emergente que padroniza como ferramentas são expostas para agentes. Adotar MCP permitiria expor as ferramentas canônicas do HB Track (validação de contratos, lint, geração de artefatos) de forma padronizada para qualquer agente compatível (Claude, Copilot, etc.).

### Por que adiar

1. **Estratégia de autenticação de agentes externas não finalizada**: ADR-007 define JWT RS256 para usuários humanos. Agentes externos via MCP precisariam de um mecanismo de credencial distinto (service token, mTLS, OAuth client_credentials) que ainda não foi analisado.

2. **Lacunas de autorização para agentes externos**: ADR-008 define RBAC para usuários com roles. Agentes externos não se encaixam no modelo de 5 roles sem definição de um role `agent` ou equivalente, com permissões restritas ao subconjunto de operações relevantes.

3. **Riscos de segurança não analisados**:
   - SSRF via ferramenta MCP que aceita URLs externas.
   - Prompt injection via conteúdo de artefato retornado por ferramenta MCP.
   - Escalada de privilégio via encadeamento de ferramentas.

4. **Maturidade do protocolo**: MCP estava em estado emergente no momento desta decisão. A especificação pode mudar de forma incompatível antes de v1.0.

5. **Complexidade de infraestrutura**: um MCP server dedicado é um serviço adicional a operar, monitorar e manter. Para v0/v0.5, isso não se justifica.

## Decision

**Esta decisão é adiada formalmente.** Nenhum MCP server será implementado antes de v1.0 em produção estável.

### Condições necessárias para revisitar (gatilhos de reabertura)

Todas as condições abaixo devem ser satisfeitas antes de reabrir ARCH-010:

1. v1.0 em produção estável (uptime > 30 dias sem incidentes críticos de segurança).
2. Revisão de segurança dedicada para autenticação e autorização de agentes externos.
3. Definição de ADR para `agent-identity` — como agentes externos recebem credentials e com que role/scope.
4. Análise formal de risco de SSRF e prompt injection na superfície MCP.
5. MCP spec em versão estável (≥ 1.0 com pelo menos 6 meses de adoção observada).

### O que pode ser feito antes de v1.0 (preparação)

- Documentar a lista de ferramentas canônicas candidatas a exposição MCP: `validate_contracts`, `generate_openapi`, `lint_contracts`, `run_gates`.
- Garantir que os scripts em `scripts/` sejam invocáveis via CLI com interface estável (flags documentadas e testadas) — prerequisito de qualquer MCP wrapper.
- Nenhum código MCP pode ser implementado antes da reabertura desta decisão.

## Consequences

### Positive
- Evita superficie de ataque prematura antes de estratégia de autenticação de agentes estar madura.
- Evita acoplamento a especificação MCP ainda em evolução.
- Reduz complexidade operacional de v0/v0.5.

### Negative
- Integração com novos agentes externos (ex: ferramentas de terceiros) permanece manual até v1.0+.
- Agentes de desenvolvimento (Copilot) continuam usando o orquestrador via file-reading em vez de ferramentas MCP nativas.

## Alternatives Considered

- **Implementar MCP server com autenticação básica agora**: superfície maior sem análise de segurança adequada. Rejeitado — segurança first.
- **Expor apenas ferramentas read-only (sem mutação de estado)**: ainda requer análise de prompt injection e autenticação. Insuficiente para justificar implementação prematura.

## Links

- Resolves: `docs/_canon/ARCHITECTURE_DECISION_BACKLOG.md` ARCH-010
- Related: `docs/_canon/decisions/ADR-007-auth-strategy.md` (JWT strategy — não cobre agent identity)
- Related: `docs/_canon/decisions/ADR-008-authz-strategy.md` (RBAC — agent role não definido)
- Related: `docs/_canon/decisions/ADR-012-secrets-policy.md` (secrets — agent credentials não abordados)
- MCP Spec: <https://spec.modelcontextprotocol.io>
