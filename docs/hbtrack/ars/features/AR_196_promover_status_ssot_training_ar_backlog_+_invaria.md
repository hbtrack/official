# AR_196 — Promover status SSOT Training: AR_BACKLOG + INVARIANTS + CONTRACT + SCREENS + FLOWS

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Classe G (Governanca documental). NAO altera codigo. Editar 6 arquivos SSOT do modulo TRAINING para refletir VERIFICADO/IMPLEMENTADO/EVIDENCIADO onde evidencia Kanban+logs existe. INSTRUCOES POR ARQUIVO:

(1) AR_BACKLOG_TRAINING.md: para cada AR-TRAIN-001,002,003,004,005,006,007,008,009,010A,010B,011,012,013,014,015,016,017,018,019,020,021 que tenha '**Status:** PENDENTE', substituir por '**Status:** VERIFICADO (YYYY-MM-DD)' usando a data de hb seal do Kanban: AR-TRAIN-001..009 + 010A = 2026-02-28; AR-TRAIN-010B..021 = 2026-03-01. Adicionar '> Promovido por Kanban+evidencia: AR_### (hb seal YYYY-MM-DD), paths: docs/hbtrack/evidence/AR_###/executor_main.log' logo abaixo do Status.

(2) INVARIANTS_TRAINING.md: localizar INV-TRAIN-040 e INV-TRAIN-041. Para cada um, alterar 'status: PARCIAL' para 'status: IMPLEMENTADO'. Atualizar ou adicionar o campo 'note:' com: 'Promovido por Kanban+evidencia: AR_173 (hb seal 2026-02-28), paths: docs/hbtrack/evidence/AR_173/executor_main.log'. Nao alterar nenhum outro campo.

(3) TRAINING_FRONT_BACK_CONTRACT.md: localizar CONTRACT-TRAIN-091, 092, 093, 094, 095 (GAP) e alterar o status na coluna da tabela de 'GAP' para 'IMPLEMENTADO'. Localizar CONTRACT-TRAIN-096, 097, 098, 099, 100, 105 (GAP) e alterar para 'IMPLEMENTADO'. Localizar CONTRACT-TRAIN-101, 102, 103, 104 (GAP) e alterar para 'IMPLEMENTADO'. Adicionar nota no rodape de cada subsecao: '> Promovido por Kanban+evidencia: AR_### (hb seal YYYY-MM-DD)'. Referencias: CONTRACT-091..095 cobertos por AR_183; CONTRACT-096..100/105 por AR_185 e AR_187; CONTRACT-101..104 por AR_192.

(4) TRAINING_SCREENS_SPEC.md: localizar SCREEN-TRAIN-013. Alterar '**Estado AS-IS:** BLOQUEADO (endpoints nao incluidos no agregador)' para '**Estado AS-IS:** EVIDENCIADO'. Adicionar nota: '> Promovido por Kanban+evidencia: AR_180 (hb seal 2026-02-28), paths: docs/hbtrack/evidence/AR_180/executor_main.log'. Tambem atualizar a entrada da tabela geral de SCREEN-TRAIN-013 na coluna Estado de 'BLOQUEADO' para 'EVIDENCIADO'.

(5) TRAINING_USER_FLOWS.md: localizar FLOW-TRAIN-004 (PARCIAL), FLOW-TRAIN-005 (PARCIAL), FLOW-TRAIN-006 (PARCIAL), FLOW-TRAIN-007 (PARCIAL), FLOW-TRAIN-012 (BLOQUEADO), FLOW-TRAIN-013 (PARCIAL). Alterar 'estado_asis: PARCIAL' e 'estado_asis: BLOQUEADO' para 'estado_asis: EVIDENCIADO' onde aplicavel. Atualizar linha na tabela de sumario de flows. Adicionar em cada flow alterado: '> Promovido por Kanban+evidencia: AR_### (hb seal YYYY-MM-DD)'. Referencias: FLOW-004 por AR_185; FLOW-005/006 por AR_187; FLOW-007 por AR_177/178; FLOW-012 por AR_179/180; FLOW-013 por AR_177/178.

(6) TEST_MATRIX_TRAINING.md: verificar apenas se ha itens criticos em GAP/PENDENTE nao cobertos. Se versao vier de AR_195 (v1.5.1) e todos os itens de §9 ja estiverem VERIFICADO, NAO alterar. Se houver gap residual menor (ex.: linha de AR-TRAIN marcada PENDENTE mas ja executada), corrigir com delta minimo e nota de rastreabilidade.

## Critérios de Aceite
AC-001: AR_BACKLOG_TRAINING.md nao contem 'Status: PENDENTE' para AR-TRAIN-001..021 (todos promovidos). AC-002: INVARIANTS_TRAINING.md nao contem 'status: PARCIAL' para INV-TRAIN-040 nem INV-TRAIN-041. AC-003: TRAINING_SCREENS_SPEC.md nao contem 'BLOQUEADO' perto de SCREEN-TRAIN-013 (Estado AS-IS). AC-004: TRAINING_FRONT_BACK_CONTRACT.md nao contem '| GAP |' para CONTRACT-TRAIN-091..095 nem 096..105. AC-005: Todos os 6 arquivos alterados contem pelo menos 1 nota 'Promovido por Kanban+evidencia'. AC-006: TEST_MATRIX_TRAINING.md: versao v1.5.1 ou superior preservada (nao regredir sem nota).

## Write Scope
- docs/hbtrack/modulos/treinos/AR_BACKLOG_TRAINING.md
- docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md
- docs/hbtrack/modulos/treinos/TRAINING_FRONT_BACK_CONTRACT.md
- docs/hbtrack/modulos/treinos/TRAINING_SCREENS_SPEC.md
- docs/hbtrack/modulos/treinos/TRAINING_USER_FLOWS.md
- docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md

## Validation Command (Contrato)
```
python -c "import re,sys;e=[];b=open('docs/hbtrack/modulos/treinos/AR_BACKLOG_TRAINING.md',encoding='utf-8').read();n_pend=len(re.findall(r'AR-TRAIN-0[12][0-9].*PENDENTE',b));e+=[f'FAIL backlog still has {n_pend} PENDENTE AR-TRAINs'] if n_pend>0 else [None];inv=open('docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md',encoding='utf-8').read();seg40=inv[inv.index('INV-TRAIN-040'):inv.index('INV-TRAIN-040')+300] if 'INV-TRAIN-040' in inv else '';seg41=inv[inv.index('INV-TRAIN-041'):inv.index('INV-TRAIN-041')+300] if 'INV-TRAIN-041' in inv else '';e+=['FAIL INV-040 still PARCIAL'] if 'PARCIAL' in seg40 else [None];e+=['FAIL INV-041 still PARCIAL'] if 'PARCIAL' in seg41 else [None];sc=open('docs/hbtrack/modulos/treinos/TRAINING_SCREENS_SPEC.md',encoding='utf-8').read();seg13=sc[sc.index('SCREEN-TRAIN-013'):sc.index('SCREEN-TRAIN-013')+400] if 'SCREEN-TRAIN-013' in sc else '';e+=['FAIL SCREEN-013 still BLOQUEADO'] if 'BLOQUEADO' in seg13 else [None];ct=open('docs/hbtrack/modulos/treinos/TRAINING_FRONT_BACK_CONTRACT.md',encoding='utf-8').read();g91=len(re.findall(r'CONTRACT-TRAIN-09[1-5].*GAP',ct));e+=[f'FAIL CONTRACT-091..095 GAP={g91}'] if g91>0 else [None];errs=[x for x in e if x];[print(x) for x in errs];print('PASS: all AC checks ok') if not errs else None;sys.exit(len(errs))"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_196/executor_main.log`

## Notas do Arquiteto
Classe G pura. Nenhum arquivo de Backend/Frontend deve ser alterado. Toda a escrita fica em docs/hbtrack/modulos/treinos/. AR_BACKLOG note: os 9 itens ja marcados 'RESOLVIDA' sao anteriores ao batch TRAINING e devem ser mantidos como estao.

## Riscos
- AR_BACKLOG: verificar linha a linha — para AR-TRAIN-003 (status pode ja ser RESOLVIDA), AR-TRAIN-005 (nao implementado como AR separada — verificar no Kanban se ha AR). Nao inventar AR-ID nao existente no Kanban.
- CONTRACT.md: alteracoes em tabela markdown — risco de quebrar formatacao. Alterar somente a coluna de status (GAP -> IMPLEMENTADO); nao mexer nas outras colunas.
- TRAINING_USER_FLOWS.md: arquivo tem dois formatos de status — tabela de sumario (linha `| FLOW-TRAIN-NNN | ... | PARCIAL |`) e bloco yaml (`estado_asis: PARCIAL`). Alterar ambos para consistencia.
- TEST_MATRIX_TRAINING.md: em v1.5.1 ja. Se houver qualquer linha de AR-TRAIN ainda como PENDENTE apos AR_193/195, corrigir; mas preservar o changelog e nao regredir a versao.
- AR-TRAIN-005 (presenças UI justified): nao foi implementada como AR separada — verificar no Kanban qual AR cobriu esse escopo parcial antes de marcar como VERIFICADO no backlog.

## Análise de Impacto

**Executor**: Codex/Copilot | **Data**: 2026-03-01

**Arquivos modificados** (somente docs/hbtrack — sem Backend/Frontend):
1. `docs/hbtrack/modulos/treinos/AR_BACKLOG_TRAINING.md` — 22 itens PENDENTE → VERIFICADO (AR-TRAIN-001..021 + 010A/010B)
2. `docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md` — INV-TRAIN-040 e INV-TRAIN-041: PARCIAL → IMPLEMENTADO
3. `docs/hbtrack/modulos/treinos/TRAINING_FRONT_BACK_CONTRACT.md` — 14 contratos: CONTRACT-TRAIN-091..095 + 096..100 + 101..104 + 105: GAP → IMPLEMENTADO
4. `docs/hbtrack/modulos/treinos/TRAINING_SCREENS_SPEC.md` — SCREEN-TRAIN-013: BLOQUEADO → EVIDENCIADO (tabela + seção)
5. `docs/hbtrack/modulos/treinos/TRAINING_USER_FLOWS.md` — 6 flows: FLOW-004/005/006/007/012/013 (tabela sumário + blocos yaml)
6. `docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md` — Verificação: v1.5.1 preservada (AR_195 já atualizou), sem gaps residuais críticos identificados

**Impacto zero em**: Backend, Frontend, scripts runtime, DB, migrações.

**Rastreabilidade por grupo**:
- AR-TRAIN-001 → AR_126 (s11, executado)
- AR-TRAIN-002 → AR_175 (s12, hb seal 2026-02-28)
- AR-TRAIN-003 → AR_169 (s11, hb seal 2026-02-28)
- AR-TRAIN-004 → AR_176 (s12, hb seal 2026-02-28)
- AR-TRAIN-005 → AR_171 (s11, hb seal 2026-02-28)
- AR-TRAIN-006 → AR_177 (s13, hb seal 2026-02-28)
- AR-TRAIN-007 → AR_178 (s13, hb seal 2026-02-28)
- AR-TRAIN-008 → AR_179 (s13, hb seal 2026-02-28)
- AR-TRAIN-009 → AR_180 (s13, hb seal 2026-02-28)
- AR-TRAIN-010A → AR_173 (s11, hb seal 2026-02-28)
- AR-TRAIN-010B → AR_195 (s19, hb seal 2026-03-01)
- AR-TRAIN-011 → AR_181 (s14, hb seal 2026-03-01)
- AR-TRAIN-012 → AR_182 (s14, hb seal 2026-03-01)
- AR-TRAIN-013 → AR_183 (s14, hb seal 2026-03-01)
- AR-TRAIN-014 → AR_184 (s14, hb seal 2026-03-01)
- AR-TRAIN-015 → AR_189 (s16, hb seal 2026-03-01)
- AR-TRAIN-016 → AR_190 (s16, hb seal 2026-03-01)
- AR-TRAIN-017 → AR_185 (s15, hb seal 2026-03-01)
- AR-TRAIN-018 → AR_186 (s15, hb seal 2026-03-01)
- AR-TRAIN-019 → AR_187 (s15, hb seal 2026-03-01)
- AR-TRAIN-020 → AR_191 (s16, hb seal 2026-03-01)
- AR-TRAIN-021 → AR_192 (s16, hb seal 2026-03-01)

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em b123a58
**Status Executor**: ❌ FALHA
**Comando**: `python -c "import re,sys;e=[];b=open('docs/hbtrack/modulos/treinos/AR_BACKLOG_TRAINING.md',encoding='utf-8').read();n_pend=len(re.findall(r'AR-TRAIN-0[12][0-9].*PENDENTE',b));e+=[f'FAIL backlog still has {n_pend} PENDENTE AR-TRAINs'] if n_pend>0 else [None];inv=open('docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md',encoding='utf-8').read();seg40=inv[inv.index('INV-TRAIN-040'):inv.index('INV-TRAIN-040')+300] if 'INV-TRAIN-040' in inv else '';seg41=inv[inv.index('INV-TRAIN-041'):inv.index('INV-TRAIN-041')+300] if 'INV-TRAIN-041' in inv else '';e+=['FAIL INV-040 still PARCIAL'] if 'PARCIAL' in seg40 else [None];e+=['FAIL INV-041 still PARCIAL'] if 'PARCIAL' in seg41 else [None];sc=open('docs/hbtrack/modulos/treinos/TRAINING_SCREENS_SPEC.md',encoding='utf-8').read();seg13=sc[sc.index('SCREEN-TRAIN-013'):sc.index('SCREEN-TRAIN-013')+400] if 'SCREEN-TRAIN-013' in sc else '';e+=['FAIL SCREEN-013 still BLOQUEADO'] if 'BLOQUEADO' in seg13 else [None];ct=open('docs/hbtrack/modulos/treinos/TRAINING_FRONT_BACK_CONTRACT.md',encoding='utf-8').read();g91=len(re.findall(r'CONTRACT-TRAIN-09[1-5].*GAP',ct));e+=[f'FAIL CONTRACT-091..095 GAP={g91}'] if g91>0 else [None];errs=[x for x in e if x];[print(x) for x in errs];print('PASS: all AC checks ok') if not errs else None;sys.exit(len(errs))"`
**Exit Code**: 1
**Timestamp UTC**: 2026-03-02T00:54:57.635961+00:00
**Behavior Hash**: fe5ac995582ab4cd77aec523c13da06cda67256fd5b1e8cb7229c014debf2af3
**Evidence File**: `docs/hbtrack/evidence/AR_196/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em b123a58
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import re,sys;e=[];b=open('docs/hbtrack/modulos/treinos/AR_BACKLOG_TRAINING.md',encoding='utf-8').read();n_pend=len(re.findall(r'AR-TRAIN-0[12][0-9].*PENDENTE',b));e+=[f'FAIL backlog still has {n_pend} PENDENTE AR-TRAINs'] if n_pend>0 else [None];inv=open('docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md',encoding='utf-8').read();seg40=inv[inv.index('INV-TRAIN-040'):inv.index('INV-TRAIN-040')+300] if 'INV-TRAIN-040' in inv else '';seg41=inv[inv.index('INV-TRAIN-041'):inv.index('INV-TRAIN-041')+300] if 'INV-TRAIN-041' in inv else '';e+=['FAIL INV-040 still PARCIAL'] if 'PARCIAL' in seg40 else [None];e+=['FAIL INV-041 still PARCIAL'] if 'PARCIAL' in seg41 else [None];sc=open('docs/hbtrack/modulos/treinos/TRAINING_SCREENS_SPEC.md',encoding='utf-8').read();seg13=sc[sc.index('SCREEN-TRAIN-013'):sc.index('SCREEN-TRAIN-013')+400] if 'SCREEN-TRAIN-013' in sc else '';e+=['FAIL SCREEN-013 still BLOQUEADO'] if 'BLOQUEADO' in seg13 else [None];ct=open('docs/hbtrack/modulos/treinos/TRAINING_FRONT_BACK_CONTRACT.md',encoding='utf-8').read();g91=len(re.findall(r'CONTRACT-TRAIN-09[1-5].*GAP',ct));e+=[f'FAIL CONTRACT-091..095 GAP={g91}'] if g91>0 else [None];errs=[x for x in e if x];[print(x) for x in errs];print('PASS: all AC checks ok') if not errs else None;sys.exit(len(errs))"`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-02T00:57:07.281697+00:00
**Behavior Hash**: 2ecd5b6ad4bf18d429393cb1bed1555f7ac76f2d8fb1e107034ed99fa4fc0608
**Evidence File**: `docs/hbtrack/evidence/AR_196/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em b123a58
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_196_b123a58/result.json`

### Selo Humano em b123a58
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-03-02T01:39:22.849307+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_196_b123a58/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_196/executor_main.log`
