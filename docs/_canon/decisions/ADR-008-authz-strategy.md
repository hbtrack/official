# ADR-008: Estratégia de Autorização — RBAC flat com enforcement por operação

- Status: Accepted
- Date: 2026-03-15
- Deciders: Equipe HB Track
- Tags: security, authorization, rbac, identity_access
- Resolves: ARCH-002

## Context

O HB Track tem operações com acesso diferenciado por perfil de usuário em todos os módulos funcionais. Placeholders nos templates referenciavam roles como `admin`, `coach`, `athlete`, mas não havia ADR formal definindo: o modelo de roles, granularidade de enforcement, herança entre contextos, ou como BOLA/BOPLA/BFLA são aplicadas operacionalmente.

Sem essa decisão, nenhum contrato com operações `role-restricted` pode ser finalizado (`BLOCKED_MISSING_ARCH_DECISION`).

`SECURITY_RULES.md` já lista perfis base como referência; esta ADR os torna normativos e define enforcement.

## Decision

### Modelo de roles

**RBAC flat** — 5 roles canônicos, sem hierarquia de herança automática entre roles.

| Role | Semântica |
|------|-----------|
| `admin` | Acesso total à plataforma — gerenciamento de times, usuários, configurações |
| `coordinator` | Gerenciamento de clube — seasons, times, escalações, competições |
| `coach` | Gestão técnica — treinos, sessões, cargas, wellness, scout |
| `athlete` | Acesso ao próprio perfil — dados pessoais, wellness, treinos atribuídos |
| `member` | Acesso de leitura a dados do time — escalações, resultados públicos |

Roles adicionais ou subroles somente via ADR formal. Não criar roles ad hoc nos contratos.

### Atribuição de roles

- Roles são atribuídos explicitamente por `admin` ou `coordinator` no módulo `identity_access`.
- Roles **não são herdados** entre times ou temporadas — um `coach` do Time A não tem acesso ao Time B sem atribuição explícita.
- Contexto ativo (time + temporada) é representado pela claim `teamId` no JWT (ver ADR-007).
- `admin` é global (independente de `teamId`).

### Granularidade de enforcement

**Por operação**, não por endpoint nem por campo individual.

Cada operação (ex: `listTrainingSessions`, `createMedicalRecord`, `deleteUser`) tem uma declaração de roles permitidos em `PERMISSIONS_<MODULE>.md` do módulo.

Exemplos:
- `listTrainingSessions`: `[admin, coordinator, coach, athlete]` (athlete vê apenas as próprias)
- `createMedicalRecord`: `[admin, coordinator, coach]`
- `deleteUser`: `[admin]`

### Enforcement por camada

| Camada | Enforcement | Tipo |
|--------|------------|------|
| Router (FastAPI) | Verificar role mínimo no JWT antes de chamar o service | BFLA (Function Level) |
| Service | Verificar ownership: `resource.owner_id == jwt.sub` para recursos de ownership individual | BOLA (Object Level) |
| Service | Aplicar allowlist de campos escritáveis por role | BOPLA (Property Level) |
| Database | Constraints de integridade (não substituem enforcement de aplicação) | Complementar |

### BOLA (Broken Object Level Authorization)

- Todo acesso/modificação a recurso individual deve comparar `resource.owner_id` (ou `resource.teamId`) com o contexto do JWT (`sub` ou `teamId`).
- `admin` e `coordinator` têm bypass explícito de ownership, declarado em `PERMISSIONS_<MODULE>.md`.
- Sem bypass: service lança `AuthorizationError` → Router retorna `403 Forbidden`.

### BOPLA (Broken Object Property Level Authorization)

- Allowlist de propriedades escritáveis por role definida em `PERMISSIONS_<MODULE>.md`.
- Service aplica allowlist antes de persistir. Campos fora da allowlist são silenciosamente ignorados (não erro).
- Campos de leitura restrita (ex: dados médicos para `member`) filtrados no service antes de serializar.

### BFLA (Broken Function Level Authorization)

- Dependency FastAPI (`require_roles([...])`) aplicada em cada router operation.
- Roles permitidos declarados explicitamente — ausência de declaração = operação bloqueada por padrão (deny-by-omission conforme `SECURITY_RULES.md` regra 1).

## Consequences

### Positive
- RBAC flat é implementável sem framework externo de políticas (ex: OPA) — reduz complexidade.
- Enforcement por operação é granular o suficiente para todos os casos de uso atuais.
- Deny-by-omission garante que endpoints não-declarados são bloqueados por padrão.
- `PERMISSIONS_<MODULE>.md` torna as permissões rastreáveis por módulo.

### Negative
- Sem herança de roles: atribuição manual quando um usuário tem múltiplos papéis. Custo operacional para clubes grandes.
- RBAC flat não suporta cenários multi-tenant complexos sem revisão. Candidato a ADR de revisão se o sistema escalar para múltiplos clubes independentes.
- Allowlist de campos (BOPLA) exige manutenção em `PERMISSIONS_<MODULE>.md` a cada novo campo de contrato.

## Alternatives Considered

- **RBAC hierárquico** (`admin > coordinator > coach > athlete > member`): herança automática reduz atribuições, mas cria complexidade em casos onde `coordinator` não deve ver dados médicos que `coach` vê. Rejeitado para v0.
- **ABAC (Attribute-Based Access Control)**: expressividade máxima, mas overhead de implementação e auditoria incompatível com o estágio atual. Candidato para v2+.
- **OPA / Casbin como policy engine**: adequado para sistemas multi-tenant ou com políticas dinâmicas. Rejeitado para v0 — adiciona dependência de infraestrutura sem necessidade imediata.

## Links

- Resolves: `docs/_canon/ARCHITECTURE_DECISION_BACKLOG.md` ARCH-002
- Related: `docs/_canon/SECURITY_RULES.md`, `docs/_canon/decisions/ADR-007-auth-strategy.md`
- Boundary: todo módulo com operações restritas deve ter `PERMISSIONS_<MODULE>.md`
- Gate: `OWASP_API_CONTROL_MATRIX_GATE` valida BOLA/BOPLA/BFLA por contrato
