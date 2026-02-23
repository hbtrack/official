# HB Track — SPEC (SSOT)

meta:
  document: HB_TRACK_SPEC
  version: "0.1"
  status: SSOT
  ssot_scope: canon_docs
  path: docs/_canon/specs/Kanban Spec.md
  last_updated: 2026-02-20
  depends_on:
    - docs/_canon/contratos/Kanban Hb Track.md
    - docs/_canon/HB_TRACK_PROFILE.yaml
    - docs/_canon/_agent/GATES_REGISTRY.yaml
    - docs/_canon/_agent/FAILURE_TO_GATES.yaml
    - docs/product/runtime/_INDEX.yaml

1. Propósito

HB Track é uma plataforma de gestão esportiva (handebol) com governança determinística.
Este SPEC descreve o sistema em termos testáveis: capabilities, SSOT por domínio, runtime scenarios mínimos e invariantes verificáveis.

2. MVP Capabilities (declarativas)

As capabilities do MVP MUST ser listadas explicitamente aqui.
Qualquer CAPABILITY fora desta lista é NÃO-ESCOPO para READY→DONE.

- AUTH
- RBAC
- ATHLETES
- TEAMS
- TRAINING
- DB_MIGRATIONS
- COMPETITIONS
- OPS_GOV (processo/gates/docs)

3. SSOT por Domínio (alinhado à precedence)

3.1 canon_docs (processo/registries)
- CONTRACT: docs/_canon/contratos/HB_TRACK_CONTRACT.md
- PROFILE: docs/_canon/HB_TRACK_PROFILE.yaml
- Agent registries: docs/_canon/_agent/*.yaml

3.2 ssot_factual / derived_promoted (artefatos promovidos)
- schema.sql: docs/ssot/schema.sql (registry via PROFILE)
- openapi.json: docs/ssot/openapi.json (registry via PROFILE)

3.3 runtime scenarios (append-only)
- Registry: docs/product/runtime/_INDEX.yaml

4. Runtime Scenarios mínimos

Para cada capability do MVP, MUST existir pelo menos 1 scenario no `docs/product/runtime/_INDEX.yaml`.
O scenario MUST apontar para gates/validação e evidência esperada.

5. Invariantes verificáveis (mínimo)

Estas invariantes só devem existir aqui se houver gate capaz de detectar violação:

- INV-AUTH-001: endpoints protegidos MUST rejeitar requisição sem token válido.
- INV-RBAC-001: role sem permissão MUST receber erro esperado.
- INV-TENANT-001: isolamento por organização/tenant MUST ser preservado quando aplicável.

6. Regra de validação por mudança (failure_type → gates)

Mudanças MUST declarar FAILURE_TYPE e CAPABILITY no card.
Os gates mínimos MUST ser derivados de `docs/_canon/_agent/FAILURE_TO_GATES.yaml`.

Exemplos (apenas ilustrativos; a fonte real é o YAML):
- AUTH + FT_AUTH_CONTRACT => gates mínimos típicos: AUTH_E2E_LOGIN, AUTH_CONTRACT_OPENAPI, AUTH_SMOKE_RUNTIME
- RBAC + FT_API_CONTRACT => gates mínimos típicos: RBAC_CONTRACT_OPENAPI, RBAC_SMOKE_PROTECTED (e outros do mapping)

7. Critério de aceite do SPEC

Este SPEC é considerado ativo quando:
- Está referenciado no `docs/_INDEX.yaml` (entrypoints canônicos)
- O Kanban exige CAPABILITY ∈ MVP e referência ao SPEC em cards READY
- Existe pelo menos 1 scenario crítico executável com Evidence Pack reproduzível