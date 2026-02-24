# AR_037 — Model: Competition.points_per_draw + Competition.points_per_loss em competition.py

**Status**: 🏗️ EM_EXECUCAO
**Versão do Protocolo**: 1.1.0

## Descrição
Atualizar Hb Track - Backend/app/models/competition.py para refletir as colunas adicionadas na task AR_036.
Dentro do bloco HB-AUTOGEN:BEGIN/END, após a linha de points_per_win (linha ~120), adicionar:

  points_per_draw: Mapped[int] = mapped_column(sa.Integer(), nullable=False, server_default=sa.text('1'))

  points_per_loss: Mapped[int] = mapped_column(sa.Integer(), nullable=False, server_default=sa.text('0'))

Verificar que imports já presentes: sa (sqlalchemy), Mapped, mapped_column.
NAO alterar __table_args__, outros campos, relationships ou lógica fora do bloco HB-AUTOGEN.

## Critérios de Aceite
1) python -c 'import sys; sys.path.insert(0, "Hb Track - Backend"); from app.models.competition import Competition; assert hasattr(Competition, "points_per_draw"); assert hasattr(Competition, "points_per_loss"); print("PASS")' retorna exit_code=0. 2) Campos são Mapped[int] com nullable=False e server_default='1'/'0'. 3) from app.models.competition import Competition não levanta ImportError nem AttributeError.

## Validation Command (Contrato)
```
python -c "import sys; sys.path.insert(0, 'Hb Track - Backend'); from app.models.competition import Competition; fields=['points_per_draw','points_per_loss']; missing=[f for f in fields if not hasattr(Competition,f)]; assert not missing,f'FAIL: missing fields {missing}'; print(f'PASS: {fields} present in Competition')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_037/executor_main.log`

## Rollback Plan (Contrato)
```
git revert HEAD  # se já commitado: desfaz o commit que adicionou os campos
# OU, antes de commit:
git restore 'Hb Track - Backend/app/models/competition.py'
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Riscos
- O bloco HB-AUTOGEN é marcado como AUTO-GENERATED — alterar manualmente pode ser sobrescrito em reruns do autogenerator. Documentar em commit que points_per_draw/points_per_loss foram adicionados no ciclo COMP-DB-003.
- Garantir que Mapped[int] (não Optional) está correto dado nullable=False — não introduzir Optional desnecessário.

## Análise de Impacto
**Executor**: Roo (💻 Code Mode)
**Data**: 2026-02-22

**Escopo da Implementação**:
1. **Atualizar Hb Track - Backend/app/models/competition.py**: Inseridas as colunas `points_per_draw` e `points_per_loss` dentro do bloco `HB-AUTOGEN`.
   - `points_per_draw`: Mapped[int] com `server_default='1'`.
   - `points_per_loss`: Mapped[int] com `server_default='0'`.
2. **Sincronização**: As colunas refletem a alteração de banco realizada na task `AR_036`.

**Impacto**:
- Alinhamento do modelo ORM com o novo schema de banco de dados.
- Permite que os serviços de negócio utilizem a pontuação configurável por competição.
- Sem efeitos colaterais em relacionamentos ou lógica existente.

**Conclusão**: O modelo `Competition` agora suporta regras de pontuação customizadas para empates e derrotas.

---
## Carimbo de Execução
_(Gerado por hb report)_


### Execução em b2e7523
**Status Final**: ✅ SUCESSO
**Comando**: `python -c "import sys; sys.path.insert(0, 'Hb Track - Backend'); from app.models.competition import Competition; fields=['points_per_draw','points_per_loss']; missing=[f for f in fields if not hasattr(Competition,f)]; assert not missing,f'FAIL: missing fields {missing}'; print(f'PASS: {fields} present in Competition')"`
**Exit Code**: 0
**Evidence File**: `docs/hbtrack/evidence/AR_037/executor_main.log`
**Python Version**: 3.11.9


### Execução Executor em 38b62a5
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import sys; sys.path.insert(0, 'Hb Track - Backend'); from app.models.competition import Competition; fields=['points_per_draw','points_per_loss']; missing=[f for f in fields if not hasattr(Competition,f)]; assert not missing,f'FAIL: missing fields {missing}'; print(f'PASS: {fields} present in Competition')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-24T17:11:03.495364+00:00
**Behavior Hash**: 37b8d7a8a18998ca710e9b5bf95672082bc871540684a61fe5a63f6a341fdca5
**Evidence File**: `docs/hbtrack/evidence/AR_037/executor_main.log`
**Python Version**: 3.11.9


### Execução Executor em 38b62a5
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import sys; sys.path.insert(0, 'Hb Track - Backend'); from app.models.competition import Competition; fields=['points_per_draw','points_per_loss']; missing=[f for f in fields if not hasattr(Competition,f)]; assert not missing,f'FAIL: missing fields {missing}'; print(f'PASS: {fields} present in Competition')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-24T17:11:57.572883+00:00
**Behavior Hash**: 37b8d7a8a18998ca710e9b5bf95672082bc871540684a61fe5a63f6a341fdca5
**Evidence File**: `docs/hbtrack/evidence/AR_037/executor_main.log`
**Python Version**: 3.11.9

