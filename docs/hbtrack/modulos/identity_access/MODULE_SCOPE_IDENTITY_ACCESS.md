---
module: "identity_access"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: false
contract_path_ref: "../../../../contracts/openapi/paths/identity_access.yaml"
schemas_ref: "../../../../contracts/schemas/identity_access/"
---

# MODULE_SCOPE_IDENTITY_ACCESS.md

## Responsabilidades
- Definir as responsabilidades do módulo `identity_access`.
- Declarar limites e boundaries com outros módulos quando houver risco de sobreposição.

## Fora do escopo
- Qualquer responsabilidade fora da taxonomia canônica deve ser formalizada via ADR antes de existir.

## Dependências e integrações
- Emissão/validação de JWT via infraestrutura soberana do módulo.
- Fluxo de recuperação de senha com email transacional via provider baseline `Resend`.
- Construção de links de recuperação com `FRONTEND_URL` do ambiente.
- Boundary com `users`: perfil e avatar pertencem a `users`; sessão, reset e RBAC pertencem a `identity_access`.
