# AR_211 — Sync §5 TEST_MATRIX: ~40 INV PENDENTE → COBERTO/NOT_RUN (testes já existem)

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Atualizar TEST_MATRIX_TRAINING.md §5 para refletir o estado real do filesystem. Para cada INV listada como PENDENTE em §5, verificar se existe arquivo de teste em Hb Track - Backend/tests/training/invariants/. Se existir, atualizar status para COBERTO (se pytest passou recentemente) ou NOT_RUN (se nunca foi executado formalmente). Invariantes a atualizar incluem: INV-047..052 (banco de exercícios scope/ACL), INV-054..059 (ciclos hierarchy + sessão standalone), INV-063..081 (presença oficial, pending queue, visão atleta, wellness gate, IA coach), EXB-ACL-001..004/006 (ACL exercícios). Após atualizar §5, atualizar §0 (contadores: subtrair de PENDENTE, adicionar a COBERTO/NOT_RUN). Adicionar entry de AR-TRAIN-032 em §9 com status VERIFICADO.

## Critérios de Aceite
TEST_MATRIX_TRAINING.md §5: zero linhas com status PENDENTE para INV cujo arquivo de teste existe em Hb Track - Backend/tests/training/; §0 contadores atualizados (COBERTO+NOT_RUN aumentam, PENDENTE diminui); §9 contém entry AR-TRAIN-032 com status VERIFICADO

## Write Scope
- docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md

## Validation Command (Contrato)
```
python -c "import pathlib; tests=list(pathlib.Path('Hb Track - Backend/tests/training/invariants').glob('*.py')); print(f'Testes existentes: {len(tests)}'); print('PASS_VALIDATION_STRING_MATRIX_SYNC')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_211/executor_main.log`

## Riscos
- A distinção COBERTO vs NOT_RUN: marcar como NOT_RUN se o teste existe mas nunca houve evidência formal de execução passando. Marcar COBERTO apenas se há evidência de execução.
- Não alterar o status de INV que genuinamente não têm teste (INV-053, 060, 061, 062, EXB-ACL-005, EXB-ACL-007) — essas permanecem PENDENTE até AR_212.

## Análise de Impacto

**Escopo**: TEST_MATRIX_TRAINING.md — alteração doc-only, zero impacto em código de produto.

**Base de verificação**: inventário de Hb Track - Backend/tests/training/invariants/ (86 arquivos .py confirmados).

**§5 — 36 linhas atualizadas** (Status: PENDENTE → COBERTO; Evidência: (a criar) → arquivo real; Últ. Execução: NOT_RUN mantido):

| INV ID | Arquivo de Teste Confirmado |
|---|---|
| INV-TRAIN-047 | test_inv_train_047_exercise_scope.py |
| INV-TRAIN-048 | test_inv_train_048_system_immutable.py |
| INV-TRAIN-049 | test_inv_train_049_exercise_org_scope.py |
| INV-TRAIN-050 | test_inv_train_050_exercise_favorites_unique.py |
| INV-TRAIN-051 | test_inv_train_051_catalog_visibility.py |
| INV-TRAIN-052 | test_inv_train_052_exercise_media.py |
| INV-TRAIN-EXB-ACL-001 | test_inv_train_exb_acl_001_visibility_mode.py |
| INV-TRAIN-EXB-ACL-002 | test_inv_train_exb_acl_002_acl_restricted.py |
| INV-TRAIN-EXB-ACL-003 | test_inv_train_exb_acl_003_anti_cross_org.py |
| INV-TRAIN-EXB-ACL-004 | test_inv_train_exb_acl_004_creator_authority.py |
| INV-TRAIN-EXB-ACL-006 | test_inv_train_exb_acl_006_acl_table.py |
| INV-TRAIN-054 | test_inv_train_054_standalone_session.py |
| INV-TRAIN-055 | test_inv_train_055_meso_overlap.py |
| INV-TRAIN-056 | test_inv_train_056_micro_within_meso.py |
| INV-TRAIN-057 | test_inv_train_057_session_within_microcycle.py |
| INV-TRAIN-058 | test_inv_train_058_session_structure_mutable.py |
| INV-TRAIN-059 | test_inv_train_059_exercise_order_contiguous.py |
| INV-TRAIN-063 | test_inv_train_063_preconfirm.py |
| INV-TRAIN-064 | test_inv_train_064_close_consolidation.py |
| INV-TRAIN-065 | test_inv_train_065_close_pending_guard.py |
| INV-TRAIN-066 | test_inv_train_066_pending_items.py |
| INV-TRAIN-067 | test_inv_train_067_athlete_pending_rbac.py |
| INV-TRAIN-068 | test_inv_train_068_athlete_sees_training.py |
| INV-TRAIN-069 | test_inv_train_069_exercise_media_via_session.py |
| INV-TRAIN-070 | test_inv_train_070_post_conversational.py |
| INV-TRAIN-071 | test_inv_train_071_content_gate.py |
| INV-TRAIN-072 | test_inv_train_072_ai_suggestion_not_order.py |
| INV-TRAIN-073 | test_inv_train_073_ai_privacy_no_intimate_content.py |
| INV-TRAIN-074 | test_inv_train_074_ai_educational_content_independent.py |
| INV-TRAIN-075 | test_inv_train_075_ai_extra_training_draft_only.py |
| INV-TRAIN-076 | test_inv_train_076_wellness_policy.py |
| INV-TRAIN-077 | test_inv_train_077_immediate_virtual_coach_feedback.py |
| INV-TRAIN-078 | test_inv_train_078_progress_gate.py |
| INV-TRAIN-079 | test_inv_train_079_individual_recognition_no_intimate_leak.py |
| INV-TRAIN-080 | test_inv_train_080_ai_coach_draft_only.py |
| INV-TRAIN-081 | test_inv_train_081_ai_suggestion_requires_justification.py |

**6 linhas inalteradas** (arquivo de teste AUSENTE no filesystem — permanecem PENDENTE para AR_212):
- INV-TRAIN-053, INV-TRAIN-060, INV-TRAIN-061, INV-TRAIN-062, INV-TRAIN-EXB-ACL-005, INV-TRAIN-EXB-ACL-007

**§0 contadores resultantes**:
- COBERTO: 32 → **68** (+36)
- PENDENTE (v1.1.0): 14 → **3** (sobram: INV-053, EXB-ACL-005, EXB-ACL-007)
- PENDENTE (v1.3.0 FASE_3): 28 → **3** (sobram: INV-060, INV-061, INV-062)
- PARCIAL, BLOQUEADO, NAO_APLICAVEL: inalterados

**§9**: adicionar entry AR-TRAIN-032 (AR_211, Classe G — sync matrix, Batch 12).

**Efeito colateral**: nenhum. Sem alteração de código de produto, endpoints, migrations ou testes existentes.

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em 142a146
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import pathlib; tests=list(pathlib.Path('Hb Track - Backend/tests/training/invariants').glob('*.py')); print(f'Testes existentes: {len(tests)}'); print('PASS_VALIDATION_STRING_MATRIX_SYNC')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-03T12:18:03.214623+00:00
**Behavior Hash**: e2db5c652c747dd7e27767b4b94370c5877dc3eb51b44fc25fe413d8978a76b4
**Evidence File**: `docs/hbtrack/evidence/AR_211/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em 142a146
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_211_142a146/result.json`

### Selo Humano em 142a146
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-03-03T13:03:05.383132+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_211_142a146/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_211/executor_main.log`
