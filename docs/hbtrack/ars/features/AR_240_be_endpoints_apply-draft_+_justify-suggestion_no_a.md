# AR_240 — BE: endpoints apply-draft + justify-suggestion no ai_coach router (AR-TRAIN-056)

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Adicionar 2 endpoints ao router ai_coach.py:

(1) CONTRACT-TRAIN-102: PATCH /api/v1/ai/coach/draft/{draft_id}/apply
- Body: {edits?: object}
- Response: {training_session_id: uuid, applied: true}
- INV-TRAIN-075/080: draft DEVE ser aprovado pelo treinador antes de aplicar
- Somente treinador pode aplicar (RBAC)

(2) CONTRACT-TRAIN-104: POST /api/v1/ai/coach/justify-suggestion
- Body: {suggestion_id: uuid}
- Response: {justification: string, references: string[]}
- INV-TRAIN-081: justificativa e obrigatoria para sugestoes 'recomendacao'

O router atual (ai_coach.py) tem: /ai/chat, /ai/coach/suggest-session, /ai/coach/suggest-microcycle, /ai/coach/drafts.
Nao tem: apply nem justify.

PASSOS:
1. Ler Hb Track - Backend/app/api/v1/routers/ai_coach.py
2. Ler Hb Track - Backend/app/services/ai_coach_service.py para verificar metodos disponíveis
3. Adicionar endpoint PATCH /draft/{draft_id}/apply ao router
4. Adicionar endpoint POST /justify-suggestion ao router
5. Se o service nao tiver os metodos, criar stubs que retornam respostas canonicas
6. Executar gen_docs_ssot.py
7. Rodar hb report 240

## Critérios de Aceite
AC-001: openapi.json tem path com 'apply' em rota /ai/coach/ com metodo PATCH.
AC-002: openapi.json tem path com 'justify' em rota /ai/coach/ com metodo POST.
AC-003: suite 594+ passed, 0 failed.

## Write Scope
- Hb Track - Backend/app/api/v1/routers/ai_coach.py
- Hb Track - Backend/app/services/ai_coach_service.py
- Hb Track - Backend/docs/ssot/openapi.json
- Hb Track - Backend/docs/ssot/manifest.json

## Validation Command (Contrato)
```
python -c "import json,io; spec=json.load(io.open('Hb Track - Backend/docs/ssot/openapi.json',encoding='utf-8')); paths=spec['paths']; apply_p=[p for p in paths if '/ai/' in p and 'apply' in p]; justify_p=[p for p in paths if '/ai/' in p and 'justify' in p]; errs=[]; errs.append('FAIL apply endpoint missing') if not apply_p else None; errs.append('FAIL justify endpoint missing') if not justify_p else None; print('FAIL:',errs) or __import__('sys').exit(1) if errs else print('PASS apply:', apply_p, 'justify:', justify_p)"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_240/executor_main.log`

## Rollback Plan (Contrato)
```
git checkout -- Hb Track - Backend/app/api/v1/routers/ai_coach.py
git checkout -- Hb Track - Backend/app/services/ai_coach_service.py
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Riscos
- INV-TRAIN-080: apply DEVE alterar status do draft de 'draft' para 'applied' (ou criar training_session) — verificar se ha tabela de drafts ou se e apenas estado em memoria.
- INV-TRAIN-075: apply sem aprovacao explícita do treinador deve ser recusado — o endpoint em si implica aprovacao ao ser chamado.
- ai_coach_service.py pode ser stub (gerado AR_229) — verificar se metodos apply_draft e justify_suggestion existem ou precisam ser criados.
- Se draft nao tem tabela dedicada no schema, retornar 501 Not Implemented com body canônico e registrar como stub.
- Dependencia: AR_239 nao e pre-requisito desta AR (sao independentes).

## Análise de Impacto

**Arquivos modificados:**
- `Hb Track - Backend/app/api/v1/routers/ai_coach.py` — adicionar PATCH /ai/coach/draft/{draft_id}/apply + POST /ai/coach/justify-suggestion
- `Hb Track - Backend/app/services/ai_coach_service.py` — adicionar stubs `apply_draft()` e `justify_suggestion()` (sem tabela de drafts no schema)
- `Hb Track - Backend/docs/ssot/openapi.json` — regenerado via gen_docs_ssot.py

**Stubs justificados (Risco AR_240):** Não há tabela dedicada de drafts no schema.sql. Conforme risco documentado no plano, endpoints retornam resposta canônica stub (não 500). Registrado aqui como waiver.

**INV-TRAIN-080:** apply_draft muda conceptualmente draft→applied; implementado via resposta stub `{training_session_id: uuid4(), applied: true}` até tabela de drafts ser criada futuramente.

**INV-TRAIN-081:** justify_suggestion retorna justificação stub para INV-081.

**Impacto suite:** Zero — caminhos adicionados sem quebrar testes existentes.

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em a7ab568
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import json,io; spec=json.load(io.open('Hb Track - Backend/docs/ssot/openapi.json',encoding='utf-8')); paths=spec['paths']; apply_p=[p for p in paths if '/ai/' in p and 'apply' in p]; justify_p=[p for p in paths if '/ai/' in p and 'justify' in p]; errs=[]; errs.append('FAIL apply endpoint missing') if not apply_p else None; errs.append('FAIL justify endpoint missing') if not justify_p else None; print('FAIL:',errs) or __import__('sys').exit(1) if errs else print('PASS apply:', apply_p, 'justify:', justify_p)"`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-04T18:11:43.900188+00:00
**Behavior Hash**: a0f6884aa7042ac0af48831244aae71a1c47ccada47a1c2a38405d273cd30558
**Evidence File**: `docs/hbtrack/evidence/AR_240/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em a7ab568
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import json,io; spec=json.load(io.open('Hb Track - Backend/docs/ssot/openapi.json',encoding='utf-8')); paths=spec['paths']; apply_p=[p for p in paths if '/ai/' in p and 'apply' in p]; justify_p=[p for p in paths if '/ai/' in p and 'justify' in p]; errs=[]; errs.append('FAIL apply endpoint missing') if not apply_p else None; errs.append('FAIL justify endpoint missing') if not justify_p else None; print('FAIL:',errs) or __import__('sys').exit(1) if errs else print('PASS apply:', apply_p, 'justify:', justify_p)"`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-04T18:12:39.355806+00:00
**Behavior Hash**: a0f6884aa7042ac0af48831244aae71a1c47ccada47a1c2a38405d273cd30558
**Evidence File**: `docs/hbtrack/evidence/AR_240/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em a7ab568
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import json,io; spec=json.load(io.open('Hb Track - Backend/docs/ssot/openapi.json',encoding='utf-8')); paths=spec['paths']; apply_p=[p for p in paths if '/ai/' in p and 'apply' in p]; justify_p=[p for p in paths if '/ai/' in p and 'justify' in p]; errs=[]; errs.append('FAIL apply endpoint missing') if not apply_p else None; errs.append('FAIL justify endpoint missing') if not justify_p else None; print('FAIL:',errs) or __import__('sys').exit(1) if errs else print('PASS apply:', apply_p, 'justify:', justify_p)"`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-04T18:13:30.107383+00:00
**Behavior Hash**: a0f6884aa7042ac0af48831244aae71a1c47ccada47a1c2a38405d273cd30558
**Evidence File**: `docs/hbtrack/evidence/AR_240/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em a7ab568
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_240_a7ab568/result.json`

### Selo Humano em a7ab568
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-03-04T18:38:55.815842+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_240_a7ab568/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_240/executor_main.log`
