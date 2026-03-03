# AR_192 — IA Coach: INV-079/080/081 + router + FE ai-chat + AICoachDraftModal

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Implementar em quatro arquivos: (1) Hb Track - Backend/app/services/ai_coach_service.py (COMPLETAR) — Adicionar: (a) INV-079: privacy filter no módulo de reconhecimento — ao gerar mensagem de reconhecimento (elogio de consistência/participação), filtrar qualquer conteúdo de conversa íntima; usar apenas métricas agregadas (taxa de resposta, frequência). (b) INV-080: draft-only guard para propostas de sessão/microciclo do treinador — toda sessão/microciclo sugerido pela IA é criado com status='draft' e source='ai_coach_suggestion'; nunca publicar/agendar automaticamente. Método: generate_session_suggestion(coach_id, context) → TrainingSessionDraft; generate_microcycle_suggestion(coach_id, context) → MicrocycleDraft. (c) INV-081: justification enforcer — validar que toda sugestão retornada tem campo 'justification' não-vazio com texto baseado em sinais do sistema (wellness, carga, consistência, objetivo do microciclo); se justification ausente, classificar como 'ideia_generica' com label distinto. (2) Hb Track - Backend/app/api/v1/routers/ai_coach.py (CRIAR) — Endpoints REST para chat e sugestões. Endpoints mínimos: POST /ai/chat (atleta ou treinador envia mensagem; retorna resposta IA com guards de privacidade); POST /ai/coach/suggest-session (treinador pede sugestão de sessão; retorna draft); POST /ai/coach/suggest-microcycle (treinador pede sugestão de microciclo; retorna draft); GET /ai/coach/drafts (lista drafts pendentes para revisão do treinador). Registrar em Hb Track - Backend/app/api/v1/api.py. (3) Hb Track - Frontend/src/app/(athlete)/ai-chat/[sessionId]/page.tsx (CRIAR) — SCREEN-TRAIN-024: interface conversacional do atleta com IA Coach pós-treino. Usa CONTRACT-TRAIN-101..104 para tipagem. Props: sessionId (route param). Exibe: histórico de conversa, caixa de input, sugestões da IA com badges 'Rascunho' quando aplicável. (4) Hb Track - Frontend/src/components/training/AICoachDraftModal.tsx (CRIAR) — SCREEN-TRAIN-025: modal de revisão de draft gerado pela IA para o treinador. Props: draft (TrainingSessionDraft | MicycleDraft), onApprove, onReject, onEdit. Exibe: detalhe do draft, justificativa da IA (obrigatório — INV-081), botões Aprovar/Editar/Rejeitar. Badge 'Aprovação Necessária' visível. PROIBIDO: IA não autodispara sessão; não remover guards INV-072..075 existentes.

## Critérios de Aceite
1) ai_coach_service.py tem INV-079 privacy filter (reconhecimento usa só métricas, não texto íntimo). 2) ai_coach_service.py tem INV-080 draft-only guard (generate_session_suggestion retorna status=draft). 3) ai_coach_service.py tem INV-081 justification enforcer (sugestão sem justification → label ideia_generica). 4) ai_coach.py router existe com endpoint POST /ai/chat e POST /ai/coach/suggest-session. 5) Router registrado em api.py. 6) FE page.tsx ai-chat existe em src/app/(athlete)/ai-chat/[sessionId]/. 7) AICoachDraftModal.tsx existe em src/components/training/ e exibe justificativa da IA. 8) Guards INV-072..075 originais preservados (não removidos nem quebrados).

## Write Scope
- Hb Track - Backend/app/services/ai_coach_service.py
- Hb Track - Backend/app/api/v1/routers/ai_coach.py
- Hb Track - Backend/app/api/v1/api.py
- Hb Track - Frontend/src/app/athlete/ai-chat/*
- Hb Track - Frontend/src/components/training/AICoachDraftModal.tsx

## Validation Command (Contrato)
```
python -c "import os; b='Hb Track - Backend'; fe='Hb Track - Frontend'; svc=open(os.path.join(b,'app','services','ai_coach_service.py')).read(); assert 'draft' in svc.lower(), 'ai_coach_service missing draft guard (INV-080)'; assert 'justif' in svc.lower(), 'ai_coach_service missing justification enforcer (INV-081)'; assert 'recognition' in svc.lower() or 'reconhec' in svc.lower() or 'privacy' in svc.lower(), 'ai_coach_service missing recognition privacy filter (INV-079)'; assert os.path.exists(os.path.join(b,'app','api','v1','routers','ai_coach.py')), 'ai_coach router missing'; api=open(os.path.join(b,'app','api','v1','api.py')).read(); assert 'ai_coach' in api, 'ai_coach router not registered in api.py'; fe_page=os.path.join(fe,'src','app','(athlete)','ai-chat'); assert os.path.exists(fe_page), 'FE ai-chat directory missing'; modal=os.path.join(fe,'src','components','training','AICoachDraftModal.tsx'); assert os.path.exists(modal), 'AICoachDraftModal.tsx missing'; print('PASS AR_192')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_192/executor_main.log`

## Rollback Plan (Contrato)
```
git checkout -- Hb Track - Backend/app/services/ai_coach_service.py
git checkout -- Hb Track - Backend/app/api/v1/api.py
git clean -fd Hb Track - Backend/app/api/v1/routers/ai_coach.py
git clean -fd Hb Track - Frontend/src/app/(athlete)/ai-chat
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Notas do Arquiteto
ai_coach_service.py já tem INV-072..075 — NÃO remover nem quebrar esses guards. Apenas adicionar INV-079/080/081 como extensão. Contratos FE: CONTRACT-TRAIN-101..104 em TRAINING_FRONT_BACK_CONTRACT.md. Flows: FLOW-TRAIN-019/020 em TRAINING_USER_FLOWS.md. Screens: SCREEN-TRAIN-024/025 em TRAINING_SCREENS_SPEC.md. Executor deve ler todos antes de implementar. AICoachDraftModal DEVE exibir a justificativa da IA de forma proeminente (INV-081: sem justificativa = ideia genérica, não recomendação).

## Riscos
- ai_coach_service.py já tem implementação parcial — Executor deve integrar novos guards sem quebrar os anteriores
- INV-079: conteúdo íntimo definido em INV-073 — Executor ler INV-073 para entender o que é 'íntimo'
- FE ai-chat: rota (athlete)/ai-chat/[sessionId] — confirmar que middleware/auth permite acesso de atleta autenticado
- api.py: verificar prefixo do router ai_coach para não colidir com outros routers

## Análise de Impacto

**Inspeção pré-implementação (2026-03-01)**:
- `ai_coach_service.py`: JÁ tem INV-072..075 + INV-077 implementados. Strings presentes: `draft` ✓ (ExtraTrainingDraft, status="draft"), `recognition` ✓ (PostTrainingFeedback.recognition), `privacy` ✓ (filter_privacy). Faltam: `justif` para INV-081 (asserted).
- INV-079: `filter_privacy()` JÁ existe mas filtra mensagem de atleta para o TREINADOR. INV-079 é sobre reconhecimento individual (elogio) — adicionar `filter_recognition_privacy()` separada que usa `INTIMATE_CONTENT_PATTERNS` para filtrar elogios que vazem contexto íntimo.
- INV-080: `ExtraTrainingDraft` (atleta→treino extra) já tem `status='draft'`. Falta: `generate_session_suggestion(coach_id, context)` e `generate_microcycle_suggestion()` para propostas do treinador (também draft-only).
- INV-081: `justif` não presente — adicionar `enforce_justification(content, justification)` que classifica sem justificativa como `label='ideia_generica'`.
- `ai_coach.py` router: não existe — criar.
- FE `(athlete)/ai-chat/[sessionId]/page.tsx`: não existe — criar diretório + arquivo.
- `AICoachDraftModal.tsx`: não existe — criar.
- `api.py`: adicionar import + include_router sem colidir (prefixo `/ai`).

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em b123a58
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import os; b='Hb Track - Backend'; fe='Hb Track - Frontend'; svc=open(os.path.join(b,'app','services','ai_coach_service.py')).read(); assert 'draft' in svc.lower(), 'ai_coach_service missing draft guard (INV-080)'; assert 'justif' in svc.lower(), 'ai_coach_service missing justification enforcer (INV-081)'; assert 'recognition' in svc.lower() or 'reconhec' in svc.lower() or 'privacy' in svc.lower(), 'ai_coach_service missing recognition privacy filter (INV-079)'; assert os.path.exists(os.path.join(b,'app','api','v1','routers','ai_coach.py')), 'ai_coach router missing'; api=open(os.path.join(b,'app','api','v1','api.py')).read(); assert 'ai_coach' in api, 'ai_coach router not registered in api.py'; fe_page=os.path.join(fe,'src','app','(athlete)','ai-chat'); assert os.path.exists(fe_page), 'FE ai-chat directory missing'; modal=os.path.join(fe,'src','components','training','AICoachDraftModal.tsx'); assert os.path.exists(modal), 'AICoachDraftModal.tsx missing'; print('PASS AR_192')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-01T08:49:49.919918+00:00
**Behavior Hash**: 6d1a3cd21aeee79921395e79d6a671e2835e6dc3e81d10f08334851be518db22
**Evidence File**: `docs/hbtrack/evidence/AR_192/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em b123a58
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_192_b123a58/result.json`

### Selo Humano em b123a58
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-03-01T09:02:10.823421+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_192_b123a58/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_192/executor_main.log`
