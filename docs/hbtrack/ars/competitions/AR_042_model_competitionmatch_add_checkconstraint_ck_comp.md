# AR_042 — Model CompetitionMatch: ADD CheckConstraint ck_competition_matches_status

**Status**: 🏗️ EM_EXECUCAO
**Versão do Protocolo**: 1.1.0

## Descrição
Atualizar Hb Track - Backend/app/models/competition_match.py.
Dentro do bloco HB-AUTOGEN:BEGIN/END, no __table_args__, adicionar o CheckConstraint de status como primeiro elemento (antes dos Index entries):

  CheckConstraint("status IN ('scheduled', 'in_progress', 'finished', 'cancelled')", name='ck_competition_matches_status'),

CheckConstraint já está importado (linha 41 do bloco HB-AUTOGEN-IMPORTS). NÃO alterar o bloco de imports. NÃO alterar outros campos, Index entries, relationships, deleted_at/deleted_reason ou lógica fora do bloco HB-AUTOGEN.

## Critérios de Aceite
1) python -c 'import sys; sys.path.insert(0,"Hb Track - Backend"); from app.models.competition_match import CompetitionMatch; args=CompetitionMatch.__table_args__; names=[getattr(a,"name",None) for a in args]; assert "ck_competition_matches_status" in names,f"FAIL: not found, got {names}"; print("PASS")' retorna exit_code=0. 2) from app.models.competition_match import CompetitionMatch não levanta ImportError.

## Validation Command (Contrato)
```
python -c "import sys; sys.path.insert(0, 'Hb Track - Backend'); from app.models.competition_match import CompetitionMatch; args=CompetitionMatch.__table_args__; names=[getattr(a,'name',None) for a in args]; check='ck_competition_matches_status'; assert check in names,f'FAIL: {check} not in __table_args__. Current: {names}'; print(f'PASS: {check} present in CompetitionMatch.__table_args__')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_042/executor_main.log`

## Rollback Plan (Contrato)
```
git revert HEAD  # se já commitado: desfaz o commit que adicionou o CheckConstraint
# OU, antes de commit:
git restore 'Hb Track - Backend/app/models/competition_match.py'
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Riscos
- O bloco HB-AUTOGEN é marcado como AUTO-GENERATED — alterar manualmente requer documentação explícita no commit (ciclo COMP-DB-006).
- Se a migration 0058 (AR_040) não tiver sido aplicada ao banco, o model terá constraint que o DB não conhece — inconsistência aceitável em DEV.
- A vírgula após o CheckConstraint no __table_args__ é obrigatória para tuple Python válida.
- competition_match.py já possui deleted_at e deleted_reason (AR_009 aplicado). Verificar que os campos de soft delete estão intactos após a edição.

## Análise de Impacto
**Executor**: Roo (💻 Code Mode)
**Data**: 2026-02-22

**Escopo da Implementação**:
1. **Atualizar Hb Track - Backend/app/models/competition_match.py**: Inserido o `CheckConstraint` `ck_competition_matches_status` no `__table_args__`.
2. **Sincronização com DB**: O constraint reflete a regra de domínio para os estados válidos de um jogo (`scheduled`, `in_progress`, `finished`, `cancelled`), conforme implementado na migration `AR_040`.
3. **Integridade ORM**: Adiciona uma camada de proteção no SQLAlchemy para validar o status antes do commit no banco.

**Impacto**:
- Alinhamento entre modelo ORM e restrições de banco.
- Proteção contra estados de jogo inválidos.
- Sem mudanças em campos de auditoria ou soft delete.

**Conclusão**: O modelo `CompetitionMatch` agora valida o ciclo de vida dos jogos de forma declarativa.

---
## Carimbo de Execução
_(Gerado por hb report)_


### Execução em b2e7523
**Status Final**: ✅ SUCESSO
**Comando**: `python -c "import sys; sys.path.insert(0, 'Hb Track - Backend'); from app.models.competition_match import CompetitionMatch; args=CompetitionMatch.__table_args__; names=[getattr(a,'name',None) for a in args]; check='ck_competition_matches_status'; assert check in names,f'FAIL: {check} not in __table_args__. Current: {names}'; print(f'PASS: {check} present in CompetitionMatch.__table_args__')"`
**Exit Code**: 0
**Evidence File**: `docs/hbtrack/evidence/AR_042/executor_main.log`
**Python Version**: 3.11.9


### Execução Executor em 38b62a5
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import sys; sys.path.insert(0, 'Hb Track - Backend'); from app.models.competition_match import CompetitionMatch; args=CompetitionMatch.__table_args__; names=[getattr(a,'name',None) for a in args]; check='ck_competition_matches_status'; assert check in names,f'FAIL: {check} not in __table_args__. Current: {names}'; print(f'PASS: {check} present in CompetitionMatch.__table_args__')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-24T17:11:07.926910+00:00
**Behavior Hash**: ada5d4e734ecac5dc87786a5582ed7256eb7bfd0dd75e4f79b63861d6fc8f363
**Evidence File**: `docs/hbtrack/evidence/AR_042/executor_main.log`
**Python Version**: 3.11.9


### Execução Executor em 38b62a5
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import sys; sys.path.insert(0, 'Hb Track - Backend'); from app.models.competition_match import CompetitionMatch; args=CompetitionMatch.__table_args__; names=[getattr(a,'name',None) for a in args]; check='ck_competition_matches_status'; assert check in names,f'FAIL: {check} not in __table_args__. Current: {names}'; print(f'PASS: {check} present in CompetitionMatch.__table_args__')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-24T17:12:02.239503+00:00
**Behavior Hash**: ada5d4e734ecac5dc87786a5582ed7256eb7bfd0dd75e4f79b63861d6fc8f363
**Evidence File**: `docs/hbtrack/evidence/AR_042/executor_main.log`
**Python Version**: 3.11.9

