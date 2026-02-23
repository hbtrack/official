# AR_048 — Criar INVARIANTS_COMPETITIONS.md (INV-COMP-001 a INV-COMP-004)

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.1.0

## Descrição
CONTEXTO: As invariantes do módulo Competitions existem apenas no código (models Python e migrations SQL) mas não estão documentadas em arquivo canônico de invariantes. Esta AR materializa as 4 principais invariantes observadas na auditoria senior.

AÇÃO: Criar o arquivo docs/hbtrack/modulos/competitions/INVARIANTS_COMPETITIONS.md com exatamente 4 blocos de invariante no formato YAML SPEC v1.0.

INV-COMP-001 (Classe A — DB constraint):
  id: INV-COMP-001
  name: ck_competitions_status
  rule: status IN ('draft', 'active', 'finished', 'cancelled')
  table: competitions
  constraint: ck_competitions_status
  evidence: Hb Track - Backend/app/models/competition.py:84
  rationale: Competição passa por ciclo de vida controlado. 'cancelled' é terminal.

INV-COMP-002 (Classe A — DB constraint):
  id: INV-COMP-002
  name: ck_competitions_modality
  rule: modality IN ('masculino', 'feminino', 'misto')
  table: competitions
  constraint: ck_competitions_modality
  evidence: Hb Track - Backend/app/models/competition.py:86
  rationale: Modalidade esportiva determina elegibilidade de atletas.

INV-COMP-003 (Classe A+B — DB constraint + trigger):
  id: INV-COMP-003
  name: ck_competition_matches_soft_delete_pair
  rule: (deleted_at IS NULL AND deleted_reason IS NULL) OR (deleted_at IS NOT NULL AND deleted_reason IS NOT NULL)
  tables: competition_matches, competition_opponent_teams, competition_phases, match_events, match_roster
  constraints: ck_{table}_deleted_reason (5 constraints)
  triggers: trg_{table}_block_delete (5 triggers)
  evidence: Hb Track - Backend/db/alembic/versions/0055_comp_db_001_soft_delete_competition_tables.py
  rationale: Soft delete atômico — remoção física bloqueada por trigger; razão obrigatória.

INV-COMP-004 (Classe A — DB constraint):
  id: INV-COMP-004
  name: uq_competition_standings_comp_phase_opponent
  rule: UNIQUE (competition_id, phase_id, opponent_team_id) NULLS NOT DISTINCT
  table: competition_standings
  constraint: uq_competition_standings_comp_phase_opponent
  evidence: Hb Track - Backend/app/models/competition_standing.py:71-73
  rationale: Classificação é única por equipe × fase. phase_id NULL = classificação geral (permitido uma vez por equipe).

Criar também o diretório docs/hbtrack/modulos/competitions/ se não existir.

## Critérios de Aceite
1) Arquivo docs/hbtrack/modulos/competitions/INVARIANTS_COMPETITIONS.md existe. 2) Contém exatamente os blocos INV-COMP-001, INV-COMP-002, INV-COMP-003, INV-COMP-004. 3) Cada bloco tem campos: id, name, rule, evidence. 4) Arquivo tem mais de 400 bytes.

## Validation Command (Contrato)
```
python -c "import pathlib; p=pathlib.Path('docs/hbtrack/modulos/competitions/INVARIANTS_COMPETITIONS.md'); assert p.exists(), f'FAIL: {p} not found'; content=p.read_text(encoding='utf-8'); missing=[inv for inv in ['INV-COMP-001','INV-COMP-002','INV-COMP-003','INV-COMP-004'] if inv not in content]; assert not missing, f'FAIL: missing invariants: {missing}'; assert p.stat().st_size > 400, f'FAIL: file too small ({p.stat().st_size} bytes)'; print(f'PASS: INVARIANTS_COMPETITIONS.md exists with all 4 INVs ({p.stat().st_size} bytes)')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_048_invariants_competitions.log`

## Rollback Plan (Contrato)
```
git revert <commit_hash>  # doc-only — nenhum schema.sql ou alembic_state.txt modificado. Apenas cria docs/hbtrack/modulos/competitions/INVARIANTS_COMPETITIONS.md. Rollback = git revert do commit ou deletar o arquivo.
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Notas do Arquiteto
Evidências de código auditadas: competition.py:82-98, competition_standing.py:70-73, competition_match.py:81-95, migration 0055. INV-COMP-003 cobre 5 tabelas de uma vez (soft delete unificado do domínio competitions/scout).

## Riscos
- Se migration 0055 ainda não foi aplicada no DB local, os triggers da INV-COMP-003 existem apenas no arquivo Python — documentar como 'pendente de aplicação' na INV.
- competition_standings não tem trigger block_delete (foi excluído da migration 0055 por design).

## Análise de Impacto
**Executor**: Claude Sonnet 4.6 (Modo Executor)
**Data**: 2026-02-22

**Escopo**: Criação de `docs/hbtrack/modulos/competitions/INVARIANTS_COMPETITIONS.md` com 4 invariantes (INV-COMP-001 a INV-COMP-004), classes A e A+B. Evidências verificadas contra código-fonte antes de escrever.

**Impacto**: Documentação — nenhum arquivo de produto ou schema alterado.

---
## Carimbo de Execução
_(Gerado por hb report)_


### Execução em b2e7523
**Status Final**: ✅ SUCESSO
**Comando**: `python -c "import pathlib; p=pathlib.Path('docs/hbtrack/modulos/competitions/INVARIANTS_COMPETITIONS.md'); assert p.exists(), f'FAIL: {p} not found'; content=p.read_text(encoding='utf-8'); missing=[inv for inv in ['INV-COMP-001','INV-COMP-002','INV-COMP-003','INV-COMP-004'] if inv not in content]; assert not missing, f'FAIL: missing invariants: {missing}'; assert p.stat().st_size > 400, f'FAIL: file too small ({p.stat().st_size} bytes)'; print(f'PASS: INVARIANTS_COMPETITIONS.md exists with all 4 INVs ({p.stat().st_size} bytes)')"`
**Exit Code**: 0
**Evidence File**: `docs/hbtrack/evidence/AR_048_invariants_competitions.log`
**Python Version**: 3.11.9


### Verificacao Testador em b2e7523
**Status Testador**: ✅ VERIFICADO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_048_b2e7523/result.json`

### Verificacao Testador em b2e7523
**Status Testador**: ✅ VERIFICADO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_048_b2e7523/result.json`
