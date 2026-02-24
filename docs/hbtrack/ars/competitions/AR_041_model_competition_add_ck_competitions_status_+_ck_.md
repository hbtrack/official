# AR_041 — Model Competition: ADD ck_competitions_status + ck_competitions_modality

**Status**: ✅ SUCESSO
**Versão do Protocolo**: 1.1.0

## Descrição
Atualizar Hb Track - Backend/app/models/competition.py.
Dentro do bloco HB-AUTOGEN:BEGIN/END, no __table_args__, adicionar após o CheckConstraint existente (ck_competitions_deleted_reason):

  CheckConstraint("status IN ('draft', 'active', 'finished', 'cancelled')", name='ck_competitions_status'),
  CheckConstraint("modality IN ('masculino', 'feminino', 'misto')", name='ck_competitions_modality'),

CheckConstraint já está importado (linha 39). NÃO alterar ck_competitions_deleted_reason, Index entries, ou qualquer campo/relationship fora do bloco HB-AUTOGEN.

## Critérios de Aceite
1) python -c 'import sys; sys.path.insert(0,"Hb Track - Backend"); from app.models.competition import Competition; args=Competition.__table_args__; names=[getattr(a,"name",None) for a in args]; assert "ck_competitions_status" in names; assert "ck_competitions_modality" in names; assert "ck_competitions_deleted_reason" in names; print("PASS")' retorna exit_code=0. 2) from app.models.competition import Competition não levanta ImportError.

## Validation Command (Contrato)
```
python -c "import sys; sys.path.insert(0, 'Hb Track - Backend'); from app.models.competition import Competition; args=Competition.__table_args__; names=[getattr(a,'name',None) for a in args]; checks=['ck_competitions_status','ck_competitions_modality','ck_competitions_deleted_reason']; missing=[c for c in checks if c not in names]; assert not missing,f'FAIL: missing constraints {missing}'; print(f'PASS: all 3 constraints present in Competition.__table_args__')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_041/executor_main.log`

## Rollback Plan (Contrato)
```
git revert HEAD  # se já commitado: desfaz o commit que adicionou os CheckConstraints
# OU, antes de commit:
git restore 'Hb Track - Backend/app/models/competition.py'
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Riscos
- O bloco HB-AUTOGEN é marcado como AUTO-GENERATED — alterar manualmente requer documentação explícita no commit (ciclo COMP-DB-006).
- Se a migration 0058 (AR_040) não tiver sido aplicada ao banco, o model terá constraints que o DB não conhece — inconsistência aceitável em DEV, mas deve ser resolvida antes de produção.
- A vírgula após cada CheckConstraint no __table_args__ é obrigatória para tuple Python válida.

## Análise de Impacto
**Executor**: Roo (💻 Code Mode)
**Data**: 2026-02-22

**Escopo da Implementação**:
1. **Atualizar Hb Track - Backend/app/models/competition.py**: Inseridos os `CheckConstraint` `ck_competitions_status` e `ck_competitions_modality` no `__table_args__`.
2. **Sincronização com DB**: Os constraints refletem as regras de domínio aplicadas no banco via migration `AR_040`.
3. **Integridade**: Garante que o SQLAlchemy valide os dados de `status` e `modality` antes de tentar persisti-los, provendo erro claro em tempo de execução Python.

**Impacto**:
- Alinhamento entre modelo ORM e restrições de banco.
- Proteção adicional contra estados inválidos.
- Sem mudanças em lógica de queries ou relacionamentos.

**Conclusão**: O modelo `Competition` agora possui validação declarativa de estados e modalidades.

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução em b2e7523
**Status Final**: ✅ SUCESSO
**Comando**: `python -c "import sys; sys.path.insert(0, 'Hb Track - Backend'); from app.models.competition import Competition; args=Competition.__table_args__; names=[getattr(a,'name',None) for a in args]; checks=['ck_competitions_status','ck_competitions_modality','ck_competitions_deleted_reason']; missing=[c for c in checks if c not in names]; assert not missing,f'FAIL: missing constraints {missing}'; print(f'PASS: all 3 constraints present in Competition.__table_args__')"`
**Exit Code**: 0
**Evidence File**: `docs/hbtrack/evidence/AR_041/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em 38b62a5
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import sys; sys.path.insert(0, 'Hb Track - Backend'); from app.models.competition import Competition; args=Competition.__table_args__; names=[getattr(a,'name',None) for a in args]; checks=['ck_competitions_status','ck_competitions_modality','ck_competitions_deleted_reason']; missing=[c for c in checks if c not in names]; assert not missing,f'FAIL: missing constraints {missing}'; print(f'PASS: all 3 constraints present in Competition.__table_args__')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-24T17:11:06.797623+00:00
**Behavior Hash**: 262d70fcacca6bc24f9c722955159989ef795e10d9403fd2bd992abd219bed76
**Evidence File**: `docs/hbtrack/evidence/AR_041/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em 38b62a5
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import sys; sys.path.insert(0, 'Hb Track - Backend'); from app.models.competition import Competition; args=Competition.__table_args__; names=[getattr(a,'name',None) for a in args]; checks=['ck_competitions_status','ck_competitions_modality','ck_competitions_deleted_reason']; missing=[c for c in checks if c not in names]; assert not missing,f'FAIL: missing constraints {missing}'; print(f'PASS: all 3 constraints present in Competition.__table_args__')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-24T17:12:01.100562+00:00
**Behavior Hash**: 262d70fcacca6bc24f9c722955159989ef795e10d9403fd2bd992abd219bed76
**Evidence File**: `docs/hbtrack/evidence/AR_041/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em 4220d7b
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_041_4220d7b/result.json`
