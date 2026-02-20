# AR_002 — Model: CompetitionStanding.team_id — mapped_column + relationship para Team

**Status**: DRAFT
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
`docs/hbtrack/evidence/AR_002_competition_standings_model_team_id.log`

## Notas do Arquiteto
A task 002 depende da task 001: o model deve ser atualizado APOS a migration ser aplicada e validada. O bloco HB-AUTOGEN no arquivo e delimitado por comentarios HB-AUTOGEN:BEGIN / HB-AUTOGEN:END — o Executor deve inserir a coluna dentro dessas marcacoes para manter consistencia com o pipeline de autogeneration.

## Riscos
- Se o model Team nao declarar back_populates='standings', o relationship em CompetitionStanding deve usar back_populates=None ou ser omitido — verificar app/models/team.py antes de adicionar relationship.
- O bloco HB-AUTOGEN e marcado como AUTO-GENERATED — alterar manualmente pode entrar em conflito com reruns do autogenerator. Documentar que team_id foi adicionado manualmente fora de ciclo automatico.

## Análise de Impacto
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_

