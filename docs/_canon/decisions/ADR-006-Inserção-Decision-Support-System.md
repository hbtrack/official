# ADR-006: Inserção do Decision Support System (DSS) no fluxo contract-driven

- Status: Accepted
- Date: 2026-03-15
- Deciders: Equipe HB Track
- Tags: governance, dss, decision-intelligence, architecture

## Context

O HB Track opera em contract-driven strict mode: trilogia normativa, paths canônicos, precedência explícita, templates como scaffold e bloqueio quando falta artefato canônico. O sistema já reconhece ADRs como artefatos de explicação e prevê decisões em aberto nos templates via `{{OPEN_DECISIONS_MD_LIST}}`.

Apesar desta governança forte, existia uma lacuna: decisões arquiteturais críticas (autenticação, autorização, timezone, políticas de dados sensíveis, readiness operacional) podiam chegar implicitamente ao momento de criação de contrato sem racional formal aprovado. Isso criava risco de preenchimento arbitrário de placeholders por agentes de IA e de descoberta tardia de incompatibilidades entre módulos.

O modelo de sport tech de handebol amplifica este risco: ingestão de dados em tempo real, múltiplos stakeholders, eventos assíncronos e métricas derivadas dependem de decisões sobre sincronização temporal, estratégias de auth e políticas de retenção que devem ser tomadas antes do primeiro contrato, não após.

## Decision

Criar uma camada formal de **Decision Support System (DSS)** dentro do fluxo contract-driven do HB Track, materializada nos seguintes artefatos e regras:

1. **Estágio `Decision Discovery`** — estágio formal anterior a `contract_creation_mode` e `contract_revision_mode` sempre que houver lacuna arquitetural identificada. Não altera contratos diretamente; identifica decisões implícitas, compara alternativas e prepara racional para aprovação humana.

2. **DSS como apoio, não como SSOT** — o DSS gera proposta estruturada (contexto, problema, alternativas, recomendação, trade-offs, riscos, impacto em canon/contratos), mas a decisão final pertence ao humano. Nenhuma sugestão do DSS pode ser executada silenciosamente.

3. **Promoção obrigatória** — toda decisão aprovada deve ser promovida para `docs/_canon/decisions/ADR-*.md` e, quando necessário, refletida em `ARCHITECTURE.md`, `API_CONVENTIONS.md`, `DATA_CONVENTIONS.md`, `SECURITY_RULES.md` e contratos técnicos.

4. **Checklist mínima de lacunas arquiteturais** — o DSS deve avaliar obrigatoriamente os seguintes tópicos antes de qualquer contrato de produção:
   `AUTH_STRATEGY`, `AUTHZ_STRATEGY`, `VERSIONING_STRATEGY`, `DEPRECATION_POLICY`, `DATE_TIME_STANDARD`, `TIMEZONE_POLICY`, `SENSITIVE_DATA_POLICY`, `RETENTION_POLICY`, `MASKING_POLICY`, `SECRETS_POLICY`, `ROTATION_POLICY`, `LOGGING_POLICY`.

5. **Impact map** — o DSS deve produzir mapeamento de quais artefatos canônicos precisarão ser alterados e quais gates precisam ser executados antes da implementação.

6. **Gatilho esportivo** — quando a decisão impactar semântica de handebol ou ciência do esporte, o DSS deve exigir leitura de `HANDBALL_RULES_DOMAIN.md` e `SPORT_SCIENCE_RULES_<MODULE>.md` antes de propor opção final.

7. **Classificação de criticidade** — o DSS classifica cada decisão em `obrigatória`, `importante` ou `opcional`. Se `obrigatória` e sem base canônica suficiente, o fluxo bloqueia com `BLOCKED_MISSING_ARCH_DECISION` antes de implementar.

8. **Artefatos canônicos instituídos por esta ADR**:
   - `docs/_canon/DECISION_POLICY.md`
   - `docs/_canon/ARCHITECTURE_DECISION_BACKLOG.md`
   - `.contract_driven/agent_prompts/decision_discovery.prompt.md`
   - Gate `ARCH_DECISION_PRESENCE_GATE` em `docs/_canon/gates/GATES_REGISTRY.yaml`

## Consequences

### Positive
- Decisões arquiteturais críticas passam a ter racional formal antes de qualquer implementação.
- Redução de inferência arbitrária de agentes de IA ao encontrar placeholders não resolvidos.
- Melhor fechamento de lacunas de produção (auth, timezone, dados sensíveis) antes do contrato nascer.
- Rastreabilidade explícita entre decisão → ADR → canon → contrato → evidência.
- O backlog torna visível ao fundador quais decisões ainda não foram tomadas.

### Negative
- Aumento de fricção no fluxo quando `Decision Discovery` é obrigatório — mais um estágio antes do contrato.
- Risco de burocracia excessiva se o backlog não for mantido enxuto e priorizado.
- Dependência de disciplina operacional: o estágio só tem valor se executado consistentemente.

## Alternatives Considered

- **Manter implícito** — decisões arquiteturais continuariam surgindo durante a criação de contratos, com risco de preenchimento arbitrário de placeholders. Rejeitado: incompatível com o princípio de bloqueio por ausência de artefato.
- **DSS como SSOT autônomo** — o DSS tomaria decisões sem aprovação humana. Rejeitado: contradiz a hierarquia de soberania do sistema; todo artefato normativo requer aprovação explícita.
- **Checklist inline nos templates de contrato** — adicionar a checklist mínima dentro dos templates de contrato em vez de um estágio separado. Rejeitado: não resolve visibilidade do backlog nem cria gate de enforcement.

## Links

- Related docs: `docs/_canon/DECISION_POLICY.md`, `docs/_canon/ARCHITECTURE_DECISION_BACKLOG.md`
- Related gates: `docs/_canon/gates/GATES_REGISTRY.yaml` (gate `ARCH_DECISION_PRESENCE_GATE`)
- Related prompt: `.contract_driven/agent_prompts/decision_discovery.prompt.md`
- Related ADRs: `ADR-001-contract-driven-development.md`, `ADR-004-api-policy-compiler-authority.md`, `ADR-005-sports-science-rules-module.md`
- Related canon: `docs/_canon/ARCHITECTURE.md` §6, `docs/_canon/CHANGE_POLICY.md`
