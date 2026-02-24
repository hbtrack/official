# AR_039 — Model: CompetitionStanding — UniqueConstraint legado → NULLS NOT DISTINCT

**Status**: ✅ SUCESSO
**Versão do Protocolo**: 1.1.0

## Descrição
Atualizar Hb Track - Backend/app/models/competition_standing.py para refletir o novo constraint.
Dentro do bloco HB-AUTOGEN:BEGIN/END, no __table_args__ (linhas ~69-79):

  REMOVER:
    UniqueConstraint('competition_id', 'phase_id', 'opponent_team_id', name='uk_competition_standings_team_phase')

  ADICIONAR (mesma posição, antes dos Index entries):
    UniqueConstraint('competition_id', 'phase_id', 'opponent_team_id',
                     name='uq_competition_standings_comp_phase_opponent',
                     postgresql_nulls_not_distinct=True)

UniqueConstraint já está importado na linha 31: from sqlalchemy import ForeignKey, CheckConstraint, Index, UniqueConstraint.
NAO alterar outros campos, relationships, indexes (ix_competition_standings_*) ou lógica fora do bloco HB-AUTOGEN.

## Critérios de Aceite
1) python -c 'import sys; sys.path.insert(0, "Hb Track - Backend"); from app.models.competition_standing import CompetitionStanding; args=CompetitionStanding.__table_args__; names=[getattr(a,"name",None) for a in args]; assert "uq_competition_standings_comp_phase_opponent" in names, "FAIL"; print("PASS")' retorna exit_code=0. 2) uk_competition_standings_team_phase NÃO está mais em __table_args__. 3) from app.models.competition_standing import CompetitionStanding não levanta ImportError.

## Validation Command (Contrato)
```
python -c "import sys; sys.path.insert(0, 'Hb Track - Backend'); from app.models.competition_standing import CompetitionStanding; args=CompetitionStanding.__table_args__; names=[getattr(a,'name',None) for a in args]; old='uk_competition_standings_team_phase'; new='uq_competition_standings_comp_phase_opponent'; errs=[]; (errs.append(f'OLD still present: {old}') if old in names else None); (errs.append(f'NEW missing: {new}') if new not in names else None); [print(e) for e in errs]; sys.exit(len(errs)) if errs else print('PASS')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_039/executor_main.log`

## Rollback Plan (Contrato)
```
git revert HEAD  # se já commitado: desfaz o commit que atualizou o UniqueConstraint
# OU, antes de commit:
git restore 'Hb Track - Backend/app/models/competition_standing.py'
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Riscos
- Se competition_standing.py não tiver UniqueConstraint importado explicitamente, adicionar sem remover imports existentes. (Verificado: já importado na linha 31).
- O bloco HB-AUTOGEN é auto-gerado — documentar em commit que a alteração é manual do ciclo COMP-DB-004.
- postgresql_nulls_not_distinct=True no UniqueConstraint do model requer SQLAlchemy 2.0.8+. SQLAlchemy 2.0.45 instalado (conforme Ambiente.md) — compatível.

## Análise de Impacto
**Executor**: Roo (💻 Code Mode)
**Data**: 2026-02-22

**Escopo da Implementação**:
1. **Atualizar Hb Track - Backend/app/models/competition_standing.py**: Substituído o `UniqueConstraint` legado `uk_competition_standings_team_phase` pelo novo `uq_competition_standings_comp_phase_opponent`.
2. **PostgreSQL NULLS NOT DISTINCT**: Adicionado o parâmetro `postgresql_nulls_not_distinct=True` ao modelo ORM para espelhar a migração `AR_038`.
3. **Conformidade**: Mantido dentro do bloco `HB-AUTOGEN:BEGIN/END` para consistência com o gerador de SSOT.

**Impacto**:
- Sincronização total entre o modelo SQLAlchemy e o schema do banco de dados PostgreSQL.
- Prevenção de inconsistências de dados ao tratar múltiplos valores NULL como duplicatas no índice de unicidade.
- Compatibilidade mantida com SQLAlchemy 2.0.45.

**Conclusão**: O modelo de standings agora impõe unicidade estrita mesmo para competições sem fases definidas.

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução em b2e7523
**Status Final**: ✅ SUCESSO
**Comando**: `python -c "import sys; sys.path.insert(0, 'Hb Track - Backend'); from app.models.competition_standing import CompetitionStanding; args=CompetitionStanding.__table_args__; names=[getattr(a,'name',None) for a in args]; old='uk_competition_standings_team_phase'; new='uq_competition_standings_comp_phase_opponent'; errs=[]; (errs.append(f'OLD still present: {old}') if old in names else None); (errs.append(f'NEW missing: {new}') if new not in names else None); [print(e) for e in errs]; sys.exit(len(errs)) if errs else print('PASS')"`
**Exit Code**: 0
**Evidence File**: `docs/hbtrack/evidence/AR_039/executor_main.log`
**Python Version**: 3.11.9

### Execução em b2e7523
**Status Final**: ✅ SUCESSO
**Comando**: `python -c "import sys; sys.path.insert(0, 'Hb Track - Backend'); from app.models.competition_standing import CompetitionStanding; args=CompetitionStanding.__table_args__; names=[getattr(a,'name',None) for a in args]; old='uk_competition_standings_team_phase'; new='uq_competition_standings_comp_phase_opponent'; errs=[]; (errs.append(f'OLD still present: {old}') if old in names else None); (errs.append(f'NEW missing: {new}') if new not in names else None); [print(e) for e in errs]; sys.exit(len(errs)) if errs else print('PASS')"`
**Exit Code**: 0
**Evidence File**: `docs/hbtrack/evidence/AR_039/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em 38b62a5
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import sys; sys.path.insert(0, 'Hb Track - Backend'); from app.models.competition_standing import CompetitionStanding; args=CompetitionStanding.__table_args__; names=[getattr(a,'name',None) for a in args]; old='uk_competition_standings_team_phase'; new='uq_competition_standings_comp_phase_opponent'; errs=[]; (errs.append(f'OLD still present: {old}') if old in names else None); (errs.append(f'NEW missing: {new}') if new not in names else None); [print(e) for e in errs]; sys.exit(len(errs)) if errs else print('PASS')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-24T17:11:05.142469+00:00
**Behavior Hash**: 01c8ecaaa6931b085591c0b4bfd55c9f076a6af3c37b9a610d0f1a8306848740
**Evidence File**: `docs/hbtrack/evidence/AR_039/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em 38b62a5
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import sys; sys.path.insert(0, 'Hb Track - Backend'); from app.models.competition_standing import CompetitionStanding; args=CompetitionStanding.__table_args__; names=[getattr(a,'name',None) for a in args]; old='uk_competition_standings_team_phase'; new='uq_competition_standings_comp_phase_opponent'; errs=[]; (errs.append(f'OLD still present: {old}') if old in names else None); (errs.append(f'NEW missing: {new}') if new not in names else None); [print(e) for e in errs]; sys.exit(len(errs)) if errs else print('PASS')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-24T17:11:59.341179+00:00
**Behavior Hash**: 01c8ecaaa6931b085591c0b4bfd55c9f076a6af3c37b9a610d0f1a8306848740
**Evidence File**: `docs/hbtrack/evidence/AR_039/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em 93156e7
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_039_93156e7/result.json`
