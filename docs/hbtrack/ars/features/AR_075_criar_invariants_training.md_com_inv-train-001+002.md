# AR_075 — Criar INVARIANTS_TRAINING.md com INV-TRAIN-001+002+003

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
CRIAR novo arquivo docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md com 3 invariantes do modulo de treinos. Usar formato SPEC YAML v1.0 (idem demais modulos). ATENCAO: existe INVARIANTES_TREINOS.md (formato tabular legado) - o novo arquivo e diferente, NAO sobrescrever.

INV-TRAIN-001 (class B - Trigger): fn_invalidate_analytics_cache
- Trigger tr_invalidate_analytics_cache dispara AFTER INSERT OR DELETE OR UPDATE em training_sessions, chamando fn_invalidate_analytics_cache() para invalidar cache de analytics.
- Evidence: schema.sql:5314 - CREATE TRIGGER tr_invalidate_analytics_cache AFTER INSERT OR DELETE OR UPDATE ON training_sessions
- Status: IMPLEMENTADO

INV-TRAIN-002 (class C1 - Servico puro): team_registrations - Multiplos Vinculos Ativos (V1.2)
- A partir da V1.2, multiplos vinculos ativos simultaneos sao PERMITIDOS em team_registrations. Regra de nao-sobreposicao RDB10 foi REVOGADA. Servico NAO deve bloquear insercao de novo vinculo ativo.
- Evidence: schema.sql COMMENT ON TABLE team_registrations (V1.2: multiplos vinculos ativos simultaneos permitidos)
- Status: IMPLEMENTADO (V1.2 revogou RDB10)

INV-TRAIN-003 (class A - DB Constraint): 1 Wellness por Atleta/Sessao (UNIQUE INDEX)
- ux_wellness_pre_session_athlete e ux_wellness_post_session_athlete garantem no maximo 1 registro wellness pre e 1 post por atleta por sessao (soft-delete aware: WHERE deleted_at IS NULL).
- Evidence: schema.sql:5286 - ux_wellness_post_session_athlete; schema.sql:5293 - ux_wellness_pre_session_athlete
- Status: IMPLEMENTADO

## Critérios de Aceite
1. Arquivo docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md criado (novo arquivo).
2. Contem INV-TRAIN-001, INV-TRAIN-002 e INV-TRAIN-003.
3. INV-TRAIN-001 referencia invalidate_analytics_cache (trigger).
4. INV-TRAIN-002 referencia team_registrations e V1.2.
5. INV-TRAIN-003 referencia ux_wellness e UNIQUE INDEX.
6. INVARIANTES_TREINOS.md (legado) NAO modificado.

## Validation Command (Contrato)
```
python -c "import pathlib; src=pathlib.Path('docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md').read_text(encoding='utf-8'); assert 'INV-TRAIN-001' in src, 'FAIL INV-TRAIN-001'; assert 'INV-TRAIN-002' in src, 'FAIL INV-TRAIN-002'; assert 'INV-TRAIN-003' in src, 'FAIL INV-TRAIN-003'; assert 'invalidate_analytics_cache' in src, 'FAIL trigger ausente'; assert 'team_registrations' in src, 'FAIL team_registrations'; assert 'ux_wellness' in src, 'FAIL wellness index'; assert 'V1.2' in src, 'FAIL V1.2 revogacao'; print('PASS: INVARIANTS_TRAINING INV-TRAIN-001+002+003 OK')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_075/executor_main.log`

## Notas do Arquiteto
Criar novo arquivo INVARIANTS_TRAINING.md (padrao portugues, formato SPEC YAML v1.0). Manter INVARIANTES_TREINOS.md intacto - e um arquivo legado diferente.

## Análise de Impacto
**Executor**: 2026-02-24

**Escopo**: Documentação pura - CRIAR novo arquivo INVARIANTS_TRAINING.md (módulo treinos).

**Riscos**:
- **BAIXO**: Criação de novo arquivo .md fora dos governed roots.
- **ATENÇÃO**: Existe arquivo legado INVARIANTES_TREINOS.md (formato tabular) — NÃO sobrescrever.

**Dependências**:
- Diretório: `docs/hbtrack/modulos/treinos/` (a criar se não existir)
- Formato: SPEC YAML v1.0 (padrão existente em INVARIANTS_COMPETITIONS.md e INVARIANTS_SCOUT.md)
- Arquivo legado: `docs/hbtrack/INVARIANTES_TREINOS.md` (manter intacto)

**Patch**:
- 1 diretório criado (se não existir): docs/hbtrack/modulos/treinos/
- 1 arquivo novo: INVARIANTS_TRAINING.md (~80 linhas)

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em c5f1ba8
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import pathlib; src=pathlib.Path('docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md').read_text(encoding='utf-8'); assert 'INV-TRAIN-001' in src, 'FAIL INV-TRAIN-001'; assert 'INV-TRAIN-002' in src, 'FAIL INV-TRAIN-002'; assert 'INV-TRAIN-003' in src, 'FAIL INV-TRAIN-003'; assert 'invalidate_analytics_cache' in src, 'FAIL trigger ausente'; assert 'team_registrations' in src, 'FAIL team_registrations'; assert 'ux_wellness' in src, 'FAIL wellness index'; assert 'V1.2' in src, 'FAIL V1.2 revogacao'; print('PASS: INVARIANTS_TRAINING INV-TRAIN-001+002+003 OK')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-24T22:40:44.949766+00:00
**Behavior Hash**: 7af66b83b1580fdb72f0a1aff1e8e9ed051ced7e4113d5cca6c1998f6d34094a
**Evidence File**: `docs/hbtrack/evidence/AR_075/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em c5f1ba8
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_075_c5f1ba8/result.json`

### Selo Humano em c5f1ba8
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-02-24T22:55:06.480327+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_075_c5f1ba8/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_075/executor_main.log`
