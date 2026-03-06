# AR_242 — FE: corrigir URLs training-phase3.ts para paths reais do Backend (AR-TRAIN-058)

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Corrigir as URLs dos stubs em training-phase3.ts para alinhar com os paths reais do Backend (openapi.json).

Divergencias identificadas pelo Arquiteto:

(1) CONTRACT-097 pre-confirm:
- training-phase3.ts usa: /training-sessions/${sessionId}/pre-confirm
- Backend real: /api/v1/attendance/sessions/${sessionId}/preconfirm (sem hifen)
- Acao: corrigir path e mover chamada para /attendance/sessions/${sessionId}/preconfirm

(2) CONTRACT-101 ai draft session:
- training-phase3.ts usa: /ai-coach/draft-session
- Backend real: /ai/coach/suggest-session
- Acao: corrigir para /ai/coach/suggest-session

(3) CONTRACT-102 apply draft:
- training-phase3.ts usa: /ai-coach/draft-session/${draftId}/apply
- Backend real (apos AR_240): /ai/coach/draft/${draftId}/apply
- Acao: corrigir path (depende de AR_240 definir path canônico)

(4) CONTRACT-103 athlete chat:
- training-phase3.ts usa: /ai-coach/athlete-chat
- Backend real: /ai/chat
- Acao: corrigir para /ai/chat

(5) CONTRACT-104 justify suggestion:
- training-phase3.ts usa: /ai-coach/justify-suggestion
- Backend real (apos AR_240): /ai/coach/justify-suggestion
- Acao: corrigir path (depende de AR_240)

(6) CONTRACT-105 wellness-content-gate:
- training-phase3.ts usa: /athlete/wellness-content-gate/${sessionId}
- Backend real (apos AR_241): /athlete/wellness-content-gate/${sessionId}
- Acao: manter (URL correta)

PASSOS:
1. Ler openapi.json para confirmar URLs canonicas pos-AR_239/240/241
2. Editar training-phase3.ts corrigindo os 4 paths divergentes
3. Atualizar comentarios JSDoc com paths corretos
4. Rodar hb report 242

DEPENDENCIAS: AR_239 (PATCH resolve), AR_240 (apply + justify), AR_241 (wellness-content-gate) — Executor deve executar APOS as ARs 239/240/241 ou adaptar stubs ao que estiver disponivel.

## Critérios de Aceite
AC-001: training-phase3.ts nao contem /ai-coach/ (prefixo errado).
AC-002: training-phase3.ts contem /ai/coach/ (prefixo correto).
AC-003: training-phase3.ts nao contem /training-sessions/${sessionId}/pre-confirm (URL errada sem /attendance/).
AC-004: comentarios JSDoc das funcoes listam os paths corretos do openapi.json.

## Write Scope
- Hb Track - Frontend/src/lib/api/training-phase3.ts

## Validation Command (Contrato)
```
python -c "import sys; c=open('Hb Track - Frontend/src/lib/api/training-phase3.ts',encoding='utf-8').read(); errs=[]; errs.append('FAIL AC-001: /ai-coach/ ainda presente') if '/ai-coach/' in c else None; errs.append('FAIL AC-003: /training-sessions/${sessionId}/pre-confirm ainda presente') if 'training-sessions/${sessionId}/pre-confirm' in c else None; print('FAIL:',errs) or sys.exit(1) if errs else print('PASS AC-001+003: URLs criticas corrigidas (AC-002/004 via inspeção manual)')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_242/executor_main.log`

## Rollback Plan (Contrato)
```
git checkout -- Hb Track - Frontend/src/lib/api/training-phase3.ts
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Riscos
- AR_242 depende de AR_240 para saber o path exato de apply e justify. Se AR_240 nao estiver verificado, usar paths provisorios e documentar no executor_main.log.
- Nenhum componente de producao chama training-phase3.ts ainda — risco de impacto em UI e zero.
- Verificar se athlete-training.ts (existente) tambem tem divergencias de URL para CONTRACT-096 e atualizar se necessario.

## Análise de Impacto

**Arquivos modificados:**
- `Hb Track - Frontend/src/lib/api/training-phase3.ts` — corrigir 4 paths divergentes

**Conferência post-AR_239/240/241 (openapi.json confirma nomes canônicos):**
- CONTRACT-097 pre-confirm: `/training-sessions/${sessionId}/pre-confirm` → `/attendance/sessions/${sessionId}/preconfirm`
- CONTRACT-101 ai draft session: `/ai-coach/draft-session` → `/ai/coach/suggest-session`
- CONTRACT-102 apply draft: `/ai-coach/draft-session/${draftId}/apply` → `/ai/coach/draft/${draftId}/apply` (AR_240 definiu path)
- CONTRACT-103 athlete chat: `/ai-coach/athlete-chat` → `/ai/chat`
- CONTRACT-104 justify: `/ai-coach/justify-suggestion` → `/ai/coach/justify-suggestion`

**Descartados (sem mudança necessária):**
- CONTRACT-098 close: `/training-sessions/${sessionId}/close` → URL já existe no backend
- CONTRACT-105 wellness-content-gate: `/athlete/wellness-content-gate/${sessionId}` → já correto

**Impacto produto:** Zero — nenhum componente chama training-phase3.ts em produção ainda (stubs).

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em a7ab568
**Status Executor**: ❌ FALHA
**Comando**: `python -c "import sys; c=open('Hb Track - Frontend/src/lib/api/training-phase3.ts',encoding='utf-8').read(); errs=[]; errs.append('FAIL AC-001: /ai-coach/ ainda presente') if '/ai-coach/' in c else None; errs.append('FAIL AC-003: /training-sessions/${sessionId}/pre-confirm ainda presente') if 'training-sessions/${sessionId}/pre-confirm' in c else None; print('FAIL:',errs) or sys.exit(1) if errs else print('PASS AC-001+003: URLs criticas corrigidas (AC-002/004 via inspeção manual)')"`
**Exit Code**: 1
**Timestamp UTC**: 2026-03-04T18:19:52.016124+00:00
**Behavior Hash**: 5cb06cb61999ef770ff05cea5228f7bcb5ac2d089616389432175525ab045e99
**Evidence File**: `docs/hbtrack/evidence/AR_242/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em a7ab568
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import sys; c=open('Hb Track - Frontend/src/lib/api/training-phase3.ts',encoding='utf-8').read(); errs=[]; errs.append('FAIL AC-001: /ai-coach/ ainda presente') if '/ai-coach/' in c else None; errs.append('FAIL AC-003: /training-sessions/${sessionId}/pre-confirm ainda presente') if 'training-sessions/${sessionId}/pre-confirm' in c else None; print('FAIL:',errs) or sys.exit(1) if errs else print('PASS AC-001+003: URLs criticas corrigidas (AC-002/004 via inspeção manual)')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-04T18:20:44.635712+00:00
**Behavior Hash**: b85fb327b85f096017110e39b252dedf9fdf7e05a0cc023fb06619c5ed4ad6df
**Evidence File**: `docs/hbtrack/evidence/AR_242/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em a7ab568
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_242_a7ab568/result.json`

### Selo Humano em a7ab568
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-03-04T18:39:01.252191+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_242_a7ab568/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_242/executor_main.log`
