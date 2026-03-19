---
module: "wellness"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: true
type: "permissions"
adr_refs:
  - "ADR-008: authz-strategy (RBAC flat, 5 roles)"
  - "ADR-007: auth-strategy (JWT Bearer)"
  - "ADR-010: sensitive-data-policy (dados de wellness são PII de saúde)"
domain_rules_ref: "./DOMAIN_RULES_WELLNESS.md"
updated_at: "2026-03-19"
---

# PERMISSIONS_WELLNESS.md

> **Nota canônica:** O módulo `identity_access` é a fonte soberana de autorização.
> Este artefato **documenta** como `wellness` aplica a policy — não a redefine.
> Roles canônicos: `admin`, `coordinator`, `coach`, `athlete`, `member` (ADR-008).
> **⚠️ Dados de wellness (sono, fadiga, humor, dor) são PII de saúde — ADR-010 aplica.**
> Enforcement por operação, via guards no Router (BFLA) e Service (BOLA, BOPLA).

---

## Tabela de Permissões por Operação

| Operação (operationId) | admin | coordinator | coach | athlete | member | Observação |
|---|---|---|---|---|---|---|
| `createWellnessEntry` | ✅ | ✅ | ✅ (contexto) | ✅ (próprio) | ❌ | **PII saúde**: athlete submete seus próprios dados; staff registra por atleta em contexto de sessão |
| `listWellnessEntries` | ✅ | ✅ | ✅ (time) | ✅ (próprias) | ❌ | BOLA: athlete vê apenas suas entradas; coach vê atletas do seu time |
| `getWellnessEntry` | ✅ | ✅ | ✅ (time) | ✅ (própria) | ❌ | **PII saúde**: BOLA rigoroso por entrada |
| `listAthleteWellnessEntries` | ✅ | ✅ | ✅ (time) | ✅ (próprias) | ❌ | Histórico de wellness por atleta — escopo BOLA |
| `getAthleteWellnessSummary` | ✅ | ✅ | ✅ (time) | ✅ (próprio) | ❌ | Resumo agregado de wellness — útil para coach gerenciar carga |

---

## Regras de contexto cross-operação

| ID | Regra | Ref |
|---|---|---|
| PERM-WEL-001 | Dados de wellness são PII de saúde; acesso por coach gera `data_access_log` obrigatório | ADR-010, DOMAIN_RULES_WELLNESS |
| PERM-WEL-002 | Athlete não pode ver dados de wellness de outros atletas em hipótese nenhuma | DOMAIN_RULES_WELLNESS, BOLA |
| PERM-WEL-003 | coach só acessa wellness de atletas do seu time ativo — histórico de ex-atletas não acessível | DOMAIN_RULES_WELLNESS |
| PERM-WEL-004 | Dados de wellness com `pain_level >= 7` devem acionar alerta para coach/coordinator (integração com training.attention_queue) | DOMAIN_RULES_WELLNESS |
