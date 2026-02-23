# AR_009 — Models: soft delete (deleted_at, deleted_reason) nos 5 models do domínio COMPETITIONS

**Status**: ✅ CONCLUIDO
**Versão do Protocolo**: 1.0.6

## Descrição
Atualizar os 5 models SQLAlchemy para refletir as colunas adicionadas na task 001. Para cada model, dentro do bloco HB-AUTOGEN:BEGIN / HB-AUTOGEN:END:

(1) Adicionar ao __table_args__ a seguinte entrada (manter virgula no final do ultimo item existente):
CheckConstraint("(deleted_at IS NULL AND deleted_reason IS NULL) OR (deleted_at IS NOT NULL AND deleted_reason IS NOT NULL)", name='ck_<table>_deleted_reason')

Onde <table> é o nome da tabela (ex: 'ck_competition_matches_deleted_reason').

(2) Adicionar os campos mapeados APÓS o __table_args__ e antes de HB-AUTOGEN:END:
deleted_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)
deleted_reason: Mapped[Optional[str]] = mapped_column(sa.Text(), nullable=True)

(3) Verificar que 'datetime' está importado de 'datetime' e 'Optional' de 'typing' em cada arquivo. Se ausente, adicionar no bloco HB-AUTOGEN-IMPORTS:BEGIN/END (sa já importado como sqlalchemy).

Arquivos a modificar (somente estes 5):
- Hb Track - Backend/app/models/competition_match.py (tabela: competition_matches, classe: CompetitionMatch)
- Hb Track - Backend/app/models/competition_opponent_team.py (tabela: competition_opponent_teams, classe: CompetitionOpponentTeam)
- Hb Track - Backend/app/models/competition_phase.py (tabela: competition_phases, classe: CompetitionPhase)
- Hb Track - Backend/app/models/match_event.py (tabela: match_events, classe: MatchEvent)
- Hb Track - Backend/app/models/match_roster.py (tabela: match_roster, classe: MatchRoster)

NAO modificar relacionamentos, outros campos, lógica de negócio ou qualquer arquivo fora desta lista.

## Critérios de Aceite
1) python -c (ver validation_command abaixo) retorna exit code 0 e imprime PASS. 2) Os atributos deleted_at e deleted_reason existem em todos os 5 models. 3) Nenhum ImportError ou AttributeError ao importar os 5 models. 4) O __table_args__ de cada model contém o CheckConstraint com nome canônico ck_<table>_deleted_reason. 5) Os campos são Mapped[Optional[datetime]] e Mapped[Optional[str]] com nullable=True.

## Validation Command (Contrato)
```
python -c "import sys; sys.path.insert(0, 'Hb Track - Backend'); from app.models.competition_match import CompetitionMatch; from app.models.competition_opponent_team import CompetitionOpponentTeam; from app.models.competition_phase import CompetitionPhase; from app.models.match_event import MatchEvent; from app.models.match_roster import MatchRoster; models=[CompetitionMatch,CompetitionOpponentTeam,CompetitionPhase,MatchEvent,MatchRoster]; errs=[f'{m.__name__}:missing {f}' for m in models for f in ['deleted_at','deleted_reason'] if not hasattr(m,f)]; [print(e) for e in errs]; sys.exit(len(errs)) if errs else print('PASS: deleted_at+deleted_reason present in all 5 models')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_009_comp_db_001_soft_delete_models.log`

## Notas do Arquiteto
Task 002 depende da task 001: o model deve ser atualizado APÓS a migration ser aplicada e validada. O bloco HB-AUTOGEN é marcado como AUTO-GENERATED — documentar que deleted_at/deleted_reason foram adicionados no ciclo COMP-DB-001 fora de ciclo automático. match_event.py já tem vários CheckConstraints em __table_args__ — adicionar o novo como último item antes do fechamento da tupla.

## Riscos
- match_event.py já contém __table_args__ com 7 CheckConstraints existentes — adicionar o ck_match_events_deleted_reason como 8o item sem remover os existentes.
- Se competition_phase.py não tiver 'datetime' importado no bloco HB-AUTOGEN-IMPORTS, adicionar: from datetime import datetime antes de fechar o bloco.
- O bloco HB-AUTOGEN é auto-gerado — alterar manualmente pode ser sobrescrito em reruns do pipeline. Documentar em notes do commit que esta alteração é manual de ciclo COMP-DB-001.

## Análise de Impacto
- Arquivos afetados: [Hb Track - Backend/app/models/competition_match.py, Hb Track - Backend/app/models/competition_opponent_team.py, Hb Track - Backend/app/models/competition_phase.py, Hb Track - Backend/app/models/match_event.py, Hb Track - Backend/app/models/match_roster.py]
- Mudança no Schema? [Não]
- Risco de Regressão? [Baixo]

---
## Carimbo de Execução
_(Gerado por hb report)_



### Execução em b2e7523
**Status Final**: ✅ SUCESSO
**Comando**: `python -c "import sys; sys.path.insert(0, 'Hb Track - Backend'); from app.models.competition_match import CompetitionMatch; from app.models.competition_opponent_team import CompetitionOpponentTeam; from app.models.competition_phase import CompetitionPhase; from app.models.match_event import MatchEvent; from app.models.match_roster import MatchRoster; models=[CompetitionMatch,CompetitionOpponentTeam,CompetitionPhase,MatchEvent,MatchRoster]; errs=[f'{m.__name__}:missing {f}' for m in models for f in ['deleted_at','deleted_reason'] if not hasattr(m,f)]; [print(e) for e in errs]; sys.exit(len(errs)) if errs else print('PASS: deleted_at+deleted_reason present in all 5 models')"`
**Exit Code**: 0
**Evidence File**: `docs/hbtrack/evidence/AR_009_comp_db_001_soft_delete_models.log`
**Python Version**: 3.11.9


