# AR_221 — Screens Smoke Tests MANUAL_GUIADO: SCREEN-001..025 (AR-TRAIN-042)

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0
**AR SSOT ID**: AR-TRAIN-042
**Batch**: 15

## Descrição
Criar 25 arquivos de evidência MANUAL_GUIADO smoke test para todas as telas do módulo TRAINING (todas PENDENTE em TEST_MATRIX §7). Cada arquivo verifica que a tela renderiza sem crash crítico visível. Seguir template smoke com campos: Status, Rota/Componente, Renders, Elementos Críticos, Resultado. Atualizar TEST_MATRIX §7 para SCREEN-001..025 = COBERTO ou NOT_APPLICABLE. FORBIDDEN: zero toque em `app/`, `Hb Track - Backend/`, `Hb Track - Frontend/`.

## Screens a Cobrir (25 telas PENDENTE)

| Screen | Rota/Componente | Notas |
|---|---|---|
| SCREEN-001 | `/training/agenda` | — |
| SCREEN-002 | `/training/calendario` | — |
| SCREEN-003 | `CreateSessionModal` | modal |
| SCREEN-004 | `SessionEditorModal` | modal |
| SCREEN-005 | `/training/sessions/[id]/edit` | — |
| SCREEN-006 | `/training/relatorio/[sessionId]` | — |
| SCREEN-007 | `/training/planejamento` | — |
| SCREEN-008 | `CreateCycleWizard` | wizard |
| SCREEN-009 | `CopyWeekModal` | modal |
| SCREEN-010 | `/training/exercise-bank` | — |
| SCREEN-011 | `ExerciseModal / CreateExerciseModal / EditExerciseModal` | modais |
| SCREEN-012 | `/training/analytics` | — |
| SCREEN-013 | `ExportPDFModal` | modal, banner degraded |
| SCREEN-014 | `/training/rankings` | — |
| SCREEN-015 | `/training/top-performers/[teamId]` | usa CONTRACT-076 |
| SCREEN-016 | `/training/eficacia-preventiva` | — |
| SCREEN-017 | `/training/configuracoes` | — |
| SCREEN-018 | `/athlete/wellness-pre/[sessionId]` | — |
| SCREEN-019 | `/athlete/wellness-post/[sessionId]` | — |
| SCREEN-020 | `/training/presencas` | — |
| SCREEN-021 | Central de Alertas/Sugestões | — |
| SCREEN-022 | `/athlete/training/[sessionId]` | — |
| SCREEN-023 | `/training/pending-queue` | verificar se rota existe |
| SCREEN-024 | `/athlete/ai-chat/[sessionId]` | AI Coach — NOT_APPLICABLE se sem feature flag |
| SCREEN-025 | `AICoachDraftModal` | AI Coach — NOT_APPLICABLE se sem feature flag |

## Critérios de Aceite
**AC-001:** 25 arquivos `_reports/training/TEST-TRAIN-SCREEN-001.md` .. `TEST-TRAIN-SCREEN-025.md` existem com conteúdo MANUAL_GUIADO válido.
**AC-002:** §7 da `TEST_MATRIX_TRAINING.md` mostra SCREEN-001..025 = COBERTO ou NOT_APPLICABLE.

## Write Scope
- `_reports/training/TEST-TRAIN-SCREEN-001.md` .. `_reports/training/TEST-TRAIN-SCREEN-025.md` (25 arquivos)
- `docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md`

## Validation Command (Contrato)
```
python -c "import os; screens=range(1,26); missing=[s for s in screens if not os.path.exists(f'_reports/training/TEST-TRAIN-SCREEN-{s:03d}.md')]; print('OK' if not missing else f'MISSING: {missing}'); exit(1 if missing else 0)"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_221/executor_main.log`

## Template de Evidência MANUAL_GUIADO Smoke (por tela)
```markdown
# MANUAL_GUIADO: SCREEN-TRAIN-NNN
Status: PASS  (ou SKIP/NOT_APPLICABLE com justificativa)
Rota/Componente: /rota/ou/NomeComponente
Renders: SIM
Elementos Críticos: [lista dos elementos principais visíveis]
Resultado: Tela renderiza sem crash crítico. [observações]
```

## Dependências
- AR-TRAIN-034 — ✅ VERIFICADO (conforme AR_BACKLOG_TRAINING.md)

## Riscos
- Telas de AI Coach (SCREEN-024, SCREEN-025) podem não estar acessíveis sem feature flag — marcar NOT_APPLICABLE com nota.
- SCREEN-023 (`/training/pending-queue`) pode não ter rota real no frontend — verificar e marcar NOT_APPLICABLE se ausente.
- Smoke test verifica apenas que a tela renderiza sem crash crítico visível — não cobre fluxo completo (isso é competência dos FLOW tests).
- Template smoke obrigatório: `# MANUAL_GUIADO: SCREEN-TRAIN-NNN` + campos Status/Rota/Renders/Elementos Críticos/Resultado.
- Não tocar em `app/`, `Hb Track - Backend/` ou `Hb Track - Frontend/` — apenas criar evidências em `_reports/training/`.

## Análise de Impacto

**Executor**: GitHub Copilot (Executor Mode)
**Data**: 2026-02-27

### Arquivos Criados
- 25 arquivos em `_reports/training/`: TEST-TRAIN-SCREEN-001..025.md
- SCREEN-024 e SCREEN-025 (AI Coach): Status = NOT_APPLICABLE (feature flag ausente)
- SCREEN-023 (`/training/pending-queue`): Status = PASS (rota existe para fila de pendências)

### Arquivos Modificados
- `docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md` — §7: 23 PENDENTE → COBERTO; 2 → NOT_APPLICABLE

### Camadas tocadas
- ⛔ `app/` não tocada. ⛔ Backend não tocado. ⛔ Frontend não tocado.
- Apenas evidências em `_reports/training/`.

---
## Carimbo de Execução

*(a preencher pelo Executor)*

### Execução Executor em 142a146
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import os; screens=range(1,26); missing=[s for s in screens if not os.path.exists(f'_reports/training/TEST-TRAIN-SCREEN-{s:03d}.md')]; print('OK' if not missing else f'MISSING: {missing}'); exit(1 if missing else 0)"`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-03T16:18:13.918757+00:00
**Behavior Hash**: d6913e35a48fbda2cab914089cbbae790f406f5857def0cc0b0cdc22d08e9713
**Evidence File**: `docs/hbtrack/evidence/AR_221/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em 142a146
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_221_142a146/result.json`

### Selo Humano em 142a146
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-03-03T16:41:42.181579+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_221_142a146/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_221/executor_main.log`
