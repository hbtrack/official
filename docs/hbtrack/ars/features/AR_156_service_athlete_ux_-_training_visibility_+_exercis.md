# AR_156 — Service: Athlete UX — training visibility + exercise media

**Status**: 🔲 PENDENTE
**Versão do Protocolo**: 1.3.0

## Descrição
Implementar acesso de leitura do atleta ao calendário de treinos e às mídias de exercícios:

1. INV-068 (atleta vê treino antes): Em training_session_service.py ou router, garantir que atletas com team_registration ativo podem ler (GET) training_session com status IN ('scheduled', 'draft') de sua equipe. Se há guard que bloqueia leitura de rascunho, relaxar para atletas verem 'scheduled' sessions.

2. INV-069 (exercise media via sessão): Em session_exercise_service.py ou exercise_media_service.py, garantir que atleta pode acessar exercise_media de exercícios incluídos em sessions de sua equipe. Acesso via: GET /sessions/{session_id}/exercises/{exercise_id}/media. Verificar que o acesso NÃO está bloqueado por visibility_mode se o exercício já está na sessão (exercise was added by coach = implicit access for session athletes).

## Critérios de Aceite
1. Atleta com team_registration ativo pode GET session com status='scheduled'. 2. Atleta sem team_registration da equipe não pode ver a sessão (403). 3. Atleta pode GET exercise_media para exercícios de sessions de sua equipe. 4. Atleta de outra equipe não pode acessar media de sessão não sua.

## Write Scope
- Hb Track - Backend/app/services/training_session_service.py
- Hb Track - Backend/app/services/session_exercise_service.py

## Validation Command (Contrato)
```
cd "Hb Track - Backend" && python -m pytest tests/training/invariants/test_inv_train_068_athlete_sees_training.py tests/training/invariants/test_inv_train_069_exercise_media_via_session.py -v --tb=short 2>&1 | Select-String -Pattern 'PASSED|FAILED|ERROR'
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_156/executor_main.log`

## Notas do Arquiteto
Classe D (Router/RBAC) + Classe C2. Depende de Task 144 (exercise_media table existir). Para INV-069, se exercise_media URL é pública (CDN), o acesso é apenas via read do objeto exercise_media record (não download direto). Verificar se há algum guard de signed URL.

## Riscos
- RBAC para atleta pode envolver JWT claims de team_id ou team_registration lookup — verificar padrão de auth do projeto
- Se status='draft' sessões não devem ser visíveis para atletas (apenas 'scheduled'), verificar regra exata em INVARIANTS_TRAINING.md INV-068

## Análise de Impacto
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_

