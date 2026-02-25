# AR_002 — Model: CompetitionStanding.team_id — mapped_column + relationship para Team

**Status**: ✅ SUCESSO
**Versão do Protocolo**: 1.0.6
**Plano Fonte**: `docs/_canon/planos/competition_standings_add_team_id.json`

## Descrição
Atualizar o model SQLAlchemy CompetitionStanding em Hb Track - Backend/app/models/competition_standing.py para refletir a coluna adicionada na task 001. Mudancas necessarias: (1) Adicionar import TYPE_CHECKING para Team se ainda nao existir. (2) Adicionar no bloco HB-AUTOGEN (entre as tags HB-AUTOGEN:BEGIN e HB-AUTOGEN:END) a coluna mapeada: team_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('teams.id', name='fk_competition_standings_team_id', ondelete='SET NULL'), nullable=True). (3) Adicionar relationship: team: Mapped[Optional['Team']] = relationship('Team', back_populates=None) — sem back_populates a menos que o model Team declare standings. (4) Adicionar ao TYPE_CHECKING block: from app.models.team import Team. NAO modificar constraints, outros campos ou logica existente.

## Critérios de Aceite
1) python -c 'import sys; sys.path.insert(0, "Hb Track - Backend"); from app.models.competition_standing import CompetitionStanding; assert hasattr(CompetitionStanding, "team_id"); print("PASS")' retorna exit code 0. 2) O atributo team_id e do tipo Mapped[Optional[UUID]] com nullable=True. 3) O atributo team e um relationship apontando para Team. 4) python -c 'from app.models.competition_standing import CompetitionStanding' nao levanta ImportError nem AttributeError. 5) alembic check nao reporta divergencia entre model e schema (se gate de models estiver disponivel no repo).

## Validation Command (Contrato)
```
python -c "import sys; sys.path.insert(0, 'Hb Track - Backend'); from app.models.competition_standing import CompetitionStanding; assert hasattr(CompetitionStanding, 'team_id'), 'FAIL: team_id not found'; print('PASS: team_id present in CompetitionStanding')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_002/executor_main.log`

## Notas do Arquiteto
A task 002 depende da task 001: o model deve ser atualizado APOS a migration ser aplicada e validada. O bloco HB-AUTOGEN no arquivo e delimitado por comentarios HB-AUTOGEN:BEGIN / HB-AUTOGEN:END — o Executor deve inserir a coluna dentro dessas marcacoes para manter consistencia com o pipeline de autogeneration.

## Riscos
- Se o model Team nao declarar back_populates='standings', o relationship em CompetitionStanding deve usar back_populates=None ou ser omitido — verificar app/models/team.py antes de adicionar relationship.
- O bloco HB-AUTOGEN e marcado como AUTO-GENERATED — alterar manualmente pode entrar em conflito com reruns do autogenerator. Documentar que team_id foi adicionado manualmente fora de ciclo automatico.

## Análise de Impacto
_(Preenchido pelo Executor)_

**Arquivos Modificados:**
- `Hb Track - Backend/app/models/competition_standing.py` (adicionar relationship `team`)

**Impacto Técnico:**
1. **Relação bidirecional**: CompetitionStanding → Team. O relationship permite navegação ORM do standing para o time vinculado.
2. **Back-reference**: Utilizado `back_populates=None` pois o model Team não declara `standings` como relationship recíproco (verificado no código).
3. **Nullabilidade**: O relationship é `Optional` (team pode ser NULL), alinhado com a FK nullable.
4. **Imports**: TYPE_CHECKING já possui `from app.models.team import Team` (linha 48).

**Impacto em SSOTs:**
- ❌ Não toca `schema.sql` (a coluna já existe via AR-001)
- ❌ Não toca `alembic_state.txt` (sem migrations nesta AR)
- ❌ Não toca `openapi.json` (model layer apenas)

**Riscos Mitigados:**
- ✅ A coluna `team_id` já existe no DB (AR-001 já foi executada e verificada)
- ✅ Import de Team já existe no TYPE_CHECKING
- ✅ back_populates=None evita erro de referência circular

**Compatibilidade Reversa:**
- ✅ Adição de relationship **não quebra** código existente que use apenas `team_id`
- ✅ Código que já filtra por `team_id` continua funcionando
- ✅ Lazy loading por padrão (não carrega Team automaticamente)

**Checklist Pré-Execução:**
- [x] AR-001 está ✅ VERIFICADO (coluna team_id existe no DB)
- [x] Model Team importado em TYPE_CHECKING
- [x] Bloco HB-AUTOGEN identificado (linhas 65-125)
- [x] Validation command preparado

---
## Carimbo de Execução
_(Gerado por hb report)_

> 📋 Kanban routing: Executor: Evidence Pack missing or incomplete

### Execução Executor em f8f030f
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import sys; sys.path.insert(0, 'Hb Track - Backend'); from app.models.competition_standing import CompetitionStanding; assert hasattr(CompetitionStanding, 'team_id'), 'FAIL: team_id not found'; print('PASS: team_id present in CompetitionStanding')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-24T23:39:55.577176+00:00
**Behavior Hash**: b4a8f84c31298107daa3def2e6ecc167fb20039b886433e9c7176e2bdf17efb4
**Evidence File**: `docs/hbtrack/evidence/AR_002/executor_main.log`
**Python Version**: 3.11.9

### Selo Humano em f8f030f
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-02-24T23:53:34.565822+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_002_f8f030f/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_002/executor_main.log`

### Verificacao Testador em 529b87c
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_002_529b87c/result.json`
