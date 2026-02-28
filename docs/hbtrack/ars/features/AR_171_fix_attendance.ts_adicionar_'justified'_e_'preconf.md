# AR_171 — Fix attendance.ts: adicionar 'justified' e 'preconfirm' ao PresenceStatus

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Corrigir src/lib/api/attendance.ts: expandir type PresenceStatus para incluir todos os valores do enum DB.

=== ANCORA: schema.sql ===
Constraint `ck_attendance_status`:
  CHECK (presence_status IN ('present', 'absent', 'justified', 'preconfirm'))

=== CORRECAO NECESSARIA ===
Atual:
```typescript
export type PresenceStatus = 'present' | 'absent';
```

Corrigir para:
```typescript
export type PresenceStatus = 'present' | 'absent' | 'justified' | 'preconfirm';
```

=== VERIFICAR: reason_absence em AttendanceInput ===
AttendanceInput deve ter campo reason_absence opcional (para quando status = 'justified').
Se nao existir, adicionar:
```typescript
export interface AttendanceInput {
  athlete_id: string;          // UUID do atleta
  presence_status: PresenceStatus;
  reason_absence?: string;     // obrigatorio logicamente quando justified, opcional no tipo
  arrival_time?: string;       // ISO time quando presente com atraso
  notes?: string;
}
```
Se ja tiver reason_absence, apenas verificar que o tipo nao foi omitido.

=== ARQUIVOS A MODIFICAR ===
- Hb Track - Frontend/src/lib/api/attendance.ts (UNICO arquivo desta task)

## Critérios de Aceite
1) PresenceStatus inclui 'justified' e 'preconfirm' alem de 'present' e 'absent'.
2) AttendanceInput tem reason_absence?: string.
3) TypeScript compila sem erros em attendance.ts.

## Write Scope
- Hb Track - Frontend/src/lib/api/attendance.ts

## Validation Command (Contrato)
```
cd "Hb Track - Frontend" && python -c "import sys; c=open('src/lib/api/attendance.ts', encoding='utf-8').read(); checks=[('justified' in c, 'justified in PresenceStatus'), ('preconfirm' in c, 'preconfirm in PresenceStatus'), ('reason_absence' in c, 'reason_absence in AttendanceInput')]; failed=[msg for ok,msg in checks if not ok]; print('PASS: attendance.ts type checks OK') if not failed else sys.exit('FAIL: '+str(failed))" && npx tsc --noEmit --skipLibCheck 2>&1 | python -c "import sys; lines=sys.stdin.read(); errs=[l for l in lines.splitlines() if 'attendance.ts' in l and 'error TS' in l]; print('PASS: attendance.ts tsc ok') if not errs else sys.exit('FAIL tsc: '+chr(10).join(errs[:5]))"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_171/executor_main.log`

## Notas do Arquiteto
ANCORA: schema.sql constraint ck_attendance_status. Task 165 (AttendanceTab.tsx) depende desta task.

## Riscos
- Componentes que fazem switch/if sobre PresenceStatus podem gerar TS warnings sobre cases nao cobertos (strict exhaustive check) -- Executor trata em Task 165
- Tests E2E que usam PresenceStatus = 'present' | 'absent' como type literal podem precisar de atualizacao -- Executor verificar em tests/

## Análise de Impacto
- Escopo: `Hb Track - Frontend/src/lib/api/attendance.ts` (único arquivo).
- Mudança: expansão do type `PresenceStatus` para incluir `'justified'` e `'preconfirm'`, alinhado ao constraint `ck_attendance_status` do schema.
- Adição de campo `reason_absence?: string` no interface `AttendanceInput`.
- Risco DB: zero (mudança apenas em tipos TypeScript de frontend).
- Risco regressão: baixo — adds são aditivos; nenhum caso existente de `'present'/'absent'` é afetado.
- Estado verificado: `justified`, `preconfirm` e `reason_absence` já presentes no arquivo (OK pré-validado).

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em 07760d4
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `cd "Hb Track - Frontend" && python -c "import sys; c=open('src/lib/api/attendance.ts', encoding='utf-8').read(); checks=[('justified' in c, 'justified in PresenceStatus'), ('preconfirm' in c, 'preconfirm in PresenceStatus'), ('reason_absence' in c, 'reason_absence in AttendanceInput')]; failed=[msg for ok,msg in checks if not ok]; print('PASS: attendance.ts type checks OK') if not failed else sys.exit('FAIL: '+str(failed))" && npx tsc --noEmit --skipLibCheck 2>&1 | python -c "import sys; lines=sys.stdin.read(); errs=[l for l in lines.splitlines() if 'attendance.ts' in l and 'error TS' in l]; print('PASS: attendance.ts tsc ok') if not errs else sys.exit('FAIL tsc: '+chr(10).join(errs[:5]))"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-28T10:06:23.682673+00:00
**Behavior Hash**: 5257c66fb8175f85d3501996387b06a01c283fefdb7f03d4e24585758246a2d1
**Evidence File**: `docs/hbtrack/evidence/AR_171/executor_main.log`
**Python Version**: 3.11.9

### Selo Humano em 07760d4
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-02-28T10:31:15.313051+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_171_07760d4/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_171/executor_main.log`

### Verificacao Testador em 07760d4
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_171_07760d4/result.json`

### Selo Humano em 07760d4
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-02-28T17:32:47.342790+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_171_07760d4/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_171/executor_main.log`
