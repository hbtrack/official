# AR_172 — Fix AttendanceTab.tsx: UI para status justified + reason_absence

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Atualizar src/components/training/attendance/AttendanceTab.tsx para suportar o status 'justified' no fluxo de registro de presencas.

=== FLUXO ESPERADO ===
Quando treinador registra presenca de atleta:
1. Status options: [Presente] [Ausente] [Justificado]
   ('preconfirm' nao e exposto para selecao manual -- e gerenciado automaticamente)
2. Se status = 'justified': exibir campo de texto/select para `reason_absence`
3. Se status = 'absent': reason_absence opcional (treinador pode ou nao informar)
4. Se status = 'present': reason_absence nao exibido/irrelevante

=== ANCORA: PresenceStatus expandido (Task 164) ===
PresenceStatus = 'present' | 'absent' | 'justified' | 'preconfirm'

=== MUDANCAS NA UI ===

1. Toggle/select de status: adicionar botao/opcao 'Justificado' ao lado de 'Presente' e 'Ausente'.
   Exemplo (se usa botoes tipo toggle):
   ```tsx
   <StatusToggle
     options={[
       { value: 'present', label: 'Presente' },
       { value: 'absent', label: 'Ausente' },
       { value: 'justified', label: 'Justificado' },
     ]}
     value={item.presence_status}
     onChange={(v) => handleStatusChange(item.athlete_id, v)}
   />
   ```

2. Campo reason_absence: exibir quando status = 'justified' (ou 'absent'):
   ```tsx
   {(item.presence_status === 'justified' || item.presence_status === 'absent') && (
     <input
       type="text"
       placeholder="Motivo da ausencia"
       value={item.reason_absence || ''}
       onChange={(e) => handleReasonChange(item.athlete_id, e.target.value)}
     />
   )}
   ```

3. Estado local: garantir que o objeto de edicao de presenca inclui `reason_absence` no tipo.

4. Payload para batchRecordAttendance: incluir `reason_absence` quando preenchido.

5. Exibicao de presencas existentes: se attendance existente tem `presence_status = 'justified'`, exibir badge/tag 'Justificado' (nao apenas 'Ausente').

=== GARANTIR: nenhum athlete_id de atleta no payload ===
DEC-TRAIN-001: o payload ja inclui athlete_id dos atletas DA SESSAO (correto -- e o ID do atleta sendo registrado, nao o do usuario logado). Manter comportamento.

ARQUIVOS A MODIFICAR:
- Hb Track - Frontend/src/components/training/attendance/AttendanceTab.tsx

## Critérios de Aceite
1) UI exibe opcao 'Justificado' como status de presenca selecionavel.
2) Campo reason_absence aparece quando status = 'justified' ou 'absent'.
3) Componente compila sem erros TypeScript.
4) Attendance existente com status 'justified' exibida com label correto (nao 'Ausente' ou valor tecnico).
5) Payload de batchRecordAttendance inclui reason_absence quando preenchido.

## Write Scope
- Hb Track - Frontend/src/components/training/attendance/AttendanceTab.tsx

## Validation Command (Contrato)
```
cd "Hb Track - Frontend" && python -c "import sys; c=open('src/components/training/attendance/AttendanceTab.tsx', encoding='utf-8').read(); checks=[('justified' in c, 'justified status in UI'), ('reason_absence' in c, 'reason_absence field in component'), ('Justificado' in c, 'label Justificado in UI text')]; failed=[msg for ok,msg in checks if not ok]; print('PASS: AttendanceTab justified support checks OK') if not failed else sys.exit('FAIL: '+str(failed))" && npx tsc --noEmit --skipLibCheck 2>&1 | python -c "import sys; lines=sys.stdin.read(); errs=[l for l in lines.splitlines() if 'AttendanceTab' in l and 'error TS' in l]; print('PASS: AttendanceTab tsc ok') if not errs else sys.exit('FAIL tsc: '+chr(10).join(errs[:5]))"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_172/executor_main.log`

## Notas do Arquiteto
Esta task depende da Task 164. ANCORA: schema.sql ck_attendance_status. 'preconfirm' nao exposto na UI manual mas deve ser exibido corretamente se carregado do servidor (badge 'Pre-confirmado').

## Riscos
- Se AttendanceTab usa um componente de status fixo que nao aceita extensao, pode necessitar refactor do componente inner -- Executor avalia e adapta UX coerentemente
- reason_absence pode ja estar no tipo AttendanceInput mas nao no estado local -- Executor verificar e alinhar
- Se attendance.ts tinha ReasonAbsence como enum separado, verificar que o input de reason_absence aceita texto livre OU enum -- usar string por ora

## Análise de Impacto
- Escopo: `Hb Track - Frontend/src/components/training/attendance/AttendanceTab.tsx` (único arquivo).
- Mudança: UI suporta status `'justified'` com label 'Justificado' e campo `reason_absence` condicional.
- Depende de AR_171 (PresenceStatus expandido) — já implementado.
- Risco DB: zero.
- Risco UX: baixo — mudança aditiva, fluxo existente `'present'/'absent'` inalterado.
- Estado verificado: `justified`, `reason_absence` e `Justificado` já presentes no arquivo (OK pré-validado).

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em 07760d4
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `cd "Hb Track - Frontend" && python -c "import sys; c=open('src/components/training/attendance/AttendanceTab.tsx', encoding='utf-8').read(); checks=[('justified' in c, 'justified status in UI'), ('reason_absence' in c, 'reason_absence field in component'), ('Justificado' in c, 'label Justificado in UI text')]; failed=[msg for ok,msg in checks if not ok]; print('PASS: AttendanceTab justified support checks OK') if not failed else sys.exit('FAIL: '+str(failed))" && npx tsc --noEmit --skipLibCheck 2>&1 | python -c "import sys; lines=sys.stdin.read(); errs=[l for l in lines.splitlines() if 'AttendanceTab' in l and 'error TS' in l]; print('PASS: AttendanceTab tsc ok') if not errs else sys.exit('FAIL tsc: '+chr(10).join(errs[:5]))"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-28T10:06:44.242197+00:00
**Behavior Hash**: 2e4fa785242e7f9130a1e7b475f2e742ef5f9bc1f4f96cc3d33f58a371a42cad
**Evidence File**: `docs/hbtrack/evidence/AR_172/executor_main.log`
**Python Version**: 3.11.9

### Selo Humano em 07760d4
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-02-28T10:32:27.844604+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_172_07760d4/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_172/executor_main.log`

### Verificacao Testador em 07760d4
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_172_07760d4/result.json`

### Selo Humano em 07760d4
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-02-28T17:32:47.680706+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_172_07760d4/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_172/executor_main.log`
