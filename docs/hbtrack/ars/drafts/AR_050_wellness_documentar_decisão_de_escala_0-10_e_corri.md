# AR_050 — Wellness: documentar decisão de escala 0-10 e corrigir Field descriptions

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.1.0

## Descrição
CONTEXTO (AR_002.5_C): PRD Seção 7 (US-002) especifica 'escala 1-5' mas o DB usa escalas diferentes:
- fatigue_pre: 0-10 (PRD diz 1-5)
- stress_level: 0-10 semântica inversa (0=ótimo, 10=pior)
- muscle_soreness: 0-10 (PRD diz 1-5)
- pain_level: 0-10 (PRD diz 1-5)
- sleep_quality: 1-5 (alinhado com PRD)

DECISÃO ARQUITETURAL (2026-02-22): MANTER escala 0-10 no PostgreSQL. Não há migration. A decisão é de documentação apenas.

AÇÃO DO EXECUTOR em Hb Track - Backend/app/schemas/wellness.py:
1) Verificar que as descriptions dos Fields já refletem os ranges corretos (0-10 vs 1-5). O arquivo já tem ge=0, le=10 nos campos corretos e ge=1, le=5 em sleep_quality.
2) Adicionar comentário de bloco no topo do arquivo documentando a decisão arquitetural:
   # DECISÃO AR_050 (2026-02-22): Manter escala 0-10 para fatigue_pre, stress_level,
   # muscle_soreness, pain_level. sleep_quality permanece 1-5 (alinhado PRD).
   # PRD Seção 7 US-002 deve ser atualizado em próximo ciclo de PRD sync.
3) Garantir que Field(description=...) de cada campo menciona explicitamente o range e a semântica:
   - fatigue: 'Fadiga pré-treino (0-10). 0=sem fadiga, 10=exausto.'
   - stress: 'Humor/Disposição — proxy stress_level (0-10). 0=muito bem, 10=muito estressado. Semântica inversa.'
   - muscle_soreness: 'Dor muscular (0-10). 0=sem dor, 10=dor intensa.'
   - sleep_quality: 'Qualidade do sono (1-5). 1=péssimo, 5=excelente.' (sem mudança)

NAO alterar ge/le nem criar migration — apenas descriptions dos Fields.

## Critérios de Aceite
1) wellness.py contém pelo menos 4 ocorrências de 'ge=0' + 'le=10' (ou '0-10' nas descriptions). 2) sleep_quality mantém ge=1, le=5. 3) Arquivo tem comentário mencionando AR_050 ou a decisão de manter 0-10. 4) python -c 'from app.schemas.wellness import WellnessPreCreate' executa sem ImportError.

## Validation Command (Contrato)
```
python -c "import sys, os, pathlib; os.chdir('Hb Track - Backend'); sys.path.insert(0, '.'); from app.schemas.wellness import WellnessPreBase, WellnessPostBase; src=pathlib.Path('app/schemas/wellness.py').read_text(encoding='utf-8'); scale_refs=src.count('0-10') + src.count('ge=0'); assert scale_refs >= 4, f'FAIL: expected >= 4 scale refs (0-10/ge=0), got {scale_refs}'; assert 'ge=1' in src and 'le=5' in src, 'FAIL: sleep_quality 1-5 not found'; print(f'PASS: wellness.py has {scale_refs} scale refs, sleep_quality 1-5 preserved')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_050_wellness_scale_decision.log`

## Rollback Plan (Contrato)
```
git revert <commit_hash>  # doc-only — apenas atualiza Field descriptions em wellness.py. Nenhum schema.sql ou alembic_state.txt modificado. Nenhuma migration necessária.
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Notas do Arquiteto
Esta task fecha o item pendente AR_002.5_C. Nenhuma alteração de banco. O PRD sync formal fica para próximo ciclo de PRD v2.3.

## Riscos
- Não alterar ge/le — as constraints Pydantic já estão corretas. Apenas descriptions textuais devem mudar.

## Análise de Impacto
**Executor**: Claude Sonnet 4.6 (Modo Executor)
**Data**: 2026-02-22

**Escopo**: `app/schemas/wellness.py` — adicionado comentário de decisão AR_050; descriptions de fatigue (0=sem fadiga, 10=exausto), muscle_soreness (0=sem dor, 10=dor intensa) e sleep_quality (1=péssimo, 5=excelente) atualizadas. ge/le NÃO alterados.

**Impacto**: Melhoria de DX — campo descriptions no OpenAPI agora refletem a semântica real. Fecha AR_002.5_C (divergência de escala PRD vs DB).

---
## Carimbo de Execução
_(Gerado por hb report)_


### Execução em b2e7523
**Status Final**: ✅ SUCESSO
**Comando**: `python -c "import sys, os, pathlib; os.chdir('Hb Track - Backend'); sys.path.insert(0, '.'); from app.schemas.wellness import WellnessPreBase, WellnessPostBase; src=pathlib.Path('app/schemas/wellness.py').read_text(encoding='utf-8'); scale_refs=src.count('0-10') + src.count('ge=0'); assert scale_refs >= 4, f'FAIL: expected >= 4 scale refs (0-10/ge=0), got {scale_refs}'; assert 'ge=1' in src and 'le=5' in src, 'FAIL: sleep_quality 1-5 not found'; print(f'PASS: wellness.py has {scale_refs} scale refs, sleep_quality 1-5 preserved')"`
**Exit Code**: 0
**Evidence File**: `docs/hbtrack/evidence/AR_050_wellness_scale_decision.log`
**Python Version**: 3.11.9


### Verificacao Testador em b2e7523
**Status Testador**: ✅ VERIFICADO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_050_b2e7523/result.json`
