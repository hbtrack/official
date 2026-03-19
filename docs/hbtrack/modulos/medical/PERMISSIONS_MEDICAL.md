---
module: "medical"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: true
type: "permissions"
adr_refs:
  - "ADR-008: authz-strategy (RBAC flat, 5 roles)"
  - "ADR-007: auth-strategy (JWT Bearer)"
  - "ADR-010: sensitive-data-policy (PHI/PII)"
domain_rules_ref: "./DOMAIN_RULES_MEDICAL.md"
updated_at: "2026-03-19"
---

# PERMISSIONS_MEDICAL.md

> **Nota canônica:** O módulo `identity_access` é a fonte soberana de autorização.
> Este artefato **documenta** como `medical` aplica a policy — não a redefine.
> Roles canônicos: `admin`, `coordinator`, `coach`, `athlete`, `member` (ADR-008).
> **⚠️ Dados médicos são PHI/PII — ADR-010 aplica restrições adicionais de acesso.**
> Enforcement por operação, via guards no Router (BFLA) e Service (BOLA, BOPLA).

---

## Tabela de Permissões por Operação

| Operação (operationId) | admin | coordinator | coach | athlete | member | Observação |
|---|---|---|---|---|---|---|
| `listMedicalRecords` | ✅ | ✅ | ✅ (time) | ✅ (próprios) | ❌ | **PHI**: coach vê apenas atletas do seu time; BOLA por atleta |
| `createMedicalRecord` | ✅ | ✅ | ✅ | ❌ | ❌ | Criação de registro médico por profissional ou staff autorizado |
| `getMedicalRecord` | ✅ | ✅ | ✅ (time) | ✅ (próprio) | ❌ | **PHI**: BOLA rigoroso — athlete acessa apenas seus dados; coach apenas atletas do time |
| `updateMedicalRecord` | ✅ | ✅ | ✅ | ❌ | ❌ | Atualização de registro médico requer staff |
| `deleteMedicalRecord` | ✅ | ❌ | ❌ | ❌ | ❌ | Deleção de PHI restrita a admin (LGPD compliance) |

---

## Regras de contexto cross-operação

| ID | Regra | Ref |
|---|---|---|
| PERM-MED-001 | Dados médicos (PHI) só acessíveis ao próprio atleta e ao staff diretamente responsável | ADR-010, DOMAIN_RULES_MEDICAL |
| PERM-MED-002 | Todo acesso a dados médicos gera `data_access_log` de conformidade (LGPD Art. 37) | ADR-010 |
| PERM-MED-003 | Deleção de registros médicos segue política de retenção obrigatória (5 anos mínimo CFEF) | DOMAIN_RULES_MEDICAL |
| PERM-MED-004 | coach não pode acessar dados médicos históricos de atletas que não estão mais no seu time | DOMAIN_RULES_MEDICAL, BOLA |
