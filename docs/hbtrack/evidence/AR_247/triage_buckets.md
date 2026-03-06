# AR_247 — Triage 4 Buckets (Fase 1)

**Data**: 2026-03-05
**Suite**: tests/training/
**Baseline confirmado**: 610p/4s/1xf/0f (idempotência verificada em 2 runs)

## Tabela de Triage

| # | Arquivo | Teste | Tipo | Bucket |
|---|---------|-------|------|--------|
| 1 | `tests/training/contracts/test_contract_train_096_101_105_ia_athlete.py` | `TestContractTrain105WellnessContentGate::test_wellness_content_gate_not_yet_implemented` | SKIP | B=Contrato/Endpoint |
| 2 | `tests/training/invariants/test_inv_train_016_attendance_auth_scoped.py` | `TestInvTrain016AttendanceAuthScoped::test_authenticated_request_bypasses_auth_guard` | SKIP | C=Regra/Invariante |
| 3 | `tests/training/invariants/test_inv_train_058_session_structure_mutable.py` | `TestInvTrain058SessionStructureMutable::test_invalid_session_readonly_rejects_add_exercise` | SKIP | C=Regra/Invariante |
| 4 | `tests/training/invariants/test_inv_train_059_exercise_order_contiguous.py` | `TestInvTrain059ExerciseOrderContiguous::test_invalid_gap_in_order_2_4` | SKIP | C=Regra/Invariante |
| 5 | `tests/training/invariants/test_inv_train_148_exercise_bank_services.py` | `TestInvTrain148ExerciseBankServices::test_acl_003_cross_org_blocked` | XFAIL | C=Regra/Invariante |

## Legenda de Buckets
- **A** = Infra/DB/Seed — falhas de infra, conexão, seed, migration
- **B** = Contrato/Endpoint — contrato de API, endpoint não implementado
- **C** = Regra/Invariante — regra de negócio, invariante de domínio
- **D** = UI/E2E — frontend, E2E, Playwright

## Observações
- 0 FAILs reais encontrados — apenas SKIPs e XFAILs conhecidos
- Bucket A: 0 itens
- Bucket B: 1 item (SKIP — feature not_yet_implemented: wellness content gate)
- Bucket C: 4 itens (3 SKIPs + 1 XFAIL por ACL cross-org pendente)
- Bucket D: 0 itens
- XFAIL `test_acl_003_cross_org_blocked`: comportamento esperado (ACL cross-org bloqueio declarado como not-yet-enforced)
